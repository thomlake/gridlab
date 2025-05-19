import dataclasses
import random
import string
from abc import ABC, abstractmethod

from gridlab.component import Identity, KeyCollector, Position, Timer
from gridlab.description import DESCRIPTION_TEMPLATE_MAP
from gridlab.entity import Entity
from gridlab.visuals import Symbol, load_symbol_map
from gridlab.world import World


class View(ABC):
    @abstractmethod
    def __call__(self, world: World) -> str:
        pass


class TextDescription(View):
    def __init__(self, templates: dict[Entity, str] | None = None):
        templates = templates or {}
        self.templates = {**DESCRIPTION_TEMPLATE_MAP, **templates}

    def __call__(self, world: World) -> str:
        width, height = world.grid.width, world.grid.height
        id_map: dict[int, Identity] = world.em.get(Identity)
        pos_map: dict[int, Position] = world.em.get(Position)
        timer_map: dict[int, Timer] = world.em.get(Timer)
        key_collector_map: dict[int, KeyCollector] = world.em.get(KeyCollector)

        lines = []
        lines.append(f'The grid is {width} tiles wide and {height} tiles high.')

        if timer_map:
            (_, timer), = timer_map.items()
            lines.append(f'You have {timer.remain} moves remaining.')

        if key_collector_map:
            (_, key_collector), = key_collector_map.items()
            lines.append(f'You have {key_collector.count} keys.')

        for e, id in id_map.items():
            template = self.templates.get(id.type)
            if template:
                line = template.format(pos=pos_map.get(e))
                lines.append(line)

        value = '\n'.join(lines)
        return value


class TextGrid(View):
    symbol_map: dict[Entity, Symbol] | None = None

    def __init__(
            self,
            *,
            symbols: str | None = 'desert',
            symbol_map: dict[Entity, Symbol] | None = None,
    ):
        _symbol_map: dict[Entity, Symbol] = {}
        if symbols:
            _symbol_map.update(load_symbol_map(symbols))

        if symbol_map:
            _symbol_map.update(symbol_map)

        self.symbol_map = _symbol_map

    def randomize_symbols(
            self,
            choices: str | None = None,
            keep: list[Entity] | None = None,
    ):
        if choices is None:
            choices = string.ascii_letters + string.digits + string.punctuation

        if keep is None:
            keep = {Entity.EMPTY}

        replace = {e for e in self.symbol_map.keys() if e not in keep}

        symbol_map = {}
        for e in keep:
            v = self.symbol_map[e]
            symbol_map[e] = v
            choices = choices.replace(v.plain_char, '')

        chosen = random.sample(choices, k=len(replace))
        for e, char in zip(replace, chosen):
            symbol_map[e] = dataclasses.replace(
                self.symbol_map[e],
                plain_char=char,
                fancy_char=char,
            )

        self.symbol_map = symbol_map

    def legend_items(self, world: World) -> list[tuple[Entity, Symbol]]:
        id_map: dict[int, Identity] = world.em.get(Identity)
        entities = set()
        for v in id_map.values():
            entities.add(v.type)

        return [(e, self.symbol_map[e]) for e in entities]

    def format_legend_plain(self, world: World) -> str:
        legend = self.legend_items(world)
        return '\n'.join(f'- {s.plain()}: {str(e)}' for e, s in legend)

    def format_legend_fancy(self, world: World) -> str:
        legend = self.legend_items(world)
        return '\n'.join(f'- {s.fancy()}: {str(e)}' for e, s in legend)

    def format_legend_html(self, world: World) -> str:
        legend = self.legend_items(world)
        items = '\n'.join(f'<li>{s.html_span()}: {str(e)}</li>' for e, s in legend)
        return f'<ul>\n{items}\n</ul>'

    def get_status_items(self, world: World, ent: int | None = None) -> list[tuple[str, str]]:
        if ent is None:
            ent = world.player

        status_items = []

        timer_map: dict[int, Timer] = world.em.get(Timer)
        timer = timer_map.get(ent)
        if timer:
            status_items.append(('Moves', str(timer.remain)))

        key_collector_map: dict[int, KeyCollector] = world.em.get(KeyCollector)
        key_collector = key_collector_map.get(ent)
        if key_collector:
            status_items.append(('Keys', str(key_collector.count)))

        return status_items

    def format_status(self, world: World, ent: int | None = None) -> str:
        status_items = self.get_status_items(world, ent=ent)
        return '\n'.join(f'- {k}: {v}' for k, v in status_items)

    def _build_symbol_grid(self, world: World) -> list[list[Symbol]]:
        width, height = world.grid.width, world.grid.height
        id_map: dict[int, Identity] = world.em.get(Identity)
        pos_map: dict[int, Position] = world.em.get(Position)
        empty = self.symbol_map[Entity.EMPTY]
        symbol_grid = [[empty for _ in range(width)] for _ in range(height)]
        for e, id in id_map.items():
            pos = pos_map.get(e)
            if pos:
                symbol_grid[pos.y][pos.x] = self.symbol_map[id.type]

        return symbol_grid

    def format_grid(self, world: World, style: str = 'plain'):
        symbol_grid = self._build_symbol_grid(world)
        if style == 'plain':
            return '\n'.join(''.join(s.plain() for s in row) for row in symbol_grid)
        elif style == 'fancy':
            return '\n'.join(''.join(s.fancy() for s in row) for row in symbol_grid)
        elif style == 'html_table':
            table = [''.join(s.html_table_cell() for s in row) for row in symbol_grid]
            table = '\n'.join(f'<tr>{row}</tr>' for row in table)
            return table
        else:
            raise ValueError(f'unknown style {style}')

    def __call__(self, world: World) -> str:
        elements = [
            '## Legend', self.format_legend(world),
            '## Status', self.format_status(world),
            f'## Turn {world.turn}', self.format_grid(world),
        ]
        return '\n\n'.join(e for e in elements if e)


