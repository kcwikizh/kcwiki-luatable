import asyncio
import json
import re

from config import (DB_PATH, JSON_PATH, KCDATA_SHIP_ALL_JSON,
                    KCDATA_SLOTITEM_ALL_JSON, LUATABLE_PATH, OUPUT_PATH,
                    SHINKAI_EXTRA_JSON, SHINKAI_ITEMS_DATA, SHINKAI_SHIPS_DATA,
                    WIKIA_OUTPUT_JSON)
from HttpClient import HttpClient
from slpp import slpp as lua
from utils import jsonFile2dic, luatable, sortDict

LUATABLE_PATTERN = re.compile(r'{[\s\S]*}')
REDIRECT_PATTERN = re.compile(r'\[\[(.*)\]\]')

RANGE = {
    0: '无', 1: '短', 2: '中', 3: '长', 4: '超长', 5: '超超长', -1: '未知'
}
SPEED = {
    0: '陆上单位', 5: '低速', 10: '高速', -1: '未知'
}

ATTRS = {
    '_can_debuff': '削甲'
}

STATS = {
    '_luck': '运',  '_shelling_accuracy': '命中',
    '_bombing': '爆装', '_torpedo': '雷装', '_hp': '耐久',
    '_armor': '装甲', '_aa': '对空', '_asw': '对潜',
    '_los': '索敌', '_speed': '速力', '_evasion': '回避',
    '_firepower': '火力', '_range': '射程',
    '_torpedo_accuracy': '雷击命中'
}
STATS_EXTRA = {
    '_opening_torpedo': '开幕鱼雷',
    '_slots': '格数',
    '_night_bombing': '夜战轰炸',
    '_air_power': '制空值',
    '_asw_attack': '开幕反潜'
}
REMARKS = {
    560: '可提供夜战连击'
}

REDIRECT = {
    '22inch Torpedo Late Model': 'High-speed Abyssal Torpedo'
}
STYPE = {
    1: '海防舰', 2: '驱逐舰', 3: '轻巡洋舰', 4: '重雷装巡洋舰', 5: '重巡洋舰',
    6: '航空巡洋舰', 7: '轻空母', 8: '战舰', 9: '战舰', 10: '航空战舰',
    11: '正规空母', 12: '超弩级战舰', 13: '潜水艇', 14: '潜水空母', 15: '输送舰',
    16: '水上机母舰', 17: '扬陆舰', 18: '装甲空母', 19: '工作舰', 20: '潜水母舰',
    21: '练习巡洋舰', 22: '补给舰'
}

SKIP_SUFFIXES = ['New Year 2017']


