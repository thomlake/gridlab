from typing import Type

from gridlab.action import Action
from gridlab.world import World


WORLD_REGISTRY: dict[str, Type[World]] = {}


def world_names():
    return list(WORLD_REGISTRY.keys())


def register_world(name: str):
    if name in WORLD_REGISTRY:
        raise ValueError(f'duplicate world name: {name}')

    def inner(world_class: Type[World]):
        world_class.name = name
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
        self.create_grid(3, 3)
        self.add_player(0, 2)
        self.add_goal(2, 0)

    def solve(self):
        return [
            Action.UP,
            Action.UP,
            Action.RIGHT,
            Action.RIGHT,
        ]


@register_world('demo1')
class DemoWorld_01(World):
    def layout(self):
        text_grid = """
        ####################
        ###..1...#...#######
        #...^..^..0...######
        #.@...1^^^1.^^######
        #...^^...^.0..######
        #........^0^..##...#
        ###...1...0.#...X.#
        ################...#
        ####################
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            '^': self.add_spike,
            '1': lambda x, y: self.add_patrol_enemy(x, y, delta=(0, -1)),
        }
        self.initialize(text_grid=text_grid, char_map=char_map)


@register_world('fog')
class FogWorld_01(World):
    def layout(self):
        text_grid = """
        #############
        #@..~~~######
        ####~~~######
        ###1~.~######
        ####~~~######
        ####~.~2#####
        ####~~~##.X.#
        ####~~~.....#
        #############
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            '^': self.add_spike,
            '~': self.add_fog,
            '1': lambda x, y: self.add_patrol_enemy(x, y, delta=(1, 0)),
            '2': lambda x, y: self.add_patrol_enemy(x, y, delta=(-1, 0)),
        }
        self.initialize(text_grid=text_grid, char_map=char_map)


@register_world('switch')
class SwitchWorld_01(World):
    def layout(self):
        text_grid = """
        #########
        #.......#
        #.@.#.X.#
        #...#...#
        #########
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
        }
        self.initialize(text_grid=text_grid, char_map=char_map)
        self.add_switch((1, 1), [(4, 1)])


@register_world('switch2')
class SwitchWorld_02(World):
    def layout(self):
        text_grid = """
        #########
        #.......#
        #@.X....#
        #.......#
        #########
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
        }
        self.initialize(text_grid=text_grid, char_map=char_map)
        self.add_switch_toggle((2, 1), (4, 1), [(3, 1)], [(5, 2)])


@register_world('blockade')
class BlockadeWorld(World):
    def layout(self):
        text_grid = """
        ##########
        #........#
        #........#
        #..##..#.#
        #...1.##X#
        #.##.....#
        #..#.##.2#
        #........#
        #@.......#
        ##########
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '1': self.add_chase_enemy,
            '2': lambda x, y: self.add_patrol_enemy(x, y, delta=(0, -1)),
        }
        self.initialize(text_grid=text_grid, char_map=char_map)


@register_world('door')
class DoorWorld(World):
    def layout(self):
        text_grid = """
        #########
        #@...K..#
        #.......#
        #^^#+#^^#
        #...X...#
        #########
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '^': self.add_spike,
            'K': self.add_key,
            '+': self.add_door,
        }
        self.initialize(text_grid=text_grid, char_map=char_map)


@register_world('spike')
class SpikeWorld_01(World):
    def layout(self):
        text_grid = """
        #######
        #..^..#
        #.....#
        #..^..#
        #@.^.X#
        #######
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '^': self.add_spike,
        }
        self.initialize(text_grid=text_grid, char_map=char_map)

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
        #######
        #..T..#
        #@...X#
        #.....#
        #######
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            'T': self.add_timer_reset,
        }
        self.initialize(text_grid=text_grid, char_map=char_map)
        self.add_timer(limit=3)

    def solve(self):
        return [
            (1, 0),
            (1, 0),
            (0, 1),
            (0, -1),
            (1, 0),
            (1, 0),
        ]


@register_world('mirror')
class MirrorWorld_01(World):
    def layout(self):
        text_grid = """
        #######
        #X.e..#
        #...#.#
        #.....#
        #..@..#
        #######
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            'e': self.add_mirror_enemy,
        }
        self.initialize(text_grid=text_grid, char_map=char_map)

    def solve(self):
        return [
            Action.RIGHT,
            Action.RIGHT,
            Action.UP,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.UP,
            Action.UP,
        ]


