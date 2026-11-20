import asyncio
import json
import os

import aiohttp

# 2026-11 起，Cloudflare 对 en.kancollewiki.net 的托管 runner 出口 IP（AS8075 / Azure）
# 直接返回人机校验页：403 + `cf-mitigated: challenge` + "Just a moment..."。
# 实测 curl / urllib / aiohttp、换 UA、换 Referer、换 HTTP 版本都一样被拦，
# 属于按出口 IP/ASN 的挑战，客户端无法自行通过；需要非受限出口时用 KCWIKI_PROXY 指定代理。
DEFAULT_HEADERS = {
    'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/126.0.0.0 Safari/537.36'),
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8,zh-CN;q=0.6',
}
RETRY_TIMES = 3
RETRY_BACKOFF = 2


class HttpChallengeError(Exception):
    """站点返回人机校验（403 + cf-mitigated: challenge），换 UA/重试都没有意义。"""


class HttpStatusError(Exception):
    def __init__(self, url, status, snippet=''):
        super().__init__('{} 返回 HTTP {}：{}'.format(url, status, snippet))
        self.url = url
        self.status = status


class HttpContentTypeError(Exception):
    pass


class HttpClient:

    def __init__(self):
        # 出口代理：优先 KCWIKI_PROXY；未设置时 trust_env 会读取 HTTPS_PROXY / HTTP_PROXY
        self.proxy = os.environ.get('KCWIKI_PROXY') or None
        self.session = aiohttp.ClientSession(headers=DEFAULT_HEADERS, trust_env=True)

    def __del__(self):
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(self.session.close(), loop)

    async def request(self, url, method='GET', **kwargs):
        """GET/POST 并返回 (body, headers)。5xx / 429 / 网络错误按指数退避重试；人机校验立即失败。"""
        last_error = None
        for attempt in range(RETRY_TIMES):
            if attempt:
                await asyncio.sleep(RETRY_BACKOFF * (2 ** (attempt - 1)))
            try:
                async with self.session.request(method, url, proxy=self.proxy, **kwargs) as resp:
                    body = await resp.read()
                    if resp.headers.get('cf-mitigated'):
                        raise HttpChallengeError(
                            '{} 被人机校验拦截（cf-mitigated: {}）。'
                            '这是按出口 IP/ASN 的 Cloudflare 挑战，换 UA 或重试都无效：'
                            '请设置 KCWIKI_PROXY 走非受限出口，或联系站点管理员放行。'
                            .format(url, resp.headers.get('cf-mitigated')))
                    if resp.status == 429 or resp.status >= 500:
                        last_error = HttpStatusError(url, resp.status, body[:120].decode('utf-8', 'replace'))
                        continue
                    if resp.status >= 400:
                        raise HttpStatusError(url, resp.status, body[:120].decode('utf-8', 'replace'))
                    return body, resp.headers
            except (aiohttp.ClientError, asyncio.TimeoutError) as error:
                last_error = error
        raise last_error

    async def get_text(self, url, **kwargs):
        body, _ = await self.request(url, **kwargs)
        return body.decode('utf-8', 'replace')

    async def get_json(self, url, **kwargs):
        body, headers = await self.request(url, **kwargs)
        content_type = (headers.get('Content-Type') or '').lower()
        if 'json' not in content_type:
            raise HttpContentTypeError('{} 返回的 Content-Type 是 {}，不是 json：{}'
                                       .format(url, content_type, body[:160].decode('utf-8', 'replace')))
        return json.loads(body.decode('utf-8', 'replace'))
