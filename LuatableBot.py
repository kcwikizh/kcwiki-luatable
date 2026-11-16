#!/usr/bin/env python3

import asyncio
import os
import shutil
import subprocess
import time
import traceback
from os import environ, path

from config import (AIRPOWER_TABLE, AKASHI_LIST_OUTPUT_LUA, BONUS_JS, DB_PATH,
                    ENTITIES_DB, ITEM_TYPES_DB, ITEMS_DATA, ITEMS_DATA_V2, ITEMS_DB, SHIP_REMODEL_EXTRA,
                    JSON_PATH, KCDATA_SHIP_ALL_JSON, KCDATA_SLOTITEM_ALL_JSON,
                    KCKIT_NAME, LUATABLE_PATH, OUPUT_PATH, SCRIPTS_PATH,
                    SEASONAL_PATH, SHINKAI_ITEMS_DATA, SHINKAI_SHIPS_DATA,
                    SHIP_CLASSES_DB, SHIP_NAMESUFFIX_DB, SHIP_SERIES_DB,
                    SHIP_TYPE_COLLECTIONS_DB, SHIP_TYPES_DB,
                    SHIPCLASSES_MAPPING_DATA, SHIPS_DATA, SHIPS_DB,
                    WCTF_DB_NAME)
from crawlers import (AkashiListCrawler, SeasonalCrawler,
                      WikiwikiCrawler)
from DBDownloader import DBDownloader
from ShinkaiLuatable import ShinkaiLuatable
from ShipClassMappingLuatable import ShipClassMappingLuatable
from ShipLuatable import ShipLuatable
from utils import nedb2json
from WikiBot import WikiBot

def LuatableBotTask(skip_fails = False):
    def inner(fn):
        async def wrapper(*args, **kw):
            print('[{}]: Task starting...'.format(fn.__name__))
            START = time.time()
            try:
                await fn(*args, **kw)
            except Exception as e:
                if not skip_fails:
                    raise e
                else:
                    print('[{}]: Task skip'.format(fn.__name__))
                    traceback.print_exc()
                    # 让跳过在 CI 里显式可见（GitHub Actions 注解），而不是只藏在日志里
                    print('::warning title={} skipped::{}'.format(
                        fn.__name__, str(e).replace('\n', ' ')[:400]))
            END = time.time()
            print('[{}]: Task total used {}s'.format(fn.__name__, round(END - START, 3)))
        return wrapper
    return inner

def Switch(name):
    def inner(fn):
        async def wrapper(*args, **kw):
            if environ.get(name):
                await fn(*args, **kw)
        return wrapper
    return inner

class LuatableBotException(Exception):
    def __init__(self, message):
        super().__init__(message)

def exec(args, check=False):
    print('exec: ' + ' '.join(args))
    try:
        result = subprocess.run(args)
    except Exception as e:
        raise LuatableBotException(e)
    if check and result.returncode != 0:
        raise LuatableBotException('命令执行失败（exit {}）：{}'.format(result.returncode, ' '.join(args)))

