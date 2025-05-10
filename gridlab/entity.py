import itertools
from enum import StrEnum


class EntityManager:
    def __init__(self):
        self._next_ent = itertools.count()
        self._components = {}  # map component -> {entity_id: component}

    def create(self):
        return next(self._next_ent)

    def get(self, cls: type):
        return self._components.get(cls, {})

    def remove(self, ent):
        for component_map in self._components.values():
            component_map.pop(ent, None)

    def remove_all(self, entities):
        for ent in entities:
            self.remove(ent)

    def add_component(self, ent, component):
        self._components.setdefault(type(component), {})[ent] = component

    def remove_component(self, ent, component):
        self._components[type(component)].pop(ent)


class Entity(StrEnum):
    PLAYER: str = 'player'
    GOAL: str = 'goal'
    KEY: str = 'key'
    TIMER_RESET: str = 'timer_reset'
    ENEMY: str = 'enemy'
    SPIKE: str = 'spike'
    WALL: str = 'wall'
    BLOCK: str = 'block'
    DOOR: str = 'door'
    EMPTY: str = 'empty'
    GOAL_REACHED: str = 'goal_reached'
    PLAYER_DIED: str = 'player_died'
