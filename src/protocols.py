from pathlib import Path
from typing import Protocol


class File(Protocol):
    @property
    def path(self) -> Path:
        ...

    @property
    def name(self) -> str:
        ...


class Readable(Protocol):
    def _read(self) -> list:
        ...


class Downloadable(File, Protocol):
    def download(self) -> None:
        ...


class Extractable(Protocol):
    def extract(self) -> None:
        ...
