import asyncio
import json

from config import (AKASHI_LIST_OUTPUT_JSON, BONUS_JSON, DB_PATH, ENTITIES_DB,
                    ITEM_REMARKS_EXTRA, ITEM_TYPES_DB, ITEMS_DATA, ITEMS_DB,
                    JSON_PATH, KCDATA_SHIP_ALL_JSON, KCDATA_SLOTITEM_ALL_JSON,
                    LUATABLE_PATH, OUPUT_PATH, SHIP_CLASSES_DB,
                    SHIP_NAMESUFFIX_DB, SHIP_REMODEL_EXTRA, SHIP_SERIES_DB,
                    SHIP_TYPE_COLLECTIONS_DB, SHIP_TYPES_DB, SHIPS_DATA,
                    SHIPS_DB)
from utils import jsonFile2dic, luatable, sortDict

STYPE = {
    #1=海防舰
    31: 1,
    #2=驱逐舰
    1: 2, 19: 2,
    #3=轻型巡洋舰
    28: 3, 2: 3,
    #4=重型雷装巡洋舰
    3: 4,
    #5=重型巡洋舰
    4: 5, 23: 5,
    #6=航空巡洋舰
    5: 6,
    #7=轻型航空母舰
    9: 7, 32: 7, 30: 7,
    #8=战列巡洋舰
    18: 8, 7: 8,
    #9=战列舰
    6: 9,
    #10=航空战列舰
    8: 10, 33: 10,
    #11=航空母舰
    10: 11,
    #12=超弩级战舰
    20: 12,
    #13=潜水舰
    13: 13,
    #14=潜水航空母舰
    14: 14,
    #16=水上机母舰
    24: 16, 12: 16,
    #17=扬陆舰
    15: 17,
    #18=装甲航空母舰
    11: 18,
    #19=工作舰
    16: 19,
    #20=潜水母舰
    17: 20,
    #21=练习巡洋舰
    21: 21,
    #22=补给舰
    29: 22,
    #23=轻航空巡洋舰
    34: 23,
    #24=改装航空巡洋舰
    36: 24,
    #25=兵装实验轻巡
    35: 25,
    #未使用
    26: None, 25: None, 27: None, 22: None
}
COST = {
    'ammo': '弹药',
    'steel': '钢材',
    'fuel': '燃料'
}

RANGE = ['无', '短', '中', '长', '超长']
WEEK = ['日', '一', '二', '三', '四', '五', '六']
STAT = {
    'torpedo': '雷装', 'fire': '火力', 'los': '索敌', 'aa': '对空',
    'range': '射程', 'distance': '航程', 'asw': '对潜', 'bomb': '爆装',
    'armor': '装甲', 'evasion': '回避', 'hit': '命中'
}
CONSUMABLE = {
    'consumable_57': '勋章',
    'consumable_70': '熟练搭乘员',
    'consumable_71': 'ネ(Ne)式引擎',
    'consumable_75': '新型炮熕兵装资材',
    'consumable_77': '新型航空兵装資材',
    'consumable_78': '戦闘詳報',
    'consumable_92': '新型噴進装備開発資材',
    'consumable_94': '新型兵装資材'
}
RANK_UPGARDABLE = [
    15, 16, 17, 51, 21, 50, 45, 18,
    60, 19, 61, 20, 55, 56, 22, 23, 53, 54, 59
]

REMODEL_TYPES = ['', '', '改装设计图x1', '改装设计图x1 试制甲板用弹射器x1']
AREA_MAP = {
    'North': '北方'
}

def getArea(_id):
    if _id not in AREA_MAP:
        return _id
    return AREA_MAP[_id]


