from enum import StrEnum


class Action(StrEnum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    NONE = 'none'

    @property
    def move_delta(self):
        return _MOVE_DELTA_MAP[self]

    @classmethod
    def _missing_(cls, value):
        value = value.lower()
        value = _ALIASES.get(value, value)
        for member in cls:
            if member == value:
                return member

        raise ValueError(f'unknown value for Action: {repr(value)}')


_ALIASES = {
    'u': 'up',
    'd': 'down',
    'l': 'left',
    'r': 'right',
    'n': 'none',
}

_MOVE_DELTA_MAP = {
    Action.UP: (0, -1),
    Action.DOWN: (0, 1),
    Action.LEFT: (-1, 0),
    Action.RIGHT: (1, 0),
    Action.NONE: (0, 0),
}
