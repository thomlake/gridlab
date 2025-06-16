import dataclasses
import itertools
from enum import StrEnum
from typing import Type, TypeVar


class Entity(StrEnum):
    PLAYER = 'player'
    GOAL = 'goal'
    KEY = 'key'
    TIMER_RESET = 'timer_reset'
    SWITCH_PRESSABLE = 'switch_pressable'
    SWITCH_UNPRESSABLE = 'switch_unpressable'
    # PATROL_ENEMY = 'patrol_enemy'
    # CHASE_ENEMY = 'chase_enemy'
    # MIRROR_ENEMY = 'mirror_enemy'
    # SNAKE_ENEMY = 'snake_enemy'
    ENEMY = 'enemy'
    SPIKE = 'spike'
    BLOCK = 'block'
    DOOR = 'door'
    WALL = 'wall'
    FOG = 'fog'
    EMPTY = 'empty'
    GOAL_REACHED = 'goal_reached'
    PLAYER_DIED = 'player_died'


C = TypeVar('C')


class EntityManager:
    def __init__(self):
        self._next_ent = itertools.count()
        self._components = {}  # map component -> {entity_id: component}

    def create(self):
        return next(self._next_ent)

    def get(self, cls: Type[C]) -> dict[int, C]:
        return self._components.get(cls, {})

    def remove(self, ent: int):
        for component_map in self._components.values():
            component_map.pop(ent, None)

    def remove_all(self, entities: list[int]):
        entities = list(entities)
        for ent in entities:
            self.remove(ent)

    def add_component(self, ent: int, component):
        self._components.setdefault(type(component), {})[ent] = component

    def remove_component(self, ent: int, component):
        if not isinstance(component, type):
            component = type(component)

        self._components[component].pop(ent)

    def get_frozen_state(self):
        data = []
        for component_type, component_map in self._components.items():
            name = component_type.__name__
            fields = dataclasses.fields(component_type)
            component_data = []
            for ent, comp in component_map.items():
                if fields:
                    field_values = tuple(getattr(comp, f.name) for f in fields)
                    component_data.append((ent, field_values))
                else:
                    component_data.append((ent,))

            data.append((name, *component_data))

        return tuple(data)
