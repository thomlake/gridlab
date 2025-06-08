from dataclasses import dataclass, field
from typing import Callable


@dataclass
class State:
    _player_dead: bool = False
    _goal_reached: bool = False
    _terminated: bool = False

    player_dead_callbacks: list[Callable[[], None]] = field(default_factory=list)
    goal_reached_callbacks: list[Callable[[], None]] = field(default_factory=list)

    @property
    def player_dead(self):
        return self._player_dead

    @player_dead.setter
    def player_dead(self, value: bool):
        self._player_dead = value
        if self._player_dead:
            for callback in self.player_dead_callbacks:
                callback()

    @property
    def goal_reached(self):
        return self._goal_reached

    @goal_reached.setter
    def goal_reached(self, value: bool):
        self._goal_reached = value
        if self._goal_reached:
            for callback in self.goal_reached_callbacks:
                callback()

    @property
    def terminated(self):
        return self._terminated

    @terminated.setter
    def terminated(self, value: bool):
        self._terminated = value

    @property
    def is_finished(self):
        return self.player_dead or self.goal_reached or self.terminated


# class EventManager:
#     events: dict[tuple[str, int], list[Callable[[tuple[str, int]], None]]] = None
#     invoked: dict[tuple[str, int], bool]

#     def add_callback(
#             self,
#             name: str,
#             entity: int,
#             callback: Callable[[int], None],
#     ):
#         self.events = self.events or {}
#         self.events[name, entity].append(callback)

#     def invoke(self, name: str, entity: int):
#         event_id = name, entity
#         callbacks = self.events.get(event_id, [])
#         for callback in callbacks:
#             callback(entity)

#         self.invoked[event_id] = True
