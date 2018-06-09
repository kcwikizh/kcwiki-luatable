#!/usr/bin/env python3

from os import path
import asyncio

from HttpClient import HttpClient
from config import DB_PATH


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
        print('DBDownloader: {} ({}kB) ok!'.format(dest, round(size / 1024, 2)))

    async def start(self):
        tasks = []
        for task in self.tasks:
            tasks.append(asyncio.ensure_future(self.download(*task)))
        dones, pendings = await asyncio.wait(tasks)
        print('DBDownloader: {} done, {} pendings.'.format(len(dones), len(pendings)))
