import os, shutil, aiofiles
from pydantic import BaseModel

from log import logger
from config import JobExcelLockerOptions
from services.forma import FormaService
from services.excel_manager import ExcelManager
from typing import ClassVar, Optional
from .base import IJob


class FtelItem(BaseModel):
    id: int
    file_id: int
    completed_path: str
    unlock_columns: Optional[list[str]]

class FormaTaskExcelLockerJob(IJob):
    """ Lock excel cells """

    _temp_folder: ClassVar[str] = 'temp/fttel/'
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

        fpath = self._forma.publication_address + self._config.source_publication_alias
        async with self._forma.request(fpath) as resp:
            assert resp.ok, f"EXCLOCKJOB: Cannot retrieve items. Status '{resp.status}' returned"
            try:
                json_items = await resp.json()
            except Exception:
                raise Exception(f'EXCLOCKJOB: Cannot parse json with items.')
            a = 0
            for item in json_items:
                a = a + 1
                if a > self._config.portion:
                    logger.info(f'EXCLOCKJOB: {a}/{len(json_items)} items successfully handled')
                    return 
                await self._handle_item(FtelItem(**item))
            logger.info(f'EXCLOCKJOB: all {len(json_items)} items successfully handled')
            
    async def _handle_item(self, item: FtelItem) -> None:
        """ Handling an item """
        
        unlock_columns = item.unlock_columns or self._config.unlock_columns
        completed_path = (self._config.completed_folder or "") + item.completed_path
        saved_path = f'{self._temp_folder}{item.file_id}.xlsx'
        await self._forma.cmd.file_download(item.file_id, saved_path, makedir=True)
        self._lock_cells(saved_path, unlock_columns)
        self._save_file(saved_path, completed_path)
        os.unlink(saved_path)

    def _lock_cells(self, file_path: str, unlock_columns: Optional[list[str]]):
        """ Locking cells """

        em = ExcelManager(file_path)
        em.lock(unlock_columns=unlock_columns)
        em.save()
        logger.debug(f"EXCLOCKJOB: File '{file_path}' has been locked")
    
    def _save_file(self, file_path: str, path_to_save: str) -> None:
        """ Save a file """

        shutil.copyfile(file_path, path_to_save)
        logger.debug(f"EXCLOCKJOB: Saved completed file at '{path_to_save}'")
    
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
                logger.error("EXCLOCKJOB: Failed to delete temporary folder '%s': %s" % (file_path, e))
                return
        logger.debug("EXCLOCKJOB: Temp folder cleared")
        
