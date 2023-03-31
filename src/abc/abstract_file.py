from abc import ABCMeta
from pathlib import Path
from typing import Generic, TypeVar

from ..protocols import File

T = TypeVar("T")


class AbstractFile(File, Generic[T], metaclass=ABCMeta):

    __slots__ = ("_path", "_name", "_size", "_type")

    def __init__(
        self,
        path: Path | str,
        type_: T,
        size: int = 0,
    ) -> None:
        self._path: Path = Path(path)
        self._name: str = self._path.name
        self._type: T = type_
        self._size: int = size

    @property
    def path(self) -> Path:
        return self._path

    @property
    def name(self) -> str:
        return self._name

    @property
    def size(self) -> int:
        return self._size
