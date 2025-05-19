from dataclasses import dataclass
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


@dataclass
class Symbol:
    plain_char: str
    fancy_char: str | None = None
    color: str | None = None
    background: str | None = None
    bold: bool = False

    def __post_init__(self):
        self.fancy_char = self.fancy_char or self.plain_char

    def plain(self):
        return self.plain_char

    def fancy(self):
        c = self.fancy_char
        c = color_background(c, self.background)
        c = color_foreground(c, self.color)
        if self.bold:
            c = make_bold(c)

        return c

    def html_table_cell(
            self,
            font_size: str = '32px',
            font_family: str = "'Source Code Pro', monospace",
            line_height: str = '1.5em',
            padding: str = '2px 16px',
            border: str = 'none',
            border_radius: str = '0px',
    ):
        style_elements = [
            f'font-size: {font_size}',
            f'font-family: {font_family}',
            f'line-height: {line_height}',
            f'padding: {padding}',
            f'border: {border}',
            f'border-radius: {border_radius}',
        ]

        if self.background:
            style_elements.append(f'background: {self.background}')

        if self.color:
            style_elements.append(f'color: {self.color}')

        if self.bold:
            style_elements.append('font-weight: bold')

        style = '; '.join(style_elements)
        return f'<td align="center" style="{style}">{self.fancy_char}</td>'

    def html_span(
            self,
            font_size: int = 16,
            font_family: str = "'Source Code Pro', monospace",
            line_height: str = '1.5em',
    ):
        style_elements = [
            f'font-size: {font_size}px',
            f'font-family: {font_family}',
            f'line-height: {line_height}',
        ]

        if self.background:
            style_elements.append(f'background: {self.background}')

        if self.color:
            style_elements.append(f'color: {self.color}')

        if self.bold:
            style_elements.append(f'font-weight: {self.bold}')

        style = '; '.join(style_elements)
        return f'<span style="{style}">{self.fancy_char}</span>'


#
# @@@@@⊟⊠⊡⏍▢▢▢▢▣◪◪▣▣
# ☼☀︎▣◩◪⚉☬⚇⚙︎★♦︎⛳︎⌑☠▢★✦⭑⍈
# ..⛳︎.⚑
# ....█▅
# ■▢
# #▣@◪
# ⎡⎺⎤
# | |
# ⎣⎽⎦
# ⌜⎺⌝
# | |
# ⌞⎽⌟
#


PLAIN_CHAR_MAP = {
    Entity.PLAYER: '@',
    Entity.GOAL: '$',
    Entity.KEY: 'k',
    Entity.TIMER_RESET: '+',
    Entity.ENEMY: 'e',
    Entity.SPIKE: '^',
    Entity.WALL: '|',
    Entity.BLOCK: '=',
    Entity.DOOR: '#',
    Entity.EMPTY: '.',
    Entity.GOAL_REACHED: '$',
    Entity.PLAYER_DIED: '_',
}

FANCY_CHAR_MAP = {
    **PLAIN_CHAR_MAP,
    Entity.WALL: '█',
    Entity.BLOCK: '■',
}


def create_symbol_map(
        palette: dict[Entity, str],
        background: dict[Entity, str] | None = None,
):
    background = background or {}
    symbol_map: dict[Entity, Symbol] = {}
    for e, color in palette.items():
        tv = Symbol(
            plain_char=PLAIN_CHAR_MAP[e],
            fancy_char=FANCY_CHAR_MAP[e],
            color=color,
            background=background.get(e),
            bold=e != Entity.EMPTY,
        )
        symbol_map[e] = tv

    return symbol_map


