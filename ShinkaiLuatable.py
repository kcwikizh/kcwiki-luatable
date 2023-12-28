import asyncio
import json
import re
import math

from config import (DB_PATH, JSON_PATH, KCDATA_SHIP_ALL_JSON,
                    KCDATA_SLOTITEM_ALL_JSON, LUATABLE_PATH, OUPUT_PATH,
                    SHINKAI_EXTRA_JSON, SHINKAI_ITEMS_DATA, SHINKAI_SHIPS_DATA,
                    WIKIA_OUTPUT_JSON, AIRPOWER_TABLE)
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

IS_BOMBER = [7, 8, 11]
IS_FIGHTER = [6, 7, 8, 11, 47]
IS_RECON = [10]
IS_CARRIER = [7, 11, 18]

class ShinkaiLuatable(HttpClient):
    WIKIA_RAW_URL = 'https://en.kancollewiki.net/{}?action=raw'
    SHINKAI_ITEMS_URL = 'https://en.kancollewiki.net/w/api.php?action=query&list=allpages&apprefix=Data%2FEnemyEquipment%2F&apnamespace=828&aplimit=max&format=json'
    SHINKAI_SHIP_URL = 'https://en.kancollewiki.net/w/api.php?action=query&list=allpages&apprefix=Data%2FEnemy%2F&apnamespace=828&aplimit=max&format=json'
    DETAIL_URL = 'https://en.kancollewiki.net/w/api.php?action=expandtemplates&text={{{{EnemyShipInfoKai|{}}}}}&format=json'
    NUM_PATTERN = re.compile(r'\d+')
    
    def __init__(self):
        super().__init__()
        self.items_id_map = {}
        self.items_data = {}
        self.ships_data = {}
        self.airpower_table = {}
        self.labs_airpower_table = {}
        self.SHINKAI_EXTRA = {}
        self.SLOTITEMS_KCDATA = jsonFile2dic(DB_PATH + KCDATA_SLOTITEM_ALL_JSON, masterKey='id')
        self.SHIPS_KCDATA = jsonFile2dic(DB_PATH + KCDATA_SHIP_ALL_JSON, masterKey='id')

    async def __get_allitems(self):
        async with self.session.get(self.SHINKAI_ITEMS_URL) as resp:
            res = await resp.json()
            return res['query']['allpages']

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

        # kcdata use >1000 id for shinkai slotitem
        kcdata_slotitem_id = item_id
        if item_id < 1000:
            kcdata_slotitem_id += 1000

        chinese_name = self.SLOTITEMS_KCDATA[kcdata_slotitem_id]['chinese_name']
        chinese_name = chinese_name if chinese_name else ''
        self.items_data[item_id] = {
            '日文名': item_info['_japanese_name'],
            '中文名': chinese_name,
            '类型': self.SLOTITEMS_KCDATA[kcdata_slotitem_id]['type'],
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
        async with self.session.get(self.SHINKAI_SHIP_URL) as resp:
            res = await resp.json()
            return res['query']['allpages']

    async def __wikia_crawler(self, title, variant):
        url = self.DETAIL_URL.format(title[18:] + '/' + variant)
        async with self.session.get(url) as resp:
            res_json = await resp.json()
            val = res_json['expandtemplates']['*']
            txt = val.split("'''")
            dayBattle = 0
            re_res = self.NUM_PATTERN.search(txt[47].strip())
            if re_res:
                dayBattle = int(re_res.group(0))
            airPower = txt[36].split('|')[3].strip()
            if airPower.find('?') != -1:
                airPower = airPower.strip('?')
            try:
                airPower = int(airPower)
            except ValueError:
                airPower = 9999
        return (airPower, dayBattle)

    async def __append_shinkai_ship(self, title):
        resp = await self.session.get(self.WIKIA_RAW_URL.format(title))
        resp_text = await resp.text()
        _luatable = LUATABLE_PATTERN.search(resp_text)
        _luatable = _luatable.group(0)
        shinkai_infos = lua.decode(_luatable)
        for variant, shinkai_info in shinkai_infos.items():
            if type(shinkai_info) is not dict:
                continue
            if '_api_id' not in shinkai_info:
                continue
            if '_seasonal' in shinkai_info:
                continue
            api_id = shinkai_info['_api_id']
            if api_id < 1000:
                api_id += 1000
            if api_id not in self.SHIPS_KCDATA:
                continue
            _api_id = str(api_id)
            yomi = self.SHIPS_KCDATA[api_id]['yomi']
            yomi = yomi if yomi else ''
            chinese_name = self.SHIPS_KCDATA[api_id]['chinese_name']
            chinese_name = chinese_name if chinese_name else ''
            category = ''
            stype = self.SHIPS_KCDATA[api_id]['stype']
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
            equips_air_power = 9999
            labs_air = 0
            equips_firepower = 0
            equips_torpedo = 0
            equips_bombing = 0
            for key, val in shinkai_info.items():
                if key == '_id' or key == '_api_id':
                    continue
                if val == None:
                    continue
                if key == '_range':
                    val = RANGE[val]
                elif key == '_speed':
                    val = SPEED[val]
                if val == 0:
                    continue
                elif key == '_equipment':
                    equips = {
                        '格数': len(val),
                        '搭载': [],
                        '装备': []
                    }
                    equips_air_power = 0
                    for att in val:
                        slot_size = att['size'] if 'size' in att and att['size'] else 0
                        equips['搭载'].append(slot_size)
                        equip_name = att['equipment']
                        equip_id = -1
                        current_equip = {}
                        if equip_name and equip_name not in self.items_id_map:
                            if equip_name in REDIRECT:
                                equip_name = REDIRECT[equip_name]
                        if equip_name and equip_name in self.items_id_map:
                            equip_id = self.items_id_map[equip_name]
                            current_equip = self.items_data[equip_id]
                        equips['装备'].append(equip_id)
                        if equip_id == -1:
                            equips_air_power = 9999
                        else:
                            if slot_size > 0:
                                equip_air_power = current_equip["对空"] if "对空" in current_equip else 0
                                equip_torpedo = current_equip["雷装"] if "雷装" in current_equip else 0
                                equip_bombing = current_equip["爆装"] if "爆装" in current_equip else 0
                                equip_type = current_equip["类型"][2] if "类型" in current_equip else 0
                                if equip_type in IS_RECON:
                                    labs_air += math.floor(math.sqrt(slot_size) * equip_air_power)
                                if equips_air_power != 9999:
                                    if equip_type in IS_FIGHTER:
                                        equips_air_power += math.floor(math.sqrt(slot_size) * equip_air_power)
                                    if equip_type in IS_BOMBER:
                                        equips_torpedo += equip_torpedo
                                        equips_bombing += equip_bombing
                            equip_firepower = current_equip["火力"] if "火力" in current_equip else 0
                            equips_firepower += equip_firepower
                    self.ships_data[_api_id].update({
                        '装备': equips
                    })
                elif val == True:
                    val = 1
                elif val == False:
                    val = 0
                if key in STATS:
                    self.ships_data[_api_id]['属性'][STATS[key]] = val
                elif key in ATTRS:
                    self.ships_data[_api_id].update({
                        ATTRS[key]: val
                    })
            
            if '火力' not in self.ships_data[_api_id]['属性']:
                self.ships_data[_api_id]['属性']['火力'] = 0
            if equips_air_power == 9999:
                equips_air_power, day_battle_power = await self.__wikia_crawler(title, variant)
            else:
                current_ship_stats = self.ships_data[_api_id]['属性']
                equips_firepower += current_ship_stats["火力"] if "火力" in current_ship_stats else 0
                equips_torpedo += current_ship_stats["雷装"] if "雷装" in current_ship_stats else 0
                day_battle_power = math.floor(1.5 * (equips_firepower + equips_torpedo + math.floor(1.3 * equips_bombing))) + 55
                if labs_air > 0:
                    self.labs_airpower_table[_api_id] = labs_air
            if equips_air_power > 0:
                self.airpower_table[_api_id] = equips_air_power
            if stype in IS_CARRIER or (stype == 10 and self.ships_data[_api_id]['属性']['速力'] == '陆上单位'):
                if day_battle_power > 0:
                    self.ships_data[_api_id]['属性']['火力'] = [self.ships_data[_api_id]['属性']['火力'], day_battle_power]
        print('ShinkaiLuatable: {} ok!'.format(title))

    async def genShinkaiShips(self):
        CATEGORY_MEMBERS = await self.__get_allships()
        tasks = []
        for category in CATEGORY_MEMBERS:
            title = category['title']
            if title.startswith('Module:Data/Enemy/Vita:'):
                continue
            elif title.startswith('Module:Data/Enemy/Mist:'):
                continue
            elif title == "Module:Data/Enemy/Transport Ship Wa-Class B":
                continue
            elif title == "Module:Data/Enemy/Harbour Summer Princess B":
                continue
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
        air_luatable = 'local p = { }\np.enemyFighterPowerDataTb = '
        air_luatable += luatable(sortDict(self.airpower_table))
        air_luatable += '\np.enemyFighterPowerDataTb2 = '
        air_luatable += luatable(sortDict(self.labs_airpower_table))
        air_luatable += '\nreturn p\n'
        with open(OUPUT_PATH + LUATABLE_PATH + SHINKAI_SHIPS_DATA + '.lua', 'w', encoding='utf-8') as fp:
            fp.write(ships_luatable)
        with open(OUPUT_PATH + JSON_PATH + SHINKAI_SHIPS_DATA + '.json', 'w', encoding='utf-8') as fp:
            json.dump(self.ships_data, fp, ensure_ascii=False, indent=4)
        with open(OUPUT_PATH + LUATABLE_PATH + AIRPOWER_TABLE, 'w', encoding='utf-8') as fp:
            fp.write(air_luatable)

    async def start(self):
        await self.genShinkaiItems()
        await self.genShinkaiShips()
