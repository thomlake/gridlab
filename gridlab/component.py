from dataclasses import dataclass, field

from gridlab.entity import Entity
from gridlab.utils import grid_neighbors


@dataclass
class Identity:
    """Entity identity (player, enemy, wall, etc)."""
    type: Entity


@dataclass
class Active:
    """Is the entity active."""
    pass


@dataclass
class Position:
    """Position of an entity in the grid."""
    x: int
    y: int

    def is_adjacent(self, other: 'Position', diagonal: bool = False):
        p1 = self.x, self.y
        p2 = other.x, other.y
        return p2 in grid_neighbors(p1, diagonal=diagonal)


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
class Fog:
    """Entity that masks other entities from view."""
    pass


@dataclass
class Switch:
    """A floor switch you can step on."""
    group: list[int] | None = None
    pressed: bool = False
    pressable: bool = True
    trigger_types: list[Entity] = field(default_factory=lambda: [Entity.PLAYER])
    trigger_entities: list[int] = field(default_factory=lambda: [])

    def is_triggered(self, ent: int, type: Entity):
        return ent in self.trigger_entities or type in self.trigger_types


@dataclass
class Switchable:
    """Add or delete the component.Active on switch trigger."""
    triggers: list[int]  # Link to switches


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
    allow: tuple[int, ...] | None = None

    def is_blocked(self, other: int):
        if self.allow is None:
            return True

        return other not in self.allow


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
    steps: int = 1
    stagger: int = 1
    tick: int = 0
    diagonal: bool = False


@dataclass
class MirrorAI:
    """Entity that copies a target entity's movement on x-axis and mirrors on the y-axis."""
    target: int
    mirror_x: bool = False
    mirror_y: bool = True

    def reflect(self, x: int, y: int):
        if self.mirror_x:
            x = -x

        if self.mirror_y:
            y = -y

        return x, y


@dataclass
class PatrolAI:
    """Entity that moves along a fixed path."""
    delta: tuple[int, int]


@dataclass
class FixedAI:
    """Entity that moves along a fixed path."""
    moves: list[tuple[int, int]]
    move_index: int = 0


@dataclass
class SnakeAI:
    """Entity that occupies multiple spaces."""
    target: int
    head: int
    next: int | None
    steps: int = 1
    diagonal: bool = False
    delta: tuple[int, int] | None = None


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
