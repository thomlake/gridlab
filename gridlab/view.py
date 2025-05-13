import random
import string
from abc import ABC, abstractmethod

from gridlab.component import Identity, KeyCollector, Position, Timer
from gridlab.description import DESCRIPTION_TEMPLATE_MAP
from gridlab.entity import Entity
from gridlab.visuals import Style, get_char_map
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
    def __init__(
            self,
            *,
            style: Style = Style.PRETTY,
            char_map: dict[Entity, str] | None = None,
    ):
        base_char_map = dict(get_char_map(style=style))
        char_map = char_map or {}
        self.char_map = {**base_char_map, **char_map}

    def randomize_char_map(self, choices: str | None = None):
        entities_to_keep = {Entity.EMPTY}
        entities_to_replace = {e for e in self.char_map.keys() if e not in entities_to_keep}

        if choices is None:
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

    def create_legend(self, world: World) -> str:
        id_map: dict[int, Identity] = world.em.get(Identity)
        entity_types = set()
        for v in id_map.values():
            entity_types.add(v.type)

        return '\n'.join(f'- {self.char_map[t]}: {str(t)}' for t in entity_types)

    def create_status(self, world: World) -> str:
        statuses = []

        timer_map: dict[int, Timer] = world.em.get(Timer)
        if timer_map:
            (_, timer), = timer_map.items()
            remain = f'Moves: {timer.remain}'
            statuses.append(remain)

        key_collector_map: dict[int, KeyCollector] = world.em.get(KeyCollector)
        if key_collector_map:
            (_, key_collector), = key_collector_map.items()
            statuses.append(f'Keys: {key_collector.count}')

        return '\n'.join(statuses)

    def create_grid(self, world: World) -> list[list[str]]:
        width, height = world.grid.width, world.grid.height
        id_map: dict[int, Identity] = world.em.get(Identity)
        pos_map: dict[int, Position] = world.em.get(Position)
        empty = self.char_map[Entity.EMPTY]
        grid = [[empty for _ in range(width)] for _ in range(height)]
        for e, id in id_map.items():
            pos = pos_map.get(e)
            if pos:
                grid[pos.y][pos.x] = self.char_map[id.type]

        value = '\n'.join(''.join(row) for row in grid)
        return value

    def __call__(self, world: World) -> str:
        elements = [
            self.create_legend(world),
            self.create_status(world),
            self.create_grid(world),
        ]
        return '\n\n'.join(e for e in elements if e)


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
