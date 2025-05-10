from typing import Callable

from gridlab import component, system, view
from gridlab.entity import Entity, EntityManager
from gridlab.grid import Grid
from gridlab.interface import Actor, Observer, TerminalActor, TerminalObserver
from gridlab.state import State


class AbstractWorld:
    state: State
    em: EntityManager
    grid: Grid
    mech_systems: list[Callable[[], None]]
    view_systems: list[Callable[[], None]] | None = None
    actor: Actor | None = None
    observer: Observer | None = None
    player: int | None = None

    def solve(self) -> list[tuple[int, int]]:
        """Return the list of moves that result in success."""
        raise NotImplementedError()

    def initialize(self, *, shape: tuple[int, int] | None = None, layout: str | None = None):
        self.state = State()
        self.em = EntityManager()
        self.player = None

        if layout is not None:
            self._init_grid_from_layout(layout)
        elif shape is not None:
            w, h = shape
            self.grid = Grid(w, h)
        else:
            raise ValueError('shape or layout must be provided')

    def _init_grid_from_layout(self, layout: str):
        lines = [line.strip() for line in layout.strip().split('\n')]
        w, h = len(lines[0]), len(lines)
        self.grid = Grid(w, h)

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

    def run(self):
        self.initialize()
        assert self.player is not None
        self.setup_systems()

        for s in self.view_systems:
            s()

        systems = self.mech_systems + self.view_systems
        while not self.state.is_finished:
            for s in systems:
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

        actor = self.actor or TerminalActor()
        observer = self.observer or TerminalObserver()

        input_sys = system.InputSystem(self.em, self.state, actor=actor, player=self.player)
        movement_sys = system.MovementSystem(self.em, self.state, grid=self.grid)

        patrol_ai_sys = system.PatrolAISystem(self.em, self.state)
        mirror_ai_sys = system.MirrorAISystem(self.em, self.state)
        chase_ai_sys = system.ChaseAISystem(self.em, self.state, grid=self.grid)

        death_sys = system.DeathSystem(self.em, self.state, player=self.player)
        goal_sys = system.GoalSystem(self.em, self.state, player=self.player)
        timer_sys = system.TimerSystem(self.em, self.state, player=self.player)
        door_sys = system.DoorSystem(self.em, self.state)

        self.mech_systems = [
            input_sys,
            movement_sys,
            death_sys,
            patrol_ai_sys,
            mirror_ai_sys,
            chase_ai_sys,
            movement_sys,
            door_sys,
            death_sys,
            goal_sys,
            timer_sys,
        ]

        if self.view_systems is None:
            self.view_systems = [
                view.DescriptionSystem(),
                # view.ASCIIRichRenderSystem(),
                view.ASCIIRenderSystem(),
            ]

        for view_sys in self.view_systems:
            view_sys.initialize(em=self.em, grid=self.grid, observer=observer)

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
