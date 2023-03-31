import sqlite3
from pathlib import Path


class MDB:
    __slots__ = ("_mdb", "_c")

    def __init__(self, path: str | Path) -> None:
        self._mdb: sqlite3.Connection = sqlite3.connect(path)
        self._c: sqlite3.Cursor = self._mdb.cursor()

    @property
    def c(self) -> sqlite3.Cursor:
        return self._c

    def __del__(self):
        self._mdb.close()