class ShipLuatable:

    def __init__(self):
        self.ships_data = {}
        self.items_data = {}

        self.SHIP_REMODEL_EXTRA = jsonFile2dic(DB_PATH + SHIP_REMODEL_EXTRA)
        self.ITEM_REMARKS_EXTRA = jsonFile2dic(DB_PATH + ITEM_REMARKS_EXTRA)

        self.SHIPS_KCDATA = jsonFile2dic(DB_PATH + KCDATA_SHIP_ALL_JSON, masterKey='id')
        self.SLOTITEMS_KCDATA = jsonFile2dic(DB_PATH + KCDATA_SLOTITEM_ALL_JSON, masterKey='id')
        self.SHIPS_DB = jsonFile2dic(DB_PATH + SHIPS_DB + '.json', masterKey='id')
        self.ITEMS_DB = jsonFile2dic(DB_PATH + ITEMS_DB + '.json', masterKey='id')
        self.ITEM_TYPES_DB = jsonFile2dic(DB_PATH + ITEM_TYPES_DB + '.json', masterKey='id')
        self.SHIP_NAMESUFFIX_DB = jsonFile2dic(DB_PATH + SHIP_NAMESUFFIX_DB + '.json', masterKey='id')
        self.SHIP_CLASSES_DB = jsonFile2dic(DB_PATH + SHIP_CLASSES_DB + '.json', masterKey='id')
        self.SHIP_SERIES_DB = jsonFile2dic(DB_PATH + SHIP_SERIES_DB + '.json', masterKey='id')
        self.ENTITIES_DB = jsonFile2dic(DB_PATH + ENTITIES_DB + '.json', masterKey='id')
        self.BONUS = jsonFile2dic(DB_PATH + BONUS_JSON)

        self.ITEM_LINKS = {}
        self.SHIP_TYPES_DB = {}

    def __map_lvl_up(self):
        ship_series_data = {}
        for series in self.SHIP_SERIES_DB.values():
            ship_loopable = False
            series_ships = series['ships']
            for i in range(len(series_ships)):
                series_ship = series_ships[i]
                
                #next_blueprint = 'next_blueprint' in series_ship and series_ship[
                    #'next_blueprint'] == 'on'
                #next_catapult = 'next_catapult' in series_ship and series_ship[
                    #'next_catapult'] == 'on'
                #next_level = series_ship['next_lvl'] if 'next_lvl' in series_ship \
                    #and series_ship['next_lvl'] else 0

                
                shipid = series_ship['id']
                _ship = self.SHIPS_DB[shipid]
                try:
                    ship_kcid = str(self.SHIPS_KCDATA[shipid]['wiki_id'])
                except KeyError:
                    continue
                next_loop = 'next_loop' in series_ship and series_ship['next_loop'] == 'on'
                is_last_ship = i == len(series_ships)-1
                is_first_ship = i == 0
                
                if not(ship_loopable) and next_loop:
                    ship_loopable = True
                    first_loopable_shipid = shipid
                    first_loopable_kcid = ship_kcid

                if ship_loopable and is_last_ship:
                    _ship['remodel'].update({
                        'next': first_loopable_shipid,
                        'next_lvl': ''
                    })


                if is_first_ship:
                    first_ship = ship_kcid
                    ship_series_data[first_ship] = {}
                    ship_series_data[first_ship]['编号'] = []
                    ship_series_data[first_ship]['符号'] = []

                ship_series_data[first_ship]['编号'].append(ship_kcid)
                _ship['remodel_series'] = first_ship

                if ship_loopable:
                    ship_series_data[first_ship]['符号'].append('⇒')
                    if is_last_ship:
                        ship_series_data[first_ship]['编号'].append(first_loopable_kcid)
                        ship_series_data[first_ship]['符号'].append('end')
                else:
                    if is_last_ship:
                        ship_series_data[first_ship]['符号'].append('end')
                    else:
                        ship_series_data[first_ship]['符号'].append('→')
                
                if ('remodel' in _ship) and ('next' in _ship['remodel']) and not(is_last_ship):
                    next_shipid = _ship['remodel']['next']
                    #can_remodel = 1
                    #if next_blueprint:
                        #can_remodel += 1
                    #if next_catapult:
                        #can_remodel += 1
                    self.SHIPS_DB[next_shipid]['remodel_info'] = 1
                    #self.SHIPS_DB[shipid]['next_type'] = can_remodel
                    
        ships_series_luatable = 'local d = {}\n'
        ships_series_luatable += '------------------------\n'
        ships_series_luatable += '--   以下为舰娘系列数据列表  -- \n'
        ships_series_luatable += '------------------------\n'
        ships_series_luatable += '\nd.shipSeriesDataTb = '
        ships_series_luatable += luatable(ship_series_data)
        ships_series_luatable += '\n'
        ships_series_luatable += '\nreturn d\n'
        with open(OUPUT_PATH + LUATABLE_PATH + SHIP_SERIES_DB + '.lua', 'w', encoding='utf-8') as fp:
            fp.write(ships_series_luatable)
        with open(OUPUT_PATH + JSON_PATH + SHIP_SERIES_DB + '.json', 'w', encoding='utf-8') as fp:
            json.dump(ship_series_data, fp, ensure_ascii=False, indent=4)

    def __get_ship_namesuffix(self, suffix, lan):
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

    def __get_shipremodel(self, ship_id, next_type, wctf_ship, wiki_ship):
        remodel_cost = wctf_ship['remodel_cost']
        ret = {'等级': 0}
        if 'after_lv' in wiki_ship and wiki_ship['after_lv']:
            ret['等级'] = wiki_ship['after_lv']
        if isinstance(remodel_cost, dict):
            for cost_type, cost in remodel_cost.items():
                ret[COST[cost_type]] = cost
        ret.update({
            '改造前': -1,
            '改造后': -1
        })
        if 'remodel' in wctf_ship and 'prev' in wctf_ship['remodel']:
            ret['改造前'] = str(self.SHIPS_KCDATA[wctf_ship['remodel']['prev']]['wiki_id'])
        if 'after_ship_id' in wiki_ship and wiki_ship['after_ship_id']:
            ret['改造后'] = str(self.SHIPS_KCDATA[wiki_ship['after_ship_id']]['wiki_id'])

        remodel_extra = ''
        if ship_id in self.SHIP_REMODEL_EXTRA:
            remodel_extra = self.SHIP_REMODEL_EXTRA[ship_id]
        else:
            remodel_extra = REMODEL_TYPES[next_type]
        if remodel_extra:
            ret.update({ '图纸': remodel_extra })
        if 'remodel_series' in wctf_ship:
            ret.update({'系列': wctf_ship['remodel_series']})
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
        if wctf_ship['class'] in self.SHIP_CLASSES_DB:
            ship_class = self.SHIP_CLASSES_DB[wctf_ship['class']]['name']['zh_cn']
        else:
            ship_class = '?'
        self.ships_data[str(wiki_ship['wiki_id'])] = {
            'ID': ship_id,
            '图鉴号': wctf_ship['no'],
            '日文名': wctf_ship['name']['ja_jp'] + self.__get_ship_namesuffix(wctf_ship['name']['suffix'], 'ja_jp'),
            '假名': wctf_ship['name']['ja_kana'] + self.__get_ship_namesuffix(wctf_ship['name']['suffix'], 'ja_kana'),
            '中文名': wctf_ship['name']['zh_cn'] + self.__get_ship_namesuffix(wctf_ship['name']['suffix'], 'zh_cn'),
            '舰种': STYPE[wctf_ship['type']],
            '级别': [
                ship_class + '型',
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
                '射程': wctf_ship['stat']['range'],
                '稀有': wctf_ship['rare']
            },
            '装备': {
                '格数': slot_size,
                '搭载': wctf_ship['slot'],
                '初期装备': self.__get_equips(wctf_ship['equip'], slot_size)
            },
            '消耗': {
                '燃料': wctf_ship['consum']['fuel'],
                '弹药': wctf_ship['consum']['ammo']
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
                _ship_id, next_type, wctf_ship, wiki_ship
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
        wiki_links = wctf_ship['links'] if 'links' in wctf_ship else []
        for wiki_link in wiki_links:
            self.ships_data[str(wiki_ship['wiki_id'])].update({
                wiki_link['name']: wiki_link['url']
            })

    def genShipsData(self):
        placeholder = 0
        for ship_id in self.SHIPS_KCDATA.keys():
            if self.SHIPS_KCDATA[ship_id]['wiki_id'] == None:
                placeholder += 1
                self.SHIPS_KCDATA[ship_id]['wiki_id'] = '临时编号' + str(placeholder).zfill(3)
        self.__map_lvl_up()
        for ship_id in self.SHIPS_DB.keys():
            if ship_id in self.SHIPS_KCDATA:
                self.__append_ship(ship_id)
        self.ships_data = sortDict(self.ships_data)
        ships_luatable = 'local d = {}\n'
        ships_luatable += '------------------------\n'
        ships_luatable += '--   以下为舰娘数据列表  -- \n'
        ships_luatable += '------------------------\n'
        ships_luatable += '\nd.shipDataTb = '
        ships_luatable += luatable(self.ships_data)
        ships_luatable += '\n'
        ships_luatable += '\nreturn d\n'
        with open(OUPUT_PATH + LUATABLE_PATH + SHIPS_DATA + '.lua', 'w', encoding='utf-8') as fp:
            fp.write(ships_luatable)
        with open(OUPUT_PATH + JSON_PATH + SHIPS_DATA + '.json', 'w', encoding='utf-8') as fp:
            json.dump(self.ships_data, fp, ensure_ascii=False, indent=4)

    def __load_akashi_list(self):
        with open(OUPUT_PATH + JSON_PATH + AKASHI_LIST_OUTPUT_JSON, 'r', encoding='utf-8') as fp:
            akashiList = json.load(fp)['items']
            for key, val in akashiList.items():
                self.ITEM_LINKS[int(key)] = {
                    '日文Wiki': val['JA_Wiki'] if 'JA_Wiki' in val else '',
                    '英文Wiki': val['EN_Wiki'] if 'EN_Wiki' in val else ''
                }

    def __load_ship_types(self):
        SHIP_TYPES = jsonFile2dic(DB_PATH + SHIP_TYPES_DB + '.json', masterKey='id')
        SHIP_TYPE_COLLECTIONS = jsonFile2dic(DB_PATH + SHIP_TYPE_COLLECTIONS_DB + '.json', masterKey='id')
        for collections in SHIP_TYPE_COLLECTIONS.values():
            types = collections['types']
            for _type in types:
                if type(_type) is list:
                    for _t in _type:
                        self.SHIP_TYPES_DB[_t] = SHIP_TYPES[_type[0]]['name']['zh_cn']
                else:
                    self.SHIP_TYPES_DB[_type] = SHIP_TYPES[_type]['name']['zh_cn']

    def __get_itemstats(self, stats):
        if not stats:
            return {}
        ret = {}
        for key, val in stats.items():
            if key == 'cost':
                continue
            elif key == 'range':
                if isinstance(val, int):
                    val = RANGE[val]
            if not val:
                continue
            #if key == 'range' and 'distance' in stats:
                #continue
            ret[STAT[key]] = val
        return ret

    def __get_item_equipable(self, item_type, equipable_extra_ship):
        _type = self.ITEM_TYPES_DB[item_type]
        ret = []
        if 'equipable_on_type' in _type:
            for ship_typeid in _type['equipable_on_type']:
                ship_codegame = self.SHIP_TYPES_DB[ship_typeid]
                if ship_codegame not in ret:
                    ret.append(ship_codegame)
        if 'equipable_extra_ship' in _type:
            for ship_id in _type['equipable_extra_ship']:
                wctf_ship = self.SHIPS_DB[ship_id]
                ship_name = wctf_ship['name']['zh_cn'] + self.__get_ship_namesuffix(wctf_ship['name']['suffix'], 'zh_cn')
                if ship_name not in ret:
                    ret.append(ship_name)
        if equipable_extra_ship:
            for ship_id in equipable_extra_ship:
                wctf_ship = self.SHIPS_DB[ship_id]
                ship_name = wctf_ship['name']['zh_cn'] + \
                    self.__get_ship_namesuffix(
                        wctf_ship['name']['suffix'], 'zh_cn')
                if ship_name not in ret:
                    ret.append(ship_name)
        return ret

    def __append_item_improvement(self, __item_id, improvements):
        idx = 1
        for improvement in improvements:
            upgrade = improvement['upgrade']
            base_resource = improvement['resource'][0]
            primary_resource = improvement['resource'][1]
            middle_resource = improvement['resource'][2]
            primary_cosume_equip = ''
            primary_cosume_count = 0
            if isinstance(primary_resource[4], list):
                primary_cosume_equip = primary_resource[4][0][0] if primary_resource[4][0][0] else ''
                primary_cosume_count = primary_resource[4][0][1] if primary_resource[4][0][1] else 0
            else:
                primary_cosume_equip = primary_resource[4] if primary_resource[4] else ''
                primary_cosume_count = primary_resource[5] if primary_resource[5] else 0
            middle_cosume_equip = ''
            middle_cosume_count = 0
            if isinstance(middle_resource[4], list):
                middle_cosume_equip = middle_resource[4][0][0] if middle_resource[4][0][0] else ''
                middle_cosume_count = middle_resource[4][0][1] if middle_resource[4][0][1] else 0
            else:
                middle_cosume_equip = middle_resource[4] if middle_resource[4] else ''
                middle_cosume_count = middle_resource[5] if middle_resource[5] else 0
            improve = {
                '资源消费': {
                    '燃料': base_resource[0], '弹药': base_resource[1],
                    '钢材': base_resource[2], '铝': base_resource[3]
                },
                '初期消费': {
                    '开发': [primary_resource[0], primary_resource[1]],
                    '改修': [primary_resource[2], primary_resource[3]],
                    '装备数': primary_cosume_count
                },
                '中段消费': {
                    '开发': [middle_resource[0], middle_resource[1]],
                    '改修': [middle_resource[2], middle_resource[3]],
                    '装备数': middle_cosume_count
                }
            }
            if primary_cosume_count:
                improve['初期消费'].update({
                    '装备': str(primary_cosume_equip).zfill(3)
                })
            if middle_cosume_count:
                improve['中段消费'].update({
                    '装备': str(middle_cosume_equip).zfill(3)
                })
            extra_kits = []
            if upgrade:
                upgrade_resource = improvement['resource'][3]
                upgrade_cosume_equip = ''
                upgrade_cosume_count = 0
                if isinstance(upgrade_resource[4], list):
                    if upgrade_resource[4][0][0]:
                        if isinstance(upgrade_resource[4][0][0], int):
                            upgrade_cosume_equip = upgrade_resource[4][0][0]
                            upgrade_cosume_count = upgrade_resource[4][0][1]
                            if len(upgrade_resource[4]) > 1:
                                extra_kits = upgrade_resource[4][1:]
                        else:
                            extra_kits = upgrade_resource[4]
                elif isinstance(upgrade_resource[4], int):
                    upgrade_cosume_equip = upgrade_resource[4]
                    upgrade_cosume_count = upgrade_resource[5]
                else:
                    extra_kits = [[upgrade_resource[4], upgrade_resource[5]]]
                improve.update({
                    '更新消费': {
                        '开发': [upgrade_resource[0], upgrade_resource[1]],
                        '改修': [upgrade_resource[2], upgrade_resource[3]],
                        '装备数': upgrade_cosume_count
                    }
                })
                if upgrade_cosume_count:
                    improve['更新消费'].update({
                        '装备': str(upgrade_cosume_equip).zfill(3)
                    })
                improve.update({
                    '更新装备': {
                        '装备': str(upgrade[0]).zfill(3),
                        '等级': upgrade[1]
                    }
                })
            req = improvement['req']
            req_items = [[] for i in range(7)]
            for week in req:
                weekdays = week[0]
                support_ships = []
                if isinstance(week[1], list):
                    for ship_id in week[1]:
                        wctf_ship = self.SHIPS_DB[ship_id]
                        ship_name = wctf_ship['name']['zh_cn'] + \
                            self.__get_ship_namesuffix(wctf_ship['name']['suffix'], 'zh_cn')
                        if ship_name not in support_ships:
                            support_ships.append(ship_name)
                else:
                    support_ships.append('〇')
                for i in range(7):
                    if weekdays[i]:
                        for ship_name in support_ships:
                            if ship_name not in req_items[i]:
                                req_items[i].append(ship_name)
            improve['日期'] = {}
            req_idx = 0
            for _req in req_items:
                improve['日期'][WEEK[req_idx]] = _req if _req else ['×']
                req_idx += 1
            extra_remarks = []
            for extra_kit in extra_kits:
                extra_remarks.append('更新时消耗<font color=red>{}</font>x{}{}'.format(
                    CONSUMABLE[extra_kit[0]], extra_kit[1],
                    '，失败时不消耗' if extra_kit[0] != 'consumable_70' else ''))
            improve.update({
                '改修备注': ', '.join(extra_remarks)
            })
            _idx = idx if idx > 1 else ''
            self.items_data[__item_id].update({
                '装备改修{}'.format(_idx): improve
            })
            idx += 1

    def __get_shipname_byid(self, _id):
        return self.SHIPS_DB[_id]['name']['zh_cn'] + self.__get_ship_namesuffix(self.SHIPS_DB[_id]['name']['suffix'], 'zh_cn')

    def __append_item_bonus(self, __item_id, bonuses):
        idx = 1
        for _bonus in bonuses:
            bonus = {}
            if _bonus['star']:
                bonus['改修等级'] = _bonus['star']
            if _bonus['combined']:
                bonus['装备组合'] = []
                for cb in _bonus['combined']:
                    if type(cb) is str:
                        bonus['装备组合'].append(cb)
                    elif type(cb) is int:
                        bonus['装备组合'].append(self.ITEMS_DB[cb]['name']['zh_cn'])
                    elif type(cb) is list:
                        cbs = []
                        for c in cb:
                            cbs.append(self.ITEMS_DB[c]['name']['zh_cn'])
                        bonus['装备组合'].append('/'.join(cbs))
            _include = _bonus['ship']['include']
            _exclude = _bonus['ship']['exclude']
            include = []
            exclude = []
            if _include:
                for itype in _include:
                    if itype == 'id':
                        for sid in _include[itype]:
                            include.append(self.__get_shipname_byid(sid))
                    elif itype == 'type':
                        for tid in _include[itype]:
                            include.append(self.SHIP_TYPES_DB[tid])
                    elif itype == 'class':
                        for cid in _include[itype]:
                            include.append(self.SHIP_CLASSES_DB[cid]['name']['zh_cn'] + '级')
                bonus['适用舰娘'] = include
            if _exclude:
                for itype in _exclude:
                    if itype == 'id':
                        for sid in _exclude[itype]:
                            exclude.append(self.__get_shipname_byid(sid))
                    elif itype == 'type':
                        for tid in _exclude[itype]:
                            exclude.append(self.SHIP_TYPES_DB[tid])
                    elif itype == 'class':
                        for cid in _exclude[itype]:
                            exclude.append(self.SHIP_CLASSES_DB[cid]['name']['zh_cn'] + '级')
                bonus['非适用舰娘'] = exclude
            if _bonus['bonus']['type'] == '-':
                bonus['收益类型'] = '通用'
                bonus['收益属性'] = self.__get_itemstats(_bonus['bonus']['bonus'])
            elif _bonus['bonus']['type'] == 'count':
                bonus['收益类型'] = '数量'
                bonus['收益属性'] = {}
                for c in _bonus['bonus']['bonus']:
                    bonus['收益属性'][c] = self.__get_itemstats(_bonus['bonus']['bonus'][c])
            elif _bonus['bonus']['type'] == 'improve':
                bonus['收益类型'] = '改修'
                bonus['收益属性'] = {}
                for i in _bonus['bonus']['bonus']:
                    bonus['收益属性'][i] = self.__get_itemstats(_bonus['bonus']['bonus'][i])
            elif _bonus['bonus']['type'] == 'area':
                bonus['收益类型'] = '区域'
                bonus['收益属性'] = {}
                for i in _bonus['bonus']['bonus']:
                    bonus['收益属性'][getArea(i)] = self.__get_itemstats(_bonus['bonus']['bonus'][i])
            if 'accumulate' in _bonus:
                bonus['累计套装加成'] = {}
                bonus['累计套装加成'] = self.__get_itemstats(_bonus['accumulate'])

            _idx = idx if idx > 1 else ''
            self.items_data[__item_id].update({
                '额外收益{}'.format(_idx): bonus
            })
            idx += 1

    def __append_item(self, item_id):
        _item_id = str(item_id)
        wctf_item = self.ITEMS_DB[item_id]
        kcdata_item = self.SLOTITEMS_KCDATA[item_id]
        __item_id = _item_id.zfill(3)
        item_category = []
        item_type = wctf_item['type']
        if 'type_ingame' in wctf_item:
            item_category = wctf_item['type_ingame']
        elif 'type' in kcdata_item:
            item_category = kcdata_item['type']
        self.items_data[__item_id] = {
            'ID': item_id,
            '日文名': wctf_item['name']['ja_jp'],
            '中文名': wctf_item['name']['zh_cn'],
            '类别': item_category,
            '稀有度': '☆' * (wctf_item['rarity'] + 1),
            '状态': {
                '开发': 1 if 'craftable' in wctf_item and wctf_item['craftable'] else 0,
                '改修': 1 if 'improvable' in wctf_item and wctf_item['improvable'] else 0,
                '更新': 1 if 'improvement' in wctf_item and 'upgrade' in wctf_item['improvement'] and wctf_item['improvement']['upgrade'] else 0,
                '熟练': 1 if item_type in RANK_UPGARDABLE else 0
            },
            '属性': self.__get_itemstats(wctf_item['stat']),
            '废弃': {
                '燃料': wctf_item['dismantle'][0], '弹药': wctf_item['dismantle'][1],
                '钢材': wctf_item['dismantle'][2], '铝': wctf_item['dismantle'][3]
            },
            '装备适用': self.__get_item_equipable(item_type, wctf_item['equipable_extra_ship'] if 'equipable_extra_ship' in wctf_item else None),
            '备注': self.ITEM_REMARKS_EXTRA[__item_id] if __item_id in self.ITEM_REMARKS_EXTRA else ''
        }
        if _item_id in self.BONUS:
            bonuses = self.BONUS[_item_id]
            self.__append_item_bonus(__item_id, bonuses)
        if 'improvement' in wctf_item and wctf_item['improvement']:
            improvements = wctf_item['improvement']
            self.__append_item_improvement(__item_id, improvements)
        if item_id in self.ITEM_LINKS:
            item_links = self.ITEM_LINKS[item_id]
            for link_title, link_url in item_links.items():
                self.items_data[__item_id].update({
                    link_title: link_url
                })

    def genItemsData(self):
        self.__load_akashi_list()
        self.__load_ship_types()
        for item_id in self.ITEMS_DB.keys():
            if item_id in self.SLOTITEMS_KCDATA:
                self.__append_item(item_id)
        self.items_data = sortDict(self.items_data)
        items_luatable = 'local d = {}\n'
        items_luatable += '------------------------\n'
        items_luatable += '--   以下为装备数据列表  -- \n'
        items_luatable += '------------------------\n'
        items_luatable += '\nd.equipDataTb = '
        items_luatable += luatable(self.items_data)
        items_luatable += '\n'
        items_luatable += '\nreturn d\n'
        with open(OUPUT_PATH + LUATABLE_PATH + ITEMS_DATA + '.lua', 'w', encoding='utf-8') as fp:
            fp.write(items_luatable)
        with open(OUPUT_PATH + JSON_PATH + ITEMS_DATA + '.json', 'w', encoding='utf-8') as fp:
            json.dump(self.items_data, fp, ensure_ascii=False, indent=4)

    def start(self):
        self.genShipsData()
        self.genItemsData()
