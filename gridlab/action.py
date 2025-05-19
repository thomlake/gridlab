from enum import StrEnum


class Action(StrEnum):
    UP = 'u'
    DOWN = 'd'
    LEFT = 'l'
    RIGHT = 'r'

    @property
    def move_delta(self):
        return MOVE_DELTA_MAP[self]


MOVE_DELTA_MAP = {
    Action.UP: (0, -1),
    Action.DOWN: (0, 1),
    Action.LEFT: (-1, 0),
    Action.RIGHT: (1, 0),
}