class ShinkaiLuatable(HttpClient):
    WIKIA_RAW_URL = 'http://kancolle.wikia.com/wiki/{}?action=raw'

    def __init__(self):
        super().__init__()
        self.items_id_map = {}
        self.items_data = {}
        self.ships_data = {}
        self.SHINKAI_EXTRA = {}
        self.SLOTITEMS_KCDATA = jsonFile2dic(DB_PATH + KCDATA_SLOTITEM_ALL_JSON, masterKey='id')
        self.SHIPS_KCDATA = jsonFile2dic(DB_PATH + KCDATA_SHIP_ALL_JSON, masterKey='id')

    async def __get_allitems(self):
        SHINKAI_ITEMS_URL = 'http://kancolle.fandom.com/api.php?action=query&list=categorymembers&cmtitle=Category:Enemy_equipment_modules&cmlimit=500&format=json'
        async with self.session.get(SHINKAI_ITEMS_URL) as resp:
            res = await resp.json()
            return res['query']['categorymembers']

    async def __append_shinkai_item(self, title):
        resp = await self.session.get(self.WIKIA_RAW_URL.format(title))
        item_info_text = await resp.text()
        while item_info_text.find('REDIRECT') != -1:
            title = REDIRECT_PATTERN.search(item_info_text).group(1).strip()
            resp = await self.session.get(self.WIKIA_RAW_URL.format('Module:' + title))
            item_info_text = await resp.text()
        _luatable = re.search(LUATABLE_PATTERN, item_info_text)
        if not _luatable:
            return
        _luatable = _luatable.group(0)
        item_info = lua.decode(_luatable)
        item_id = item_info['_id']
        chinese_name = self.SLOTITEMS_KCDATA[item_id]['chinese_name']
        chinese_name = chinese_name if chinese_name else ''
        self.items_data[item_id] = {
            '日文名': item_info['_japanese_name'],
            '中文名': chinese_name,
            '类型': self.SLOTITEMS_KCDATA[item_id]['type'],
            '稀有度': item_info['_rarity']
        }
        self.items_id_map[item_info['_name']] = item_id
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
            tasks.append(asyncio.ensure_future(
                self.__append_shinkai_item(title)))
        dones, pendings = await asyncio.wait(tasks)
        print('Shinkai-Items: {} done, {} pendings.'.format(len(dones), len(pendings)))
        self.items_data = sortDict(self.items_data)
        items_luatable = 'local d = {}\n'
        items_luatable += '\nd.equipDataTable = '
        items_luatable += luatable(self.items_data)
        items_luatable += '\n'
        items_luatable += '\nreturn d\n'
        with open(OUPUT_PATH + LUATABLE_PATH + SHINKAI_ITEMS_DATA + '.lua', 'w', encoding='utf-8') as fp:
            fp.write(items_luatable)
        with open(OUPUT_PATH + JSON_PATH + SHINKAI_ITEMS_DATA + '.json', 'w', encoding='utf-8') as fp:
            json.dump(self.items_data, fp, ensure_ascii=False, indent=4)

    async def __get_allships(self):
        ret = []
        async with self.session.get('http://kancolle.fandom.com/api.php?action=query&list=categorymembers&cmtitle=Category:Enemy_ship_modules&cmlimit=500&format=json') as resp:
            res = await resp.json()
            CATEGORY_MEMBERS = res['query']['categorymembers']
            for category in CATEGORY_MEMBERS:
                title = category['title']
                if title.startswith('Module') and title not in ret:
                    ret.append(title)
        async with self.session.get('https://kancolle.fandom.com/api.php?action=query&list=allpages&apprefix=Data%2FEnemy%2F&apnamespace=828&aplimit=max&format=json') as resp:
            res = await resp.json()
            CATEGORY_MEMBERS = res['query']['allpages']
            for category in CATEGORY_MEMBERS:
                title = category['title']
                if title.startswith('Module:Data/Enemy/Vita:'):
                    continue
                if title.startswith('Module') and title not in ret:
                    ret.append(title)
        return ret

    def __load_extra(self):
        self.SHINKAI_EXTRA = jsonFile2dic(DB_PATH + SHINKAI_EXTRA_JSON)
        wikia_data = jsonFile2dic(DB_PATH + WIKIA_OUTPUT_JSON)
        for _id, value in wikia_data.items():
            if _id not in self.SHINKAI_EXTRA:
                self.SHINKAI_EXTRA[_id] = {}
            self.SHINKAI_EXTRA[_id].update(value)

    async def __append_shinkai_ship(self, title):
        resp = await self.session.get(self.WIKIA_RAW_URL.format(title))
        resp_text = await resp.text()
        _luatable = LUATABLE_PATTERN.search(resp_text)
        _luatable = _luatable.group(0)
        shinkai_infos = lua.decode(_luatable)
        for shinkai_info in shinkai_infos.values():
            if type(shinkai_info) is not dict:
                continue
            if '_api_id' not in shinkai_info:
                continue
            if '_suffix' in shinkai_info and shinkai_info['_suffix'] in SKIP_SUFFIXES:
                continue
            api_id = shinkai_info['_api_id']
            if api_id < 1000:
                api_id += 1000
            if api_id not in self.SHIPS_KCDATA:
                continue
            _api_id = str(api_id)
            extra_data = self.SHINKAI_EXTRA[_api_id] if _api_id in self.SHINKAI_EXTRA else {
            }
            yomi = self.SHIPS_KCDATA[api_id]['yomi']
            yomi = yomi if yomi else ''
            chinese_name = self.SHIPS_KCDATA[api_id]['chinese_name']
            chinese_name = chinese_name if chinese_name else ''
            category = ''
            stype = self.SHIPS_KCDATA[api_id]['stype']
            if 'Stype' in extra_data:
                category = extra_data['Stype']
            else:
                category = STYPE[stype]
            self.ships_data[_api_id] = {
                '日文名': shinkai_info['_japanese_name'],
                '中文名': chinese_name,
                'kcwiki分类': category,
                '属性': {
                    '耐久': 0,
                    '装甲': 0,
                    '火力': 0,
                    '雷装': 0,
                    '对潜': 0,
                    '对空': 0,
                    '回避': 0,
                    '索敌': 0,
                    '运': 0,
                    '速力': "未知",
                    '射程': "未知"
                },
                '装备': {}
            }
            for key, val in shinkai_info.items():
                if key == '_id' or key == '_api_id':
                    continue
                if val == None or val == 0:
                    continue
                if key == '_range':
                    val = RANGE[val]
                elif key == '_speed':
                    val = SPEED[val]
                elif key == '_equipment':
                    equips = {
                        '格数': len(val),
                        '搭载': [],
                        '装备': []
                    }
                    for att in val:
                        equips['搭载'].append(att['size'] if att['size'] else 0)
                        equip_name = att['equipment']
                        equip_id = -1
                        if equip_name and equip_name not in self.items_id_map:
                            if equip_name in REDIRECT:
                                equip_name = REDIRECT[equip_name]
                        if equip_name and equip_name in self.items_id_map:
                            equip_id = self.items_id_map[equip_name]
                        equips['装备'].append(equip_id)
                    self.ships_data[_api_id].update({
                        '装备': equips
                    })
                elif val == True:
                    val = 1
                elif val == False:
                    val = 0
                if key in STATS:
                    if key == '_firepower' and\
                        (chinese_name.find('WO') != -1 or chinese_name.find('NU') != -1) and\
                            'DayBattle' in extra_data:
                        val = [val, extra_data['DayBattle']]
                    self.ships_data[_api_id]['属性'][STATS[key]] = val
                elif key in ATTRS:
                    self.ships_data[_api_id].update({
                        ATTRS[key]: val
                    })
            if (chinese_name.find('WO') != -1 or chinese_name.find('NU') != -1) and\
                    'DayBattle' in extra_data:
                if '火力' not in self.ships_data[_api_id]['属性']:
                    self.ships_data[_api_id]['属性']['火力'] = [0, extra_data['DayBattle']]

    async def genShinkaiShips(self):
        self.__load_extra()
        categories = await self.__get_allships()
        tasks = []
        for title in categories:
            tasks.append(asyncio.ensure_future(
                self.__append_shinkai_ship(title)))
        dones, pendings = await asyncio.wait(tasks)
        print('Shinkai-Ships: {} done, {} pendings.'.format(len(dones), len(pendings)))
        self.ships_data = sortDict(self.ships_data)
        ships_luatable = 'local d = {}\n'
        ships_luatable += '\nd.shipDataTable = '
        ships_luatable += luatable(self.ships_data)
        ships_luatable += '\n'
        ships_luatable += '\nreturn d\n'
        with open(OUPUT_PATH + LUATABLE_PATH + SHINKAI_SHIPS_DATA + '.lua', 'w', encoding='utf-8') as fp:
            fp.write(ships_luatable)
        with open(OUPUT_PATH + JSON_PATH + SHINKAI_SHIPS_DATA + '.json', 'w', encoding='utf-8') as fp:
            json.dump(self.ships_data, fp, ensure_ascii=False, indent=4)

    async def start(self):
        await self.genShinkaiItems()
        await self.genShinkaiShips()
