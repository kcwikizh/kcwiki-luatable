import asyncio
import json
import lxml
from bs4 import BeautifulSoup, element

from HttpClient import HttpClient
from config import OUPUT_PATH, SEASONAL_PATH

CATEGORY_URL = 'https://zh.kcwiki.org/wiki/Special:前缀索引/季节性/'
KCWIKI_URL = 'https://zh.kcwiki.org/wiki/{}?action=raw'


class SeasonalCrawler(HttpClient):

    def __init__(self):
        super().__init__()
        self.categories = []
        self.seasonals = {}

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
            tmp[attr] = value

        for item in items:
            wiki_id = item['编号']
            arch_name = item['档名']
            if wiki_id not in self.seasonals:
                self.seasonals[wiki_id] = {}
            if key not in self.seasonals[wiki_id]:
                self.seasonals[wiki_id][key] = {}
            if arch_name in self.seasonals[wiki_id][key]:
                continue
            cnt += 1
            self.seasonals[wiki_id][key][arch_name] = item

        print('[SeasonalSubtitles]: {} - {} 条语音。'.format(key, cnt))

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
            tasks.append(asyncio.ensure_future(self.__fetch_seasonal(category)))
        await asyncio.wait(tasks)
        for wiki_id, subtitles in self.seasonals.items():
            with open(OUPUT_PATH + SEASONAL_PATH + '{}.json'.format(wiki_id), 'w') as fp:
                json.dump(subtitles, fp, ensure_ascii=False, sort_keys=True, indent=2)
