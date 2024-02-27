# -*- coding: UTF-8 -*-
import asyncio
import datetime
import hashlib
import json
import os
import re
from os import path

import lxml
import pytz
from bs4 import BeautifulSoup, element
from jinja2 import Template

from config import (DOCS_PATH, GITHUB_PAGES_URL, IGNORE_FILES, OUPUT_PATH,
                    SEASONAL_PATH, TIMEZONE)
from HttpClient import HttpClient
from utils import format_filesize

RETRY_TIMES = 5
ACTIVITY_VOICE_PULL_ENABLE = False  # 是否拉取活动友军语音
CATEGORY_URL = 'https://zh.kcwiki.cn/wiki/Special:前缀索引/季节性/'
ACTIVITY_CATEGORY_URL = 'https://zh.kcwiki.cn/index.php?title=活动限定海域&action=raw'
KCWIKI_URL = 'https://zh.kcwiki.cn/wiki/{}?action=raw'
KCAPI_URL = 'https://bot.kcwiki.moe/seasonal/{}.json'
VoiceMap = {
    'Intro': '入手/登入时', 'Sec1': '秘书舰1', 'Sec2': '秘书舰2', 'Sec3': '秘书舰3', 'ConstComplete': '建造完成',
    'DockComplete': '修复完成', 'Return': '归来', 'Achievement': '战绩', 'Equip1': '装备/改修/改造1', 'Equip2': '装备/改修/改造2',
    'DockLightDmg': '小破入渠', 'DockMedDmg': '中破入渠', 'FleetOrg': '编成', 'Sortie': '出征', 'Battle': '战斗开始', 'Atk1': '攻击1',
    'Atk2': '攻击2', 'NightBattle': '夜战', 'LightDmg1': '小破1', 'LightDmg2': '小破2', 'MedDmg': '中破', 'Sunk': '击沉',
    'MVP': 'MVP', 'Proposal': '结婚', 'LibIntro': '图鉴介绍', 'Equip3': '装备', 'Resupply': '补给', 'SecWed': '秘书舰（婚后）', 'Idle': '放置',
    '0000': '〇〇〇〇时报', '0100': '〇一〇〇时报', '0200': '〇二〇〇时报', '0300': '〇三〇〇时报', '0400': '〇四〇〇时报',
    '0500': '〇五〇〇时报', '0600': '〇六〇〇时报', '0700': '〇七〇〇时报', '0800': '〇八〇〇时报', '0900': '〇九〇〇时报',
    '1000': '一〇〇〇时报', '1100': '一一〇〇时报', '1200': '一二〇〇时报', '1300': '一三〇〇时报', '1400': '一四〇〇时报',
    '1500': '一五〇〇时报', '1600': '一六〇〇时报', '1700': '一七〇〇时报', '1800': '一八〇〇时报', '1900': '一九〇〇时报',
    '2000': '二〇〇〇时报', '2100': '二一〇〇时报', '2200': '二二〇〇时报', '2300': '二三〇〇时报'
}
ARCH_PATTERN = re.compile(r'^[0-9a-z]+-([0-9A-Za-z]+)')

class KcwikiException(Exception):
    pass

