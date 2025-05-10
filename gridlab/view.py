import random
import string
from abc import ABC, abstractmethod

from gridlab.component import Identity, KeyCollector, Position, Timer
from gridlab.description import ENTITY_DESCRIPTION_TEMPLATE_MAP
from gridlab.entity import Entity, EntityManager
from gridlab.visuals import ENTITY_ASCII_MAP, ENTITY_RICH_ASCII_MAP
from gridlab.grid import Grid
from gridlab.interface import Observer


class ViewSystem(ABC):
    em: EntityManager
    grid: Grid
    observer: Observer

    def initialize(self, em: EntityManager, grid: Grid, observer: Observer):
        self.em = em
        self.grid = grid
        self.observer = observer

    @abstractmethod
    def __call__(self) -> str:
        pass


class DescriptionSystem(ViewSystem):
    def __call__(self) -> str:
        id_map: dict[int, Identity] = self.em.get(Identity)
        pos_map: dict[int, Position] = self.em.get(Position)
        timer_map: dict[int, Timer] = self.em.get(Timer)
        key_collector_map: dict[int, KeyCollector] = self.em.get(KeyCollector)
        width, height = self.grid.width, self.grid.height

        lines = []
        lines.append(f'The grid is {width} tiles wide and {height} tiles high.')

        if timer_map:
            (_, timer), = timer_map.items()
            lines.append(f'You have {timer.remain} moves remaining.')

        if key_collector_map:
            (_, key_collector), = key_collector_map.items()
            lines.append(f'You have {key_collector.count} keys.')

        for e, id in id_map.items():
            template = ENTITY_DESCRIPTION_TEMPLATE_MAP.get(id.type)
            if template:
                line = template.format(pos=pos_map.get(e))
                lines.append(line)

        value = '\n'.join(lines)
        self.observer.observe(value)


BORDER_MAP = {}
BORDER_MAP['blank'] = [
    '   ',
    '  ',
    '   ',
]
BORDER_MAP['simple'] = [
    ' ⎽ ',
    '||',
    ' ⎺ ',
]


def add_boarder(grid: list[list[str]], style='blank'):
    t, m, b = BORDER_MAP[style]
    top = [t[0], *(len(grid[0])*t[1]), t[2]]
    bottom = [b[0], *(len(grid[-1])*b[1]), b[2]]
    grid = [[m[0], *row, m[1]] for row in grid]
    return [top] + grid + [bottom]


class ASCIIRenderSystem(ViewSystem):
    char_map: dict[Entity, str] = ENTITY_ASCII_MAP

    def randomize_char_map(self):
        entities_to_keep = {Entity.EMPTY}
        entities_to_replace = {e for e in self.char_map.keys() if e not in entities_to_keep}

        choices = string.ascii_letters + string.digits + string.punctuation
        new_char_map = {}
        for e in entities_to_keep:
            s = self.char_map[e]
            new_char_map[e] = s
            choices = choices.replace(s, '')

        chosen = random.sample(choices, k=len(entities_to_replace))
        for e, s in zip(entities_to_replace, chosen):
            new_char_map[e] = s

        self.char_map = new_char_map

    def layout_grid(self) -> list[list[str]]:
        id_map: dict[int, Identity] = self.em.get(Identity)
        pos_map: dict[int, Position] = self.em.get(Position)
        width, height = self.grid.width, self.grid.height
        empty = self.char_map[Entity.EMPTY]
        grid = [[empty for _ in range(width)] for _ in range(height)]
        for e, id in id_map.items():
            pos = pos_map.get(e)
            if not pos:
                continue

            grid[pos.y][pos.x] = self.char_map[id.type]

        value = '\n'.join(''.join(row) for row in grid)
        return value

    def layout_status(self):
        statuses = []

        timer_map: dict[int, Timer] = self.em.get(Timer)
        if timer_map:
            (_, timer), = timer_map.items()
            remain = f'Moves: {timer.remain}'
            statuses.append(remain)

        key_collector_map: dict[int, KeyCollector] = self.em.get(KeyCollector)
        if key_collector_map:
            (_, key_collector), = key_collector_map.items()
            statuses.append(f'Keys: {key_collector.count}')

        return '\n'.join(statuses)

    def __call__(self) -> str:
        status = self.layout_status()
        grid = self.layout_grid()
        if status:
            value = f'{status}\n{grid}'
        else:
            value = grid

        self.observer.observe(value)


class ASCIIRichRenderSystem(ASCIIRenderSystem):
    char_map = ENTITY_RICH_ASCII_MAP
