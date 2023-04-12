from enum import Enum

class TaskState(str, Enum):
    isClosed = 'isClosed'
    isOpened = 'isOpened'
    isRejected = 'isRejected'


class TaskInfoParts(str, Enum):
    performers = 'performers'
    subscribers = 'subscribers'
    MainParams = 'MainParams'
    toolbar = 'toolbar'
    Actions = 'Actions'
    OptionalSignatures = 'OptionalSignatures'
    CustomTasksUsed = 'CustomTasksUsed'
    ExtParams = 'ExtParams'