class SeasonalCrawler(HttpClient):

    def __init__(self):
        super().__init__()
        self.files = []
        self.categories = []
        self.seasonals = {}
        self.rofiles = []
        self.lofiles = []
        with open(DOCS_PATH + 'seasonal.html', 'r') as fp:
            self.template = Template(fp.read())

    def __get_text(self, node):
        if not node:
            return ''
        if isinstance(node, element.NavigableString):
            return node.string.strip()
        return node.get_text().strip()

    async def _fetch_from_remote(self, url):
        try:
            resp = await self.session.get(url)
            resp.raise_for_status()
            return await resp.text()
        except Exception:
            return ''

    def _get_from_local(self, fpath):
        with open(fpath, 'r', encoding='utf-8') as fp:
            return fp.read()

    async def diff_files(self):
        content = await self._fetch_from_remote(GITHUB_PAGES_URL + 'seasonal/index.html')
        soup = BeautifulSoup(content, 'lxml')
        rfiles = []
        fstats = {}
        for rf in soup.select('#files > li > a'):
            rfname = self.__get_text(rf)
            if not rfname:
                continue
            rfiles.append(rfname)
            fstats[rfname] = -1
        for lf in self.files:
            lfname = lf[0]
            if lfname not in fstats:
                fstats[lfname] = 1
            else:
                fstats[lfname] = 0
        for fname, fstat in fstats.items():
            if fstat == -1:
                self.rofiles.append(fname)
            elif fstat == 1:
                self.lofiles.append(fname)
        return len(self.rofiles) != 0 or len(self.lofiles) != 0
        
    async def diff_all(self):
        for lf in self.files:
            fname = lf[0]
            rtxt = await self._fetch_from_remote(GITHUB_PAGES_URL + '{}{}'.format(SEASONAL_PATH, fname))
            ltxt = self._get_from_local(OUPUT_PATH + SEASONAL_PATH + fname)
            if rtxt != ltxt:
                return True
        return False
    
    async def get_remote_index(self):
        txt = await self._fetch_from_remote(GITHUB_PAGES_URL + 'seasonal/index.html')
        with open(OUPUT_PATH + SEASONAL_PATH + 'index.html', 'w') as fp:
            fp.write(txt)

    async def gen_new_index(self):
        now = datetime.datetime.now(TIMEZONE)
        with open(OUPUT_PATH + SEASONAL_PATH + 'index.html', 'w') as fp:
            fp.write(self.template.render(update=now.strftime('%Y-%m-%d %H:%M:%S'), files=sorted(self.files)))

    async def __get_categories(self):
        resp = await self.session.get(CATEGORY_URL)
        content = await resp.text()
        soup = BeautifulSoup(content, 'lxml')
        categoryies_items = soup.select('#mw-content-text > div.mw-prefixindex-body > ul > li > a')
        for item in categoryies_items:
            category = self.__get_text(item)
            if not category:
                continue
            if category.endswith('特典语音'):  # 不加入特典语音(格式与游戏不符容易报错)
                continue
            self.categories.append(category)

        if ACTIVITY_VOICE_PULL_ENABLE:
            resp = await self.session.get(ACTIVITY_CATEGORY_URL)
            content = await resp.text()
            regex = r'link=([^\|]+)\|class=eventBanner'
            self.categories.extend(re.findall(regex, content))

        # print('Seasonal categories: {}'.format(self.categories))

    async def __process_wikicode(self, key, wiki_txt, isSeasonal=True):
        lines = wiki_txt.split('\n')
        items = []
        tmp = {}
        ok = False
        cnt = 0
        for _line in lines:
            line = _line.strip()
            if not line:
                continue
            if line == '==旧语音==':
                ok = False
                break
            if isSeasonal and line.startswith('{{台词翻译表/页头|type=seasonal}}'):
                ok = True
                continue
            if not isSeasonal and line.startswith('{{台词翻译表/页头}}'):  # 活动语音页面处理
                ok = True
                continue
            
            if line.startswith('{{页尾}}'):
                ok = False
                continue
            if not ok:
                continue
            
            if line.startswith('{{台词翻译表|type=seasonal') or (not isSeasonal and line.startswith('{{台词翻译表')):
                if tmp:
                    items.append(tmp)
                tmp = {}
                continue
            if line.startswith('}}'):
                continue
            line = line[1:]
            attr = ''
            val = ''
            iidx = 0
            while iidx < len(line):
                if line[iidx] == '=':
                    iidx += 1
                    break
                iidx += 1
            attr = line[:iidx - 1].strip()
            attr = re.sub(r'\|', '', attr).strip()  # 处理喜欢在行头写|的情况

            val = line[iidx:].strip()
            val = re.sub(r'<(.*)>.*?</\1>', '', val)
            val = re.sub(r'<.*?/>', '', val)
            val = re.sub(r'<.*?>', '', val)
            val = re.sub(r'{{ruby-zh\|(.*?)\|(.*?)}}', r'\1(\2)', val)
            tmp[attr] = val
        for item in items:
            wid = ''
            arch = ''
            talker_name = ''
            zh = ''
            ja = ''
            try:
                talker_name = item.get('场合', '')
                arch = item['档名']
                wid = item['编号']
                zh = item['中文译文']
                ja = item['日文台词']
            except KeyError:
                print(f'Seasonal: !!! 错误语音 =\n{{季节性前缀 = {key}, 编号 = {wid}, 档名 = {arch}, 对象名 = {talker_name}}}')
                continue
            if wid not in self.seasonals:
                self.seasonals[wid] = {}
            if key not in self.seasonals[wid]:
                self.seasonals[wid][key] = {}
            cnt += 1
            md5hash = hashlib.md5((arch + '.mp3').encode())
            digest = md5hash.hexdigest()
            try:
                res = ARCH_PATTERN.match(arch).group(1)
            except Exception:
                print('Seasonal Voice Exception:', arch)
            vname = '-'
            for k, val in VoiceMap.items():
                if res.startswith(k):
                    vname = val
            self.seasonals[wid][key][arch] = {
                'zh': zh,
                'ja': ja,
                'vname': vname,
                'file': '/{}/{}/{}.mp3'.format(digest[0], digest[:2], arch)
            }
        print('Seasonal:「{}」共{}条语音'.format(key, cnt))

    async def __dump_all_json(self):
        print('Seasonal: generating all.json...')
        file_name = 'all.json'
        with open(OUPUT_PATH + SEASONAL_PATH + file_name, 'w') as fp:
            json.dump(self.seasonals, fp, ensure_ascii=False, sort_keys=True, indent=2)
        file_size = format_filesize(os.path.getsize(OUPUT_PATH + SEASONAL_PATH + file_name))
        self.files.append((file_name, file_size))

    async def __fetch_seasonal(self, category):
        retry = RETRY_TIMES
        wiki_txt = ''
        while retry:
            try:
                resp = await self.session.get(KCWIKI_URL.format(category))
                resp.raise_for_status()
                wiki_txt = await resp.text()
                if retry != RETRY_TIMES:
                    print('Seasonal:「{}」第{}/{}次重试成功'.format(category, RETRY_TIMES - retry, RETRY_TIMES))
                break
            except Exception as e:
                retry -= 1
                print('Seasonal:「{}」开始重试第{}/{}次 原因：{}'.format(category, RETRY_TIMES - retry, RETRY_TIMES, e))
                continue
        isSeasonal = '季节性' in category
        await self.__process_wikicode(category, wiki_txt, isSeasonal=isSeasonal)
        

    async def start(self):
        await self.__get_categories()
        tasks = []
        for category in self.categories:
            tasks.append(asyncio.ensure_future(self.__fetch_seasonal(category)))
        await asyncio.wait(tasks)

        for wiki_id, subtitles in self.seasonals.items():
            if not subtitles:
                continue
            file_name = '{}.json'.format(wiki_id)
            with open(OUPUT_PATH + SEASONAL_PATH + file_name, 'w') as fp:
                json.dump(subtitles, fp, ensure_ascii=False, sort_keys=True, indent=2)
            file_size = format_filesize(os.path.getsize(OUPUT_PATH + SEASONAL_PATH + file_name))
            self.files.append((file_name, file_size))
        await self.__dump_all_json()

        is_filesdiff = await self.diff_files()
        if is_filesdiff:
            if len(self.rofiles):
                print('Seasonal: 共删除{}个文件'.format(len(self.rofiles)))
                for fname in self.rofiles:
                    print('Seasonal: - {}'.format(fname))
            if len(self.lofiles):
                print('Seasonal: 共新增{}个文件'.format(len(self.lofiles)))
                for fname in self.lofiles:
                    print('Seasonal: + {}'.format(fname))
            await self.gen_new_index()
            return
        is_alldiff = await self.diff_all()
        if is_alldiff:
            await self.gen_new_index()
            return
        await self.get_remote_index()  
