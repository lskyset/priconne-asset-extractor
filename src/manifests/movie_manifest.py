from pathlib import Path

from ..config import ManifestType
from ..files import MovieFile
from .abstract_manifest import AbstractManifest


class MovieManifest(AbstractManifest[MovieFile]):
    def __init__(self, version: int):
        super().__init__("movie2manifest", version, ManifestType.MOVIE)

    def _read(self) -> list[MovieFile]:
        self.download()
        with self.path.open() as f:
            rows = f.readlines()
        files: list[MovieFile] = []
        for row in rows:
            path, _old_hash, new_hash, _, size, *_ = row.split(",")
            new_path = Path(path)
            files.append(
                MovieFile(
                    new_path.parent / "usm" / new_path.name,
                    new_hash,
                    int(size),
                ),
            )
        return files
