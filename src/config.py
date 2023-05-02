from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import UnityPy


class ManifestType(Enum):
    ASSET = "dl/Resources/%s/Jpn/AssetBundles/Windows/manifest/%s"
    MOVIE = "dl/Resources/%s/Jpn/Movie/PC/High/manifest/%s"
    SOUND = "dl/Resources/%s/Jpn/Sound/manifest/%s"


class AssetType(Enum):
    ASSET = "dl/pool/AssetBundles"
    MOVIE = "dl/pool/Movie"
    SOUND = "dl/pool/Sound"


class BundleType(Enum):
    TEXTURE_2D = "Texture2D"
    Sprite = "Sprite"
    TEXT_ASSET = "TextAsset"


class BundleSource(Enum):
    WEB = 0
    LOCAL = 1  # not implemented


class PricoHost(Enum):
    JP = "prd-priconne-redive.akamaized.net"
    EN = "assets-priconne-redive-us.akamaized.net"  # not implemented


@dataclass(frozen=True)
class Config:
    image_format: str = ".png"
    bundle_source: BundleSource = BundleSource.WEB
    host = PricoHost.JP
    usmtoolkit_path = Path("usmtoolkit/UsmToolkit.exe")
    vgmstream_path = usmtoolkit_path.parent / "vgmstream" / "test.exe"


UnityPy.config.FALLBACK_UNITY_VERSION = "2021.3.20f1"
