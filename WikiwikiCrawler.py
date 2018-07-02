import asyncio
import json

from bs4 import BeautifulSoup, element

from config import OUPUT_PATH, WIKIWIKI_TABLE
from HttpClient import HttpClient


class WikiwikiCrawler(HttpClient):

    URLS = [
        'https://wikiwiki.jp/kancolle/%E8%89%A6%E8%88%B9%E6%9C%80%E5%A4%A7%E5%80%A4/%E6%97%A9%E8%A6%8B%E8%A1%A8%E4%B8%80%E8%A6%A7A',
        'https://wikiwiki.jp/kancolle/%E8%89%A6%E8%88%B9%E6%9C%80%E5%A4%A7%E5%80%A4/%E6%97%A9%E8%A6%8B%E8%A1%A8%E4%B8%80%E8%A6%A7B',
        'https://wikiwiki.jp/kancolle/%E8%89%A6%E8%88%B9%E6%9C%80%E5%A4%A7%E5%80%A4/%E6%97%A9%E8%A6%8B%E8%A1%A8%E4%B8%80%E8%A6%A7C',
        'https://wikiwiki.jp/kancolle/%E8%89%A6%E8%88%B9%E6%9C%80%E5%A4%A7%E5%80%A4/%E6%97%A9%E8%A6%8B%E8%A1%A8%E4%B8%80%E8%A6%A7D'
    ]

    def __init__(self):
        super().__init__()
        self.fp = open(OUPUT_PATH + WIKIWIKI_TABLE, 'w')

    def __del__(self):
        super().__del__()
        self.fp.close()

    def __getInnerText(self, node):
        if not node:
            return ''
        if isinstance(node, element.NavigableString):
            return node.string.strip()
        return node.get_text().strip()

    def __genHTML(self, title, thead, table):
        colors = ['#FFFF99', '#FDE9D9']
        html = f'=={title}==\n{{| class="wikitable sortable"\n'
        for th in thead:
            html += f'!{th}\n'
        for tr in table:
            html += '|-\n'
            for td in tr:
                style = ''
                if td[1] != -1:
                    style = f'style="background-color: {colors[td[1]]};"|'
                html += f'|{style}{td[0]}\n'
        html += '|}\n'
        self.fp.write(html)

    async def __getTable(self, url):
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
                self.__genHTML(title, theads, table_data)

    async def start(self):
        for url in self.URLS:
            await self.__getTable(url)


async def main():
    bot = WikiwikiCrawler()
    await bot.start()

if __name__ == '__main__':
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(main())