def _symbol_map_01():
    white = '#ffffff'
    teal = '#66C2C2'
    pink = '#EB5197'
    indigo = '#325478'
    purple = '#806AD6'
    dark_gray = '#787C85'
    light_gray = '#E4E4E4'

    palette = {
        Entity.PLAYER: indigo,
        Entity.GOAL: pink,
        Entity.KEY: teal,
        Entity.TIMER_RESET: teal,
        Entity.ENEMY: purple,
        Entity.SPIKE: purple,
        Entity.WALL: dark_gray,
        Entity.BLOCK: dark_gray,
        Entity.DOOR: dark_gray,
        Entity.EMPTY: light_gray,
        Entity.GOAL_REACHED: pink,
        Entity.PLAYER_DIED: indigo,
    }
    background = {k: white for k in palette.keys()}
    return create_symbol_map(palette, background=background)


def _symbol_map_02():
    white = '#ffffff'
    teal = '#4090A0'
    pink = '#DB3EAB'
    blue = '#4086E4'
    purple = '#4E40B8'
    orange = '#EB9047'
    yellow = '#F1C553'
    light_gray = '#E4E4E4'

    palette = {
        Entity.PLAYER: teal,
        Entity.GOAL: blue,
        Entity.KEY: orange,
        Entity.TIMER_RESET: orange,
        Entity.ENEMY: pink,
        Entity.SPIKE: pink,
        Entity.WALL: purple,
        Entity.BLOCK: purple,
        Entity.DOOR: purple,
        Entity.EMPTY: light_gray,
        Entity.GOAL_REACHED: blue,
        Entity.PLAYER_DIED: pink,
    }
    background = {k: white for k in palette.keys()}
    return create_symbol_map(palette, background=background)


def _symbol_map_03():
    white = '#ffffff'
    teal = '#308695'
    red = '#D45769'
    yellow = '#E69D45'
    purple = '#574D68'
    green = '#76C369'
    light_gray = '#E4E4E4'

    palette = {
        Entity.PLAYER: teal,
        Entity.GOAL: teal,
        Entity.KEY: yellow,
        Entity.TIMER_RESET: yellow,
        Entity.ENEMY: red,
        Entity.SPIKE: red,
        Entity.WALL: purple,
        Entity.BLOCK: purple,
        Entity.DOOR: purple,
        Entity.EMPTY: light_gray,
        Entity.GOAL_REACHED: teal,
        Entity.PLAYER_DIED: teal,
    }
    background = {k: white for k in palette.keys()}
    return create_symbol_map(palette, background=background)


def _symbol_map_primary():
    white = '#ffffff'
    teal = '#44898B'
    red = '#C64C56'
    yellow = '#E5A250'
    purple = '#5F496D'
    green = '#548D55'
    blue = '#519FD1'
    light_gray = '#E4E4E4'

    palette = {
        Entity.PLAYER: blue,
        Entity.GOAL: blue,
        Entity.KEY: yellow,
        Entity.TIMER_RESET: yellow,
        Entity.ENEMY: red,
        Entity.SPIKE: red,
        Entity.WALL: purple,
        Entity.BLOCK: purple,
        Entity.DOOR: purple,
        Entity.EMPTY: light_gray,
        Entity.GOAL_REACHED: blue,
        Entity.PLAYER_DIED: red,
    }
    background = {k: white for k in palette.keys()}
    return create_symbol_map(palette, background=background)


def _symbol_map_desert():
    light = '#F4EFE3'
    teal = '#4F9397'
    orange = '#D4674A'
    gold = '#C79756'
    dark = '#3B3A36'
    olive = '#56583B'
    tan = '#DAC6A3'

    palette = {
        Entity.PLAYER: teal,
        Entity.GOAL: gold,
        Entity.KEY: gold,
        Entity.TIMER_RESET: gold,
        Entity.ENEMY: orange,
        Entity.SPIKE: orange,
        Entity.WALL: dark,
        Entity.BLOCK: dark,
        Entity.DOOR: dark,
        Entity.EMPTY: tan,
        Entity.GOAL_REACHED: teal,
        Entity.PLAYER_DIED: orange,
    }
    background = {k: light for k in palette.keys()}
    background[Entity.WALL] = dark
    return create_symbol_map(palette, background=background)


