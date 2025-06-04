from typing import Callable

from gridlab import component, system
from gridlab.action import Action
from gridlab.entity import Entity, EntityManager
from gridlab.grid import Grid
from gridlab.state import State


class World:
    name: str = '???'
    state: State
    em: EntityManager
    grid: Grid
    action_system: system.ActionSystem
    systems: list[Callable[[], None]]
    turn: int = 1
    _player: int | None

    def __init__(self):
        self.reset()

    def solve(self) -> list[Action]:
        """Return the list of moves that result in success."""
        raise NotImplementedError()

    @property
    def char_map(self) -> dict[str, None | Callable[[int, int], int]]:
        return {
            '.': None,
            '#': self.add_wall,
            '@': self.add_player,
            'X': self.add_goal,
            '0': self.add_block,
            'K': self.add_key,
            '+': self.add_door,
            'T': self.add_timer_reset,
            '^': self.add_spike,
        }

    @property
    def player(self):
        if self._player is None:
            raise ValueError('player not registered!')

        return self._player

    def register_player(self, ent: int):
        if self._player is not None:
            raise ValueError('player already registered!')

        self._player = ent

    def reset(self):
        self.state = State()
        self.em = EntityManager()
        self.grid = None
        self.action_system = None
        self.systems = []
        self.turn = 1
        self._player = None
        self.layout()
        self.setup_systems()

    def create_grid(self, width: int, height: int):
        self.grid = Grid(width, height)

    def initialize(
            self,
            text_grid: str,
            char_map: dict[str, None | Callable[[int, int], int]] | None = None,
            player_chars: list[str] | None = None,
    ):
        lines = [line.strip() for line in text_grid.strip().split('\n')]
        w, h = len(lines[0]), len(lines)
        self.create_grid(w, h)

        char_map = char_map or self.char_map
        player_chars = player_chars or ['@']
        positions = [(c, (x, y)) for y, line in enumerate(lines) for x, c in enumerate(line)]

        for c, (x, y) in positions:
            if c in player_chars:
                char_map[c](x, y)

        for c, (x, y) in positions:
            if c not in player_chars:
                method = char_map[c]
                if method is not None:
                    method(x, y)

    def step(
            self,
            *,
            action: Action | None = None,
            actions: list[tuple[int, Action]] | None = None,
    ):
        if self.state.is_finished:
            return False

        actions = actions or []
        if action is not None:
            actions = [(self.player, action), *actions]

        actions = [(e, Action(a)) for e, a in actions]
        self.action_system.add_actions(actions)
        for s in self.systems:
            s()

        self.turn += 1

    def setup_systems(self):
        def clear_fog():
            fog = self.em.get(component.Fog)
            self.em.remove_all(list(fog.keys()))

        def on_player_death():
            clear_fog()
            pos = self.em.get(component.Position)[self.player]
            e = self.em.create()
            self.em.add_component(e, component.Identity(Entity.PLAYER_DIED))
            self.em.add_component(e, component.Active())
            self.em.add_component(e, component.Position(pos.x, pos.y))

        self.state.player_dead_callbacks.append(on_player_death)

        def on_goal_reached():
            clear_fog()
            pos = self.em.get(component.Position)[self.player]
            e = self.em.create()
            self.em.add_component(e, component.Identity(Entity.GOAL_REACHED))
            self.em.add_component(e, component.Active())
            self.em.add_component(e, component.Position(pos.x, pos.y))

        self.state.goal_reached_callbacks.append(on_goal_reached)

        action_system = system.ActionSystem(self.em, self.state, grid=self.grid)

        patrol_ai_system = system.PatrolAISystem(self.em, self.state, grid=self.grid)
        mirror_ai_system = system.MirrorAISystem(self.em, self.state, grid=self.grid)
        chase_ai_system = system.ChaseAISystem(self.em, self.state, grid=self.grid)
        snake_ai_system = system.SnakeAISystem(self.em, self.state, grid=self.grid)

        death_system = system.DeathSystem(self.em, self.state, player=self.player)
        goal_system = system.GoalSystem(self.em, self.state, player=self.player)
        timer_system = system.TimerSystem(self.em, self.state, player=self.player)
        door_system = system.DoorSystem(self.em, self.state)
        switch_system = system.SwitchSystem(self.em, self.state)

        self.action_system = action_system
        self.systems = [
            action_system,
            death_system,
            door_system,
            switch_system,
            patrol_ai_system,
            mirror_ai_system,
            chase_ai_system,
            snake_ai_system,
            death_system,
            goal_system,
            timer_system,
        ]

    def add_player(self, x: int, y: int) -> int:
        """Add the player at the given position and return its id."""
        e = self.em.create()
        self.register_player(e)

        self.em.add_component(e, component.Identity(Entity.PLAYER))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.Pusher())
        self.em.add_component(e, component.KeyCollector())
        return e

    def add_goal(self, x: int, y: int) -> int:
        """Add a goal at the given position and return its id."""
        e = self.em.create()
        self.em.add_component(e, component.Identity(Entity.GOAL))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.Goal())
        return e

    def add_timer(self, limit: int, ent: int | None = None) -> None:
        """Add a timer to the given entity (or the player if ent is None).

        Timers limit the number of game ticks an entity can exist for.
        If a timer expires on the player, the player dies and the session terminates.
        All other entities are removed when their timer expires.
        A timer can be reset by picking up a timer reset.
        """
        if ent is None:
            ent = self.player

        self.em.add_component(self.player, component.Timer(limit=limit))

    def add_timer_reset(self, x: int, y: int) -> int:
        """Add a timer reset at the given position and return its id."""
        e = self.em.create()
        self.em.add_component(e, component.Identity(Entity.TIMER_RESET))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.TimerReset())
        return e

    def add_key(self, x: int, y: int) -> int:
        """Add a key at the given position and return its id.

        Keys can be used to unlock doors.
        """
        e = self.em.create()
        self.em.add_component(e, component.Identity(Entity.KEY))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.Key())
        return e

    def add_fog(self, x: int, y: int) -> int:
        """Add fog at the given position and return its id.

        Fog hides entities at the same location.
        """
        e = self.em.create()
        self.em.add_component(e, component.Identity(Entity.FOG))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.Fog())
        return e

    def add_wall(self, x: int, y: int) -> int:
        """Add a wall at the given position and return its id.

        Walls cannot be moved through by any entities."""
        e = self.em.create()
        self.em.add_component(e, component.Identity(Entity.WALL))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.Solid())
        return e

    def add_door(self, x: int, y: int) -> int:
        """Add a door at the given position and return its id.

        Doors cannot be moved through until they are unlocked by an entity with a key.
        """
        e = self.em.create()
        self.em.add_component(e, component.Identity(Entity.DOOR))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.Solid())
        self.em.add_component(e, component.Door())
        return e

    def add_block(self, x: int, y: int) -> int:
        """Add a block at the given position and return its id.

        Blocks can be pushed by the player if the path is clear, but cannot be moved through."""
        e = self.em.create()
        self.em.add_component(e, component.Identity(Entity.BLOCK))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.Solid())
        self.em.add_component(e, component.Pushable())
        return e

    def add_spike(self, x: int, y: int) -> int:
        """Add a spike at the given position and return its id.

        Spikes kill the player on contact but do not block other entities.
        """
        e = self.em.create()
        self.em.add_component(e, component.Identity(Entity.SPIKE))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.Deadly())
        return e

    def add_chase_enemy(
            self,
            x: int,
            y: int,
            steps: int = 1,
            stagger: int = 1,
            tick: int = 0,
            diagonal: bool = False,
    ) -> int:
        """Add a enemy at the given position that moves toward the player and return its id.

        Chase enemies move toward the player at each step using the A* algorithm.
        """
        e = self.em.create()
        self.em.add_component(e, component.Identity(Entity.ENEMY))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.Solid(allow=(self.player,)))
        self.em.add_component(e, component.Deadly())
        self.em.add_component(
            e,
            component.ChaseAI(
                target=self.player,
                steps=steps,
                stagger=stagger,
                tick=tick,
                diagonal=diagonal,
            ),
        )
        return e

    def add_patrol_enemy(self, x: int, y: int, delta: tuple[int, int]) -> int:
        """Add an enemy at the given position with a fixed movement pattern and return its id.

        Patrol enemies move by delta each step tick.
        If a movement fails, they move in the opposite direction.
        """
        e = self.em.create()
        self.em.add_component(e, component.Identity(Entity.ENEMY))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.Solid(allow=(self.player,)))
        self.em.add_component(e, component.Deadly())
        self.em.add_component(e, component.PatrolAI(delta=delta))
        return e

    def add_fixed_enemy(self, x: int, y: int, moves: list[tuple[int, int]]) -> int:
        """Add an enemy at the given position with a fixed movement pattern and return its id.

        Fixed enemies cycle through a list or pre-specified list of movements.
        """
        e = self.em.create()
        self.em.add_component(e, component.Identity(Entity.ENEMY))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.Solid(allow=(self.player,)))
        self.em.add_component(e, component.Deadly())
        self.em.add_component(e, component.FixedAI(moves=moves))
        return e

    def add_mirror_enemy(self, x: int, y: int, mirror_x: bool = False, mirror_y: bool = True) -> int:
        """Add an enemy at the given position that mirrors the player's movement and return its id.

        Mirror enemies copy or mirror the player movement along a given axis.
        """
        e = self.em.create()
        self.em.add_component(e, component.Identity(Entity.ENEMY))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.Solid(allow=(self.player,)))
        self.em.add_component(e, component.Deadly())
        self.em.add_component(e, component.MirrorAI(target=self.player, mirror_x=mirror_x, mirror_y=mirror_y))
        return e

    def add_snake_enemy(
            self,
            positions: tuple[tuple[int, int], ...],
            delta: tuple[int, int] | None = None
    ) -> tuple[int, ...]:
        """Add multiple enemies that move as if connected and return their ids."""
        entities = [self.em.create() for _ in positions]
        entities.append(None)
        head = entities[0]
        for i, (x, y) in enumerate(positions):
            e = entities[i]
            e_next = entities[i + 1]
            self.em.add_component(e, component.Identity(Entity.ENEMY))
            self.em.add_component(e, component.Active())
            self.em.add_component(e, component.Position(x, y))
            self.em.add_component(e, component.Solid(allow=(self.player,)))
            self.em.add_component(e, component.Deadly())
            self.em.add_component(e, component.SnakeAI(target=self.player, head=head, next=e_next, delta=delta))

        return tuple(entities)

    def add_switch(
            self,
            position: tuple[int, int],
            active_switchable_positions: list[tuple[int, int]] | None = None,
            inactive_switchable_positions: list[tuple[int, int]] | None = None,
    ) -> dict[str, list[int]]:
        active_switchable_positions = active_switchable_positions or []
        inactive_switchable_positions = inactive_switchable_positions or []
        if not (active_switchable_positions or inactive_switchable_positions):
            raise ValueError(
                'at least one of active_switchable_positions or '
                'inactive_switchable_positions must be provided'
            )

        switch = self.em.create()
        self.em.add_component(switch, component.Identity(Entity.SWITCH_PRESSABLE))
        self.em.add_component(switch, component.Active())
        self.em.add_component(switch, component.Position(*position))
        self.em.add_component(switch, component.Switch())

        switchables = []
        switchables.extend([(True, p) for p in active_switchable_positions])
        switchables.extend([(False, p) for p in inactive_switchable_positions])
        for active, (x, y) in switchables:
            switchable = self.add_wall(x, y)
            self.em.add_component(switchable, component.Switchable(triggers=[switch]))
            if not active:
                self.em.remove_component(switchable, component.Active)

    def add_switch_toggle(
            self,
            position1: tuple[int, int],
            position2: tuple[int, int],
            active_switchable_positions: list[tuple[int, int]] | None = None,
            inactive_switchable_positions: list[tuple[int, int]] | None = None,
    ) -> dict[str, list[int]]:
        active_switchable_positions = active_switchable_positions or []
        inactive_switchable_positions = inactive_switchable_positions or []
        if not (active_switchable_positions or inactive_switchable_positions):
            raise ValueError(
                'at least one of active_switchable_positions or '
                'inactive_switchable_positions must be provided'
            )

        switch_configs = [
            (self.em.create(), position1, True),
            (self.em.create(), position2, False),
        ]
        switches = [s for s, *_ in switch_configs]

        for switch, position, pressable in switch_configs:
            entity_type = Entity.SWITCH_PRESSABLE if pressable else Entity.SWITCH_UNPRESSABLE
            self.em.add_component(switch, component.Identity(entity_type))
            self.em.add_component(switch, component.Active())
            self.em.add_component(switch, component.Position(*position))
            self.em.add_component(switch, component.Switch(group=switches, pressable=pressable))

        switchables = []
        switchables.extend([(True, p) for p in active_switchable_positions])
        switchables.extend([(False, p) for p in inactive_switchable_positions])
        for active, (x, y) in switchables:
            switchable = self.add_wall(x, y)
            self.em.add_component(switchable, component.Switchable(triggers=switches))
            if not active:
                self.em.remove_component(switchable, component.Active)

    @classmethod
    def format_method_stubs(cls, prefix: str = 'add_'):
        import inspect

        def make_method_stub(attr: str):
            method = getattr(cls, attr)
            signature = inspect.signature(method)
            result = f'def {method.__name__}{signature}:'

            doc = inspect.getdoc(method)
            if doc:
                doc = f'"""{doc}\n"""'
                doc = '\n'.join(4 * ' ' + line for line in doc.split('\n'))
                result = f'{result}\n{doc}'

            result = f'{result}\n    pass'
            return '\n'.join(4 * ' ' + line for line in result.split('\n'))

        attrs = [attr for attr in dir(cls) if attr.startswith(prefix)]
        sections = [make_method_stub(attr) for attr in attrs]
        methods_stubs = '\n\n'.join(sections)
        return f'class {cls.__name__}:\n{methods_stubs}'
