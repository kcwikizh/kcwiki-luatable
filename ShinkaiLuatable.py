import asyncio
import re
import json

from config import (DB_PATH, KCDATA_SLOTITEM_ALL_JSON, OUPUT_PATH,
                    SHINKAI_ITEMS_DATA, SHINKAI_SHIPS_DATA)
from HttpClient import HttpClient
from slpp import slpp as lua
from utils import jsonFile2dic, luatable, sortDict

LUATABLE_PATTERN = re.compile(r'{[\s\S]*}')
REDIRECT_PATTERN = re.compile(r'\[\[(.*)\]\]')
RANGE = ['无', '短', '中', '长', '超长', '超超长']

STATS = {
    '_luck': '运', '_shelling_accuracy': '命中',
    '_bombing': '爆装', '_torpedo': '雷装',
    '_armor': '装甲', '_aa': '对空', '_asw': '对潜',
    '_los': '索敌', '_speed': '速力', '_evasion': '回避',
    '_firepower': '火力', '_range': '射程',
    '_torpedo_accuracy': '雷击命中'
}

REMARKS = {
    560: '可提供夜战连击'
}


class ShinkaiLuatable(HttpClient):
    WIKIA_RAW_URL = 'http://kancolle.wikia.com/wiki/{}?action=raw'

    def __init__(self):
        super().__init__()
        self.items_data = {}
        self.SLOTITEMS_KCDATA = jsonFile2dic(DB_PATH + KCDATA_SLOTITEM_ALL_JSON, masterKey='id')

    async def __get_allitems(self):
        SHINKAI_ITEMS_URL = 'http://kancolle.wikia.com/api.php?action=query&list=categorymembers&cmtitle=Category:Enemy_equipment&cmlimit=500&format=json'
        async with self.session.get(SHINKAI_ITEMS_URL) as resp:
            res = await resp.json()
            return res['query']['categorymembers']

    async def __append_shinkai_item(self, title):
        resp = await self.session.get(self.WIKIA_RAW_URL.format('Module:' + title))
        item_info_text = await resp.text()
        while item_info_text.find('REDIRECT') != -1:
            title = REDIRECT_PATTERN.search(item_info_text).group(1).strip()
            resp = await self.session.get(self.WIKIA_RAW_URL.format('Module:' + title))
            item_info_text = await resp.text()
        luatable = re.search(LUATABLE_PATTERN, item_info_text)
        if not luatable:
            return
        luatable = luatable.group(0)
        item_info = lua.decode(luatable)
        item_id = item_info['_id']
        chinese_name = self.SLOTITEMS_KCDATA[item_id]['chinese_name']
        chinese_name = chinese_name if chinese_name else ''
        self.items_data[item_id] = {
            '日文名': item_info['_japanese_name'],
            '中文名': chinese_name,
            '类型': self.SLOTITEMS_KCDATA[item_id]['type'],
            '稀有度': item_info['_rarity']
        }
        for key, val in item_info.items():
            if key not in STATS:
                continue
            if val == False:
                continue
            if key == '_range':
                val = RANGE[val]
            self.items_data[item_id].update({
                STATS[key]: val
            })
        if item_id in REMARKS:
            self.items_data[item_id].update({
                '备注':  REMARKS[item_id]
            })

    async def genShinkaiItems(self):
        CATEGORY_MEMBERS = await self.__get_allitems()
        tasks = []
        for category in CATEGORY_MEMBERS:
            title = category['title']
            if title.startswith('Template'):
                continue
            tasks.append(asyncio.ensure_future(self.__append_shinkai_item(title)))
        dones, pendings = await asyncio.wait(tasks)
        print('Shinkai-Items: {} done, {} pendings.'.format(len(dones), len(pendings)))
        self.items_data = sortDict(self.items_data)
        items_luatable = 'local d = {}\n'
        items_luatable += '\nd.equipDataTable = '
        items_luatable += luatable(self.items_data)
        items_luatable += '\n'
        items_luatable += '\nreturn d\n'
        with open(OUPUT_PATH + SHINKAI_ITEMS_DATA + '.lua', 'w', encoding='utf-8') as fp:
            fp.write(items_luatable)
        with open(OUPUT_PATH + SHINKAI_ITEMS_DATA + '.json', 'w', encoding='utf-8') as fp:
            json.dump(self.items_data, fp, ensure_ascii=False, indent=4)

    async def start(self):
        await self.genShinkaiItems()
