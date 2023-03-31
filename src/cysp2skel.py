import struct
from io import BufferedReader, BytesIO, RawIOBase
from pathlib import Path
from typing import cast

from .mdb import MDB


class Cysp2Skel:
    _base: BufferedReader | None = None
    _animation_count_index: int = 0
    _base_animation_count: int = 0
    _unit_class_data: dict[str, str] | None = None

    __slots__ = ("_cysp_dir", "mdb")

    def __init__(self, cysp_dir: str | Path, mdb: MDB) -> None:
        self._cysp_dir = Path(cysp_dir)
        self.mdb = mdb

    @property
    def base(self) -> BufferedReader:
        if Cysp2Skel._base is not None:
            Cysp2Skel._base.seek(0)
            return Cysp2Skel._base

        base_id = "000000"
        files: list[str] = [
            f"{base_id}_{name}.cysp"
            for name in [
                "CHARA_BASE",
                "DEAR",
                "NO_WEAPON",
                "POSING",
                "RACE",
                "RUN_JUMP",
                "SMILE",
            ]
        ]

        paths: list[Path] = [self._cysp_dir / file for file in files]

        base = BytesIO()
        for file in paths:
            with file.open("rb") as f:
                f.seek(12)
                count = _read_varint(f)
                f.seek((count + 1) * 32)
                base.write(f.read())
                if file.name == "000000_CHARA_BASE.cysp":
                    Cysp2Skel._animation_count_index = base.tell()
                    base.write(b"\0")
                else:
                    Cysp2Skel._base_animation_count += count
        base.seek(Cysp2Skel._animation_count_index)
        base.write(bytes([Cysp2Skel._base_animation_count]))
        base.seek(0)
        Cysp2Skel._base = BufferedReader(cast(RawIOBase, base))
        return Cysp2Skel._base

    def get_unit_class_data(self) -> dict:
        data = self.mdb.c.execute(
            "select unit_id,motion_type from unit_data"
        ).fetchall()
        return {str(id_): str(type_) for id_, type_ in data}

    @property
    def unit_class_data(self) -> dict[str, str]:
        if Cysp2Skel._unit_class_data is None:
            Cysp2Skel._unit_class_data = self.get_unit_class_data()
        return Cysp2Skel._unit_class_data

    def get_skeleton_buffer(self, unit_id: int) -> BufferedReader | None:
        class_type = self.unit_class_data.get(str(unit_id // 100) + "01")
        if class_type is None:
            return None
        chara_class: str = class_type.rjust(2, "0")
        files: list[str] = []
        files.append(f"{chara_class}_COMMON_BATTLE.cysp")
        files.append(f"{unit_id//100}01_BATTLE.cysp")
        paths: list[Path] = [self._cysp_dir / file for file in files]

        skel = BytesIO()
        skel.write(self.base.read())
        class_animation_count = 0
        for file in paths:
            with file.open("rb") as f:
                f.seek(12)
                count = _read_varint(f)
                f.seek((count + 1) * 32)
                skel.write(f.read())
                class_animation_count += count
        skel.seek(Cysp2Skel._animation_count_index)
        anim_count = Cysp2Skel._base_animation_count + class_animation_count
        skel.write(bytes([anim_count]))
        skel.seek(0)
        return BufferedReader(cast(RawIOBase, skel))


def int32(x: int) -> int:
    if x > 0xFFFFFFFF:
        raise OverflowError
    if x > 0x7FFFFFFF:
        x = 0x100000000 - x
        if x < 2147483648:
            return -x
        else:
            return -2147483648
    return x


def _read_byte(input: BufferedReader) -> int:
    return struct.unpack(">B", input.read(1))[0]


def _read_varint(input: BufferedReader, optimizePositive: bool = True) -> int:
    b = _read_byte(input)
    value = b & 0x7F
    if b & 0x80:
        b = _read_byte(input)
        value |= (b & 0x7F) << 7
        if b & 0x80:
            b = _read_byte(input)
            value |= (b & 0x7F) << 14
            if b & 0x80:
                b = _read_byte(input)
                value |= (b & 0x7F) << 21
                if b & 0x80:
                    value |= (_read_byte(input) & 0x7F) << 28
    if not optimizePositive:
        value = (value >> 1) ^ -(value & 1)
    return int32(value)
