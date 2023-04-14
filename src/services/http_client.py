from aiohttp import ClientSession, ClientTimeout, ClientResponse, TCPConnector, request
from aiohttp.typedefs import StrOrURL, LooseHeaders, LooseCookies
from aiohttp.helpers import BasicAuth, sentinel
from contextlib import asynccontextmanager
from typing import Any, Optional, Mapping, AsyncIterator

DEFAULT_TIMEOT = ClientTimeout(
    connect = 5,
    sock_connect = 5,
    sock_read = 5
)


class HttpClient():

    @staticmethod
    @asynccontextmanager
    async def fetch(
        url: StrOrURL,
        method = 'GET',
        data: Any = None,
        json: Any = None,
        headers: Optional[LooseHeaders] = None,
        params: Optional[Mapping[str, str]] = None,
        cookies: Optional[LooseCookies] = None,
        allow_redirects: bool = True,
        auth: Optional[BasicAuth] = None,
        timeout: ClientTimeout = DEFAULT_TIMEOT,
    ) -> AsyncIterator[ClientResponse]:
        if not timeout:
            timeout = DEFAULT_TIMEOT
        try:
            async with ClientSession(connector=TCPConnector(ssl=False)) as session:
                async with session.request(
                    method, 
                    url = url,
                    data = data,
                    json = json,
                    headers = headers,
                    params = params,
                    cookies = cookies,
                    allow_redirects = allow_redirects,
                    auth = auth,
                    timeout = timeout
                ) as resp:
                    yield resp
        finally:
            pass