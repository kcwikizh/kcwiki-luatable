import datetime

import pytz

from config import (AKASHI_LIST_OUTPUT_LUA, ITEMS_DATA, OUPUT_PATH,
                    SHINKAI_ITEMS_DATA, SHINKAI_SHIPS_DATA, SHIPS_DATA)
from HttpClient import HttpClient


class KcwikiException(Exception):
    def __init__(self, message):
        super().__init__(message)


class WikiBot(HttpClient):

    KCWIKI_API_URL = 'https://zh.kcwiki.org/api.php'
    HEADERS = {
        'Cache-Control': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
    }

    def __init__(self, username, password):
        super().__init__()
        self.tz = pytz.timezone('Asia/Shanghai')
        self.loginToken = ''
        self.editToken = ''
        self.username = username
        self.password = password

    async def login(self):
        rdata = {
            'action': 'query',
            'meta': 'tokens',
            'type': 'login',
            'format': 'json'
        }
        async with self.session.post(self.KCWIKI_API_URL, data=rdata) as resp:
            try:
                resp_json = await resp.json()
                if not resp_json:
                    raise KcwikiException('Wiki-Bot: Failed to get login token!')
                self.loginToken = resp_json['query']['tokens']['logintoken']
            except Exception:
                raise KcwikiException('Wiki-Bot: Failed to get login token!')
        rdata = {
            'action': 'login',
            'format': 'json',
            'lgtoken': self.loginToken
        }
        rdata['lgname'] = self.username
        rdata['lgpassword'] = self.password
        async with self.session.post(self.KCWIKI_API_URL, data=rdata) as resp:
            try:
                resp_json = await resp.json()
                if not resp_json:
                    raise KcwikiException('Wiki-Bot: Failed to log in!')
                if resp_json['login']['result'] == 'Failed':
                    raise KcwikiException(resp_json['login']['reason'])
            except Exception:
                raise KcwikiException('Wiki-Bot: Failed to log in!')
        rdata = {
            'action': 'query',
            'meta': 'tokens',
            'format': 'json'
        }
        async with self.session.post(self.KCWIKI_API_URL, data=rdata) as resp:
            try:
                resp_json = await resp.json()
                if not resp_json:
                    raise KcwikiException('Wiki-Bot: Failed to get edit token!')
                self.editToken = resp_json['query']['tokens']['csrftoken']
            except Exception:
                raise KcwikiException('Wiki-Bot: Failed to get edit token!')

        if self.editToken == '+\\':
            raise KcwikiException('Wiki-Bot: Incorrect edittoken \'+\\\' !')
        print('Wiki-Bot: Login Successfully!')

    async def updatePage(self, page_title, filename):
        now = datetime.datetime.now(self.tz)
        comment = 'KcWiki Robot: Update {}'.format(now.strftime('%Y-%m-%d %H:%M:%S'))
        rdata = {
            'action': 'edit',
            'title': page_title,
            'token': self.editToken,
            'summary': comment,
            'format': 'json'
        }
        with open(filename, 'r', encoding='utf-8') as fp:
            text = fp.read()
            rdata.update({
                'text': text
            })
        async with self.session.post(self.KCWIKI_API_URL, data=rdata) as resp:
            try:
                resp_json = await resp.json()
                if resp_json['edit']['result'] != 'Success':
                    raise KcwikiException('Wiki-Bot: Failed to update page!')
            except Exception:
                raise KcwikiException('Wiki-Bot: Failed to update page!')
        print('Wiki-Bot: Page {{{{{}}}}} update successfully'.format(page_title))

    async def start(self):
        await self.login()
        await self.updatePage('模块:舰娘数据', OUPUT_PATH + SHIPS_DATA + '.lua')
        await self.updatePage('模块:舰娘装备数据改', OUPUT_PATH + ITEMS_DATA + '.lua')
        await self.updatePage('模块:深海装备数据', OUPUT_PATH + SHINKAI_ITEMS_DATA + '.lua')
        await self.updatePage('模块:深海栖舰数据改二', OUPUT_PATH + SHINKAI_SHIPS_DATA + '.lua')
        await self.updatePage('模块:明石工厂数据', OUPUT_PATH + AKASHI_LIST_OUTPUT_LUA)
