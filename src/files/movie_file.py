import os
from pathlib import Path

from ..abc import AbstractManifestFile
from ..config import AssetType, Config
from ..protocols import Extractable


class MovieFile(AbstractManifestFile, Extractable):
    def __init__(self, path: Path | str, hash_: str, size: int = 0) -> None:
        super().__init__(path, hash_, AssetType.MOVIE, size)

    def extract(self) -> None:
        self.download()
        extract_path = self.path.parent.parent / (self.path.stem + ".mp4")
        if extract_path.exists():
            return

        os.system(
            f"cd {Config.usmtoolkit_path.parent.absolute()}"
            f" && {Config.usmtoolkit_path.name} convert"
            f" -c {self.path.absolute()}"
            f" -o {extract_path.parent.absolute()}"
        )
        print(f"EX {self.name} -> {extract_path.absolute()}")
