from typing import Type

from gridlab.world import World


WORLD_REGISTRY: dict[str, Type[World]] = {}


def world_names():
    return list(WORLD_REGISTRY.keys())


def register_world(name: str):
    if name in WORLD_REGISTRY:
        raise ValueError(f'duplicate world name: {name}')

    def inner(world_class: Type[World]):
        WORLD_REGISTRY[name] = world_class
        return world_class

    return inner


def create_world(name: str) -> World:
    world_class = WORLD_REGISTRY[name]
    world = world_class()
    return world


@register_world('empty')
class EmptyWorld(World):
    def layout(self):
        self.initialize(shape=(3, 4))
        self.add_player(0, 0)
        self.add_goal(2, 3)

    def solve(self):
        return [
            (0, 1),
            (0, 1),
            (0, 1),
            (1, 0),
            (1, 0),
        ]


@register_world('blockade')
class BlockadeWorld(World):
    def layout(self):
        text_grid = """
        ........
        ........
        ..##..#.
        .....##o
        .##.....
        ..#.##..
        ........
        @.......
        """
        self.initialize(text_grid=text_grid)
        self.add_chase_enemy(3, 3)
        moves = 4*[(0, -1)] + 4*[(0, 1)]
        self.add_patrol_enemy(7, 5, moves=moves)


@register_world('door')
class DoorWorld(World):
    def layout(self):
        text_grid = """
        @...k..
        .......
        ^^#!#^^
        ...o...
        """
        self.initialize(text_grid=text_grid)


@register_world('spike')
class SpikeWorld_01(World):
    def layout(self):
        text_grid = """
        ...^....
        ........
        ...^....
        @..^..o.
        """
        self.initialize(text_grid=text_grid)

    def solve(self):
        return [
            (1, 0),
            (0, 1),
            (0, 1),
            (0, 1),
            (0, 1),
            (-1, 0),
        ]


@register_world('timer')
class TimerWorld_01(World):
    def layout(self):
        text_grid = """
        ..+..
        @...o
        .....
        """
        self.initialize(text_grid=text_grid)
        self.add_timer(limit=3)

    def solve(self):
        return [
            (1, 0),
            (1, 0),
            (0, 1),
            (1, 0),
            (1, 0),
            (0, -1),
        ]


@register_world('mirror')
class MirrorWorld_01(World):
    def layout(self):
        self.initialize(shape=(5, 4))
        self.add_player(2, 0)
        self.add_mirror_enemy(2, 3)
        self.add_wall(3, 2)
        self.add_goal(0, 3)

    def solve(self):
        return [
            (1, 0),
            (1, 0),
            (0, 1),
            (-1, 0),
            (-1, 0),
            (-1, 0),
            (-1, 0),
            (0, 1),
            (0, 1),
        ]


@register_world('patrol')
class PatrolWorld_01(World):
    def layout(self):
        self.initialize(shape=(3, 5))
        self.add_player(1, 0)
        # moves = [(-1, 0), (1, 0), (1, 0), (-1, 0)]
        moves = [(1, 0), (-1, 0)]
        self.add_patrol_enemy(1, 2, moves=moves)
        self.add_goal(1, 3)
        self.add_wall(1, 1)
        self.add_block(0, 2)

    def solve(self):
        return [
            (-1, 0),
            (0, 1),
            (0, 1),
            (0, -1),
            (0, -1),
            (1, 0),
            (1, 0),
            (0, -1),
            (0, -1),
            (0, -1),
            (-1, 0),
        ]


# ChatGPT


class MirrorBarrierWorld(World):
    def layout(self):
        self.initialize(shape=(7, 7))  # 7×7 grid

        # 1) Build a solid barrier across row y=3, leaving exactly one gap at (3,3)
        for x in range(7):
            if x != 3:
                self.add_wall(x, 3)

        # 2) Seal that gap with a pushable block
        self.add_block(3, 3)

        # 3) Put the player below the barrier
        self.add_player(3, 6)

        # 4) Put a mirror‐movement enemy above the barrier
        self.add_mirror_enemy(5, 1)

        # 5) Place the goal on the far side, above the barrier
        self.add_goal(1, 0)

    def solve(self):
        return [
            (0, 1),
            (0, 1),
            (0, 1),
            (1, 0),
            (1, 0),
        ]


class MirrorMazeWorld(World):
    def initialize(self):
        super().initialize(shape=(7, 7))
        # carve out a “+” corridor: row y=3 and column x=3 are open, everything else is wall
        for y in range(7):
            for x in range(7):
                if x != 3 and y != 3:
                    self.add_wall(x, y)

        # start the player two tiles left of the center intersection
        self.add_player(1, 3)
        # mirror enemy just to their right
        self.add_mirror_enemy(2, 3)
        # goal at the bottom of the vertical branch
        self.add_goal(3, 6)

    def solve(self):
        return [
            (0, 1),
            (0, 1),
            (0, 1),
            (1, 0),
            (1, 0),
        ]


class SpikeMirrorBranchWorld(World):
    def initialize(self):
        super().initialize(shape=(9, 7))

        self.add_player(3, 6)

        # 1) Build the sealed barrier across y=2, gap at x=4
        for x in range(1, 8):
            if x != 4:
                self.add_wall(x, 2)

        # 2) Carve out the spike-trap branch beneath the barrier
        #    (we’ll funnel the mirror here)
        self.add_spike(4, 5)
        # Side-walls around the spike path
        self.add_wall(3, 3)
        self.add_wall(5, 3)
        self.add_wall(3, 4)
        self.add_wall(5, 4)

        # 3) Place the block in front of the barrier
        self.add_block(4, 4)

        # 4) Put the mirror above
        self.add_mirror_enemy(3, 0)

        # 6) And the goal just past the barrier
        self.add_goal(6, 4)

    def solve(self):
        pass


class MirrorChaseSpikeTrapWorld(World):
    def solve(self):
        pass

    def initialize(self):
        super().initialize(shape=(11, 9))   # 11×9 grid

        self.add_player(1, 2)  # top‐left corner, inside the barrier gap at (2,4)

        # 1) Outer border walls
        for x in range(11):
            self.add_wall(x, 0)
            self.add_wall(x, 8)
        for y in range(1, 8):
            self.add_wall(0, y)
            self.add_wall(10, y)

        # 2) Vertical barrier at x=2, with a single gap at y=4
        for y in range(1, 8):
            if y != 4:
                self.add_wall(2, y)

        # 3) A sealed horizontal corridor at y=5: walls everywhere except x=5
        for x in range(3, 9):
            if x != 5:
                self.add_wall(x, 5)
        self.add_block(5, 5)  # block seals it

        # 4) Spike trap chute at x=6, rows y=2–4
        for y in (2, 3, 4):
            self.add_spike(6, y)

        # 5) Enemies
        self.add_mirror_enemy(8, 1)  # top‐right
        self.add_chase_enemy(1, 7)   # bottom‐left

        # 6) Player start and goal
        self.add_goal(9, 7)    # bottom‐right