def _symbol_map_icy():
    shades = [
        '#2F363A',
        '#454D55',
        '#6B7F89',
        '#A6B6BC',
    ]

    white = '#FFFFFF'
    pink = '#E1417F'
    yellow = '#EFA00B'
    blue = '#67BADC'
    green = '#99F3A2'

    palette = {
        Entity.PLAYER: blue,
        Entity.GOAL: blue,
        Entity.KEY: blue,
        Entity.TIMER_RESET: blue,
        Entity.ENEMY: yellow,
        Entity.SPIKE: yellow,
        Entity.WALL: shades[1],
        Entity.BLOCK: shades[1],
        Entity.DOOR: shades[1],
        Entity.EMPTY: shades[3],
        Entity.GOAL_REACHED: blue,
        Entity.PLAYER_DIED: yellow,
    }
    background = {k: white for k in palette.keys()}
    background[Entity.WALL] = shades[1]
    return create_symbol_map(palette, background=background)


_SYMBOL_MAPS = {
    '01': _symbol_map_01(),
    '02': _symbol_map_02(),
    '03': _symbol_map_03(),
    'primary': _symbol_map_primary(),
    'desert': _symbol_map_desert(),
    'icy': _symbol_map_icy(),
}


def load_symbol_map(name: str):
    return _SYMBOL_MAPS[name]


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
# TEAL = '#66C2C2'
# PINK = '#EB5197'
# INDIGO = '#325478'
# LIGHT_INDIGO = '#657F9A'
# BLUE = '#00A1FF'
# PURPLE = '#806AD6'
# # YELLOW = '#EEC584'
# YELLOW = '#ECC30B'
# GREEN = '#2B9720'
# ORANGE = '#FC814A'
# WHITE = '#ffffff'
# BLACK = '#000000'
# # DARK_GRAY = '#333333'
# DARK_GRAY = '#787C85'
# # LIGHT_GRAY = '#BFBFBF'
# LIGHT_GRAY = '#E4E4E4'


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

# BACKGROUND_COLOR = WHITE

# COLOR_MAP = {
#     Entity.PLAYER: PURPLE,
#     Entity.GOAL: TEAL,
#     Entity.KEY: TEAL,
#     Entity.TIMER_RESET: TEAL,
#     Entity.ENEMY: PINK,
#     Entity.SPIKE: PINK,
#     Entity.WALL: DARK_GRAY,
#     Entity.BLOCK: DARK_GRAY,
#     Entity.DOOR: DARK_GRAY,
#     Entity.EMPTY: LIGHT_GRAY,
#     Entity.GOAL_REACHED: TEAL,
#     Entity.PLAYER_DIED: PINK,
# }


# class Formatter:
#     def __init__(self, text_visual_map: dict[Entity, Symbol]):
#         self.text_visual_map = text_visual_map

#     def get_entity_plain(self, e: Entity):
#         tv = self.text_visual_map[e]
#         return tv.char

#     def get_entity_fancy(self, e: Entity):
#         tv = self.text_visual_map[e]
#         c = tv.char
#         c = color_background(c, tv.background)
#         c = color_foreground(c, tv.color)
#         if tv.bold:
#             c = make_bold(c)

#         return c

#     def format_plain(self, grid: list[list[Entity]]):
#         text_grid = [[self.get_entity_plain(e) for e in row] for row in grid]
#         return '\n'.join(text_grid)

#     def format_fancy(self, grid: list[list[Entity]]):
#         text_grid = [[self.get_entity_fancy(e) for e in row] for row in grid]
#         return '\n'.join(text_grid)

#     def format_html(self, grid: list[list[Entity]]):
#         pass


# def make_palette_01():
#     white = '#ffffff'
#     teal = '#66C2C2'
#     pink = '#EB5197'
#     indigo = '#325478'
#     purple = '#806AD6'
#     dark_gray = '#787C85'
#     light_gray = '#E4E4E4'

