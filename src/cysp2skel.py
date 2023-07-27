import struct
from io import BufferedReader, BytesIO, RawIOBase
from pathlib import Path
from typing import cast

from .mdb import MDB


class Cysp2Skel:
    _default_base: BufferedReader | None = None
    _default_base_animation_count: int = 0
    _default_animation_count_index: int = 0

    _unit_class_data: dict[str, str] | None = None

    __slots__ = (
        "_cysp_dir",
        "mdb",
        "_current_base",
        "_current_base_animation_count",
        "_current_animation_count_index",
    )

    def __init__(self, cysp_dir: str | Path, mdb: MDB) -> None:
        self._cysp_dir = Path(cysp_dir)
        self.mdb = mdb
        self._current_base: BufferedReader | None = None
        self._current_base_animation_count: int = 0
        self._current_animation_count_index: int = 0

    def _get_base(self, str_id: str) -> RawIOBase:
        files: list[str] = [
            f"{str_id}_{name}.cysp"
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

        self._current_base_animation_count = 0
        base = BytesIO()
        for file in paths:
            try:
                with file.open("rb") as f:
                    f.seek(12)
                    count = _read_varint(f)
                    f.seek((count + 1) * 32)
                    base.write(f.read())
                    if "CHARA_BASE.cysp" in file.name:
                        self._current_animation_count_index = base.tell()
                        base.write(b"\0")
                    else:
                        self._current_base_animation_count += count
            except FileNotFoundError as e:
                print(f"Ignoring {e}")
        base.seek(self._current_animation_count_index)
        base.write(bytes([self._current_base_animation_count]))
        base.seek(0)
        return base

    def get_default_base(self) -> BufferedReader:
        if Cysp2Skel._default_base is not None:
            Cysp2Skel._default_base.seek(0)
            self._current_base_animation_count = Cysp2Skel._default_base_animation_count
            self._current_animation_count_index = (
                Cysp2Skel._default_animation_count_index
            )
            return Cysp2Skel._default_base

        Cysp2Skel._default_base = BufferedReader(self._get_base("000000"))
        Cysp2Skel._default_base_animation_count = self._current_base_animation_count
        Cysp2Skel._default_animation_count_index = self._current_animation_count_index

        return Cysp2Skel._default_base

    def get_unit_data(self) -> dict[str | dict[str | str]]:
        unit_data = self.mdb.c.execute(
            "select unit_id,prefab_id,prefab_id_battle,motion_type from unit_data"
        ).fetchall()

        unit_enemy_data = self.mdb.c.execute(
            "select unit_id,prefab_id,motion_type from unit_enemy_data"
        ).fetchall()

        unit_data_dict = {
            str(unit_id): {
                "motion_type": str(motion_type),
                "prefab_id": str(prefab_id),
                "prefab_id_battle": str(prefab_id_battle),
            }
            for unit_id, prefab_id, prefab_id_battle, motion_type in unit_data
        }
        enemy_data_dict = {
            str(unit_id): {
                "motion_type": str(motion_type),
                "prefab_id": str(prefab_id),
            }
            for unit_id, prefab_id, motion_type in unit_enemy_data
        }

        return {**unit_data_dict, **enemy_data_dict}

    @property
    def unit_data(self) -> dict:
        if Cysp2Skel._unit_class_data is None:
            Cysp2Skel._unit_class_data = self.get_unit_data()
        return Cysp2Skel._unit_class_data

    def get_skeleton_buffer(self, unit_id: int) -> BufferedReader | None:
        base_unit_id = str(unit_id // 100) + "01"

        if (unit := self.unit_data.get(base_unit_id)) is None:
            for unit in self.unit_data.values():
                if unit.get("prefab_id") == base_unit_id:
                    break
                if unit.get("prefab_id_battle") == base_unit_id:
                    break

        motion_type: str = unit.get("motion_type")

        if motion_type is None:
            return None
        if motion_type == "0":
            motion_type = base_unit_id
            self._current_base = self._get_base(base_unit_id)
        else:
            self._current_base = self.get_default_base()

        chara_class: str = motion_type.rjust(2, "0")
        files: list[str] = []
        files.append(f"{chara_class}_COMMON_BATTLE.cysp")
        # files.append(f"{chara_class}_LOADING.cysp")
        files.append(f"{unit.get('prefab_id')}_BATTLE.cysp")
        paths: list[Path] = [self._cysp_dir / file for file in files]

        skel = BytesIO()
        skel.write(self._current_base.read())
        class_animation_count = 0
        for file in paths:
            with file.open("rb") as f:
                f.seek(12)
                count = _read_varint(f)
                f.seek((count + 1) * 32)
                skel.write(f.read())
                class_animation_count += count
        skel.seek(self._current_animation_count_index)
        anim_count = self._current_base_animation_count + class_animation_count
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
