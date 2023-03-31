import os
from pathlib import Path

from ..abc import AbstractManifestFile
from ..config import AssetType, Config
from ..protocols import Extractable


class SoundFile(AbstractManifestFile, Extractable):
    def __init__(self, path: Path | str, hash_: str, size: int = 0) -> None:
        super().__init__(path, hash_, AssetType.SOUND, size)

    def extract(self) -> None:
        self.download()
        if ".acb" in self.name:
            return
        extract_path = self.path.parent.parent / (self.path.stem + ".wav")
        extract_path_2 = self.path.parent.parent / (self.path.stem + "_1.wav")
        if extract_path.exists() or extract_path_2.exists():
            return
        print(
            f"{Config.vgmstream_path.absolute()}"
            f" -S 0 {self.path.absolute()}"
            f" -o {extract_path.parent.absolute()}/?n_?s.wav"
        )
        stream = os.popen(
            f"{Config.vgmstream_path.absolute()}"
            f" -S 0 {self.path.absolute()}"
            f" -o {extract_path.parent.absolute()}/?n_?s.wav"
        )
        stream.read()
        files = [*extract_path.parent.glob(f"{self.path.stem};*")] + [
            *extract_path.parent.glob(f"{self.path.stem}_*")
        ]
        for file in files:
            rename = file.stem.split(";")[0]
            file = file.replace(file.with_stem(rename).absolute())
            print(f"EX {self.name} -> {file.absolute()}")
