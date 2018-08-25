import os
import re
from os import path

from config import GITHUB_PAGES_URL, IGNORE_FILES, OUPUT_PATH
from HttpClient import HttpClient


class DiffTool(HttpClient):

    def __init__(self):
        super().__init__()

    async def _fetch_from_remote(self, url):
        ret = ''
        async with self.session.get(url) as resp:
            ret = await resp.text()
        return ret

    async def _mkdiff(self, absolute, relative):
        url = f'{GITHUB_PAGES_URL}{relative}'
        res = False
        async with self.session.get(url) as resp:
            if resp.status != 200:
                return True
            with open(absolute, 'r', encoding='utf-8') as fp:
                lidx = 0
                fline = fp.readline()
                rline = await resp.content.readline()
                while fline and rline:
                    rrline = rline.decode().strip()
                    fline = fline.strip()
                    if fline != rrline:
                        print(
                            f'++--@@ {relative}:{lidx + 1} {rrline} -> {fline} ')
                    fline = fp.readline()
                    rline = await resp.content.readline()
                    lidx += 1
                if fline and not rline:
                    res = True
                    while fline:
                        fline = fline.strip()
                        print(
                            f'++--@@ {relative}:{lidx + 1} <[+]> -> {fline} ')
                        fline = fp.readline()
                        lidx += 1
                if rline and not fline:
                    res = True
                    while rline:
                        rrline = rline.decode().strip()
                        print(
                            f'++--@@ {relative}:{lidx + 1} {rrline} -> <[-]> ')
                        rline = await resp.content.readline()
                        lidx += 1
        return res

    async def _repair(self):
        for ignore_file in IGNORE_FILES:
            url = f'{GITHUB_PAGES_URL}{ignore_file}'
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    return
                with open(OUPUT_PATH + ignore_file, 'w', encoding='utf-8') as fp:
                    async for line in resp.content:
                        fp.write(line.decode())

    async def _diff(self, root, parrent=''):
        items = os.listdir(root)
        res = False
        for item in items:
            ignore = False
            itemname = path.join(root, item)
            relative = path.join(parrent, item)
            for ignore_file in IGNORE_FILES:
                if ignore_file == relative:
                    ignore = True
                    break
            if ignore:
                continue
            if path.isfile(itemname):
                res = await self._mkdiff(itemname, relative)
            elif path.isdir(itemname):
                res = await self._diff(itemname, relative)
        return res

    async def perform(self):
        res = await self._diff(OUPUT_PATH)
        if not res:
            print('[Difftool] No file changed.')
            await self._repair()
