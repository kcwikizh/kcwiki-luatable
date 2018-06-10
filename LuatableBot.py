import asyncio
import functools
import os
import time
from os import path

from AkashiListCrawler import AkashiListCrawler
from config import (DB_PATH, ENTITIES_DB, ITEM_TYPES_DB, ITEMS_DB,
                    KCDATA_SHIP_ALL_JSON, KCDATA_SLOTITEM_ALL_JSON, OUPUT_PATH,
                    SHIP_CLASSES_DB, SHIP_NAMESUFFIX_DB, SHIP_SERIES_DB,
                    SHIP_TYPE_COLLECTIONS_DB, SHIP_TYPES_DB, SHIPS_DB)
from DBDownloader import DBDownloader
from ShipLuatable import ShipLuatable
from utils import nedb2json
from WikiaCrawler import WikiaCrawler


def LuatableBotTask(fn):
    async def wrapper(*args, **kw):
        print('[{}]: Task starting...'.format(fn.__name__))
        START = time.time()
        await fn(*args, **kw)
        END = time.time()
        print('[{}]: Task total used {}s'.format(fn.__name__, round(END - START, 3)))
    return wrapper


class LuatableBot:

    def __init__(self):
        if not path.isdir(DB_PATH):
            os.mkdir(DB_PATH)
        if not path.isdir(OUPUT_PATH):
            os.mkdir(OUPUT_PATH)

    @LuatableBotTask
    async def FetchDBS(self):
        dbDownloader = DBDownloader()
        dbDownloader.appendTask('https://kcwikizh.github.io/kcdata/ship/all.json', DB_PATH + KCDATA_SHIP_ALL_JSON)
        dbDownloader.appendTask('https://kcwikizh.github.io/kcdata/slotitem/all.json', DB_PATH + KCDATA_SLOTITEM_ALL_JSON)
        dbDownloader.appendTask('https://raw.githubusercontent.com/TeamFleet/WhoCallsTheFleet-DB/master/db/entities.nedb')
        dbDownloader.appendTask('https://raw.githubusercontent.com/TeamFleet/WhoCallsTheFleet-DB/master/db/item_types.nedb')
        dbDownloader.appendTask('https://raw.githubusercontent.com/TeamFleet/WhoCallsTheFleet-DB/master/db/items.nedb')
        dbDownloader.appendTask('https://raw.githubusercontent.com/TeamFleet/WhoCallsTheFleet-DB/master/db/ship_classes.nedb')
        dbDownloader.appendTask('https://raw.githubusercontent.com/TeamFleet/WhoCallsTheFleet-DB/master/db/ship_namesuffix.nedb')
        dbDownloader.appendTask('https://raw.githubusercontent.com/TeamFleet/WhoCallsTheFleet-DB/master/db/ship_series.nedb')
        dbDownloader.appendTask('https://raw.githubusercontent.com/TeamFleet/WhoCallsTheFleet-DB/master/db/ship_types.nedb')
        dbDownloader.appendTask('https://raw.githubusercontent.com/TeamFleet/WhoCallsTheFleet-DB/master/db/ship_type_collections.nedb')
        dbDownloader.appendTask('https://raw.githubusercontent.com/TeamFleet/WhoCallsTheFleet-DB/master/db/ships.nedb')
        await dbDownloader.start()

    @LuatableBotTask
    async def Nedb2json(self):
        nedb2json(DB_PATH + ENTITIES_DB + '.nedb', DB_PATH + ENTITIES_DB + '.json')
        nedb2json(DB_PATH + ITEM_TYPES_DB + '.nedb', DB_PATH + ITEM_TYPES_DB + '.json')
        nedb2json(DB_PATH + ITEMS_DB + '.nedb', DB_PATH + ITEMS_DB + '.json')
        nedb2json(DB_PATH + SHIP_CLASSES_DB + '.nedb', DB_PATH + SHIP_CLASSES_DB + '.json')
        nedb2json(DB_PATH + SHIP_NAMESUFFIX_DB + '.nedb', DB_PATH + SHIP_NAMESUFFIX_DB + '.json')
        nedb2json(DB_PATH + SHIP_SERIES_DB + '.nedb', DB_PATH + SHIP_SERIES_DB + '.json')
        nedb2json(DB_PATH + SHIP_TYPES_DB + '.nedb', DB_PATH + SHIP_TYPES_DB + '.json')
        nedb2json(DB_PATH + SHIP_TYPE_COLLECTIONS_DB + '.nedb', DB_PATH + SHIP_TYPE_COLLECTIONS_DB + '.json')
        nedb2json(DB_PATH + SHIPS_DB + '.nedb', DB_PATH + SHIPS_DB + '.json')

    @LuatableBotTask
    async def AkashiList(self):
        akashiListCrawler = AkashiListCrawler()
        await akashiListCrawler.start()

    @LuatableBotTask
    async def WikiaData(self):
        wikiaCrawler = WikiaCrawler()
        await wikiaCrawler.start()

    @LuatableBotTask
    async def ShipLuatable(self):
        shipLuatable = ShipLuatable()
        shipLuatable.start()

    async def main(self):
        await self.FetchDBS()
        await self.Nedb2json()
        await self.AkashiList()
        await self.WikiaData()
        await self.ShipLuatable()
        


if __name__ == '__main__':
    luatableBot = LuatableBot()
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(luatableBot.main())
