from abc import ABCMeta
from pathlib import Path
from typing import Generic, TypeVar
from urllib.request import urlretrieve

from ..config import Config, ManifestType
from ..protocols import Downloadable
from .abstract_file import AbstractFile

T = TypeVar("T")


class AbstractManifestFile(
    AbstractFile,
    Downloadable,
    Generic[T],
    metaclass=ABCMeta,
):
    def __init__(
        self,
        path: Path | str,
        hash_: str,
        type_: T,
        size: int = 0,
        version: int = 0,
    ) -> None:
        AbstractFile.__init__(self, path, type_, size)
        self._hash = hash_
        self._version = version

    @property
    def url(self) -> str:
        if type(self._type) == ManifestType:
            endpoint = f"{self._type.value % (self._version,self.name)}"
        else:
            endpoint = f"{self._type.value}/{self._hash[:2]}/{self._hash}"

        return f"https://{Config.host.value}/{endpoint}"

    def download(self) -> None:
        if self.path.exists():
            if self.path.stat().st_size == self.size:
                return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(self.url, self.path)
        print(f"DL {self.url} -> {self.path.absolute()}")
