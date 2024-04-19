from ..config import ManifestType
from .manifest import AbstractManifest, Manifest


class AssetManifest(AbstractManifest[Manifest]):
    def __init__(self, version: int):
        AbstractManifest.__init__(
            self, "manifest_assetmanifest", version, ManifestType.ASSET
        )

    def _read(self) -> list[Manifest]:
        self.download()
        with self.path.open() as f:
            rows = f.readlines()
        files = []
        for row in rows:
            path, hash_, _, evertutocom, size, *_ = row.split(",")
            manifest = Manifest(
                path, hash_, self.version, ManifestType.ASSET, int(size)
            )
            files.append(manifest)
        return files