#     return {
#         'background': white,
#         'palette': {
#             Entity.PLAYER: indigo,
#             Entity.GOAL: pink,
#             Entity.KEY: teal,
#             Entity.TIMER_RESET: teal,
#             Entity.ENEMY: purple,
#             Entity.SPIKE: purple,
#             Entity.WALL: dark_gray,
#             Entity.BLOCK: dark_gray,
#             Entity.DOOR: dark_gray,
#             Entity.EMPTY: light_gray,
#             Entity.GOAL_REACHED: pink,
#             Entity.PLAYER_DIED: indigo,
#         },
#     }


# def make_palette_02():
#     white = '#ffffff'
#     teal = '#4090A0'
#     pink = '#DB3EAB'
#     blue = '#4086E4'
#     purple = '#4E40B8'
#     orange = '#EB9047'
#     yellow = '#F1C553'
#     light_gray = '#E4E4E4'

#     return {
#         'background': white,
#         'palette': {
#             Entity.PLAYER: teal,
#             Entity.GOAL: blue,
#             Entity.KEY: orange,
#             Entity.TIMER_RESET: orange,
#             Entity.ENEMY: pink,
#             Entity.SPIKE: pink,
#             Entity.WALL: purple,
#             Entity.BLOCK: purple,
#             Entity.DOOR: purple,
#             Entity.EMPTY: light_gray,
#             Entity.GOAL_REACHED: blue,
#             Entity.PLAYER_DIED: pink,
#         },
#     }


# def make_palette_03():
#     white = '#ffffff'
#     teal = '#308695'
#     red = '#D45769'
#     yellow = '#E69D45'
#     purple = '#574D68'
#     green = '#76C369'
#     light_gray = '#E4E4E4'

#     return {
#         'background': white,
#         'palette': {
#             Entity.PLAYER: teal,
#             Entity.GOAL: yellow,
#             Entity.KEY: yellow,
#             Entity.TIMER_RESET: yellow,
#             Entity.ENEMY: red,
#             Entity.SPIKE: red,
#             Entity.WALL: purple,
#             Entity.BLOCK: purple,
#             Entity.DOOR: purple,
#             Entity.EMPTY: light_gray,
#             Entity.GOAL_REACHED: teal,
#             Entity.PLAYER_DIED: teal,
#         },
#     }


# def make_palette_04():
#     white = '#ffffff'
#     teal = '#44898B'
#     red = '#C64C56'
#     yellow = '#E5A250'
#     purple = '#5F496D'
#     green = '#548D55'
#     blue = '#519FD1'
#     light_gray = '#E4E4E4'

#     return {
#         'background': white,
#         'palette': {
#             Entity.PLAYER: blue,
#             Entity.GOAL: blue,
#             Entity.KEY: yellow,
#             Entity.TIMER_RESET: yellow,
#             Entity.ENEMY: red,
#             Entity.SPIKE: red,
#             Entity.WALL: purple,
#             Entity.BLOCK: purple,
#             Entity.DOOR: purple,
#             Entity.EMPTY: light_gray,
#             Entity.GOAL_REACHED: yellow,
#             Entity.PLAYER_DIED: red,
#         },
#     }


# def make_pretty_terminal_symbol(
#         e: Entity,
#         v: str,
#         palette: dict[Entity, str],
#         background: str | None = None,
# ) -> str:
#     if e != Entity.EMPTY:
#         v = make_bold(v)

#     v = color_foreground(v, palette.get(e))
#     v = color_background(v, background)
#     return v


# def make_pretty_html_symbol(
#         e: Entity,
#         v: str,
#         palette: dict[Entity, str],
#         background: str | None = None,
#         font_size: int = 32,
# ) -> str:
#     style_elements = [
#         "font-family: 'Source Code Pro', monospace",
#         f'font-size: {font_size}px',
#         'line-height: 1.5em',
#         'border: solid #efefef',
#         'border-radius: 0px',
#     ]
#     if background:
#         style_elements.append(f'background: {background}')

#     color = palette.get(e)
#     if color:
#         style_elements.append(f'color: {color}')

#     style = '; '.join(style_elements)
#     """<code style="
#         font-family: 'Source Code Pro', monospace;
#         font-size: 32px;
#         line-height: 1.5em;
#         background: #ffffff;
#         border: solid #efefef;
#         border-radius: 0px;
#         color: {color};
#     ">{content}</code>
#     """
#     return


