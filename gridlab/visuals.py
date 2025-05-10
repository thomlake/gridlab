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


ENTITY_ASCII_MAP = {
    Entity.PLAYER: '@',
    Entity.GOAL: 'o',
    Entity.KEY: 'k',
    Entity.TIMER_RESET: '+',
    Entity.ENEMY: 'e',
    Entity.SPIKE: '^',
    Entity.WALL: '|',
    Entity.BLOCK: '#',
    Entity.DOOR: '!',
    Entity.EMPTY: '.',
    Entity.GOAL_REACHED: '*',
    Entity.PLAYER_DIED: 'X',
}

ENTITY_ASCII_REPLACEMENTS = {
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


ENTITY_COLOR_MAP = {
    Entity.PLAYER: INDIGO,
    Entity.GOAL: PINK,
    Entity.KEY: TEAL,
    Entity.TIMER_RESET: TEAL,
    Entity.ENEMY: PURPLE,
    Entity.SPIKE: PURPLE,
    Entity.WALL: DARK_GRAY,
    Entity.BLOCK: DARK_GRAY,
    Entity.DOOR: DARK_GRAY,
    Entity.EMPTY: LIGHT_GRAY,
    Entity.GOAL_REACHED: PINK,
    Entity.PLAYER_DIED: INDIGO,
}


def make_rich_status(v: str):
    return color_background(color_foreground(v, WHITE), DARK_GRAY)


def make_rich_entity_symbol(k: Entity, v: str | list[str]):
    if isinstance(v, list):
        return [make_rich_entity_symbol(s) for s in v]

    v = ENTITY_ASCII_REPLACEMENTS.get(k, v)

    if k != Entity.EMPTY:
        v = make_bold(v)

    v = color_foreground(v, ENTITY_COLOR_MAP.get(k))
    v = color_background(v, '#ffffff')
    return v


ENTITY_RICH_ASCII_MAP = {k: make_rich_entity_symbol(k, v) for k, v in ENTITY_ASCII_MAP.items()}
