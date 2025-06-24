from typing import Type, TypedDict

from gridlab.action import Action
from gridlab.difficulty import Difficulty, get_difficulty_score
from gridlab.entity import Entity
from gridlab.world import World


class WorldMetadata(TypedDict):
    name: str
    difficulty: Difficulty
    difficulty_score: int
    entity_types: list[Entity]


WORLD_REGISTRY: dict[str, Type[World]] = {}


def world_names():
    return list(WORLD_REGISTRY.keys())


def world_metadata(name: str) -> WorldMetadata:
    world_class = WORLD_REGISTRY[name]
    return {
        'name': world_class.name,
        'difficulty': world_class.difficulty,
        'difficulty_score': get_difficulty_score(world_class.difficulty),
        'entity_types': world_class.entity_types,
    }


def create_world(name: str) -> World:
    world_class = WORLD_REGISTRY[name]
    world = world_class()
    return world


def register_world(world_class: Type[World]):
    name = world_class.name
    if name in WORLD_REGISTRY:
        raise ValueError(f'duplicate world name: {name}')

    WORLD_REGISTRY[name] = world_class
    return world_class


@register_world
class EmptyWorld(World):
    name = 'empty'
    difficulty = Difficulty.TRIVIAL
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
    ]

    def build(self):
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


@register_world
class DemoWorld(World):
    name = 'demo'
    difficulty = Difficulty.MODERATE
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.SPIKE,
        Entity.ENEMY,
    ]

    def build(self):
        text = """
        ############
        ####.#######
        ##..0..^.X##
        ##...0###e##
        ##.@.......#
        ############
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            '^': self.add_spike,
            'e': self.add_chase_enemy,
        }
        self.populate(text=text, initializers=initializers)

    def solve(self):
        return [
            Action.UP,
            Action.RIGHT,
            Action.UP,
            Action.RIGHT,
            Action.DOWN,
            Action.LEFT,
            Action.DOWN,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.DOWN,
            Action.DOWN,
            Action.RIGHT,
            Action.UP,
            Action.UP,
        ]


@register_world
class DemoWorld_01(World):
    name = 'demo1'
    difficulty = Difficulty.UNCLASSIFIED
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.SPIKE,
        Entity.ENEMY,
    ]

    def build(self):
        text = """
        ####################
        ###..1...#...#######
        #...^..^..0...######
        #.@...1^^^1.^^######
        #...^^...^.0..######
        #........^0^..##...#
        ###...1...0.#....X.#
        ################...#
        ####################
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            '^': self.add_spike,
            '1': lambda x, y: self.add_patrol_enemy(x, y, delta=(0, -1)),
        }
        self.populate(text=text, initializers=initializers)


@register_world
class DemoWorld_02(World):
    name = 'demo2'
    difficulty = Difficulty.UNCLASSIFIED
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
        Entity.FOG,
    ]

    def build(self):
        text = """
        ####################
        #......~112~.......#
        #......~1~~~.......#
        #..@...#~~~~.......#
        #......#~#.........#
        #......#~#.........#
        #......#...........#
        #......###.........#
        ####################
        """

        def add_custom_1(x, y):
            self.add_fog(x, y)
            self.add_block(x, y)

        def add_custom_2(x, y):
            self.add_fog(x, y)
            self.add_chase_enemy(x, y)

        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            '^': self.add_spike,
            '~': self.add_fog,
            '1': add_custom_1,
            '2': add_custom_2,
            '?': lambda x, y: self.add_patrol_enemy(x, y, delta=(0, -1)),
        }
        self.populate(text=text, initializers=initializers)


