import base64
from enum import Enum
from struct import unpack


class CommandId(Enum):
    NONE = -1
    TITLE = 0
    OUTLINE = 1
    VISIBLE = 2
    FACE = 3
    FOCUS = 4
    BACKGROUND = 5
    PRINT = 6
    TAG = 7
    GOTO = 8
    BGM = 9
    TOUCH = 10
    CHOICE = 11
    VO = 12
    WAIT = 13
    IN_L = 14
    IN_R = 15
    OUT_L = 16
    OUT_R = 17
    FADEIN = 18
    FADEOUT = 19
    IN_FLOAT = 20
    OUT_FLOAT = 21
    JUMP = 22
    SHAKE = 23
    POP = 24
    NOD = 25
    SE = 26
    BLACK_OUT = 27
    BLACK_IN = 28
    WHITE_OUT = 29
    WHITE_IN = 30
    TRANSITION = 31
    SITUATION = 32
    COLOR_FADEIN = 33
    FLASH = 34
    SHAKE_TEXT = 35
    TEXT_SIZE = 36
    SHAKE_SCREEN = 37
    DOUBLE = 38
    SCALE = 39
    TITLE_TELOP = 40
    WINDOW_VISIBLE = 41
    LOG = 42
    NOVOICE = 43
    CHANGE = 44
    FADEOUT_ALL = 45
    MOVIE = 46
    MOVIE_STAY = 47
    BATTLE = 48
    STILL = 49
    BUSTUP = 50
    ENV = 51
    TUTORIAL_REWARD = 52
    NAME_EDIT = 53
    EFFECT = 54
    EFFECT_DELETE = 55
    EYE_OPEN = 56
    MOUTH_OPEN = 57
    AUTO_END = 58
    EMOTION = 59
    EMOTION_END = 60
    ENV_STOP = 61
    BGM_PAUSE = 62
    BGM_RESUME = 63
    BGM_VOLUME_CHANGE = 64
    ENV_RESUME = 65
    ENV_VOLUME = 66
    SE_PAUSE = 67
    CHARA_FULL = 68
    SWAY = 69
    BACKGROUND_COLOR = 70
    PAN = 71
    STILL_UNIT = 72
    SLIDE_CHARA = 73
    SHAKE_SCREEN_ONCE = 74
    TRANSITION_RESUME = 75
    SHAKE_LOOP = 76
    SHAKE_DELETE = 77
    UNFACE = 78
    WAIT_TOKEN = 79
    EFFECT_ENV = 80
    BRIGHT_CHANGE = 81
    CHARA_SHADOW = 82
    UI_VISIBLE = 83
    FADEIN_ALL = 84
    CHANGE_WINDOW = 85
    BG_PAN = 86
    STILL_MOVE = 87
    STILL_NORMALIZE = 88
    VOICE_EFFECT = 89
    TRIAL_END = 90
    SE_EFFECT = 91
    CHARACTER_UP_DOWN = 92
    BG_CAMERA_ZOOM = 93
    BACKGROUND_SPLIT = 94
    CAMERA_ZOOM = 95
    SPLIT_SLIDE = 96
    BGM_TRANSITION = 97
    SHAKE_ANIME = 98
    INSERT_STORY = 99
    PLACE = 100
    IGNORE_BGM = 101
    MULTI_LIPSYNC = 102
    JINGLE = 103
    TOUCH_TO_START = 104
    EVENT_ADV_MOVE_HORIZONTAL = 105
    BG_PAN_X = 106
    BACKGROUND_BLUR = 107
    SEASONAL_REWARD = 108
    MINI_GAME = 109
    MAX = 110
    UNKNOWN = 112  # todo: find the actual name


def deserialize_command(data) -> tuple[CommandId, list[str]]:
    index = data[0]
    args = []
    if len(data) > 1:
        args = data[1:]
    array = []
    for arg in args:
        array2 = []
        for byte in arg:
            if byte > 127:
                array2.append(255 - byte)
            else:
                array2.append(byte)
        str_ = base64.b64decode(bytearray(array2))
        array.append(str_.decode())
    return (CommandId(index), array)


def deserialize_story_raw(bytes_: bytes) -> list[tuple[CommandId, list[str]]]:
    commands = []
    fs = 0
    raw_commands = []
    i = 2
    while i < len(bytes_):
        args: list[bytes | int] = []
        index = int(unpack(">H", bytes_[fs : fs + 2])[0])
        fs += 2
        args.append(index)
        num = i
        while True:
            length = int(unpack(">l", bytes_[fs : fs + 4])[0])
            fs += 4
            if length == 0:
                break
            array = bytes_[fs : fs + length]
            fs += length
            args.append(array)
            num += 4 + length
        i = num + 4
        raw_commands.append(args)
        i += 2
    for raw_command in raw_commands:
        if len(raw_command) > 1:
            commands.append(deserialize_command(raw_command))
    return commands


def deserialize_story(bytes_: bytes) -> dict:
    commands = deserialize_story_raw(bytes_)
    story: dict[int, dict] = {}
    num = 0
    story[num] = {}
    block: dict[str, str | tuple | dict] = story[num]
    for command_id, args in commands:
        match command_id:
            case CommandId.PRINT:
                cmd = block.setdefault(command_id.name.lower(), {})
                cmd.setdefault("name", args[0])
                cmd["text"] = (cmd.get("text") or "") + clean_text(args[1])
            case CommandId.CHOICE:
                block.setdefault(command_id.name.lower(), [])
                block[command_id.name.lower()].append(
                    {
                        "text": args[0],
                        "tag": args[1],
                    }
                )
            case CommandId.BUSTUP:
                num += 1
                block = story.setdefault(num, {})
            case CommandId.TAG:
                story.setdefault(num + 1, {})
                story[num + 1][command_id.name.lower()] = args[0]
            case CommandId.TITLE | CommandId.SITUATION | CommandId.OUTLINE | CommandId.VO | CommandId.GOTO:
                if len(args) == 1:
                    args = args[0]
                block[command_id.name.lower()] = args
    return story


def clean_text(text: str) -> str:
    replace_pairs = (
        ("\\n", "\n"),
        ("{0}", "{player_name}"),
        ('\\"', '"'),
    )
    for pair in replace_pairs:
        text = text.replace(*pair)
    return text
