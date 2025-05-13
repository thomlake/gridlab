from dataclasses import dataclass, field

from gridlab.entity import Entity


@dataclass
class Identity:
    """Entity identity (player, enemy, wall, etc)."""
    type: Entity


@dataclass
class Position:
    """Position of an entity in the grid."""
    x: int
    y: int

    def neighbors(self):
        x, y = self.x, self.y
        return [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]

    def is_adjacent(self, other: 'Position'):
        pos = other.x, other.y
        return pos in self.neighbors()


@dataclass
class MovementRequest:
    x: int
    y: int


@dataclass
class PositionDelta:
    """Most recent change in a entity's position (cleared before the MovementSystem executes)."""
    x: int
    y: int


@dataclass
class Goal:
    """Entity that when reached triggers successful completion."""
    pass


@dataclass
class Door:
    """Entity that cannot be passed through without a key."""
    pass


@dataclass
class Key:
    """Entity that can be picked up and later used to unlock a door."""
    pass


@dataclass
class KeyCollector:
    """Entity that can pickup keys."""
    count: int = 0


@dataclass
class Solid:
    """Entity cannot be overlapped or moved through."""
    allow: set[int] = field(default_factory=set)


@dataclass
class Pusher:
    """Entity can push a pushable."""
    pass


@dataclass
class Pushable:
    """Entity can be pushed if the destination is free."""
    max_pushes: int | None = None


@dataclass
class Deadly:
    """Entity will kill the player on contact."""
    pass


@dataclass
class ChaseAI:
    """Entity that moves toward the target."""
    target: int


@dataclass
class MirrorAI:
    """Entity that copies a target entity's movement on x-axis and mirrors on the y-axis."""
    target: int


@dataclass
class PatrolAI:
    """Entity that moves along a fixed path."""
    moves: list[tuple[int, int]]
    move_index: int = 0


@dataclass
class Timer:
    """Time limit for game."""
    limit: int
    tick: int = 0

    @property
    def remain(self):
        return self.limit - self.tick


@dataclass
class TimerReset:
    """Reset the game timer."""
    pass
