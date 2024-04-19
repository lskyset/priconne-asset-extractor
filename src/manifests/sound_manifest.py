from pathlib import Path

from ..config import ManifestType
from ..files.sound_file import SoundFile
from .abstract_manifest import AbstractManifest


class SoundManifest(AbstractManifest[SoundFile]):
    def __init__(self, version: int):
        super().__init__("soundmanifest", version, ManifestType.SOUND)

    def _read(self) -> list[SoundFile]:
        self.download()
        with self.path.open() as f:
            rows = f.readlines()
        files: list[SoundFile] = []
        for row in rows:
            path, hash_, _, evertutocom, size, *_ = row.split(",")
            new_path: Path = Path(path)
            files.append(
                SoundFile(
                    new_path.parent / "awb" / new_path.name,
                    hash_,
                    int(size),
                ),
            )
        return files
