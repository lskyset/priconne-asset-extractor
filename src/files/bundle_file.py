from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import UnityPy  # type: ignore[import]

from ..config import BundleType, Config
from ..protocols import Extractable

if TYPE_CHECKING:
    from ..asset_bundle import AssetBundle


class BundleFile(Extractable):

    __slots__ = (
        "_parent_path",
        "_object",
        "_type",
        "_data",
        "image",
        "script",
        "container",
        "_asset_name",
        "_is_picklable",
    )

    def __init__(
        self, pcr_file: AssetBundle, obj: UnityPy.environment.ObjectReader
    ) -> None:
        self._parent_path: Path = pcr_file.path.parent.parent
        self._object: UnityPy.environment.ObjectReader | None = obj
        self._type: BundleType = BundleType(obj.type.name)
        self._data: Any = None
        self.image: Any = None
        self.script: Any = None
        self.container: str | None = None
        self._asset_name: str | None = None
        self._is_picklable: bool = False

        # for Protocol
        self._name = self.name
        self._path = self.path
        self._size = self.size

    @property
    def parent_path(self) -> Path:
        return self._parent_path

    @property
    def type(self) -> BundleType:
        return self._type

    @property
    def data(self) -> Any:
        if self._data is None and self._object:
            self._data = self._object.read()
            self._object = None
        return self._data

    @property
    def extention(self) -> str:
        if self.is_image:
            return Config().image_format
        return ""

    @property
    def name(self) -> str:
        if self._asset_name is None and self.data:
            self._asset_name = self.data.name
        if self._asset_name:
            return self._asset_name + self.extention
        else:
            raise Exception("Name cannot be None.")

    @property
    def size(self) -> int:
        return 0

    @property
    def path(self) -> Path:
        if self.data:
            self.container = cast(str | None, self.data.container)
        if self.container:
            str_path = self.container.replace(
                "assets/_elementsresources/resources", "a"
            )
            return Path(str_path).parent / self.name
        else:
            return self._parent_path / self.name

    @property
    def is_image(self) -> bool:
        return self.type in [BundleType.TEXTURE_2D, BundleType.Sprite]

    @property
    def is_text(self) -> bool:
        return self.type == BundleType.TEXT_ASSET

    def extract(self) -> None:
        if self.path.exists():
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self.process_data()
        if self.image:
            self._extract_image()
        elif self.script:
            self._extract_text()
        print(f"EX {self.name} -> {self.path.absolute()}")

    def _extract_image(self):
        self.image.save(self.path, lossless=True)

    def _extract_text(self):
        with self.path.open("wb") as f:
            f.write(bytes(self.script))

    def process_data(self) -> None:
        if self._data is None:
            return
        if self.is_image:
            self.image = self.data.image
        elif self.is_text:
            self.script = bytes(self.data.script)
        self._asset_name = self.data.name
        self.container = self.data.container
        self._data = None

    def __getstate__(self) -> tuple[None, dict]:
        self.process_data()
        slot_dict: dict[str, Any] = {}
        for attribute in self.__slots__:
            slot_dict[attribute] = getattr(self, attribute)
        return (None, slot_dict)
