# -*- coding: UTF-8 -*-
import asyncio
import json
import re
import time

import aiohttp

from config import (AIRPOWER_TABLE, DB_PATH, LUATABLE_PATH, OUPUT_PATH, WIKIA_OUTPUT_JSON)
from HttpClient import HttpClient


class WikiaCrawler(HttpClient):

    CATE_MEMBER_URL = 'https://kancolle.fandom.com/api.php?action=query&list=categorymembers&cmtitle=Category:Enemy_ship_modules&cmlimit=500&format=json'
    SHIP_CATE_URL = 'https://kancolle.fandom.com/api.php?action=query&list=categorymembers&cmtitle={}&cmlimit=500&format=json'
    SHIP_URL = 'https://kancolle.fandom.com/wiki/{}?action=raw'
    DETAIL_URL = 'https://kancolle.fandom.com/api.php?action=expandtemplates&text={}&format=json'
    BOSS_CATE_URL = 'https://kancolle.fandom.com/api.php?action=query&list=allpages&apprefix=Data%2FEnemy%2F&apnamespace=828&aplimit=max&format=json'
    MODULE_PATTERN = re.compile(r'Module:')
    SHIPTYPE_PATTERN = re.compile(r'\["(.*)"\]')
    NUM_PATTERN = re.compile(r'\d+')

    def __init__(self):
        super().__init__()

    async def getDetail(self, moduleName):
        MODULE_NAME = '_'.join(moduleName.strip()[18:].split())
        if MODULE_NAME.find('(fog)') != -1:
            return []
        ret = []
        url = self.SHIP_URL.format('_'.join(moduleName.split()))
        async with self.session.get(url) as resp:
            content = await resp.text()
            if content.startswith('#REDIRECT'):
                redirect_module_name = content.strip()[12:-2]
                ret = await self.getDetail(redirect_module_name)
                return ret
            all_types = self.SHIPTYPE_PATTERN.findall(content)
            text = ''
            for _type in all_types:
                text += '{{{{EnemyShipInfoKai|{}/{}}}}}'.format('_'.join(MODULE_NAME.split()), _type.strip('{}'))
            url = self.DETAIL_URL.format(text)
            async with self.session.get(url) as resp:
                res_json = await resp.json()
                htmlArr = res_json['expandtemplates']['*'].split("{|")[1:]
                for val in htmlArr:
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
                    res = {
                        'id': txt[3].split('No.')[1].split(' ')[0].strip(),
                        'DayBattle': dayBattle,
                        'AirPower': airPower
                        # 'Slots': txt[36].split('|')[5].strip(),
                        # 'OpeningAirstrike': txt[43].strip(),
                        # 'OpeningTorpedo': txt[45].strip(),
                        # 'ArtillerySpotting': txt[49].strip(),
                        # 'ClosingTorpedo': txt[51].strip(),
                        # 'ASWAttack': txt[53].strip(),
                        # 'NightBattle': txt[55].strip()
                    }
                    if res['id'] == '??':
                        continue
                    res['id'] = int(res['id'])
                    if res['id'] < 1000:
                        res['id'] += 1000
                    ret.append(res)
        print('Wikia-Crawler: {} ok!'.format(MODULE_NAME))
        return ret

    async def start(self):
        ships = []
        cates = []
        async with self.session.get(self.CATE_MEMBER_URL) as resp:
            res_json = await resp.json()
            categorymembers = list(
                map(lambda x: x['title'], res_json['query']['categorymembers']))
            ships = list(
                filter(lambda x: self.MODULE_PATTERN.match(x), categorymembers))
            cates = list(
                filter(lambda x: not self.MODULE_PATTERN.match(x), categorymembers))

        for catName in cates:
            if catName == 'Category:Enemy boss ship modules':
                async with self.session.get(self.BOSS_CATE_URL) as resp:
                    res_json = await resp.json()
                    categorymembers = list(
                        map(lambda x: x['title'], res_json['query']['allpages']))
                    ships += categorymembers
            else:
                async with self.session.get(self.SHIP_CATE_URL.format(catName)) as resp:
                    res_json = await resp.json()
                    categorymembers = list(
                        map(lambda x: x['title'], res_json['query']['categorymembers']))
                    ships += categorymembers

        tasks = []

        for moduleName in ships:
            if moduleName.startswith('Module:Data/Enemy/Vita:'):
                continue
            if moduleName.endswith('(fog)'):
                continue
            tasks.append(asyncio.ensure_future(self.getDetail(moduleName)))

        dones = (await asyncio.wait(tasks))[0]
        ids = set()
        result = {}
        for task in dones:
            results = task.result()
            for detail in results:
                _id = detail['id']
                detail.pop('id')
                result[_id] = detail
                if _id not in ids:
                    ids.add(_id)
                else:
                    i1 = json.dumps(detail)
                    i2 = json.dumps(result[_id])
                    if i1 != i2:
                        print('Wikia-Crawler: === duplicate ===')
                        print('Wikia-Crawler: ' + i1)
                        print('Wikia-Crawler: ' + i2)
                        print('Wikia-Crawler: === duplicate ===')
        airPowerTable = '''local p = { }

p.enemyFighterPowerDataTb = {
'''
        for _id in sorted(result):
            detail = result[_id]
            if not detail["AirPower"]:
                continue
            airPowerTable += '    ["{}"] = {},\n'.format(
                _id, detail["AirPower"])
        airPowerTable += '''}

p.enemyFighterPowerDataTb2 = {

    -- 陆航阶段的深海栖舰制空值
    ["1505"] = 1,
    ["1506"] = 1,
    ["1507"] = 1,
    ["1509"] = 1,
    ["1511"] = 1,
    ["1518"] = 1,
    ["1519"] = 1,
    ["1520"] = 1,
    ["1522"] = 2,
    ["1527"] = 2,
    ["1529"] = 2,
    ["1541"] = 2,
    ["1543"] = 2,
    ["1555"] = 1,
    ["1566"] = 4,
    ["1567"] = 4,
    ["1591"] = 1,
    ["1592"] = 1,
    ["1594"] = 2,
    ["1595"] = 2,
    ["1601"] = 1,
    ["1602"] = 1,
    ["1603"] = 2,
    ["1604"] = 2,
    ["1659"] = 4,
    ["1660"] = 4,
    ["1661"] = 4,
    ["1662"] = 4,
    ["1663"] = 4,
    ["1664"] = 4,
    ["1684"] = 4,
    ["1685"] = 4,
    ["1686"] = 4,
    ["1687"] = 4,
    ["1688"] = 4,
    ["1689"] = 4,
    ["1705"] = 4,
    ["1706"] = 4,
    ["1707"] = 4,
    ["1790"] = 2,
    ["1791"] = 2,
    ["1792"] = 2,
    ["1793"] = 2,
    ["1794"] = 2,
    ["1795"] = 2,
    ["1796"] = 2,
    ["1797"] = 2,
    ["1798"] = 2,
    ["1862"] = 1,
    ["1863"] = 4,
    ["1864"] = 4,
    ["1895"] = 4,
    ["1896"] = 4,
    ["1897"] = 4,
    ["1898"] = 4,
    ["1899"] = 4,
    ["1900"] = 4,
    ["1901"] = 4,
    ["1902"] = 4,
    ["1903"] = 4,
}

return p

'''
        with open(OUPUT_PATH + LUATABLE_PATH + AIRPOWER_TABLE, 'w', encoding='utf-8') as fp:
            fp.write(airPowerTable)
        with open(DB_PATH + WIKIA_OUTPUT_JSON, 'w', encoding='utf-8') as fp:
            json.dump(result, fp, ensure_ascii=False, indent=4, sort_keys=True)