@register_world('mirror-block')
class MirrorBlockWorld(World):
    def layout(self):
        text_grid = """
        #######
        #X.e..#
        #.....#
        #...0.#
        #..@..#
        #######
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            'e': self.add_mirror_enemy,
        }
        self.initialize(text_grid=text_grid, char_map=char_map)

    def solve(self):
        return [
            Action.RIGHT,
            Action.UP,
            Action.DOWN,
            Action.LEFT,
            Action.UP,
            Action.RIGHT,
            Action.RIGHT,
            Action.UP,
            Action.UP,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
        ]


@register_world('mirror-block-flip')
class MirrorBlockFlipWorld(World):
    def layout(self):
        text_grid = """
        #######
        #..@..#
        #...0##
        #^^...#
        #X.e..#
        #######
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            '^': self.add_spike,
            'e': lambda x, y: self.add_mirror_enemy(x, y, True, True),
        }
        self.initialize(text_grid=text_grid, char_map=char_map)

    def solve(self):
        return [
            Action.RIGHT,
            Action.DOWN,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.UP,
            Action.DOWN,
            Action.RIGHT,
            Action.RIGHT,
            Action.DOWN,
            Action.DOWN,
            Action.LEFT,
            Action.LEFT,
        ]


@register_world('patrol')
class PatrolWorld_01(World):
    def layout(self):
        text_grid = """
        #####
        #.X.#
        #0.e#
        #.#.#
        #.@.#
        #####
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            'e': lambda x, y: self.add_patrol_enemy(x, y, delta=(1, 0)),
        }
        self.initialize(text_grid=text_grid, char_map=char_map)

    def solve(self):
        return [
            Action.LEFT,
            Action.UP,
            Action.UP,
            Action.DOWN,
            Action.DOWN,
            Action.RIGHT,
            Action.RIGHT,
            Action.UP,
            Action.UP,
            Action.UP,
            Action.LEFT,
        ]


@register_world('patrol+')
class PatrolWorld_Advanced(World):
    def layout(self):
        text_grid = """
        ###########
        #.....3...#
        #..^.2..#.#
        #.@..^.0.1#
        #...###.X^#
        ###########
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            '^': self.add_spike,
            '1': lambda x, y: self.add_patrol_enemy(x, y, delta=(1, 0)),
            '2': lambda x, y: self.add_patrol_enemy(x, y, delta=(-1, 0)),
            '3': lambda x, y: self.add_patrol_enemy(x, y, delta=(0, -1)),
        }
        self.initialize(text_grid=text_grid, char_map=char_map)

    def solve(self):
        return [
            (-1, 0),
            (0, 1),
            (0, 1),
            (0, -1),
            (0, -1),
            (1, 0),
            (1, 0),
            (0, 1),
            (0, 1),
            (0, 1),
            (-1, 0),
        ]


@register_world('snake')
class SnakeWorld_01(World):
    def layout(self):
        text_grid = """
        #####
        #..X#
        #...#
        #...#
        #...#
        #...#
        #...#
        #...#
        #...#
        #...#
        #@..#
        #####
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
        }
        self.initialize(text_grid=text_grid, char_map=char_map)
        self.add_snake_enemy(
            [
                (1, 4), (2, 4), (3, 4),
                (3, 3), (2, 3), (1, 3),
                (1, 2), (2, 2), (3, 2),
            ],
        )


@register_world('chase')
class ChaseWorld_01(World):
    def layout(self):
        text_grid = """
        #########
        #.......#
        #...X...#
        #...#...#
        #e......#
        #......e#
        #.....#.#
        #.##....#
        #....#..#
        #@......#
        #########
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            'e': self.add_chase_enemy
        }
        self.initialize(text_grid=text_grid, char_map=char_map)


@register_world('chase-test')
class ChaseWorld_02(World):
    def layout(self):
        text_grid = """
        #########
        #......X#
        #.......#
        #.......#
        #.......#
        #.......#
        #.......#
        #.......#
        #.......#
        #@......#
        #########
        """
        self.initialize(text_grid=text_grid)
        self.add_chase_enemy(4, 2)

    def solve(self):
        raise NotImplementedError()


@register_world('chase-push')
class ChaseWorld_03(World):
    def layout(self):
        text_grid = """
        #########
        #...0...#
        #@..0.e.#
        #..00...#
        #...000X#
        #########
        """
        char_map = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            'e': self.add_chase_enemy
        }
        self.initialize(text_grid=text_grid, char_map=char_map)
        # self.add_chase_enemy(6, 2)

    def solve(self):
        raise NotImplementedError()