# def make_pretty_char_map(palette: dict[Entity, str], background: str | None = None):
#     char_map = {}
#     for e, v in CHAR_MAP.items():
#         v = PRETTY_CHAR_REPLACEMENTS.get(e, v)
#         char_map[e] = make_pretty_char(e, v, palette=palette, background=background)

#     return char_map


# PRETTY_CHAR_MAP = make_pretty_char_map(**make_palette_03())


# class Style(StrEnum):
#     PLAIN = 'plain'
#     PRETTY = 'pretty'


# # STYLES = {
# #     Style.PLAIN: CHAR_MAP,
# #     Style.PRETTY: PRETTY_CHAR_MAP,
# # }


# def get_char_map(style: Style):
#     return STYLES[style]


# # class TextGridSymbols:
# #     def __init__(
# #             self,
# #             *,
# #             char_map: dict[Entity, str] | None = None,
# #             color_map: dict[Entity, str] | None = None,
# #     ):
# #         self.char_map = char_map
# #         self.color_map = color_map

# #     def randomize(self):


# # def randomize_char_map(choices: str | None = None):
# #     entities_to_keep = {Entity.EMPTY}
# #     entities_to_replace = {e for e in self.char_map.keys() if e not in entities_to_keep}

# #     if choices is None:
# #         choices = string.ascii_letters + string.digits + string.punctuation

# #     new_char_map = {}
# #     for e in entities_to_keep:
# #         s = self.char_map[e]
# #         new_char_map[e] = s
# #         choices = choices.replace(s, '')

# #     chosen = random.sample(choices, k=len(entities_to_replace))
# #     for e, s in zip(entities_to_replace, chosen):
# #         new_char_map[e] = s

# #     self.char_map = new_char_map


# def format_symbol_plain(tv: Symbol):
#     return tv.plain_char


# def format_symbol_fancy(tv: Symbol):
#     c = tv.fancy_char
#     c = color_background(c, tv.background)
#     c = color_foreground(c, tv.color)
#     if tv.bold:
#         c = make_bold(c)

#     return c


# def format_symbol_html_td(
#         tv: Symbol,
#         font_size: int = 16,
#         font_family: str = "'Source Code Pro', monospace",
#         line_height: str = '1.5em',
#         border: str = 'solid #efefef',
#         border_radius: str = '0px',
# ):
#     style_elements = [
#         f'font-size: {font_size}px',
#         f'font-family: {font_family}',
#         f'line-height: {line_height}',
#         f'border: {border}',
#         f'border-radius: {border_radius}',
#     ]

#     if tv.background:
#         style_elements.append(f'background: {tv.background}')

#     if tv.color:
#         style_elements.append(f'color: {tv.color}')

#     if tv.bold:
#         style_elements.append(f'font-weight: {tv.bold}')

#     style = '; '.join(style_elements)
#     return f'<td style="{style}">{tv.fancy_char}</td>'


# class HTMLFormatter:
#     def __init__(
#             self,
#             tv_map: dict[Entity, Symbol],
#             font_size: int = 16,
#     ):
#         self.tv_map = tv_map
#         self.font_size = font_size

#     def __call__(self, tv: Symbol):
#         style_elements = [
#                 "font-family: 'Source Code Pro', monospace",
#                 f'font-size: {self.font_size}px',
#                 'line-height: 1.5em',
#                 'border: solid #efefef',
#                 'border-radius: 0px',
#             ]
#         if background:
#             style_elements.append(f'background: {background}')

#         color = palette.get(e)
#         if color:
#             style_elements.append(f'color: {color}')

#         style = '; '.join(style_elements)
#         """<code style="
#             font-family: 'Source Code Pro', monospace;
#             font-size: 32px;
#             line-height: 1.5em;
#             background: #ffffff;
#             border: solid #efefef;
#             border-radius: 0px;
#             color: {color};
#         ">{content}</code>
#         """
#         return style