@register_world
class Causeway(World):
    name = 'causeway'
    difficulty = Difficulty.EASY
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
    ]

    def build(self):
        text = """
        ##############
        #.....####...#
        #...00####.X.#
        #...0.####...#
        ###...1..2...#
        ###.@.########
        ##############
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            '1': lambda x, y: self.add_patrol_enemy(x, y, delta=(1, 0)),
            '2': lambda x, y: self.add_patrol_enemy(x, y, delta=(-1, 0)),
        }
        self.populate(text=text, initializers=initializers)

    def solve(self):
        return [
            Action.UP,
            Action.RIGHT,
            Action.UP,
            Action.UP,
            Action.LEFT,
            Action.DOWN,
            Action.RIGHT,
            Action.NONE,
            Action.NONE,
            Action.NONE,
            Action.NONE,
            Action.NONE,
            Action.NONE,
            Action.DOWN,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.UP,
            Action.UP,
            Action.RIGHT,
        ]


@register_world
class KiteWorld(World):
    name = 'kite'
    difficulty = Difficulty.EASY
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
    ]

    def build(self):
        text = """
        #############
        #.......#####
        #.......#.X.#
        #...0000#...#
        #..0......e.#
        #...0000#####
        #.@......####
        #........####
        #############
        """

        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            'e': self.add_chase_enemy,
        }
        self.populate(text=text, initializers=initializers)

    def solve(self):
        return [
            Action.UP,
            Action.RIGHT,
            Action.UP,
            Action.RIGHT,
            Action.RIGHT,
            Action.UP,
            Action.UP,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.DOWN,
            Action.DOWN,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.UP,
            Action.UP,
        ]


@register_world
class FogWorld_01(World):
    name = 'fog'
    difficulty = Difficulty.MODERATE
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
        Entity.FOG,
    ]

    def build(self):
        text = """
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
        initializers = {
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
        self.populate(text=text, initializers=initializers)

    def solve(self):
        return [
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.DOWN,
            Action.RIGHT,
            Action.DOWN,
            Action.DOWN,
            Action.RIGHT,
            Action.DOWN,
            Action.DOWN,
            Action.DOWN,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.UP,
        ]


@register_world
class SwitchWorld_01(World):
    name = 'switch'
    difficulty = Difficulty.EASY
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
        Entity.SWITCH_PRESSABLE,
    ]

    def build(self):
        text = """
        #########
        #.......#
        #.@.#.X.#
        #...#...#
        #########
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
        }
        self.populate(text=text, initializers=initializers)

        switch = """
        #########
        #1..A...#
        #.@.#.X.#
        #...#...#
        #########
        """
        self.populate_switches(text=switch)
        self.add_switch((1, 1), [(4, 1)])

    def solve(self):
        return [
            Action.UP,
            Action.LEFT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.DOWN,
            Action.RIGHT,
        ]


@register_world
class SwitchWorld_02(World):
    name = 'switch2'
    difficulty = Difficulty.UNCLASSIFIED
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.SWITCH_PRESSABLE,
        Entity.SWITCH_UNPRESSABLE,
    ]

    def build(self):
        text = """
        #########
        #.......#
        #@.X....#
        #.......#
        #########
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
        }
        self.populate(text=text, initializers=initializers)
        self.add_switch_toggle((2, 1), (4, 1), [(3, 1)], [(5, 2)])


