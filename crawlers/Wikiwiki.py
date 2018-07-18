import asyncio
import json

from bs4 import BeautifulSoup, element

from config import OUPUT_PATH
from HttpClient import HttpClient

WIKIWIKI_MaxValue_TABLE = 'wikiwiki_MaxValue_table.txt'
WIKIWIKI_Compare_TABLE = 'wikiwiki_Compare_table.txt'


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

    def __getInnerText(self, node):
        if not node:
            return ''
        if isinstance(node, element.NavigableString):
            return node.string.strip()
        return node.get_text().strip()

    def __genMaxValueHTML(self, title, thead, table):
        colors = ['#FFFF99', '#FDE9D9']
        html = f'=={title}==\n{{| class="wikitable sortable"\n'
        for th in thead:
            html += f'!{th}\n'
        for tr in table:
            html += '|-\n'
            nos = []
            for x in tr[0][0].split('・'):
                if x.endswith('b'):
                    x = x[:-1].zfill(3) + 'a'
                else:
                    x = x.zfill(3)
                nos.append(x)
            tr[0][0] = '・'.join(nos)
            for td in tr:
                style = ''
                if td[1] != -1:
                    style = f'style="background-color: {colors[td[1]]};"|'
                html += f'|{style}{td[0]}\n'
            mark = ''.join(list(map(lambda x: f'{{{{舰娘备注|{x}}}}}', nos)))
            html += f'|{mark}\n'
        html += '|}\n'
        self.fpMaxValue.write(html)

    async def __getMaxValueTable(self, url):
        async with self.session.get(url) as resp:
            res = await resp.text()
            bs = BeautifulSoup(res, 'lxml')
            all_tables = bs.select('#body table.style_table')
            all_titles = bs.select('#body h1 a')
            for i in range(len(all_tables)):
                table = all_tables[i]
                title = self.__getInnerText(all_titles[i])
                ths = table.thead.tr.contents
                theads = []
                table_data = []
                for th in ths:
                    theads.append(self.__getInnerText(th))
                theads.append('-')
                rows = table.tbody.contents
                for row in rows:
                    cols = row.contents
                    row_data = []
                    for i in range(len(cols)):
                        col = cols[i]
                        d_type = -1
                        if 'style' in col.attrs:
                            style = col.attrs['style']
                            if style.find('#FFFF99') != -1:
                                d_type = 0
                            elif style.find('#FDE9D9') != -1:
                                d_type = 1
                        row_data.append([
                            self.__getInnerText(col),
                            d_type
                        ])
                    table_data.append(row_data)
                self.__genMaxValueHTML(title, theads, table_data)

    async def __getCompareTables(self, url):
        async with self.session.get(url) as resp:
            content = await resp.text()
            soup = BeautifulSoup(content, 'lxml')
            table_containers = soup.select('h2#h2_content_1_17 ~ table')
            for table_container in table_containers:
                title = self.__getInnerText(table_container.select_one('tr:nth-of-type(1) > td:nth-of-type(3)'))
                table = table_container.select_one('table.style_table')
                trs = table.select('tr')
                tdata = []
                for tr in trs:
                    trdata = []
                    tds = tr.select('td')
                    ths = tr.select('th')
                    for td in tds:
                        cnt = 1
                        style = ''
                        if 'rowspan' in td.attrs:
                            cnt = int(td.attrs['rowspan'])
                        if 'style' in td.attrs and td.attrs['style'].find('color') != -1:
                            style = td.attrs['style']
                        trdata.append({
                            'val': self.__getInnerText(td),
                            'cnt': cnt,
                            'style': style,
                            'tag': 'td'
                        })
                    for th in ths:
                        cnt = 1
                        style = ''
                        if 'colspan' in th.attrs:
                            cnt = int(th.attrs['colspan'])
                        if 'style' in th.attrs and th.attrs['style'].find('color') != -1:
                            style = th.attrs['style']
                        trdata.append({
                            'val': self.__getInnerText(th),
                            'cnt': cnt,
                            'style': style,
                            'tag': 'th'
                        })
                    if not trdata:
                        continue
                    tdata.append(trdata)
                self.__genCompareHTML(title, tdata)

    def __genCompareHTML(self, title, tdata):
        html = f'=={title}==\n{{| class="wikitable sortable"\n'
        for tr in tdata:
            html += '|-\n'
            for ti in tr:
                sp = '|'
                span = 'rowspan'
                style = ''
                if ti['tag'] == 'th':
                    sp = '!'
                    span = 'colspan'
                if ti['style']:
                    style = f"style=\"{ti['style']}\"|"
                if ti['cnt'] > 1:
                    html += f"{sp}{style}{span}=\"{ti['cnt']}\"| {ti['val']}\n"
                else:
                    html += f"{sp}{style} {ti['val']}\n"
        html += '|}\n'
        self.fpCompare.write(html)

    async def start(self):
        # for url in self.MaxValueURLS:
        #     await self.__getMaxValueTable(url)
        await self.__getCompareTables(self.CompareURL)
