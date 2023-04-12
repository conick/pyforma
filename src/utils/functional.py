from enum import Enum

def list_enum2str(items: list[Enum]) -> list[str]:
    if not items:
        return None 
    return [str(item.value) for item in items]