def create_entity_grid(world: World) -> list[list[Symbol]]:
    width, height = world.grid.width, world.grid.height
    id_map: dict[int, Identity] = world.em.get(Identity)
    pos_map: dict[int, Position] = world.em.get(Position)
    grid = [[Entity.EMPTY for _ in range(width)] for _ in range(height)]
    for e, id in id_map.items():
        pos = pos_map.get(e)
        if pos:
            grid[pos.y][pos.x] = id.type

    return grid


def create_html_table_cell(
        symbol: Symbol,
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

    if symbol.background:
        style_elements.append(f'background: {symbol.background}')

    if symbol.color:
        style_elements.append(f'color: {symbol.color}')

    if symbol.bold:
        style_elements.append('font-weight: bold')

    style = '; '.join(style_elements)
    return f'<td align="center" style="{style}">{symbol.fancy_char}</td>'


def format_html_table(world: World, symbol_map: dict[str, Symbol], **kwargs):
    entity_grid = create_entity_grid(world)
    symbol_grid = [[symbol_map[e] for e in row] for row in entity_grid]
    cell_grid = [[create_html_table_cell(s) for s in row] for row in symbol_grid]
    content = '\n'.join(f'<tr>{"".join(row)}</tr>' for row in cell_grid)
    return f'<table>\n{content}\n</table>'


def create_html_span(
        symbol,
        font_size: int = 16,
        font_family: str = "'Source Code Pro', monospace",
        line_height: str = '1.25em',
):
    style_elements = [
        f'font-size: {font_size}px',
        f'font-family: {font_family}',
        f'line-height: {line_height}',
    ]

    if symbol.background:
        style_elements.append(f'background: {symbol.background}')

    if symbol.color:
        style_elements.append(f'color: {symbol.color}')

    if symbol.bold:
        style_elements.append('font-weight: bold')

    style = '; '.join(style_elements)
    return f'<span style="{style}">{symbol.fancy_char}</span>'


def format_html_pre(
        world: World,
        symbol_map: dict[str, Symbol],
        line_height: str = '1.25em',
        **kwargs,
):
    def f(s):
        return create_html_span(s, line_height=line_height, **kwargs)

    entity_grid = create_entity_grid(world)
    symbol_grid = [[symbol_map[e] for e in row] for row in entity_grid]
    span_grid = [[f(s) for s in row] for row in symbol_grid]
    content = '\n'.join(''.join(row) for row in span_grid)

    style = f'line-height: {line_height}'
    return f'<pre style="{style}">\n{content}\n</pre>'



# def text_description(
#         world: World,
#         templates: dict[Entity, str] | None = None,
#         indent: str = ''
# ):
#     templates = templates or {}
#     templates = {**DESCRIPTION_TEMPLATE_MAP, **templates}

#     width, height = world.grid.width, world.grid.height
#     id_map: dict[int, Identity] = world.em.get(Identity)
#     pos_map: dict[int, Position] = world.em.get(Position)
#     timer_map: dict[int, Timer] = world.em.get(Timer)
#     key_collector_map: dict[int, KeyCollector] = world.em.get(KeyCollector)

#     lines = []
#     lines.append(f'The grid is {width} tiles wide and {height} tiles high.')

#     if timer_map:
#         (_, timer), = timer_map.items()
#         lines.append(f'You have {timer.remain} moves remaining.')

#     if key_collector_map:
#         (_, key_collector), = key_collector_map.items()
#         lines.append(f'You have {key_collector.count} keys.')

#     for e, id in id_map.items():
#         template = templates.get(id.type)
#         if template:
#             line = template.format(pos=pos_map.get(e))
#             lines.append(line)

#     value = '\n'.join(f'{indent}{line}' for line in lines)
#     return value
