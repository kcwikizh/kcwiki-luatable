import json
from collections import OrderedDict


def nedb2json(nedbFilename, jsonFilename):
    jsonFile = open(jsonFilename, 'w', encoding='utf-8')
    with open(nedbFilename, 'r', encoding='utf-8') as nedbFile:
        jsonFile.write('[\n')
        line = nedbFile.readline()
        while line:
            in_line = line.rstrip() + ','
            line = nedbFile.readline()
            if not line:
                in_line = in_line.rstrip(',')
            jsonFile.write(in_line + '\n')
        jsonFile.write(']')
    jsonFile.close()


def json2dic(data, masterKey=None):
    if not masterKey:
        return data
    dic = {}
    for entry in data:
        if not entry[masterKey]:
            continue
        dic[entry[masterKey]] = entry
    return dic


def sortDict(dic):
    ret = {}
    for key in sorted(dic.keys()):
        ret[key] = dic[key]
    return ret


def jsonFile2dic(jsonFilename, masterKey=None):
    dic = {}
    with open(jsonFilename, 'r', encoding='utf-8') as jsonFile:
        dic = json2dic(json.load(jsonFile), masterKey)
    return dic


def luatable(data, layer=1, tab='\t', indent=False):
    ret = ''
    if type(data) is int or type(data) is str:
        if indent:
            ret = (tab * (layer - 1)) + \
                '{}'.format(json.dumps(data, ensure_ascii=False))
        else:
            ret = '{}'.format(json.dumps(data, ensure_ascii=False))
    elif type(data) is list:
        idx = 0
        if indent:
            ret = (tab * (layer - 1)) + '{\n'
        else:
            ret = '{\n'
        for item in data:
            if not idx:
                ret += luatable(item, layer + 1, indent=True)
            else:
                ret += ',\n' + \
                    luatable(item, layer + 1, indent=True)
            idx += 1
        ret += '\n' + (tab * (layer - 1)) + '}'
    elif type(data) is dict or type(data) is OrderedDict:
        if indent:
            ret = (tab * (layer - 1)) + '{\n'
        else:
            ret = '{\n'
        idx = 0
        for k, v in data.items():
            if not idx:
                ret += (tab * layer) + \
                    '["{}"] = '.format(
                        k) + luatable(v, layer + 1)
            else:
                ret += ',\n' + \
                    (tab * layer) + \
                    '["{}"] = '.format(
                        k) + luatable(v, layer + 1)
            idx += 1
        ret += '\n' + (tab * (layer - 1)) + '}'
    return ret


UNIT_NAMES = ['B', 'kB', 'MB', 'GB']


def format_filesize(size):
    unit_idx = 0
    while size > 1024:
        size /= 1024
        unit_idx += 1
    return '{} {}'.format(round(size, 2), UNIT_NAMES[unit_idx])
