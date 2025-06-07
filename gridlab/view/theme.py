import random
import string
from dataclasses import dataclass, replace
from typing import Type

from gridlab.entity import Entity

ASCII_MAP = {
    Entity.PLAYER: '@',
    Entity.GOAL: 'X',
    Entity.KEY: 'K',
    Entity.TIMER_RESET: 'T',
    Entity.SWITCH_PRESSABLE: '=',
    Entity.SWITCH_UNPRESSABLE: '-',
    Entity.FOG: '~',
    Entity.ENEMY: 'e',
    Entity.SPIKE: '^',
    Entity.WALL: '#',
    Entity.BLOCK: '0',
    Entity.DOOR: '+',
    Entity.EMPTY: '.',
    Entity.GOAL_REACHED: '*',
    Entity.PLAYER_DIED: '_',
}

FANCY_MAP = {
    **ASCII_MAP,
    Entity.SWITCH_PRESSABLE: '●',
    Entity.SWITCH_UNPRESSABLE: '○',
    Entity.FOG: '≈',
    Entity.SPIKE: '▴',
    Entity.WALL: '█',
    Entity.BLOCK: '■',
    Entity.DOOR: '⊞',
}


@dataclass
class Symbol:
    char: str
    color: str | None = None
    background: str | None = None
    bold: bool = False


