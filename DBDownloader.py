#!/usr/bin/env python3

from os import path
import asyncio

from HttpClient import HttpClient
from config import DB_PATH

SUFFIXS = ['B', 'KB', 'MB', 'GB']


class DBDownloader(HttpClient):

    def __init__(self):
        super().__init__()
        self.tasks = []

    def appendTask(self, src, dest=None):
        filename = path.basename(src)
        if not dest:
            dest = DB_PATH + filename
        self.tasks.append([src, dest])

    async def download(self, src, dest):
        size = 0
        with open(dest, 'w', encoding='utf-8') as fp:
            async with self.session.get(src) as resp:
                content = await resp.text()
                fp.write(content)
                size = len(content)
        suff_idx = 0
        while size > 1024:
            size /= 1024
            suff_idx += 1
        print('DBDownloader: {} ({}{}) ok!'.format(dest, round(size, 2), SUFFIXS[suff_idx]))

    async def start(self):
        tasks = []
        for task in self.tasks:
            tasks.append(asyncio.ensure_future(self.download(*task)))
        dones, pendings = await asyncio.wait(tasks)
        print('DBDownloader: {} done, {} pendings.'.format(len(dones), len(pendings)))
