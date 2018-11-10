# -*- coding: UTF-8 -*-
import asyncio
import json

from bs4 import BeautifulSoup, element

from config import (DB_PATH, OUPUT_PATH, WIKIWIKI_TRANSLATION,
                    WIKIWIKI_Compare_TABLE, WIKIWIKI_MaxValue_TABLE)
from HttpClient import HttpClient

TRANSLATION = {}

with open(DB_PATH + WIKIWIKI_TRANSLATION, 'r', encoding='utf-8') as fp:
    TRANSLATION = json.load(fp)

class TBlock:
    @staticmethod
    def getInnerText(node):
        if not node:
            return ''
        if isinstance(node, element.NavigableString):
            return node.string.strip()
        return node.get_text().strip()

    def __init__(self, tag, block):
        self.value = self.getInnerText(block)
        if self.value in TRANSLATION:
            self.value = TRANSLATION[self.value]
        self.tag = tag
        self.style = ''
        self.colspan = 1
        self.rowspan = 1
        if 'style' in block.attrs and block.attrs['style'].find('color') != -1:
            self.style = block.attrs['style']
        if 'colspan' in block.attrs:
            self.colspan = int(block.attrs['colspan'])
        if 'rowspan' in block.attrs:
            self.rowspan = int(block.attrs['rowspan'])

    def __str__(self):
        style = self.style
        if style:
            style = f'style=\"{style}\"|'
        if self.rowspan > 1:
            style += f'rowspan=\"{self.rowspan}\"|'
        if self.colspan > 1:
            style += f'colspan=\"{self.colspan}\"|'
        if self.tag == 'th':
            return f'!{style} {self.value}\n'
        elif self.tag == 'td':
            return f'|{style} {self.value}\n'
        else:
            return ''


class WikiwikiCrawler(HttpClient):

    MaxValueURLS = [
        'https://wikiwiki.jp/kancolle/%E8%89%A6%E8%88%B9%E6%9C%80%E5%A4%A7%E5%80%A4/%E6%97%A9%E8%A6%8B%E8%A1%A8%E4%B8%80%E8%A6%A7A',
        'https://wikiwiki.jp/kancolle/%E8%89%A6%E8%88%B9%E6%9C%80%E5%A4%A7%E5%80%A4/%E6%97%A9%E8%A6%8B%E8%A1%A8%E4%B8%80%E8%A6%A7B',
        'https://wikiwiki.jp/kancolle/%E8%89%A6%E8%88%B9%E6%9C%80%E5%A4%A7%E5%80%A4/%E6%97%A9%E8%A6%8B%E8%A1%A8%E4%B8%80%E8%A6%A7C',
        'https://wikiwiki.jp/kancolle/%E8%89%A6%E8%88%B9%E6%9C%80%E5%A4%A7%E5%80%A4/%E6%97%A9%E8%A6%8B%E8%A1%A8%E4%B8%80%E8%A6%A7D'
    ]

    CompareURL = 'https://wikiwiki.jp/kancolle/%E8%A3%85%E5%82%99%E8%80%83%E5%AF%9F'

    def __init__(self):
        super().__init__()
        self.fpMaxValue = open(OUPUT_PATH + WIKIWIKI_MaxValue_TABLE, 'w')
        self.fpCompare = open(OUPUT_PATH + WIKIWIKI_Compare_TABLE, 'w')

    def __del__(self):
        super().__del__()
        self.fpMaxValue.close()
        self.fpCompare.close()

    async def __getMaxValueTable(self, url):
        async with self.session.get(url) as resp:
            res = await resp.text()
            bs = BeautifulSoup(res, 'lxml')
            all_tables = bs.select('#body table.style_table')
            all_titles = bs.select('#body h1 a')
            for i in range(len(all_tables)):
                table = all_tables[i]
                title = TBlock.getInnerText(all_titles[i])
                trs = table.select('tr')
                ths = trs[0]
                trs = trs[1:]
                trdata = []
                for th in ths:
                    trdata.append(TBlock('th', th))
                trdata.append('! -\n')
                tdata = [trdata]
                for tr in trs:
                    trdata = []
                    tds = tr.select('td')
                    for td in tds:
                        trdata.append(TBlock('td', td))
                    
                    if not trdata:
                        continue

                    no = TBlock.getInnerText(tds[0])
                    nl = []
                    np = no.split('・')
                    for n in np:
                        if n.endswith('b'):
                            n = n[:-1].zfill(3) + 'a'
                        else:
                            n = n.zfill(3)
                        nl.append(n)
                    trdata[0] = f"| {'・'.join(nl)}\n"
                    mark = '・'.join(list(map(lambda x: f'{{{{舰娘备注|{x}}}}}', nl)))
                    trdata.append(f"| {mark}\n")
                    tdata.append(trdata)
                self.__genHTML(self.fpMaxValue, title, tdata)

    def __genHTML(self, fp, title, tdata):
        html = f'===={title}====\n{{| class="wikitable sortable"\n'
        for tr in tdata:
            html += '|-\n'
            for td in tr:
                html += str(td)
        html += '|}\n'
        fp.write(html)

    async def __getCompareTables(self, url):
        async with self.session.get(url) as resp:
            content = await resp.text()
            soup = BeautifulSoup(content, 'lxml')
            table_containers = soup.select('h2#h2_content_1_17 ~ table')
            for table_container in table_containers:
                title = TBlock.getInnerText(table_container.select_one('tr:nth-of-type(1) > td:nth-of-type(3)'))
                table = table_container.select_one('table.style_table')
                trs = table.select('tr')
                tdata = []
                for tr in trs:
                    trdata = []
                    tds = tr.select('td')
                    ths = tr.select('th')
                    for td in tds:
                        trdata.append(TBlock('td', td))
                    for th in ths:
                        trdata.append(TBlock('th', th))
                    if not trdata:
                        continue
                    tdata.append(trdata)
                self.__genHTML(self.fpCompare, title, tdata)

    async def start(self):
        for url in self.MaxValueURLS:
            await self.__getMaxValueTable(url)
        await self.__getCompareTables(self.CompareURL)
