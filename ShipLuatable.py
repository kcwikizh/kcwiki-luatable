import asyncio
import json

from config import (DB_PATH, ENTITIES_DB, ITEM_TYPES_DB, ITEMS_DB,
                    KCDATA_SHIP_ALL_JSON, KCDATA_SLOTITEM_ALL_JSON, OUPUT_PATH,
                    SHIP_CLASSES_DB, SHIP_NAMESUFFIX_DB, SHIP_REMARKS_EXTRA,
                    SHIP_REMODEL_EXTRA, SHIP_SERIES_DB,
                    SHIP_TYPE_COLLECTIONS_DB, SHIP_TYPES_DB, SHIPS_DATA,
                    SHIPS_DB)
from utils import jsonFile2dic, luatable, sortDict

STYPE_MAP = {
    1: 2, 2: 3, 3: 4, 4: 5, 5: 5,
    6: 9, 7: 9, 8: 9, 9: 7, 10: 11,
    11: 18, 12: 16, 13: 13, 14: 13, 15: 17,
    16: 19, 17: 20, 18: 9, 19: 2, 20: 9,
    21: 21, 22: None, 23: 5, 24: 16, 25: None,
    26: None, 27: None, 28: 3, 29: 22, 30: 7,
    31: 1, 32: 7
}

COST_MAP = {
    'ammo': '弹药',
    'steel': '钢材',
    'fuel': '燃料'
}

REMODEL_TYPES = ['', '', '改装设计图x1', '改装设计图x1 试制甲板用弹射器x1']


