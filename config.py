import pytz

# global
DB_PATH = 'db/'
OUPUT_PATH = 'output/'
SCRIPTS_PATH = 'scripts/'
LUATABLE_PATH = 'luatable/'
JSON_PATH = 'json/'
DOCS_PATH = 'docs/'

KCKIT_NAME = 'KCKit'
WCTF_DB_NAME = 'WCTF_DB'

# timezone
TIMEZONE = pytz.timezone('Asia/Shanghai')

# seasonal
SEASONAL_PATH = 'seasonal/'

# akashiListCrawler
AKASHI_LIST_URL = 'https://akashi-list.me'
AKASHI_LIST_OUTPUT_JSON = 'akashi-list.json'
AKASHI_LIST_OUTPUT_LUA = 'akashi-list.lua'

# wikiaCrawler
WIKIA_OUTPUT_JSON = 'wikia_enemy_extra.json'

# kcdata
KCDATA_SHIP_ALL_JSON = 'kcdata_ship_all.json'
KCDATA_SLOTITEM_ALL_JSON = 'kcdata_slotitem_all.json'

# database
ENTITIES_DB = 'entities'
ITEM_TYPES_DB = 'item_types'
ITEMS_DB = 'items'
SHIP_CLASSES_DB = 'ship_classes'
SHIP_NAMESUFFIX_DB = 'ship_namesuffix'
SHIP_SERIES_DB = 'ship_series'
SHIP_TYPES_DB = 'ship_types'
SHIP_TYPE_COLLECTIONS_DB = 'ship_type_collections'
SHIPS_DB = 'ships'

# extra
SHIP_REMODEL_EXTRA = 'ship_remodel.json'
ITEM_REMARKS_EXTRA = 'item_remarks.json'
SHINKAI_EXTRA_JSON = 'shinkai_extra.json'

# output
SHIPS_DATA = 'ships'
ITEMS_DATA = 'items'
SHIPCLASSES_MAPPING_DATA = 'shipclasses_mapping'
SHINKAI_SHIPS_DATA = 'shinkai-ships'
SHINKAI_ITEMS_DATA = 'shinkai-items'

# bonus
BONUS_JS = 'bonus.js'
BONUS_JSON = 'bonus.json'

# wikiwiki subtitles
WIKIWIKI_TRANSLATION = 'wikiwiki_translation.json'
WIKIWIKI_MaxValue_TABLE = 'wikiwiki_MaxValue_table.txt'
WIKIWIKI_Compare_TABLE = 'wikiwiki_Compare_table.txt'

# diff
GITHUB_PAGES_URL = 'https://bot.kcwiki.moe/'
IGNORE_FILES = [
    'seasonal/index.html'
]

AIRPOWER_TABLE = 'airpower_table.lua'
