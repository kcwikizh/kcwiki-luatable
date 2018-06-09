#!/usr/bin/env python3

import asyncio
import json
import os
import re
import time
from collections import OrderedDict

import aiohttp
import lxml
from bs4 import BeautifulSoup, element

import utils
from config import (AKASHI_LIST_CACHE_PATH, AKASHI_LIST_OUTPUT_JSON,
                    AKASHI_LIST_OUTPUT_LUA, AKASHI_LIST_URL, DB_PATH,
                    OUPUT_PATH)
from HttpClient import HttpClient


class AkashiListCrawler(HttpClient):

    SHIP_TYPES = [
        '駆逐艦', '軽巡洋艦', '重巡洋艦', '戦艦',
        '軽空母', '正規空母', '水上機母艦', '航空戦艦',
        '航空巡洋艦', '重雷装巡洋艦', '練習巡洋艦', '揚陸艦',
        '工作艦', '潜水艦', '潜水空母',
        '補給艦', '海防艦', '基地航空隊'
    ]
    ID_PATTERN = re.compile(r'[0-9]+')

    def __init__(self, cache=True, sannma=False):
        super().__init__()
        self.cache = cache
        self.sannma = sannma
        self.tot_items = 0
        self.ok_items = 0
        self.weapon_list = {}
        self.items = {}
        if self.cache and not os.path.isdir(AKASHI_LIST_CACHE_PATH):
            os.mkdir(AKASHI_LIST_CACHE_PATH)

    def get_text(self, node):
        '''
        获取节点文本
        '''
        if not node:
            return ''
        if isinstance(node, element.NavigableString):
            return node.string.strip()
        return node.get_text().strip()

    def get_sannma(self, soup):
        '''
        获取对秋刀鱼装备数据
        '''
        sannmas = dict()
        all_aura = soup.find_all('img', attrs={'aura': '1'})
        for aura in all_aura:
            aura_weapon = aura.parent.parent
            w_id = aura_weapon.attrs['id']
            aura_stat = self.get_text(aura_weapon.find(
                'span', class_='saurytxt').contents[-1])
            sannmas[w_id] = aura_stat
        return sannmas

    async def get_weaponlist(self):
        '''
        解析首页得到全部装备的编号
        '''
        async with self.session.get(AKASHI_LIST_URL) as resp:
            content = await resp.text()
            content_soup = BeautifulSoup(content, 'lxml')
            sannma_stats = None
            if self.sannma:
                sannma_stats = self.get_sannma(content_soup)
            weapon_selector = content_soup.select('div.weapon')
            weapon_id_list = list()
            for weapon in weapon_selector:
                if 'id' in weapon.attrs:
                    weapon_id_list.append(weapon.attrs['id'].strip())
                else:
                    _id = 'w' + \
                        self.ID_PATTERN.search(
                            weapon.attrs['data-title']).group()
                    weapon_id_list.append(_id.strip())
            self.tot_items = len(weapon_id_list)
            return weapon_id_list, sannma_stats

    def get_remodel(self, resource, supports):
        '''
        获取不同改修方式的详情
        '''
        remodel_info = dict()
        remodel_info['support_ships'] = list()
        remodel_info['resource_cost'] = dict()
        upgrade = dict()

        # 二番艦
        support_ships = supports.find_all('div', class_='support-ship')
        for support_ship in support_ships:
            support_ship_name = ''
            support_weeks = list()
            for name in support_ship:
                if isinstance(name, element.NavigableString):
                    support_ship_name += self.get_text(name)
            weeks = support_ship.find('div', class_='weeks')
            for weekday in weeks.children:
                if isinstance(weekday, element.NavigableString):
                    continue
                if not 'class' in weekday.attrs:
                    support_weeks.append(0)
                    continue
                class_list = weekday.attrs['class']
                if 'enable' in class_list:
                    support_weeks.append(1)
                else:
                    support_weeks.append(0)
            remodel_info['support_ships'].append({
                'support_ship': support_ship_name,
                'support_weeks': support_weeks
            })

        # 基础资源消耗
        base_cost = dict()
        fuel_node = resource.find('td', class_='resource').find(
            'span', class_='ri-fuel')
        if fuel_node:
            fuel = int(self.get_text(fuel_node))
            if fuel:
                base_cost['fuel'] = fuel
        ammo_node = resource.find('td', class_='resource').find(
            'span', class_='ri-ammo')
        if ammo_node:
            ammo = int(self.get_text(ammo_node))
            if ammo:
                base_cost['ammo'] = ammo
        steel_node = resource.find('td', class_='resource').find(
            'span', class_='ri-steel')
        if steel_node:
            steel = int(self.get_text(steel_node))
            if steel:
                base_cost['steel'] = steel
        bauxite_node = resource.find('td', class_='resource').find(
            'span', class_='ri-bauxite')
        if bauxite_node:
            bauxite = int(self.get_text(bauxite_node))
            if bauxite:
                base_cost['bauxite'] = bauxite
        if base_cost:
            remodel_info['base_cost'] = base_cost

        for cost_line in resource.table.children:
            if isinstance(cost_line, element.NavigableString):
                continue
            thead = cost_line.th
            if thead:
                ttitle = self.get_text(thead)
                cost = dict()
                if ttitle and ttitle != '改修必要資材' and ttitle != '★':
                    tds = cost_line.find_all('td')
                    buildkit_num = self.get_text(tds[0])
                    remodelkit_num = self.get_text(tds[1])
                    equipkit = list()
                    for equip in tds[2].stripped_strings:
                        if equip:
                            equipkit.append(equip)
                    if ttitle == 'MAX':
                        upgrade['cost'] = {
                            'buildkit_num': buildkit_num,
                            'remodelkit_num': remodelkit_num,
                            'equipkit': equipkit
                        }
                    else:
                        cost['buildkit_num'] = buildkit_num
                        cost['remodelkit_num'] = remodelkit_num
                        cost['equipkit'] = equipkit
                        remodel_info['resource_cost'][ttitle] = cost

        # 升级上位
        upgrade_table = resource.select_one('tr.upgrade > td > table')
        if upgrade_table:
            all_tds = upgrade_table.find_all('td')
            if all_tds:
                for all_td in all_tds[-1].children:
                    item_name = self.get_text(all_td)
                    if item_name and '更新不可' not in item_name:
                        upgrade['item_name'] = item_name
                        break

        if upgrade:
            remodel_info['upgrade'] = upgrade

        return remodel_info

    async def get_detail(self, weaponid):
        '''
        根据武器id获取装备改修详情
        '''
        requesturl = '{0}/detail/{1}.html'.format(
            AKASHI_LIST_URL, weaponid)
        # 处理缓存
        if self.cache:
            cache_path = os.path.abspath(
                '{0}/{1}.json'.format(AKASHI_LIST_CACHE_PATH, weaponid))
            async with self.session.head(requesturl) as hand_shake:
                last_modified = hand_shake.headers.get('Last-Modified')
                if os.path.isfile(cache_path) and last_modified:
                    with open(cache_path, 'r', encoding='utf_8') as fcache:
                        try:
                            cache = json.load(fcache)
                            if cache['last_modified'] == last_modified:
                                self.ok_items += 1
                                print(
                                    'Akashi-List: ({} / {}) ok!'.format(self.ok_items, self.tot_items))
                                return cache['detail']
                        except json.JSONDecodeError:
                            pass

        # 处理没有缓存或者缓存过期的文件
        content = ''
        async with self.session.get(requesturl) as res:
            content = await res.text()
        content_soup = BeautifulSoup(content, 'lxml')
        detail = dict()
        detail['id'] = int(weaponid.lstrip('w'))

        # 解析获取编号，名字，装备类型 这三个数据
        name_selector = content_soup.select_one('div.name')
        item_no = self.get_text(name_selector.find('span', class_='no'))
        item_title = self.get_text(name_selector.find('span', class_='title'))
        wiki_links_selector = name_selector.find_all('a')
        if item_no:
            detail['no'] = item_no
        if item_title:
            detail['item_name'] = {
                'zh': self.items[detail['id']]['name']['zh_cn'],
                'ja': item_title
            }

        for name_child in name_selector:
            if isinstance(name_child, element.NavigableString):
                item_type = self.get_text(name_child)
                if not item_type:
                    continue
                detail['item_type'] = item_type
                break

        # 获取介绍
        item_intro = self.get_text(
            content_soup.select_one('div.article.jpdetail'))
        if item_intro:
            detail['item_intro'] = item_intro

        # 获取装备基本属性
        status_selector = content_soup.select_one('div.detail-status > table')

        # 给detail-status表格里的行分类
        lines_idx = 0
        is_extra_ok = False
        fit_type = None
        stat_lines = list()
        equip_lines = list()
        extra_equip_lines = list()
        fitting_lines = list()
        status_lines = status_selector.find_all('tr')
        for status_line in status_lines:
            status_title = status_line.th
            if status_title and status_title.has_attr('class') \
                    and 'title' in status_title.attrs['class']:
                class_list = status_title.attrs['class']
                if len(class_list) > 1:
                    lines_idx = 4
                    fit_select = class_list[1]
                    if fit_select == 'fit005':
                        fit_type = '命中補正値'
                    elif fit_select == 'rfit':
                        fit_type = '夜戦命中補正値'
                    elif fit_select == 'hitfit':
                        fit_type = '命中補正値?'
                    else:
                        fit_type = 'フィット命中補正値'
                else:
                    status_title_name = self.get_text(status_title)
                    if status_title_name == '装備ステータス':
                        lines_idx = 1
                    elif status_title_name == '装備可能艦種':
                        lines_idx = 2
                    elif status_title_name == '増設装備可能艦種':
                        lines_idx = 3
                    elif status_title_name == '装備可能艦種(増設装備可)':
                        lines_idx = 2
                        is_extra_ok = True
                continue
            if not lines_idx:
                continue
            elif lines_idx == 1:
                stat_lines.append(status_line)
            elif lines_idx == 2:
                equip_lines.append(status_line)
            elif lines_idx == 3:
                extra_equip_lines.append(status_line)
            elif lines_idx == 4:
                fitting_lines.append(status_line)

        # 处理stat 属性
        stat = dict()
        for stat_line in stat_lines:
            stat_name = ''
            for stat_row in stat_line:
                stat_row_name = stat_row.name
                if not stat_row_name:
                    continue
                if stat_row_name == 'th':
                    stat_name = self.get_text(stat_row)
                elif stat_row_name == 'td':
                    if not stat_name:
                        continue
                    if not stat_row.contents:
                        stat[stat_name] = ''
                    else:
                        val = ''
                        for stat_val in stat_row.children:
                            if isinstance(stat_val, element.NavigableString):
                                val += self.get_text(stat_val)
                            elif stat_val.name == 'small':
                                val += self.get_text(stat_val)
                        stat[stat_name] = val
        if stat_lines:
            detail['item_stat'] = stat

        # 处理equip 装备情况
        equip = dict()
        extra = list()
        for equip_line in equip_lines:
            equip_line_children = equip_line.find_all('td')
            for equip_row in equip_line_children:
                is_ok = equip_row.has_attr(
                    'class') and 'ok' in equip_row.attrs['class']
                ship_type = self.get_text(equip_row)
                if not ship_type:
                    continue
                if ship_type in self.SHIP_TYPES:
                    if is_ok:
                        equip[ship_type] = 1
                    else:
                        equip[ship_type] = 0
                else:
                    extra.append(ship_type)
        if extra:
            equip['extra'] = extra
        if equip:
            detail['item_equip'] = equip

        # 处理extra_equip 增设
        extra_equip = dict()
        extra_equip_extra = list()
        for extra_equip_line in extra_equip_lines:
            extra_equip_line_children = extra_equip_line.find_all('td')
            for extra_equip_row in extra_equip_line_children:
                is_ok = extra_equip_row.has_attr(
                    'class') and 'ok' in extra_equip_row.attrs['class']
                ship_type = self.get_text(extra_equip_row)
                if not ship_type:
                    continue
                if ship_type in self.SHIP_TYPES:
                    if is_ok:
                        extra_equip[ship_type] = 1
                    else:
                        extra_equip[ship_type] = 0
                else:
                    extra_equip_extra.append(ship_type)
        if extra_equip_extra:
            extra_equip['extra'] = extra_equip_extra
        if extra_equip:
            detail['item_extra_equip'] = extra_equip

        if is_extra_ok and 'item_extra_equip' not in detail and 'item_equip' in detail:
            detail['item_extra_equip'] = detail['item_equip']

        # 处理fitting 适重
        if fit_type:
            detail['item_fitting_type'] = fit_type
        fitting = list()
        for fitting_line in fitting_lines:
            fitting_line_children = fitting_line.find_all('td')
            for fitting_row in fitting_line_children:
                if not fitting_row.contents:
                    continue
                ship_correct = self.get_text(
                    fitting_row.find('span', class_='cor'))
                ship_class = self.get_text(fitting_row.contents[1])
                ship_fitting = fitting_row.attrs['class'][0]
                fitting.append({
                    'ship_class': ship_class,
                    'ship_fitting': ship_fitting,
                    'ship_correct': ship_correct,
                })
        if fitting_lines:
            detail['item_fitting'] = fitting

        # 处理remodel 改修值变化
        remodel_selector = content_soup.select_one(
            'div.remodel-table > table')
        if remodel_selector:
            remodel = dict()
            for remodel_line in remodel_selector:
                remodel_line_name = remodel_line.name
                if not remodel_line_name:
                    continue
                child_count = 0
                for remodel_row in remodel_line.children:
                    remodel_row_name = remodel_row.name
                    if remodel_row_name:
                        child_count += 1
                if child_count is 1 and 'class' not in remodel_line.attrs:
                    continue
                class_list = remodel_line.attrs['class']
                if 'equip-count' in class_list or 'equip-per-star' in class_list:
                    continue
                remodel_title = ''
                for remodel_row in remodel_line.children:
                    remodel_row_name = remodel_row.name
                    if not remodel_row_name:
                        continue
                    if remodel_row_name == 'th':
                        remodel_title = self.get_text(remodel_row)
                        if remodel_title == '砲台':
                            remodel_title += '特効倍率'
                        elif remodel_title == '特効倍率':
                            continue
                        if remodel_title not in remodel:
                            remodel[remodel_title] = list()
                    elif remodel_row_name == 'td':
                        if not remodel_title:
                            continue
                        value = self.get_text(remodel_row)
                        remodel[remodel_title].append(value)
            if '夜戦火力' in remodel and not remodel['夜戦火力']:
                remodel['夜戦火力'] = remodel['火力']
            if remodel:
                detail['item_remodel'] = remodel

        # 处理remodel-info 改修信息
        resource_tables = content_soup.find_all('div', class_='resource-table')
        support_tables = content_soup.find_all(
            'div', class_='support-ship-table')
        resource_list = list()
        support_list = list()
        for resource_table in resource_tables:
            thead = self.get_text(resource_table.table.tr.th)
            if thead == '改修必要資材':
                resource_list.append(resource_table)
        for support_table in support_tables:
            thead = self.get_text(support_table.table.tr.th)
            if thead == '二番艦':
                support_list.append(support_table)

        remodel_size = len(support_list)
        remodel_info = list()
        for i in range(remodel_size):
            remodel_info.append(self.get_remodel(
                resource_list[i], support_list[i]))

        if remodel_info:
            detail['remodel_info'] = remodel_info

        # 处理build 开发
        build_selector = content_soup.select_one('div.build-table > table')
        if build_selector:
            buid = dict()
            secretary_selector = content_soup.select_one(
                'div.build-table > table div.secretary')
            fuel_selector = content_soup.select_one(
                'div.build-table > table span.ri.ri-fuel')
            ammo_selector = content_soup.select_one(
                'div.build-table > table span.ri.ri-ammo')
            steel_selector = content_soup.select_one(
                'div.build-table > table span.ri.ri-steel')
            bauxite_selector = content_soup.select_one(
                'div.build-table > table span.ri.ri-fuel')
            if secretary_selector:
                secretary = self.get_text(secretary_selector)
                buid['secretary'] = secretary
            buid['cost'] = dict()
            if fuel_selector:
                fuel = self.get_text(fuel_selector)
                buid['cost']['fuel'] = int(fuel)
            if ammo_selector:
                ammo = self.get_text(ammo_selector)
                buid['cost']['ammo'] = int(ammo)
            if steel_selector:
                steel = self.get_text(steel_selector)
                buid['cost']['steel'] = int(steel)
            if bauxite_selector:
                bauxite = self.get_text(bauxite_selector)
                buid['cost']['bauxite'] = int(bauxite)
            if buid['cost']:
                detail['item_build'] = buid

        # 处理equip-ship 初始带有装备
        equip_ships_selector = content_soup.select(
            'div.equip-table > table > tr > td')
        if equip_ships_selector:
            equip_ships = list()
            for equip_ship in equip_ships_selector:
                equip_ship_name = self.get_text(equip_ship)
                equip_ships += equip_ship_name.split()
            detail['equip_ships'] = equip_ships

        # 添加wiki链接
        for wiki_link in wiki_links_selector:
            wiki_name = self.get_text(wiki_link)
            if wiki_name == 'Wiki':
                detail['JA_Wiki'] = wiki_link.attrs['href']
            elif wiki_name == 'Wikia':
                detail['EN_Wiki'] = wiki_link.attrs['href']

        # 重写缓存
        if self.cache and last_modified:
            if os.path.isdir(AKASHI_LIST_CACHE_PATH):
                with open(cache_path, 'w', encoding='utf_8') as fwptr:
                    json.dump({
                        'last_modified': last_modified,
                        'detail': detail
                    }, fwptr, ensure_ascii=False)
        self.ok_items += 1
        print('Akashi-List: ({} / {}) ok!'.format(self.ok_items, self.tot_items))
        return detail

    def gen_luatable(self):
        lua_table = 'local k = {}\n\n'
        lua_table += 'k.EquipUpdateTb = '
        lua_table += utils.luatable(self.weapon_list)
        lua_table += '\n\nreturn k\n'
        return lua_table

    async def start(self):
        utils.nedb2json(DB_PATH + 'items.nedb', DB_PATH + 'items.json')
        self.items = utils.jsonFile2dic(DB_PATH + 'items.json', masterKey='id')
        akashi_json = {
            'week': ['日', '月', '火', '水', '木', '金', '土'],
            # 从11星开始
            'pre_star': [
                '(5,6)', '(6,6)', '(6,7)', '(7,7)', '(7,8)',
                '(8,8)', '(8,9)', '(9,9)', '(9,10)', '(10×2)',
                '(7×3)', '(7,7,8)', '(7,8,8)', '(8×3)', '(8,8,9)',
                '(8,9,9)', '(9×3)', '(9,9,10)', '(9,10,10)', '(10×3)',
                '(7,8×3)', '(8×4)', '(8×3,9)', '(8,9)×2', '(8,9×3)',
                '(9×4)', '(9×3,10)', '(9,10)×2', '(9,10×3)', '(10×4)'
            ]
        }

        id_list, sannma_stats = await self.get_weaponlist()

        if self.sannma:
            akashi_json['sannma_stats'] = sannma_stats

        print('Akashi-List: Total {} items.'.format(len(id_list)))
        tasks = []
        for weapon_id in id_list:
            tasks.append(asyncio.ensure_future(self.get_detail(weapon_id)))
        self.weapon_list = {}
        dones, pendings = await asyncio.wait(tasks)
        for task in dones:
            detail = task.result()
            wp_id = int(detail['id'])
            self.weapon_list[wp_id] = detail
        print('Akashi-List: {} done, {} pendings.'.format(len(dones), len(pendings)))
        akashi_json['items'] = self.weapon_list
        with open(OUPUT_PATH + AKASHI_LIST_OUTPUT_JSON, 'w', encoding='utf_8') as fjson:
            json.dump(akashi_json, fjson, ensure_ascii=False,
                      indent=2, sort_keys=True)
        weapon_list = OrderedDict()
        for item_id, item_info in sorted(self.weapon_list.items()):
            weapon_list[item_id] = item_info
        self.weapon_list = weapon_list
        lua_table = self.gen_luatable()
        with open(OUPUT_PATH + AKASHI_LIST_OUTPUT_LUA, 'w', encoding='utf-8') as flua:
            flua.write(lua_table)
