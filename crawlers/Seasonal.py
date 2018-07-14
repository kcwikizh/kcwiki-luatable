import asyncio
import datetime
import hashlib
import json
import re

import lxml
import pytz
from bs4 import BeautifulSoup, element
from jinja2 import Template

from config import DOCS_PATH, OUPUT_PATH, SEASONAL_PATH, TIMEZONE
from HttpClient import HttpClient
from utils import to_filesize

CATEGORY_URL = 'https://zh.kcwiki.org/wiki/Special:前缀索引/季节性/'
KCWIKI_URL = 'https://zh.kcwiki.org/wiki/{}?action=raw'
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


class SeasonalCrawler(HttpClient):

    def __init__(self):
        super().__init__()
        self.categories = []
        self.seasonals = {}
        with open(DOCS_PATH + 'seasonal.html', 'r') as fp:
            self.template = Template(fp.read())

    def __get_text(self, node):
        if not node:
            return ''
        if isinstance(node, element.NavigableString):
            return node.string.strip()
        return node.get_text().strip()

    async def __get_categories(self):
        async with self.session.get(CATEGORY_URL) as resp:
            content = await resp.text()
            soup = BeautifulSoup(content, 'lxml')
            categoryies_items = soup.select(
                '#mw-content-text > div.mw-prefixindex-body > ul > li > a')
            for item in categoryies_items:
                category = self.__get_text(item)
                if not category:
                    continue
                self.categories.append(category)

    async def __process_wikicode(self, key, wiki_txt):

        lines = wiki_txt.split('\n')
        items = []
        tmp = {}
        ok = False
        cnt = 0
        for _line in lines:
            line = _line.strip()
            if not line:
                continue
            if line.startswith('{{台词翻译表/页头|type=seasonal}}'):
                ok = True
                continue
            if line.startswith('{{页尾}}'):
                ok = False
                continue
            if not ok:
                continue
            if line.startswith('{{台词翻译表|type=seasonal'):
                if tmp:
                    items.append(tmp)
                tmp = {}
                continue
            if line.startswith('}}'):
                continue
            line = line[1:]
            spt = line.split('=')
            attr = spt[0].strip()
            value = spt[-1].strip()
            if not value:
                value = ''
            value = re.sub(r'<(.*)>.*?</\1>', '', value)
            value = re.sub(r'<.*?/>', '', value)
            value = re.sub(r'<.*?>', '', value)
            value = re.sub(r'{{.*\|(.*?)\|(.*?)}}', r'\1(\2)', value)
            tmp[attr] = value
        for item in items:
            wid = item['编号']
            arch = item['档名']
            zh = item['中文译文']
            ja = item['日文台词']
            if wid not in self.seasonals:
                self.seasonals[wid] = {}
            if key not in self.seasonals[wid]:
                self.seasonals[wid][key] = {}
            if arch in self.seasonals[wid][key]:
                continue
            cnt += 1
            md5hash = hashlib.md5((arch + '.mp3').encode())
            digest = md5hash.hexdigest()
            res = ARCH_PATTERN.match(arch).group(1)
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

        print('Seasonal: {} - {} 条语音。'.format(key, cnt))

    async def __fetch_seasonal(self, category):
        seasonal_key = category[4:]
        async with self.session.get(KCWIKI_URL.format(category)) as resp:
            wiki_txt = await resp.text()
            await self.__process_wikicode(seasonal_key, wiki_txt)

    async def start(self):
        await self.__get_categories()
        await self.__fetch_seasonal('季节性/2013年圣诞节')
        tasks = []
        for category in self.categories:
            tasks.append(asyncio.ensure_future(
                self.__fetch_seasonal(category)))
        await asyncio.wait(tasks)

        files = []
        for wiki_id, subtitles in self.seasonals.items():
            file_name = '{}.json'.format(wiki_id)
            with open(OUPUT_PATH + SEASONAL_PATH + file_name, 'w') as fp:
                data = json.dumps(subtitles, ensure_ascii=False,
                                  sort_keys=True, indent=2)
                file_size = to_filesize(len(data))
                fp.write(data)
                files.append([file_name, file_size])

        now = datetime.datetime.now(TIMEZONE)
        with open(OUPUT_PATH + SEASONAL_PATH + 'index.html', 'w') as fp:
            fp.write(self.template.render(update=now.strftime(
                '%Y-%m-%d %H:%M:%S'), files=sorted(files)))
