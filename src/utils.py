import sys
from pathlib import Path


def get_resource_path(resource_name: str) -> str:
    """Метод получения пути ресурса. Возвращает путь к вложенному ресурсу,
    или относительный от исполняемого файла"""

    parent = getattr(sys, "_MEIPASS", Path(".").resolve())
    return str(Path(parent, resource_name))
