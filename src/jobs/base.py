from abc import ABC, abstractmethod

class IJob(ABC):

    @abstractmethod
    async def run(self):
        ...
