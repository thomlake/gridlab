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


ENTITY_DESCRIPTION = {
    Entity.PLAYER: 'The player (you)',
    Entity.GOAL: 'Successfully complete the level by occupying this tile',
    Entity.KEY: 'Used to unlock doors',
    Entity.TIMER_RESET: 'Resets the move countdown',
    Entity.SWITCH_PRESSABLE: 'Causes an environmental change when pressed',
    Entity.SWITCH_UNPRESSABLE: 'An inactive switch.',
    # Entity.PATROL_ENEMY: 'Moves in a linear path until impeded, and then moves in the opposite direction',
    # Entity.CHASE_ENEMY: 'Moves toward the player at each step using the A* algorithm to avoid obstacles',
    # Entity.MIRROR_ENEMY: 'Copies or mirrors the player movement along each axis',
    Entity.ENEMY: 'Moves around the environment and kills the player if they occupy the same tile',
    Entity.SPIKE: 'Kills the player if they move onto the tile, but does not block the movement of other entities',
    Entity.BLOCK: 'Cannot be moved through by any entity, but can be pushed by the player if the path is clear',
    Entity.DOOR: 'Cannot be moved through until it is unlocked by an entity with a key',
    Entity.WALL: 'Cannot be moved through by any entity',
    Entity.FOG: 'Hides entities at this location',
    Entity.EMPTY: 'An empty tile',
    Entity.GOAL_REACHED: 'Signifies the player reached the goal',
    Entity.PLAYER_DIED: 'Signifies the player died',
}


def describe_entity(entity: Entity):
    return ENTITY_DESCRIPTION[entity]


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