class LuatableBot:

    def __init__(self):
        self.task_status = {}
        if not path.isdir(DB_PATH):
            os.mkdir(DB_PATH)
        if not path.isdir(OUPUT_PATH):
            os.mkdir(OUPUT_PATH)
        if not path.isdir(OUPUT_PATH + LUATABLE_PATH):
            os.mkdir(OUPUT_PATH + LUATABLE_PATH)
        if not path.isdir(OUPUT_PATH + JSON_PATH):
            os.mkdir(OUPUT_PATH + JSON_PATH)
        if not path.isdir(OUPUT_PATH + SEASONAL_PATH):
            os.mkdir(OUPUT_PATH + SEASONAL_PATH)

    @LuatableBotTask()
    async def ClonseDBS(self):
        shutil.rmtree(KCKIT_NAME + '/', ignore_errors=True)
        shutil.rmtree(WCTF_DB_NAME + '/', ignore_errors=True)
        KCKIT_REPO_URL = environ.get('KCKIT_REPO_URL')
        KCKIT_REPO_BRANCH = environ.get('KCKIT_REPO_BRANCH')
        WCTF_DB_REPO_URL = environ.get('WCTF_DB_REPO_URL')
        WCTF_DB_REPO_BRANCH = environ.get('WCTF_DB_REPO_BRANCH')
        if not KCKIT_REPO_URL:
            raise LuatableBotException('KCKIT_REPO_URL 未设置，请设置 KCKIT 的仓库地址，例如 https://github.com/TeamFleet/KCKit.git')
        if not WCTF_DB_REPO_URL:
            raise LuatableBotException('WCTF_DB_REPO_URL 未设置，请设置 WhoCallsTheFleet-DB 的仓库地址，例如 https://github.com/TeamFleet/WhoCallsTheFleet-DB.git')
        self.__git_clone(KCKIT_REPO_URL, KCKIT_NAME, KCKIT_REPO_BRANCH)
        self.__git_clone(WCTF_DB_REPO_URL, WCTF_DB_NAME, WCTF_DB_REPO_BRANCH)

    def __git_clone(self, url, dest, branch = 'master'):
        exec(['git', 'clone', '--depth=1', url, '-b', branch, dest])

    @LuatableBotTask()
    async def FetchDBS(self):
        task_name = 'FetchDBS'
        if task_name not in self.task_status:
            dbDownloader = DBDownloader()
            dbDownloader.appendTask('https://kcwikizh.github.io/kcdata/ship/all.json', DB_PATH + KCDATA_SHIP_ALL_JSON)
            dbDownloader.appendTask('https://kcwikizh.github.io/kcdata/slotitem/all.json', DB_PATH + KCDATA_SLOTITEM_ALL_JSON)
            dbDownloader.appendTask('https://raw.githubusercontent.com/kcwikizh/get_kaisou_data/master/kaisou_data.json', DB_PATH + SHIP_REMODEL_EXTRA)
            await dbDownloader.start()
            self.task_status[task_name] = True

    @LuatableBotTask()
    async def Nedb2json(self):
        # 复制数据文件
        nedbs = os.listdir('{}/db'.format(WCTF_DB_NAME))
        for dbfile in nedbs:
            shutil.copyfile('{}/db/{}'.format(WCTF_DB_NAME, dbfile), 'db/{}'.format(dbfile))
        nedb2json(DB_PATH + ENTITIES_DB + '.nedb', DB_PATH + ENTITIES_DB + '.json')
        nedb2json(DB_PATH + ITEM_TYPES_DB + '.nedb', DB_PATH + ITEM_TYPES_DB + '.json')
        nedb2json(DB_PATH + ITEMS_DB + '.nedb', DB_PATH + ITEMS_DB + '.json')
        nedb2json(DB_PATH + SHIP_CLASSES_DB + '.nedb', DB_PATH + SHIP_CLASSES_DB + '.json')
        nedb2json(DB_PATH + SHIP_NAMESUFFIX_DB + '.nedb', DB_PATH + SHIP_NAMESUFFIX_DB + '.json')
        nedb2json(DB_PATH + SHIP_SERIES_DB + '.nedb', DB_PATH + SHIP_SERIES_DB + '.json')
        nedb2json(DB_PATH + SHIP_TYPES_DB + '.nedb', DB_PATH + SHIP_TYPES_DB + '.json')
        nedb2json(DB_PATH + SHIP_TYPE_COLLECTIONS_DB + '.nedb', DB_PATH + SHIP_TYPE_COLLECTIONS_DB + '.json')
        nedb2json(DB_PATH + SHIPS_DB + '.nedb', DB_PATH + SHIPS_DB + '.json')

    @LuatableBotTask()
    async def AkashiList(self):
        task_name = 'AkashiList'
        if task_name not in self.task_status:
            akashiListCrawler = AkashiListCrawler()
            await akashiListCrawler.start()
            self.task_status[task_name] = True

    @Switch('Wikiwiki')
    @LuatableBotTask()
    async def WikiwikiData(self):
        wikiwikiCrawler = WikiwikiCrawler()
        await wikiwikiCrawler.start()

    @Switch('SeasonalSubtitles')
    @LuatableBotTask()
    async def SeasonalSubtitles(self):
        seasonalCrawler = SeasonalCrawler()
        await seasonalCrawler.start()

    @Switch("ShipClassesMapping")
    @LuatableBotTask()
    async def ShipClassesMappingLuatable(self):
        shipClassesMappingLuatable = ShipClassMappingLuatable()
        shipClassesMappingLuatable.start()
        
    @Switch('Ships')
    @LuatableBotTask(True)
    async def ShipLuatable(self):
        await self.BonusJson()
        await self.AkashiList()
        shipLuatable = ShipLuatable()
        shipLuatable.start()

    @Switch('Shinkai')
    @LuatableBotTask(True)
    async def ShinkaiLuatable(self):
        shinkaiLuatable = ShinkaiLuatable()
        await shinkaiLuatable.start()

    @Switch('KcwikiUpdate')
    @LuatableBotTask()
    async def WikiBotUpdate(self):
        KCWIKI_ACCOUNT = environ.get('KCWIKI_ACCOUNT')
        KCWIKI_PASSWORD = environ.get('KCWIKI_PASSWORD')
        wikiBot = WikiBot(KCWIKI_ACCOUNT, KCWIKI_PASSWORD)
        await wikiBot.start()

    async def BonusJson(self):
        self.__exec_js(SCRIPTS_PATH + BONUS_JS)

    def __exec_lua(self, filename, check=False):
        exec(['lua', filename], check=check)

    def __exec_js(self, filename):
        exec(['node', filename])

    # 只依赖本地数据（kcdata / WCTF-DB）就能生成的表：缺失说明核心流程坏了，必须让 CI 失败
    REQUIRED_LUATABLES = [SHIPS_DATA, ITEMS_DATA, ITEMS_DATA_V2,
                          SHIPCLASSES_MAPPING_DATA, AKASHI_LIST_OUTPUT_LUA, SHIP_SERIES_DB]
    # 依赖外部 wiki 的表：源站不可达时允许缺失，由部署步骤的 keep_files 保住线上旧文件
    OPTIONAL_LUATABLES = [SHINKAI_ITEMS_DATA, SHINKAI_SHIPS_DATA, AIRPOWER_TABLE]

    @Switch('Check')
    @LuatableBotTask()
    async def CheckLuatable(self):
        missing_required = []
        missing_optional = []
        for name in self.REQUIRED_LUATABLES + self.OPTIONAL_LUATABLES:
            # 有些常量自带 .lua 后缀（AIRPOWER_TABLE / AKASHI_LIST_OUTPUT_LUA），统一在这里归一
            lua_path = OUPUT_PATH + LUATABLE_PATH + (name if name.endswith('.lua') else name + '.lua')
            if not path.isfile(lua_path):
                if name in self.REQUIRED_LUATABLES:
                    missing_required.append(path.basename(lua_path))
                else:
                    missing_optional.append(path.basename(lua_path))
                continue
            # 以前这里忽略 lua 的退出码，文件缺失/语法错误也会打印 "All the lua files is valid!"
            self.__exec_lua(lua_path, check=True)
        if missing_optional:
            print('::warning title=luatable::外部数据源不可达，以下表本次未生成（线上旧文件保留）：{}'
                  .format(', '.join(missing_optional)))
        if missing_required:
            raise LuatableBotException('缺少必需的 luatable：{}'.format(', '.join(missing_required)))
        print('CheckLuatable: All the lua files is valid!')

    async def main(self):
        await self.FetchDBS()
        await self.ClonseDBS()
        await self.Nedb2json()
        await self.SeasonalSubtitles()
        await self.WikiwikiData()
        await self.ShipLuatable()
        await self.ShipClassesMappingLuatable()
        await self.ShinkaiLuatable()
        await self.CheckLuatable()
        await self.WikiBotUpdate()


if __name__ == '__main__':
    luatableBot = LuatableBot()
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(luatableBot.main())
