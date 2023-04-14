import os, shutil, json
from pydantic import BaseModel

from log import logger
from config import JobExcelLockerOptions, ROOT_DIR
from services.forma import FormaService
from services.excel_manager import ExcelManager
from typing import ClassVar, Optional, Any
from .base import IJob

def _log_msg(msg):
    return f'EXCLOCKJOB: {msg}'

class FtelSaveFileException(Exception):
    pass

class FtelLockException(Exception):
    pass

class FtelClearTempsException(Exception):
    pass

class FtelCompleteRequestException(Exception):
    pass

class FtelFileDownloadException(Exception):
    pass

class FtelDeleteTempFileException(Exception):
    pass

class FtelReceiveListException(Exception):
    pass

class FtelItem(BaseModel):
    id: Any
    file_id: int
    completed_path: str
    unlock_columns: Optional[list[str]]

class FormaTaskExcelLockerJob(IJob):
    """ Lock excel cells """

    _temp_folder: ClassVar[str] = ROOT_DIR + 'temp/fttel/'
    _forma: FormaService = None
    _config: JobExcelLockerOptions

    def __init__(
        self,
        forma: FormaService,
        config: JobExcelLockerOptions
    ) -> None:
        """ Constructor """

        self._forma = forma
        self._config = config
        self.clear_tepm_folder()
        super().__init__()

    async def run(self) -> None:
        """ Job runner """

        items = await self._get_files_list()
        a = 0
        for item in items:
            a = a + 1
            if a > self._config.portion:
                logger.info(_log_msg(f"{a}/{len(items)} items successfully handled by 'portion' option"))
                return
            try:
                logger.debug(_log_msg(f"Item '{a}' handling ..."))
                await self._handle_item(item)
            except (
                FtelSaveFileException,
                FtelSaveFileException,
                FtelCompleteRequestException,
                FtelFileDownloadException,
                FtelDeleteTempFileException
            ) as exc:
                logger.error(str(exc))
                return
   
        logger.info(_log_msg(f'All {len(items)} items successfully handled'))
        
    async def _get_files_list(self) -> list[FtelItem]:
        req_path = self._forma.get_publication_path(self._config.source_publication_alias)
        items = []
        async with self._forma.request(req_path) as resp:
            if not resp.ok:
                raise FtelReceiveListException(_log_msg(f"Cannot retrieve items. Status '{resp.status}' returned"))
            try:
                json_items = await resp.json()
            except Exception as exc:
                raise FtelReceiveListException(_log_msg(f'Cannot parse json with items. {str(exc)}'))
        for item in json_items:
            try:
                _item = FtelItem(**item)
            except Exception as exc:
                raise FtelReceiveListException(_log_msg(f'Incorrect item format. {str(exc)}'))
            items.append(_item)
        logger.info(_log_msg(f"Received items: {len(items)}"))
        return items
            
    async def _handle_item(self, item: FtelItem) -> None:
        """ Handling an item """
        
        unlock_columns = item.unlock_columns or self._config.unlock_columns
        completed_path = (self._config.completed_folder or "") + item.completed_path
        saved_path = f'{self._temp_folder}{item.file_id}.xlsx'
        await self._download_file(item.file_id, saved_path)
        self._lock_cells(saved_path, unlock_columns)
        self._save_file(saved_path, completed_path)
        self._delete_temp_file(saved_path)
        await self._complete_request(item)
    
    async def _download_file(self, file_id: int, save_path: str) -> None:
        try:
            await self._forma.cmd.file_download(file_id, save_path, makedir=True)
        except Exception as exc:
            raise FtelFileDownloadException(_log_msg(
                f"Cannot download file_id '{file_id}'"
            ))
        logger.debug(_log_msg(f"File id '{file_id}' downloaded to '{save_path}'"))
    
    def _delete_temp_file(self, file_path: str) -> None:
        try:
            os.unlink(file_path)
        except Exception as exc:
            raise FtelDeleteTempFileException(_log_msg(
                f"Cannot delete temp file '{file_path}'"
            ))
        logger.debug(_log_msg(f"Temporary file '{file_path}' deleted"))
    
    async def _complete_request(self, item: FtelItem) -> None:
        headers = {
            "content-type": "application/json; charset=utf-8"
        }
        json_params = {
            "id": item.id,
            "file_id": item.file_id
        }
        req_path = self._forma.get_publication_path(self._config.complete_publication_alias)
        async with self._forma.request(
            req_path,
            method = 'POST',
            json = json_params,
            headers = headers
        ) as resp:
            if not resp.ok:
                raise FtelCompleteRequestException(_log_msg(
                    f"Cannot send complete request 'POST {req_path}' with body: {json.dumps(json_params)}. Status '{resp.status}' returned"
                ))
            logger.debug(_log_msg(f"Completed by 'POST {req_path}'"))

    def _lock_cells(self, file_path: str, unlock_columns: Optional[list[str]]) -> None:
        """ Locking cells """

        try:
            em = ExcelManager(file_path)
            em.lock(unlock_columns=unlock_columns)
            em.save()
        except Exception as exc:
            raise FtelLockException(_log_msg(f'Lock operation error: {str(exc)}'))
        logger.debug(_log_msg(f"File '{file_path}' protected"))
    
    def _save_file(self, file_path: str, path_to_save: str) -> None:
        """ Save a file """

        try:
            shutil.copyfile(file_path, path_to_save)
        except Exception as exc:
            raise FtelSaveFileException(f"Cannot save file: {str(exc)}")
        logger.debug(_log_msg(f"Handled file saved to '{path_to_save}'"))
    
    def clear_tepm_folder(self) -> None:
        """ Clears temporary folder """

        try:
            files = os.listdir(self._temp_folder)
        except Exception:
            return
        for filename in files:
            file_path = os.path.join(self._temp_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                raise FtelClearTempsException(_log_msg("Failed to delete temporary folder '%s'" % (file_path, e)))
        logger.debug(_log_msg("Temp folder cleared"))
        
