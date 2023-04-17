import json, os
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from log import logger
from typing import Any, Optional, Mapping, AsyncIterator, ClassVar

from config.config import FormaConfig, ROOT_DIR
from ..base import ServiceException
from ..http_client import HttpClient, LooseHeaders, ClientResponse
from .api_commands import FormaApiCommander
from .exceptions import FormaAuthException


class FormaService():
    publication_address: ClassVar[str] = '/app/v1.2/api/publications/action/'
    _token_file_path: ClassVar[str] = os.path.abspath(ROOT_DIR + 'temp/token.json')
    _access_token: str = None
    _access_token_date: datetime = None
    # _refresh_token: str = None
    # _refresh_token_date: datetime = None
    _config: FormaConfig
    cmd: FormaApiCommander

    def __init__(
        self,
        config: FormaConfig
    ) -> None:
        """ Forma service contructor """

        self._config = config
        self._load_token_info()
        self.cmd = FormaApiCommander(forma=self)

    def _get_url(self, path):
        return  f'{self._config.address}{path}'
    
    def get_publication_path(self, alias: str):
        return self.publication_address + alias

    async def _auth(self):
        """ Authentication """

        req_params = {
            "login": self._config.user_name,
            "password": self._config.password,
        }
        async with HttpClient.fetch(
            self._get_url('/api/auth/token-v2'),
            method = 'POST',
            json = req_params,
            headers = {
                "Content-Type": "application/json"
            },
        ) as resp:
            if not resp.ok:
                raise FormaAuthException(f'FRM: Cannot auth. Status {str(resp.status)} returned')
            json_resp = await resp.json()
            self._set_token(
                access_token=json_resp['data']['accessToken'],
                access_token_date=datetime.utcnow()
            )
            logger.debug(f"FRM: Authenticated by '{self._config.user_name}'")
    
    def _load_token_info(self) -> None:
        """ Sets token from file storage """

        try:
            with open(self._token_file_path, 'r') as f:
                json_data = json.loads(f.read())
        except Exception as exc:
            logger.warning(f'FRM: {str(exc)}')
            return
        if not json_data:
            return
        self._access_token = json_data.get('access_token')
        if json_data.get('access_token_date'):
            self._access_token_date = datetime.fromisoformat(json_data.get('access_token_date'))
        logger.debug(f'FRM: Token info loaded from the storage')

    def _set_token(self, access_token: str, access_token_date: datetime) -> None:
        """ Sets token info """

        json_data = {"access_token": access_token, "access_token_date": access_token_date.isoformat()}
        self._access_token = access_token
        self._access_token_date = access_token_date
        with open(self._token_file_path, 'w') as f:
            json.dump(json_data, f)
        logger.debug(f'FRM: Token has been updated')
    
    def _is_auth_required(self):
        if not self._access_token:
            return True
        token_seconds = (datetime.utcnow() - self._access_token_date).total_seconds()
        return token_seconds > self._config.token_valid_minutes * 60

    @asynccontextmanager
    async def request(
        self,
        path: str,
        method = 'GET',
        data: Any = None,
        json: Any = None,
        headers: Optional[LooseHeaders] = {},
        params: Optional[Mapping[str, str]] = None,
    ) -> AsyncIterator[ClientResponse]:     
        """ 1F http request wrapper """

        req_kwargs = {
            "url": self._get_url(path), 
            "method": method, 
            "data": data, 
            "json": json, 
            "headers": {
                **headers,
                '1FormaAuth': self._access_token
            }, 
            "params": params
        }
        if self._is_auth_required():
            await self._auth()
        try:
            async with HttpClient.fetch(**req_kwargs) as resp:
                if resp.status == 401:
                    raise FormaAuthException('FRM: Auth error')
                logger.debug(f"FRM: Request '{method.upper()} {path}'")
                yield resp
        finally:
            pass
    
  