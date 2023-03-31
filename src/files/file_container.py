import re
from abc import abstractmethod
from typing import Generic, TypeVar

from ..protocols import File

T = TypeVar("T", bound=File)


class FileContainer(Generic[T]):

    _files: list[T] | None = None

    @abstractmethod
    def _read(self) -> list[T]:
        ...

    @property
    def files(self) -> list[T]:
        if self._files is None:
            self._files = self._read()
        return self._files

    def get_file(self, match: str) -> T | None:
        for file in self.files:
            if re.search(match, file.name):
                return file
        return None

    def get_files(self, match: str) -> list[T]:
        files: list[T] = []
        for file in self.files:
            if re.search(match, file.name):
                files.append(file)
        return files