@register_world
class SwitchTrickWorld(World):
    name = 'switch-trick-world'
    difficulty = Difficulty.MODERATE
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.SWITCH_PRESSABLE,
    ]

    def build(self):
        text = """
        ###########
        #.........#
        #..@.....X#
        #.........#
        ###########
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
        }
        self.populate(text=text, initializers=initializers)

        switch_1 = """
        ###########
        #aaaA1.#AA#
        #aaaA#A#AX#
        #aaaaaaaAA#
        ###########
        """
        self.populate_switches(text=switch_1)

        switch_2 = """
        ###########
        #aaa...####
        #1aa#####X#
        #.......###
        ###########
        """
        self.populate_switches(text=switch_2)

        switch_3 = """
        ###########
        #..a...####
        #..a#A###X#
        #..a...1###
        ###########
        """
        self.populate_switches(text=switch_3)

        switch_4 = """
        ###########
        #1.....A###
        #...###A#X#
        #.......###
        ###########
        """
        self.populate_switches(text=switch_4)

    def solve(self) -> list[Action]:
        return [
            Action.UP,
            Action.LEFT,
            Action.LEFT,
            Action.RIGHT,
            Action.RIGHT,
            Action.DOWN,
            Action.DOWN,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.UP,
            Action.UP,
            Action.LEFT,
            Action.LEFT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.DOWN,
        ]


@register_world
class SwitchPushWorld(World):
    name = 'switch-push'
    difficulty = Difficulty.MODERATE
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
        Entity.SPIKE,
        Entity.SWITCH_PRESSABLE,
        Entity.SWITCH_UNPRESSABLE,
    ]

    def build(self):
        text = """
        ##############
        #......#######
        #...000#######
        #..0......####
        #...000##^####
        #......##.####
        #........=..@#
        #......##.####
        #...000##^####
        #..0....e...##
        #...000###..##
        #......###.X##
        ##############
        """

        def add_toggle(x: int, y: int):
            return self.add_switch_toggle(
                (x, y),
                (x - 2, y),
                active_switchable_positions=[
                    (x - 1, y),
                ],
                inactive_switchable_positions=[
                    (x, y - 1),
                    (x, y + 1),
                ],
            )

        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            '^': self.add_spike,
            'e': self.add_chase_enemy,
            '=': add_toggle,
        }
        self.populate(text=text, initializers=initializers)


@register_world
class SwitchMediumWorld(World):
    name = 'switch-medium'
    difficulty = Difficulty.HARD
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
        Entity.SPIKE,
        Entity.SWITCH_PRESSABLE,
        Entity.SWITCH_UNPRESSABLE,
    ]

    def build(self):
        text = """
        ###################
        ####.......########
        ####..0..00########
        ####...00..########
        ####...0.e....#####
        ####......0##^#####
        #............=0.@.#
        #.....#######^#####
        #...00#######.#####
        #..0..e.........###
        #00.00#######.X.###
        #.....#######...###
        ###################
        """

        def add_toggle(x: int, y: int):
            return self.add_switch_toggle(
                (x, y),
                (x - 1, y),
                inactive_switchable_positions=[
                    (x, y - 1),
                    (x, y + 1),
                    # (x + 1, y),
                ],
            )

        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            '^': self.add_spike,
            'e': self.add_chase_enemy,
            '=': add_toggle,
        }
        self.populate(text=text, initializers=initializers)

    def solve(self):
        return [
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.DOWN,
            Action.UP,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.UP,
            Action.LEFT,
            Action.LEFT,
            Action.DOWN,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.LEFT,
            Action.UP,
            Action.UP,
            Action.DOWN,
            Action.RIGHT,
            Action.LEFT,
            Action.LEFT,
            Action.UP,
            Action.UP,
            Action.DOWN,
            Action.DOWN,
            Action.RIGHT,
            Action.UP,
            Action.DOWN,
            Action.DOWN,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.DOWN,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.DOWN,
            Action.DOWN,
            Action.DOWN,
            Action.DOWN,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.DOWN,
        ]


@register_world
class BlockadeWorld(World):
    name = 'blockade'
    difficulty = Difficulty.EASY
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
    ]

    def build(self):
        text = """
        ##########
        #........#
        #..##..#.#
        #...1.##X#
        #.##.....#
        #..#.##.2#
        #........#
        #@.......#
        ##########
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '1': self.add_chase_enemy,
            '2': lambda x, y: self.add_patrol_enemy(x, y, delta=(0, -1)),
        }
        self.populate(text=text, initializers=initializers)


@register_world
class DoorWorld(World):
    name = 'door'
    difficulty = Difficulty.TRIVIAL
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.KEY,
        Entity.DOOR,
        Entity.ENEMY,
        Entity.SPIKE,
    ]

    def build(self):
        text = """
        #########
        #@...K..#
        #.......#
        #^^#+#^^#
        #...X...#
        #########
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '^': self.add_spike,
            'K': self.add_key,
            '+': self.add_door,
        }
        self.populate(text=text, initializers=initializers)

    def solve(self):
        return [
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.DOWN,
            Action.LEFT,
            Action.DOWN,
            Action.DOWN,
        ]


@register_world
class SpikeWorld_01(World):
    name = 'spike'
    difficulty = Difficulty.TRIVIAL
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
        Entity.SPIKE,
    ]

    def build(self):
        text = """
        #######
        #..^..#
        #.....#
        #..^..#
        #@.^.X#
        #######
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '^': self.add_spike,
        }
        self.populate(text=text, initializers=initializers)

    def solve(self):
        return [
            Action.UP,
            Action.UP,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.DOWN,
            Action.DOWN,
        ]


@register_world
class TimerWorld_01(World):
    name = 'timer'
    difficulty = Difficulty.EASY
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
        Entity.TIMER_RESET,
    ]

    def build(self):
        text = """
        #######
        #..T..#
        #@...X#
        #.....#
        #######
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            'T': self.add_timer_reset,
        }
        self.populate(text=text, initializers=initializers)
        self.add_timer(limit=3)

    def solve(self):
        return [
            Action.RIGHT,
            Action.RIGHT,
            Action.UP,
            Action.DOWN,
            Action.RIGHT,
            Action.RIGHT,
        ]


@register_world
class MirrorWorld_01(World):
    name = 'mirror'
    difficulty = Difficulty.EASY
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
    ]

    def build(self):
        text = """
        #######
        #X.e..#
        #...#.#
        #.....#
        #..@..#
        #######
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            'e': self.add_mirror_enemy,
        }
        self.populate(text=text, initializers=initializers)

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


