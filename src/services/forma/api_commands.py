import aiofiles, os
from enum import Enum
from typing import Optional, TYPE_CHECKING

from utils.functional import list_enum2str
from .types import TaskState, TaskInfoParts

if TYPE_CHECKING:
    from .service import FormaService


class FormaApiCommander():
    """ 1F api commands """

    _forma: 'FormaService'

    def __init__(self, forma: 'FormaService') -> None:
        """ Api commander constructor """

        self._forma = forma
    
    async def file_download(self, file_id: int, saved_path: str, makedir = False):
        """ Download a file """

        if makedir:
            os.makedirs(os.path.dirname(saved_path), exist_ok=True)
        async with self._forma.request(f'/api/files/download/{file_id}') as resp:
            assert resp.status == 200, "Cant download file"
            f = await aiofiles.open(saved_path, mode='wb')
            await f.write(await resp.read())
            await f.close()

    async def get_task_info(
        self,
        task_id: int,
        info_parts: Optional[TaskInfoParts] = []
    ) -> dict:
        """ Gets task info from api """

        json_params = {
            "taskId": task_id,
            "selectedInfoParts": list_enum2str(info_parts)
        }
        async with self._forma.request(
            '/api/tasks',
            method = 'POST',
            json = json_params
        ) as resp:
            response = await resp.json()
        return response
    
    async def find_subcat_tasks(
        self,
        subcat_id: int,
        start_row: int = 0,
        end_row: int = 200,
        select: list[dict] = {"field": "task", "type": "task", "extParamType": None},
        smart_expression_ids: Optional[list[int]] = None,
        filter_model: Optional[dict] = None,
        sort_model: Optional[dict] = [{"sort": "desc", "colId": "taskId"}],
        task_state: Optional[TaskState] = None
    ) -> dict:
        """ Finds subcategory tasks from api """

        json_params = {
            "aggregations": {},
            "context": None,
            "startRow": start_row,
            "endRow": end_row,
            "groupKeys": [],
            "filterModel": filter_model,
            "myTasks": None,
            "select": select,
            "sortModel": sort_model,
            "smartExpressionIds": smart_expression_ids,
            "tasksState": task_state,
            "valueCols": []
        }
        async with self._forma.request(
            f'/api-core/datasource/subcat/{subcat_id}/data',
            method = 'POST',
            json = json_params
        ) as resp:
            return await resp.json()
        
