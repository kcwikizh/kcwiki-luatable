import asyncio
import json

from config import (DB_PATH, SHIP_CLASSES_DB, SHIPS_DB, OUPUT_PATH, LUATABLE_PATH,
                    SHIPCLASSES_MAPPING_DATA, JSON_PATH)
from utils import jsonFile2dic, luatable, sortDict


class ShipClassMappingLuatable:
    
    def __init__(self):
        self.shipclass_data = {}
        self.CLASS_ID_NAME_MAP={}
        
        self.SHIP_CLASSES_DB = jsonFile2dic(DB_PATH + SHIP_CLASSES_DB + '.json', masterKey='id')
        self.SHIPS_DB = jsonFile2dic(DB_PATH + SHIPS_DB + '.json', masterKey='id')
        
    def __gen_classes(self):
        for ship_class_id in self.SHIP_CLASSES_DB.keys():
            ship_class = self.SHIP_CLASSES_DB[ship_class_id]['name']['zh_cn']
            self.shipclass_data[ship_class] = []
            self.CLASS_ID_NAME_MAP[ship_class_id] = ship_class
    
    def __fill_classes(self):
        for ship_id in self.SHIPS_DB.keys():
            wctf_ship = self.SHIPS_DB[ship_id]
            ship_class = self.CLASS_ID_NAME_MAP[wctf_ship['class']]
            if ship_class in self.shipclass_data:
                self.shipclass_data[ship_class].append(wctf_ship['id'])
            # print(self.shipclass_data)
        
    def genClassMappingData(self):
        self.__gen_classes()
        self.__fill_classes()
        
        self.shipclass_data = sortDict(self.shipclass_data)
        
        shipclass_luatable = 'local d = {}\n'
        shipclass_luatable += '---------------------------------\n'
        shipclass_luatable += '--   以下为舰娘和舰级的对应数据   -- \n'
        shipclass_luatable += '---------------------------------\n'
        shipclass_luatable += '\nd.shipclassDataTb = '
        shipclass_luatable += luatable(self.shipclass_data)
        shipclass_luatable += '\n'
        shipclass_luatable += '\nreturn d\n'
        
        with open(OUPUT_PATH + LUATABLE_PATH + SHIPCLASSES_MAPPING_DATA + '.lua', 'w',
                  encoding='utf-8') as fp:
            fp.write(shipclass_luatable)
        
        with open(OUPUT_PATH + JSON_PATH + SHIPCLASSES_MAPPING_DATA + '.json', 'w',
                  encoding='utf-8') as fp:
            json.dump(self.shipclass_data, fp, ensure_ascii=False, indent=4)
    
    def start(self):
        self.genClassMappingData()

