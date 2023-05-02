import re
from itertools import chain
from multiprocessing import Pool
from pathlib import Path
from urllib.request import urlretrieve

from src.config import Config

from . import version_finder
from .asset_bundle import AssetBundle
from .cysp2skel import Cysp2Skel
from .files import BundleFile
from .manifests import AssetManifest, Manifest, MovieManifest, SoundManifest
from .mdb import MDB
from .protocols import Extractable


class Dataminer:
    _mdb: MDB | None = None
    _cysp2skel: Cysp2Skel | None = None

    __slots__ = (
        "_asset_manifest",
        "_sound_manifest",
        "_movie_manifest",
    )

    def __init__(self, *, version: int | None = None) -> None:
        if version is None:
            version = version_finder.get_latest_version(Config.host)
        self._asset_manifest: AssetManifest = AssetManifest(version)
        self._sound_manifest: SoundManifest = SoundManifest(version)
        self._movie_manifest: MovieManifest = MovieManifest(version)

    @staticmethod
    def _pool_manifest_files(data: tuple[Manifest, str]) -> list[AssetBundle]:
        manifest, match = data
        ret = manifest.get_files(match)
        return ret

    @staticmethod
    def _pool_bundle_files(data: tuple[AssetBundle, str]) -> list[BundleFile]:
        assetbundle, match = data
        return assetbundle.get_files(match)

    @staticmethod
    def _extract_file(file: Extractable):
        file.extract()

    @staticmethod
    def download_mdb(mdb_name="master.db") -> str:
        return urlretrieve(
            "https://github.com/lskyset/nozomi-cb-data/raw/main/master.db",
            mdb_name,
        )[0]

    @property
    def mdb(self) -> MDB:
        if Dataminer._mdb is None:
            Dataminer._mdb = MDB(Dataminer.download_mdb())
        return Dataminer._mdb

    @property
    def cysp2skel(self) -> Cysp2Skel:
        if Dataminer._cysp2skel is None:
            Dataminer._cysp2skel = Cysp2Skel("a/spine/unitanimation", self.mdb)
        return Dataminer._cysp2skel

    def get_manifests(
        self, match: str = ""
    ) -> list[Manifest | SoundManifest | MovieManifest]:
        manifests: list[SoundManifest | MovieManifest] = []
        tmp: list[SoundManifest | MovieManifest] = [
            self._sound_manifest,
            self._movie_manifest,
        ]
        for manifest in tmp:
            if re.search(match, manifest.name):
                manifests.append(manifest)
        return self._asset_manifest.get_files(match) + manifests

    def datamine(
        self,
        *,
        manifest_filter: str,
        assetbundle_filter: str,
        file_filter: str,
    ):
        manifests: list[Manifest | SoundManifest | MovieManifest]
        manifests = self.get_manifests(manifest_filter)

        with Pool() as p:
            assetbundles: chain[AssetBundle] = chain(
                *p.imap(
                    self._pool_manifest_files,
                    [
                        (manifest, assetbundle_filter)
                        for manifest in manifests
                        if type(manifest) == Manifest
                    ],
                )
            )

            files: chain[Extractable] = chain(
                *p.imap(
                    self._pool_bundle_files,
                    [(assetbndl, file_filter) for assetbndl in assetbundles],
                ),
                chain(
                    *[
                        manifest.get_files(file_filter)
                        for manifest in manifests
                        if type(manifest) == SoundManifest
                        or type(manifest) == MovieManifest
                    ]
                ),
            )

            list(p.imap(self._extract_file, files))

    def get_skel(self, unit_id: int):
        if (buffer := self.cysp2skel.get_skeleton_buffer(unit_id)) is None:
            return print(f"Could not find {unit_id=}")
        path = Path(f"a/spine/sdnormal/spine_{unit_id}/{unit_id}.skel")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            f.write(buffer.read())
        print(f"EX {path.absolute()}")
