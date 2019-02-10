import asyncio

import aiohttp


class HttpClient:

    def __init__(self):
        self.session = aiohttp.ClientSession()

    def __del__(self):
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(self.session.close(), loop)
