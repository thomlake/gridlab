from abc import ABC, abstractmethod
from enum import StrEnum

from gridlab.request import MovementRequest


ACTION_NAME_MAP = {
    'u': 'up',
    'd': 'down',
    'l': 'left',
    'r': 'right',
    'q': 'quit',
}

ACTION_ALIAS_MAP = {v: k for k, v in ACTION_NAME_MAP.items()}


class Action(StrEnum):
    UP = 'u'
    DOWN = 'd'
    LEFT = 'l'
    RIGHT = 'r'

    @property
    def movement_request(self):
        return {
            Action.UP: MovementRequest(0, -1),
            Action.DOWN: MovementRequest(0, 1),
            Action.LEFT: MovementRequest(-1, 0),
            Action.RIGHT: MovementRequest(1, 0),
        }[self]


class Observer(ABC):
    @abstractmethod
    def observe(self, value: str):
        pass


class CompositeObserver(Observer):
    def __init__(self, observers: list[Observer]):
        self.observers = observers

    def observe(self, value: str):
        for observer in self.observers:
            observer.observe(value)


class TerminalObserver(Observer):
    def __init__(self, pad_left: int = 0):
        self.pad_left = pad_left

    def observe(self, value: str):
        if self.pad_left:
            value = '\n'.join(self.pad_left * ' ' + line for line in value.split('\n'))

        print(value)


class FileObserver(Observer):
    def __init__(self, file):
        self.file = file

    def observe(self, value: str):
        print(value, file=self.file)


class Actor(ABC):
    @abstractmethod
    def get_action(self) -> MovementRequest | None:
        pass


class TerminalActor(Actor):
    def get_action(self) -> MovementRequest | None:
        while True:
            cmd = input("Enter action (up/down/left/right) or 'quit': ").strip().lower()
            cmd = ACTION_ALIAS_MAP.get(cmd, cmd)
            if cmd == 'q':
                return None

            if cmd not in [a.value for a in Action]:
                print("Invalid action. Try again.")
                continue

            print()
            action = Action(cmd)
            return action.movement_request