class ShipLuatable:

    def __init__(self):
        self.ships_data = {}
        self.items_data = {}
        
        self.SHIP_REMODEL_EXTRA = jsonFile2dic(DB_PATH + SHIP_REMODEL_EXTRA)
        self.SHIP_REMARKS_EXTRA = jsonFile2dic(DB_PATH + SHIP_REMARKS_EXTRA)
        self.SHIPS_KCDATA = jsonFile2dic(DB_PATH + KCDATA_SHIP_ALL_JSON, masterKey='id')
        self.SHIPS_DB = jsonFile2dic(DB_PATH + SHIPS_DB + '.json', masterKey='id')
        self.SHIP_NAMESUFFIX_DB = jsonFile2dic(DB_PATH + SHIP_NAMESUFFIX_DB + '.json', masterKey='id')
        self.SHIP_CLASSES_DB = jsonFile2dic(DB_PATH + SHIP_CLASSES_DB + '.json', masterKey='id')
        self.SHIP_SERIES_DB = jsonFile2dic(DB_PATH + SHIP_SERIES_DB + '.json', masterKey='id')
        self.ENTITIES_DB = jsonFile2dic(DB_PATH + ENTITIES_DB + '.json', masterKey='id')

    def __map_lvl_up(self):
        for series in self.SHIP_SERIES_DB.values():
            series_ships = series['ships']
            for series_ship in series_ships:
                next_blueprint = 'next_blueprint' in series_ship and series_ship[
                    'next_blueprint'] == 'on'
                next_catapult = 'next_catapult' in series_ship and series_ship[
                    'next_catapult'] == 'on'
                next_loop = 'next_loop' in series_ship and series_ship['next_loop'] == 'on'

                next_level = series_ship['next_lvl'] if 'next_lvl' in series_ship \
                    and series_ship['next_lvl'] else 0
                shipid = series_ship['id']
                _ship = self.SHIPS_DB[shipid]
                if 'remodel' in _ship and 'next' in _ship['remodel']:
                    next_shipid = _ship['remodel']['next']
                    can_remodel = 1
                    if next_blueprint:
                        can_remodel += 1
                    if next_catapult:
                        can_remodel += 1
                    self.SHIPS_DB[next_shipid]['remodel_info'] = can_remodel
                    self.SHIPS_DB[shipid]['next_type'] = can_remodel
                    if next_loop:
                        self.SHIPS_DB[next_shipid]['remodel'].update({
                            'next': shipid,
                            'next_lvl': next_level
                        })

    def __get_namesuffix(self, suffix, lan):
        if not suffix:
            return ''
        if not suffix in self.SHIP_NAMESUFFIX_DB or not lan in self.SHIP_NAMESUFFIX_DB[suffix]:
            return ''
        return self.SHIP_NAMESUFFIX_DB[suffix][lan]

    def __get_equips(self, equips, slot_size):
        ret = [-1 for i in range(slot_size)]
        equip_size = len(equips)
        for i in range(equip_size):
            equip = equips[i]
            if not equip:
                ret[i] = -1
            elif isinstance(equip, dict):
                ret[i] = {
                    'id': equip['id'],
                    'star': equip['star']
                }
            else:
                ret[i] = equip
        return ret

    def __get_entityname(self, rel, prev_id, rel_key):
        if rel:
            return self.ENTITIES_DB[rel]['name']['ja_jp']
        if not prev_id or prev_id == -1:
            return '未知'
        prev_ship = self.SHIPS_DB[prev_id]
        return self.__get_entityname(
            prev_ship['rels'][rel_key],
            prev_ship['remodel']['prev']
            if 'remodel' in prev_ship and
            'prev' in prev_ship['remodel'] else None,
            rel_key
        )

    def __get_shipremodel(self, ship_id, next_type, remodel_cost, ship_remodel, base_lvl):
        ret = {'等级': 0}
        if not isinstance(base_lvl, str):
            base_lvl = 0
        if ship_remodel and 'next_lvl' in ship_remodel:
            ret['等级'] = ship_remodel['next_lvl']
        if ship_remodel and 'prev_loop' in ship_remodel:
            ret['等级'] = base_lvl
        if isinstance(remodel_cost, dict):
            for cost_type, cost in remodel_cost.items():
                ret[COST_MAP[cost_type]] = cost
        ret.update({
            '改造前': -1,
            '改造后': -1
        })
        if ship_remodel and 'next' in ship_remodel:
            ret['改造后'] = self.SHIPS_KCDATA[ship_remodel['next']]['wiki_id']
        if ship_remodel and 'prev' in ship_remodel:
            ret['改造前'] = self.SHIPS_KCDATA[ship_remodel['prev']]['wiki_id']

        remodel_extra = ''
        if ship_id in self.SHIP_REMODEL_EXTRA:
            remodel_extra = self.SHIP_REMODEL_EXTRA[ship_id]
        else:
            remodel_extra = REMODEL_TYPES[next_type]
        if remodel_extra:
            ret.update({
                '图纸': remodel_extra
            })
        return ret

    def __append_ship(self, ship_id):
        _ship_id = str(ship_id)
        wctf_ship = self.SHIPS_DB[ship_id]
        wiki_ship = self.SHIPS_KCDATA[ship_id]
        slot_size = len(wctf_ship['slot'])
        can_remodel = wctf_ship['remodel_info'] if 'remodel_info' in wctf_ship else 0
        can_drop = 1 if (
            'can_drop' in wiki_ship and wiki_ship['can_drop']) else -1
        can_build = 1 if 'can_construct' in wiki_ship and wiki_ship['can_construct'] else -1
        next_type = wctf_ship['next_type'] if 'next_type' in wctf_ship else 0
        self.ships_data[wiki_ship['wiki_id']] = {
            'ID': ship_id,
            '图鉴号': wctf_ship['no'],
            '日文名': wctf_ship['name']['ja_jp'] + self.__get_namesuffix(wctf_ship['name']['suffix'], 'ja_jp'),
            '假名': wctf_ship['name']['ja_kana'] + self.__get_namesuffix(wctf_ship['name']['suffix'], 'ja_kana'),
            '中文名': wctf_ship['name']['zh_cn'] + self.__get_namesuffix(wctf_ship['name']['suffix'], 'zh_cn'),
            '舰种': STYPE_MAP[wctf_ship['type']],
            '级别': [
                self.SHIP_CLASSES_DB[wctf_ship['class']
                                     ]['name']['zh_cn'] + '型',
                wctf_ship['class_no'] if wctf_ship['class_no'] else 0
            ],
            '数据': {
                '耐久': [wctf_ship['stat']['hp'], wctf_ship['stat']['hp_max']],
                '火力': [wctf_ship['stat']['fire'], wctf_ship['stat']['fire_max']],
                '雷装': [wctf_ship['stat']['torpedo'], wctf_ship['stat']['torpedo_max']],
                '对空': [wctf_ship['stat']['aa'], wctf_ship['stat']['aa_max']],
                '装甲': [wctf_ship['stat']['armor'], wctf_ship['stat']['armor_max']],
                '对潜': [wctf_ship['stat']['asw'], wctf_ship['stat']['asw_max']],
                '回避': [wctf_ship['stat']['evasion'], wctf_ship['stat']['evasion_max']],
                '索敌': [wctf_ship['stat']['los'], wctf_ship['stat']['los_max']],
                '运': [wctf_ship['stat']['luck'], wctf_ship['stat']['luck_max']],
                '速力': wctf_ship['stat']['speed'],
                '射程': [wctf_ship['stat']['range']],
                '稀有': wctf_ship['rare']
            },
            '装备': {
                '格数': slot_size,
                '搭载': wctf_ship['slot'],
                '初期装备': self.__get_equips(wctf_ship['equip'], slot_size)
            },
            '获得': {
                '掉落': can_drop, '改造': can_remodel, '建造': can_build, '时间': wctf_ship['buildtime']
            },
            '改修': {
                '火力': wctf_ship['modernization'][0], '雷装': wctf_ship['modernization'][1],
                '对空': wctf_ship['modernization'][2], '装甲': wctf_ship['modernization'][3]
            },
            '解体': {
                '燃料': wctf_ship['scrap'][0], '弹药': wctf_ship['scrap'][1],
                '钢材': wctf_ship['scrap'][2], '铝': wctf_ship['scrap'][3]
            },
            '改造': self.__get_shipremodel(
                _ship_id, next_type, wctf_ship['remodel_cost'],
                wctf_ship['remodel'], wctf_ship['base_lvl']
            ),
            '画师': self.__get_entityname(
                wctf_ship['rels']['illustrator'], wctf_ship['remodel']['prev']
                if 'remodel' in wctf_ship and 'prev' in wctf_ship['remodel'] else None,
                'illustrator'
            ),
            '声优': self.__get_entityname(
                wctf_ship['rels']['cv'], wctf_ship['remodel']['prev']
                if 'remodel' in wctf_ship and 'prev' in wctf_ship['remodel'] else None,
                'cv'
            )
        }

    def genShipsData(self):
        self.__map_lvl_up()
        for ship_id in sorted(self.SHIPS_DB.keys()):
            if ship_id in self.SHIPS_KCDATA:
                self.__append_ship(ship_id)
        self.ships_data = sortDict(self.ships_data)
        ships_luatable = 'local d = {}\n'
        ships_luatable += '------------------------\n'
        ships_luatable += '-- 以下为舰娘数据列表 -- \n'
        ships_luatable += '------------------------\n'
        ships_luatable += 'd.shipDataTb = '
        ships_luatable += luatable(self.ships_data)
        ships_luatable += '\n'
        ships_luatable += '\nreturn d\n'
        with open(OUPUT_PATH + SHIPS_DATA + '.lua', 'w', encoding='utf-8') as fp:
            fp.write(ships_luatable)
        with open(OUPUT_PATH + SHIPS_DATA + '.json', 'w', encoding='utf-8') as fp:
            json.dump(self.ships_data, fp, ensure_ascii=False, indent=4)