@register_world
class MirrorBlockWorld(World):
    name = 'mirror-block'
    difficulty = Difficulty.MODERATE
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
    ]

    def build(self):
        text = """
        #######
        #X.e..#
        #.....#
        #...0.#
        #..@..#
        #######
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            'e': self.add_mirror_enemy,
        }
        self.populate(text=text, initializers=initializers)

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


@register_world
class MirrorBlockFlipWorld(World):
    name = 'mirror-block-flip'
    difficulty = Difficulty.MODERATE
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
        Entity.SPIKE,
    ]

    def build(self):
        text = """
        #######
        #..@..#
        #...0##
        #^^...#
        #X.e..#
        #######
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            '^': self.add_spike,
            'e': lambda x, y: self.add_mirror_enemy(x, y, True, True),
        }
        self.populate(text=text, initializers=initializers)

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


@register_world
class PatrolWorld_01(World):
    name = 'patrol'
    difficulty = Difficulty.EASY
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
    ]

    def build(self):
        text = """
        #####
        #.X.#
        #0.e#
        #.#.#
        #.@.#
        #####
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            'e': lambda x, y: self.add_patrol_enemy(x, y, delta=(1, 0)),
        }
        self.populate(text=text, initializers=initializers)

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


@register_world
class PatrolWorld_Advanced(World):
    name = 'patrol-advanced'
    difficulty = Difficulty.MODERATE
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
        Entity.SPIKE,
    ]

    def build(self):
        text = """
        #########
        #...2...#
        #.@...#.#
        #....0.1#
        #####.X##
        #####2.##
        #########
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            '^': self.add_spike,
            '1': lambda x, y: self.add_patrol_enemy(x, y, delta=(1, 0)),
            '2': lambda x, y: self.add_patrol_enemy(x, y, delta=(0, -1)),
        }
        self.populate(text=text, initializers=initializers)

    def solve(self):
        return [
            Action.RIGHT,
            Action.DOWN,
            Action.NONE,
            Action.RIGHT,
            Action.RIGHT,
            Action.UP,
            Action.UP,
            Action.RIGHT,
            Action.NONE,
            Action.LEFT,
            Action.LEFT,
            Action.LEFT,
            Action.DOWN,
            Action.DOWN,
            Action.NONE,
            Action.RIGHT,
            Action.RIGHT,
            Action.DOWN,
            Action.RIGHT,
        ]


@register_world
class SnakeWorld_01(World):
    name = 'snake'
    difficulty = Difficulty.UNCLASSIFIED
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
    ]

    def build(self):
        text = """
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
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
        }
        self.populate(text=text, initializers=initializers)
        self.add_snake_enemy(
            (
                (1, 4), (2, 4), (3, 4),
                (3, 3), (2, 3), (1, 3),
                (1, 2), (2, 2), (3, 2),
            ),
        )


@register_world
class ChaseWorld_01(World):
    name = 'chase'
    difficulty = Difficulty.EASY
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
    ]

    def build(self):
        text = """
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
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            'e': self.add_chase_enemy
        }
        self.populate(text=text, initializers=initializers)

    def solve(self):
        return [
            Action.RIGHT,
            Action.RIGHT,
            Action.RIGHT,
            Action.UP,
            Action.DOWN,
            Action.RIGHT,
            Action.RIGHT,
            Action.UP,
            Action.UP,
            Action.LEFT,
            Action.UP,
            Action.UP,
            Action.UP,
            Action.UP,
            Action.UP,
            Action.LEFT,
        ]


@register_world
class ChaseWorld_02(World):
    name = 'chase-test'
    difficulty = Difficulty.UNCLASSIFIED
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
    ]

    def build(self):
        text = """
        #########
        #......X#
        #...e...#
        #.......#
        #.......#
        #.......#
        #.......#
        #.......#
        #.......#
        #@......#
        #########
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            'e': self.add_chase_enemy
        }
        self.populate(text=text, initializers=initializers)

    def solve(self):
        raise NotImplementedError()


@register_world
class ChaseWorld_03(World):
    name = 'chase-push'
    difficulty = Difficulty.MODERATE
    entity_types = [
        Entity.PLAYER,
        Entity.GOAL,
        Entity.WALL,
        Entity.BLOCK,
        Entity.ENEMY,
    ]

    def build(self):
        text = """
        #########
        #...0...#
        #@..0.e.#
        #..00...#
        #...000X#
        #########
        """
        initializers = {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            'e': self.add_chase_enemy
        }
        self.populate(text=text, initializers=initializers)

    def solve(self):
        raise NotImplementedError()