class StyleMeta(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        if not dct.get('_is_base', False):
            key = getattr(cls, '_theme_name', name.lower())
            THEME_REGISTRY[key] = cls


class Theme(metaclass=StyleMeta):
    _is_base = True

    def __init__(self, symbols: dict[Entity, Symbol]):
        self.symbols = symbols

    def randomize_symbols(
            self,
            choices: str | None = None,
            keep: list[Entity] | None = None,
    ):
        if choices is None:
            choices = string.ascii_letters + string.digits + string.punctuation

        if keep is None:
            keep = {Entity.EMPTY}

        entities = {e for e in self.symbols.keys() if e not in keep}

        symbols = {}
        for e in keep:
            v = self.symbols[e]
            symbols[e] = v
            choices = choices.replace(v.char, '')

        chosen = random.sample(choices, k=len(entities))
        for e, char in zip(entities, chosen):
            symbols[e] = replace(self.symbols[e], char=char)

        self.symbols = symbols

    def css_rules(self):
        rules = []

        for entity, symbol in self.symbols.items():
            style_dict = {}
            if symbol.background:
                style_dict['background'] = symbol.background

            if symbol.color:
                style_dict['color'] = symbol.color

            if symbol.bold:
                style_dict['font-weight'] = 'bold'

            props = '\n'.join(f'  {k}: {v};' for k, v in style_dict.items())
            css_class = f'.{entity} {{\n{props}\n}}'
            rules.append(css_class)

        return rules

    def css(self):
        return '\n\n'.join(self.css_rules())


THEME_REGISTRY: dict[str, Type[Theme]] = {}


def load_theme(name: str):
    cls = THEME_REGISTRY.get(name)
    if not cls:
        raise ValueError(f'unknown style "{name}"')

    return cls()


def theme_names():
    return list(THEME_REGISTRY.keys())


class ASCII(Theme):
    def __init__(self):
        super().__init__({e: Symbol(char=c) for e, c in ASCII_MAP.items()})


class Fancy(Theme):
    def __init__(self):
        super().__init__({e: Symbol(char=c) for e, c in FANCY_MAP.items()})


class Desert(Theme):
    def __init__(self):
        orange = '#DF6453'
        teal = '#2599A3'
        yellow = '#D9AB57'
        browns = [
            '#4C453C',
            '#B0A193',
            '#DAD1C1',
            '#F3E6D9',
        ]

        color_map = {
            Entity.PLAYER: orange,
            Entity.GOAL: teal,
            Entity.KEY: yellow,
            Entity.TIMER_RESET: yellow,
            Entity.SWITCH_PRESSABLE: yellow,
            Entity.SWITCH_UNPRESSABLE: browns[1],
            Entity.FOG: browns[1],
            Entity.ENEMY: browns[0],
            Entity.WALL: browns[1],
            Entity.SPIKE: browns[0],
            Entity.BLOCK: browns[1],
            Entity.DOOR: browns[1],
            Entity.EMPTY: browns[2],
            Entity.GOAL_REACHED: orange,
            Entity.PLAYER_DIED: orange,
        }
        background_map = {k: browns[3] for k in color_map.keys()}
        background_map[Entity.WALL] = browns[1]

        def create_symbol(e: Entity):
            return Symbol(
                char=FANCY_MAP[e],
                color=color_map[e],
                background=background_map[e],
                bold=e != Entity.EMPTY,
            )

        super().__init__({e: create_symbol(e) for e in ASCII_MAP.keys()})


class Purple(Theme):
    def __init__(self):
        ramp = [
            '#F8F1ED',
            '#E9CFCA',
            '#DAAEB2',
            '#C58D9F',
            '#AA6F90',
            '#89557F',
            '#633E68',
            '#3D294B',
        ]
        color_map = {
            Entity.PLAYER: ramp[3],
            Entity.GOAL: ramp[3],
            Entity.KEY: ramp[3],
            Entity.TIMER_RESET: ramp[3],
            Entity.SWITCH_PRESSABLE: ramp[3],
            Entity.SWITCH_UNPRESSABLE: ramp[1],
            Entity.FOG: ramp[1],
            Entity.ENEMY: ramp[5],
            Entity.SPIKE: ramp[5],
            Entity.WALL: ramp[7],
            Entity.BLOCK: ramp[7],
            Entity.DOOR: ramp[7],
            Entity.EMPTY: ramp[1],
            Entity.GOAL_REACHED: ramp[3],
            Entity.PLAYER_DIED: ramp[5],
        }
        background_map = {k: ramp[0] for k in color_map.keys()}
        background_map[Entity.WALL] = ramp[7]

        def create_symbol(e: Entity):
            return Symbol(
                char=FANCY_MAP[e],
                color=color_map[e],
                background=background_map[e],
                bold=e != Entity.EMPTY,
            )

        super().__init__({e: create_symbol(e) for e in ASCII_MAP.keys()})


class Vaporwave(Theme):
    def __init__(self):
        teal = '#68CFD9'
        pink = '#EA7DB9'
        # orange = '#F5BB8B'
        # orange = "#F4AD73"
        orange = '#F39237'
        light_purple = '#DBB3DA'
        dark_purple = '#9878C9'
        cream = '#FAEEE6'

        color_map = {
            Entity.PLAYER: pink,
            Entity.GOAL: teal,
            Entity.KEY: teal,
            Entity.TIMER_RESET: teal,
            Entity.SWITCH_PRESSABLE: pink,
            Entity.SWITCH_UNPRESSABLE: light_purple,
            Entity.FOG: light_purple,
            Entity.ENEMY: orange,
            Entity.SPIKE: orange,
            Entity.WALL: dark_purple,
            Entity.BLOCK: dark_purple,
            Entity.DOOR: dark_purple,
            Entity.EMPTY: light_purple,
            Entity.GOAL_REACHED: pink,
            Entity.PLAYER_DIED: orange,
        }
        background_map = {k: cream for k in color_map.keys()}

        def create_symbol(e: Entity):
            return Symbol(
                char=FANCY_MAP[e],
                color=color_map[e],
                background=background_map[e],
                bold=e != Entity.EMPTY,
            )

        super().__init__({e: create_symbol(e) for e in ASCII_MAP.keys()})


class Natural(Theme):
    def __init__(self):
        light = '#F4EFE3'
        teal = '#4F9397'
        orange = '#D4674A'
        gold = '#C79756'
        dark = '#3B3A36'
        # olive = '#56583B'
        tan = '#DAC6A3'

        color_map = {
            Entity.PLAYER: teal,
            Entity.GOAL: gold,
            Entity.KEY: gold,
            Entity.TIMER_RESET: gold,
            Entity.SWITCH_PRESSABLE: gold,
            Entity.SWITCH_UNPRESSABLE: dark,
            Entity.FOG: dark,
            Entity.ENEMY: orange,
            Entity.SPIKE: orange,
            Entity.WALL: dark,
            Entity.BLOCK: dark,
            Entity.DOOR: dark,
            Entity.EMPTY: tan,
            Entity.GOAL_REACHED: teal,
            Entity.PLAYER_DIED: orange,
        }
        background_map = {k: light for k in color_map.keys()}
        background_map[Entity.WALL] = dark

        def create_symbol(e: Entity):
            return Symbol(
                char=FANCY_MAP[e],
                color=color_map[e],
                background=background_map[e],
                bold=e != Entity.EMPTY,
            )

        super().__init__({e: create_symbol(e) for e in ASCII_MAP.keys()})


class Icy(Theme):
    def __init__(self):
        shades = [
            '#2F363A',
            '#454D55',
            '#6B7F89',
            '#A6B6BC',
        ]

        white = '#FFFFFF'
        # pink = '#E1417F'
        yellow = '#EFA00B'
        blue = '#67BADC'
        # green = '#99F3A2'

        color_map = {
            Entity.PLAYER: blue,
            Entity.GOAL: blue,
            Entity.KEY: blue,
            Entity.TIMER_RESET: blue,
            Entity.SWITCH_PRESSABLE: blue,
            Entity.SWITCH_UNPRESSABLE: shades[3],
            Entity.FOG: shades[3],
            Entity.ENEMY: yellow,
            Entity.SPIKE: yellow,
            Entity.WALL: shades[1],
            Entity.BLOCK: shades[1],
            Entity.DOOR: shades[1],
            Entity.EMPTY: shades[3],
            Entity.GOAL_REACHED: blue,
            Entity.PLAYER_DIED: yellow,
        }
        background_map = {k: white for k in color_map.keys()}
        background_map[Entity.WALL] = shades[1]

        def create_symbol(e: Entity):
            return Symbol(
                char=FANCY_MAP[e],
                color=color_map[e],
                background=background_map[e],
                bold=e != Entity.EMPTY,
            )

        super().__init__({e: create_symbol(e) for e in ASCII_MAP.keys()})


class ARC(Theme):
    def __init__(self):
        teal = '#46B3C7'
        pink = '#E545A8'
        yellow = '#F9DD4A'
        dark = '#191919'
        medium = '#3E3E3E'
        light = '#707070'

        color_map = {
            Entity.PLAYER: pink,
            Entity.GOAL: teal,
            Entity.KEY: teal,
            Entity.TIMER_RESET: teal,
            Entity.SWITCH_PRESSABLE: teal,
            Entity.SWITCH_UNPRESSABLE: light,
            Entity.FOG: light,
            Entity.ENEMY: yellow,
            Entity.SPIKE: yellow,
            Entity.WALL: dark,
            Entity.BLOCK: dark,
            Entity.DOOR: dark,
            Entity.EMPTY: medium,
            Entity.GOAL_REACHED: pink,
            Entity.PLAYER_DIED: pink,
        }
        background_map = {k: dark for k in color_map.keys()}
        background_map[Entity.BLOCK] = light
        background_map[Entity.DOOR] = light
        background_map[Entity.WALL] = light

        def create_symbol(e: Entity):
            return Symbol(
                char=ASCII_MAP[e],
                color=color_map[e],
                background=background_map[e],
                bold=e != Entity.EMPTY,
            )

        super().__init__({e: create_symbol(e) for e in ASCII_MAP.keys()})
