from typing import Callable

from gridlab import component, system
from gridlab.action import Action
from gridlab.entity import Entity, EntityManager
from gridlab.grid import Grid
from gridlab.state import State


class World:
    state: State
    em: EntityManager
    grid: Grid
    action_system: system.ActionSystem
    systems: list[Callable[[], None]]
    player: int | None = None

    def __init__(self):
        self.reset()

    def solve(self) -> list[tuple[int, int]]:
        """Return the list of moves that result in success."""
        raise NotImplementedError()

    def reset(self):
        self.state = State()
        self.em = EntityManager()
        self.grid = None
        self.action_system = None
        self.systems = []
        self.player = None
        self.layout()
        self.setup_systems()

    def initialize(self, *, shape: tuple[int, int] | None = None, text_grid: str | None = None):
        if text_grid:
            self.init_from_text_grid(text_grid)
        elif shape:
            self.create_grid(*shape)
        else:
            raise ValueError('shape of text_grid must be specified')

    def create_grid(self, width: int, height: int):
        self.grid = Grid(width, height)

    def init_from_text_grid(self, text_grid: str):
        lines = [line.strip() for line in text_grid.strip().split('\n')]
        w, h = len(lines[0]), len(lines)
        self.create_grid(w, h)

        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char == '@':
                    self.add_player(x, y)
                elif char == 'o':
                    self.add_goal(x, y)
                elif char == 'k':
                    self.add_key(x, y)
                elif char == '+':
                    self.add_timer_reset(x, y)
                elif char == '#':
                    self.add_wall(x, y)
                elif char == '=':
                    self.add_block(x, y)
                elif char == '!':
                    self.add_door(x, y)
                elif char == '^':
                    self.add_spike(x, y)
                elif char != '.':
                    raise ValueError(f'unknown symbol {char}')

    def step(
            self,
            player_action: Action | None = None,
            actions: list[tuple[int, Action]] | None = None,
    ):
        if self.state.is_finished:
            return False

        _actions = []
        if player_action is not None:
            _actions.append((self.player, player_action))

        if actions is not None:
            _actions.extend(actions)

        self.action_system.add_actions(_actions)

        for s in self.systems:
            s()

    def setup_systems(self):
        def on_player_death():
            pos = self.em.get(component.Position)[self.player]
            dead = self.em.create()
            self.em.add_component(dead, component.Identity(Entity.PLAYER_DIED))
            self.em.add_component(dead, component.Position(pos.x, pos.y))

        self.state.player_dead_callbacks.append(on_player_death)

        def on_goal_reached():
            pos = self.em.get(component.Position)[self.player]
            success = self.em.create()
            self.em.add_component(success, component.Identity(Entity.GOAL_REACHED))
            self.em.add_component(success, component.Position(pos.x, pos.y))

        self.state.goal_reached_callbacks.append(on_goal_reached)

        action_system = system.ActionSystem(self.em, self.state, player=self.player)
        movement_system = system.MovementSystem(self.em, self.state, grid=self.grid)

        patrol_ai_system = system.PatrolAISystem(self.em, self.state)
        mirror_ai_system = system.MirrorAISystem(self.em, self.state)
        chase_ai_system = system.ChaseAISystem(self.em, self.state, grid=self.grid)

        death_system = system.DeathSystem(self.em, self.state, player=self.player)
        goal_system = system.GoalSystem(self.em, self.state, player=self.player)
        timer_system = system.TimerSystem(self.em, self.state, player=self.player)
        door_system = system.DoorSystem(self.em, self.state)

        self.action_system = action_system
        self.systems = [
            action_system,
            movement_system,
            death_system,
            patrol_ai_system,
            mirror_ai_system,
            chase_ai_system,
            movement_system,
            door_system,
            death_system,
            goal_system,
            timer_system,
        ]

    def register_player(self, ent: int):
        if self.player is not None:
            raise ValueError('player already registered!')

        self.player = ent

    def add_player(self, x: int, y: int) -> int:
        """Add the player at the given position and return its id."""
        player = self.em.create()
        self.register_player(player)

        self.em.add_component(player, component.Identity(Entity.PLAYER))
        self.em.add_component(player, component.Position(x, y))
        self.em.add_component(player, component.Pusher())
        self.em.add_component(player, component.KeyCollector())
        return player

    def add_goal(self, x: int, y: int) -> int:
        """Add a goal at the given position and return its id."""
        goal = self.em.create()
        self.em.add_component(goal, component.Identity(Entity.GOAL))
        self.em.add_component(goal, component.Position(x, y))
        self.em.add_component(goal, component.Goal())
        return goal

    def add_timer(self, limit: int) -> int:
        timer = self.em.create()
        # self.em.add_component(timer, component.Identity(Entity.TIMER))
        self.em.add_component(timer, component.Timer(limit=limit))

    def add_timer_reset(self, x: int, y: int) -> int:
        reset = self.em.create()
        self.em.add_component(reset, component.Identity(Entity.TIMER_RESET))
        self.em.add_component(reset, component.Position(x, y))
        self.em.add_component(reset, component.TimerReset())

    def add_key(self, x: int, y: int) -> int:
        reset = self.em.create()
        self.em.add_component(reset, component.Identity(Entity.KEY))
        self.em.add_component(reset, component.Position(x, y))
        self.em.add_component(reset, component.Key())

    def add_door(self, x: int, y: int) -> int:
        reset = self.em.create()
        self.em.add_component(reset, component.Identity(Entity.DOOR))
        self.em.add_component(reset, component.Position(x, y))
        self.em.add_component(reset, component.Solid())
        self.em.add_component(reset, component.Door())

    def add_wall(self, x: int, y: int) -> int:
        """Add a wall at the given position and return its id.

        Walls cannot be passed through by any entities."""
        wall = self.em.create()
        self.em.add_component(wall, component.Identity(Entity.WALL))
        self.em.add_component(wall, component.Position(x, y))
        self.em.add_component(wall, component.Solid())
        return wall

    def add_block(self, x: int, y: int) -> int:
        """Add a block at the given position and return its id.

        Blocks can be pushed by the player if the path is clear
        but cannot be passed through by other entities."""
        block = self.em.create()
        self.em.add_component(block, component.Identity(Entity.BLOCK))
        self.em.add_component(block, component.Position(x, y))
        self.em.add_component(block, component.Pushable())
        return block

    def add_spike(self, x: int, y: int) -> int:
        """Add a spike at the given position and return its id.

        Spikes kill the player on contact but do not block other entities.
        """
        spike = self.em.create()
        self.em.add_component(spike, component.Identity(Entity.SPIKE))
        self.em.add_component(spike, component.Position(x, y))
        self.em.add_component(spike, component.Deadly())
        return spike

    def add_chase_enemy(self, x: int, y: int) -> int:
        """Add a enemy at the given position that moves toward the player and return its id.

        Chase enemies move toward the player at each step.
        """
        enemy = self.em.create()
        self.em.add_component(enemy, component.Identity(Entity.ENEMY))
        self.em.add_component(enemy, component.Position(x, y))
        self.em.add_component(enemy, component.Solid(allow={self.player}))
        self.em.add_component(enemy, component.Deadly())
        self.em.add_component(enemy, component.ChaseAI(target=self.player))
        return enemy

    def add_patrol_enemy(self, x: int, y: int, moves: list[tuple[int, int]]) -> int:
        """Add an enemy at the given position with a fixed movement pattern and return its id.

        Patrol enemies cycle through a list or pre-specified list of movements.
        """
        enemy = self.em.create()
        self.em.add_component(enemy, component.Identity(Entity.ENEMY))
        self.em.add_component(enemy, component.Position(x, y))
        self.em.add_component(enemy, component.Solid(allow={self.player}))
        self.em.add_component(enemy, component.Deadly())
        self.em.add_component(enemy, component.PatrolAI(moves=moves))
        return enemy

    def add_mirror_enemy(self, x: int, y: int) -> int:
        """Add an enemy at the given position that mirrors the player's movement and return its id.

        Mirror enemies copy the player movement on the x-axis and mirror it on the y-axis.
        """
        enemy = self.em.create()
        self.em.add_component(enemy, component.Identity(Entity.ENEMY))
        self.em.add_component(enemy, component.Position(x, y))
        self.em.add_component(enemy, component.Solid(allow={self.player}))
        self.em.add_component(enemy, component.Deadly())
        self.em.add_component(enemy, component.MirrorAI(target=self.player))
        return enemy
