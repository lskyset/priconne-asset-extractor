from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar
from urllib.request import urlretrieve

from ..abc import AbstractFile
from ..config import Config, ManifestType
from ..files import FileContainer
from ..protocols import Downloadable, File, Readable

T = TypeVar("T", bound=File)


class AbstractManifest(
    AbstractFile,
    FileContainer[T],
    Downloadable,
    Readable,
    Generic[T],
    metaclass=ABCMeta,
):
    __slots__ = ("_version",)

    def __init__(
        self,
        path: Path | str,
        version: int,
        type_: ManifestType,
        size: int = 0,
    ) -> None:
        AbstractFile.__init__(self, path, type_, size)
        self._version: int = version
        self._files: list[T] | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._path

    @property
    def url(self) -> str:
        endpoint = self._type.value % (str(self._version), self._name)
        return f"https://{Config.host.value}/{endpoint}"

    @property
    def version(self) -> int:
        return self._version

    @property
    def files(self) -> list[T]:
        if self._files is None:
            self._files = self._read()
        return self._files

    @abstractmethod
    def _read(self) -> list[T]:
        ...

    def download(self) -> None:
        if self.path.exists():
            if self.path.stat().st_size == self.size:
                return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(self.url, self.path)
        print(f"DL {self.url} -> {self.path.absolute()}")
