#!/usr/bin/env python3

import asyncio
import json
import re
import time

import aiohttp

from config import DB_PATH, WIKIA_OUTPUT_JSON
from HttpClient import HttpClient


class WikiaCrawler(HttpClient):

    CATE_MEMBER_URL = 'https://kancolle.wikia.com/api.php?action=query&list=categorymembers&cmtitle=Category:Enemy_ship_modules&cmlimit=500&format=json'
    SHIP_CATE_URL = 'https://kancolle.wikia.com/api.php?action=query&list=categorymembers&cmtitle={}&cmlimit=500&format=json'
    SHIP_URL = 'https://kancolle.wikia.com/wiki/{}?action=raw'
    DETAIL_URL = 'https://kancolle.wikia.com/api.php?action=expandtemplates&text={}&format=json'
    MODULE_PATTERN = re.compile(r'Module:')
    SHIPTYPE_PATTERN = re.compile(r'\["(.*)"\]')
    NUM_PATTERN = re.compile(r'\d+')

    def __init__(self):
        super().__init__()

    async def getDetail(self, moduleName):
        MODULE_NAME = '_'.join(moduleName.strip()[7:].split())
        ret = []
        async with self.session.get(self.SHIP_URL.format(moduleName)) as resp:
            content = await resp.text()
            all_types = self.SHIPTYPE_PATTERN.findall(content)
            text = ''
            for _type in all_types:
                text += '{{{{EnemyShipInfoKai|{}/{}}}}}'.format(
                    MODULE_NAME, _type.strip('{}'))
            async with self.session.get(self.DETAIL_URL.format(text)) as resp:
                res_json = await resp.json()
                htmlArr = res_json['expandtemplates']['*'].split("{|")[1:]
                for val in htmlArr:
                    txt = val.split("'''")
                    dayBattle = 0
                    re_res = self.NUM_PATTERN.search(txt[47].strip())
                    if re_res:
                        dayBattle = int(re_res.group(0))
                    res = {
                        'id': txt[3].split('No.')[1].split(' ')[0].strip(),
                        'DayBattle': dayBattle,
                        # 'AirPower': txt[36].split('|')[3].strip(),
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
            async with self.session.get(self.SHIP_CATE_URL.format(catName)) as resp:
                res_json = await resp.json()
                categorymembers = list(
                    map(lambda x: x['title'], res_json['query']['categorymembers']))
                ships += categorymembers

        tasks = []

        for moduleName in ships:
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
                    print('Wikia-Crawler: {duplicate}')
                    print('Wikia-Crawler: ' + json.dumps(detail))
                    print('Wikia-Crawler: ' + json.dumps(result[_id]))
        with open(DB_PATH + WIKIA_OUTPUT_JSON, 'w', encoding='utf-8') as fp:
            json.dump(result, fp, ensure_ascii=False, indent=4, sort_keys=True)
