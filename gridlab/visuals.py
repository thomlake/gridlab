import string
from enum import StrEnum

from colorist import BgColorHex, ColorHex, Effect

from gridlab.entity import Entity


def color_background(value, color):
    if color is not None:
        c = BgColorHex(color)
        value = f'{c}{value}{c.OFF}'

    return value


def color_foreground(value, color):
    if color is not None:
        c = ColorHex(color)
        value = f'{c}{value}{c.OFF}'

    return value


def make_bold(value):
    return f'{Effect.BOLD}{value}{Effect.OFF}'


#
# @@@@@⊟⊠⊡⏍▢▢▢▢▣◪◪▣▣
# ☼☀︎▣◩◪⚉☬⚇⚙︎★♦︎⛳︎⌑☠▢★✦⭑⍈
# ..⛳︎.⚑
# ....█▅
# ■▢
# ⎡⎺⎤
# | |
# ⎣⎽⎦
# ⌜⎺⌝
# | |
# ⌞⎽⌟
#


CHAR_MAP = {
    Entity.PLAYER: '@',
    Entity.GOAL: 'X',
    Entity.KEY: 'k',
    Entity.TIMER_RESET: '+',
    Entity.ENEMY: 'e',
    Entity.SPIKE: '^',
    Entity.WALL: '|',
    Entity.BLOCK: '#',
    Entity.DOOR: '/',
    Entity.EMPTY: '.',
    Entity.GOAL_REACHED: '*',
    Entity.PLAYER_DIED: '_',
}

PRETTY_CHAR_REPLACEMENTS = {
    Entity.WALL: '█',
}

# ENTITY_ASCII_MAP = {
#     Entity.PLAYER: '@',
#     Entity.GOAL: '⚑',
#     Entity.KEY: '⚿',
#     Entity.TIMER_RESET: '↻',
#     Entity.ENEMY: 'e',
#     Entity.WALL: '#',
#     Entity.BLOCK: '▢',
#     Entity.DOOR: '▣',
#     Entity.SPIKE: '☼',
#     Entity.EMPTY: '.',
#     Entity.GOAL_REACHED: '★',
#     Entity.PLAYER_DIED: '☠',
# }

# Colors
# ------
TEAL = '#66C2C2'
PINK = '#EB5197'
INDIGO = '#325478'
LIGHT_INDIGO = '#657F9A'
BLUE = '#00A1FF'
PURPLE = '#806AD6'
# YELLOW = '#EEC584'
YELLOW = '#ECC30B'
GREEN = '#2B9720'
ORANGE = '#FC814A'
WHITE = '#ffffff'
BLACK = '#000000'
# DARK_GRAY = '#333333'
DARK_GRAY = '#787C85'
# LIGHT_GRAY = '#BFBFBF'
LIGHT_GRAY = '#E4E4E4'


# ENTITY_COLOR_MAP = {
#     Entity.PLAYER: INDIGO,
#     Entity.GOAL: PINK,
#     Entity.KEY: TEAL,
#     Entity.TIMER_RESET: TEAL,
#     Entity.ENEMY: PURPLE,
#     Entity.SPIKE: PURPLE,
#     Entity.WALL: DARK_GRAY,
#     Entity.BLOCK: DARK_GRAY,
#     Entity.DOOR: DARK_GRAY,
#     Entity.EMPTY: LIGHT_GRAY,
#     Entity.GOAL_REACHED: PINK,
#     Entity.PLAYER_DIED: INDIGO,
# }

BACKGROUND_COLOR = WHITE

COLOR_MAP = {
    Entity.PLAYER: PURPLE,
    Entity.GOAL: TEAL,
    Entity.KEY: TEAL,
    Entity.TIMER_RESET: TEAL,
    Entity.ENEMY: PINK,
    Entity.SPIKE: PINK,
    Entity.WALL: DARK_GRAY,
    Entity.BLOCK: DARK_GRAY,
    Entity.DOOR: DARK_GRAY,
    Entity.EMPTY: LIGHT_GRAY,
    Entity.GOAL_REACHED: TEAL,
    Entity.PLAYER_DIED: PINK,
}


def make_pretty_char(e: Entity, v: str):
    if e != Entity.EMPTY:
        v = make_bold(v)

    v = color_foreground(v, COLOR_MAP.get(e))
    v = color_background(v, WHITE)
    return v


def make_pretty_char_map():
    char_map = {}
    for e, v in CHAR_MAP.items():
        v = PRETTY_CHAR_REPLACEMENTS.get(e, v)
        char_map[e] = make_pretty_char(e, v)

    return char_map


PRETTY_CHAR_MAP = make_pretty_char_map()


class Style(StrEnum):
    PLAIN = 'plain'
    PRETTY = 'pretty'


STYLES = {
    Style.PLAIN: CHAR_MAP,
    Style.PRETTY: PRETTY_CHAR_MAP,
}


def get_char_map(style: Style):
    return STYLES[style]


# class TextGridSymbols:
#     def __init__(
#             self,
#             *,
#             char_map: dict[Entity, str] | None = None,
#             color_map: dict[Entity, str] | None = None,
#     ):
#         self.char_map = char_map
#         self.color_map = color_map

#     def randomize(self):


# def randomize_char_map(choices: str | None = None):
#     entities_to_keep = {Entity.EMPTY}
#     entities_to_replace = {e for e in self.char_map.keys() if e not in entities_to_keep}

#     if choices is None:
#         choices = string.ascii_letters + string.digits + string.punctuation

#     new_char_map = {}
#     for e in entities_to_keep:
#         s = self.char_map[e]
#         new_char_map[e] = s
#         choices = choices.replace(s, '')

#     chosen = random.sample(choices, k=len(entities_to_replace))
#     for e, s in zip(entities_to_replace, chosen):
#         new_char_map[e] = s

#     self.char_map = new_char_map