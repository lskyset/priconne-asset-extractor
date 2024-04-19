from pathlib import Path

from ..abc.abstract_manifest_file import AbstractManifestFile
from ..asset_bundle import AssetBundle
from ..config import ManifestType
from .abstract_manifest import AbstractManifest


class Manifest(
    AbstractManifestFile,
    AbstractManifest[AssetBundle],
):
    def __init__(
        self,
        path: Path | str,
        hash_: str,
        version: int,
        type_: ManifestType,
        size: int = 0,
    ) -> None:
        AbstractManifest.__init__(self, path, version, type_, size)
        AbstractManifestFile.__init__(self, path, hash_, type_, size, version)

    def _read(self) -> list[AssetBundle]:
        self.download()
        with self.path.open() as f:
            rows = f.readlines()
        files = []
        for row in rows:
            path, hash_, _, evertutocom, size, *_ = row.split(",")
            files.append(AssetBundle(path, hash_, int(size)))
        return files
