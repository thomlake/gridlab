import string
from typing import Callable

from gridlab import component, system
from gridlab.action import Action
from gridlab.difficulty import Difficulty
from gridlab.entity import Entity, EntityManager
from gridlab.grid import Grid
from gridlab.layer import Layer
from gridlab.state import State


class World:
    # Metadata
    name: str = '???'
    difficulty: Difficulty = Difficulty.UNCLASSIFIED
    entity_types: list[Entity] = []

    # State
    state: State
    em: EntityManager
    turn: int = 1

    # Private
    _grid: Grid | None
    _systems: list[Callable[[], None]] | None
    _action_system: system.ActionSystem | None
    _player: int | None

    def __init__(self):
        self.reset()

    def build(self) -> None:
        """Initialize the world and add entities."""
        raise NotImplementedError()

    def solve(self) -> list[Action]:
        """Return the list of moves that result in success."""
        raise NotImplementedError()

    @property
    def grid(self):
        if self._grid is None:
            raise ValueError('grid not set!')

        return self._grid

    @property
    def systems(self):
        if self._systems is None:
            raise ValueError('systems not set!')

        return self._systems

    @property
    def action_system(self):
        if self._action_system is None:
            raise ValueError('action_system not set!')

        return self._action_system

    @property
    def player(self):
        if self._player is None:
            raise ValueError('player not set!')

        return self._player

    def create_grid(self, width: int, height: int):
        self._grid = Grid(width, height)

    def register_player(self, ent: int):
        if self._player is not None:
            raise ValueError('player already registered!')

        self._player = ent

    def reset(self):
        self.state = State()
        self.em = EntityManager()
        self.turn = 1
        self._grid = None
        self._systems = None
        self._action_system = None
        self._player = None
        self.build()
        self.setup_systems()

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

        position_delta_system = system.PositionDeltaSystem(self.em, self.state)
        death_system = system.DeathSystem(self.em, self.state, player=self.player)
        goal_system = system.GoalSystem(self.em, self.state, player=self.player)
        timer_system = system.TimerSystem(self.em, self.state, player=self.player)
        door_system = system.DoorSystem(self.em, self.state)
        switch_system = system.SwitchSystem(self.em, self.state)

        self._action_system = action_system
        self._systems = [
            position_delta_system,
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
        assert Entity.PLAYER in self.entity_types, 'missing PLAYER'

        e = self.em.create()
        self.register_player(e)

        self.em.add_component(e, component.Identity(Entity.PLAYER))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.Pusher())
        self.em.add_component(e, component.KeyCollector())
        self.em.add_component(e, component.SwitchPresser())
        return e

    def add_goal(self, x: int, y: int) -> int:
        """Add a goal at the given position and return its id."""
        assert Entity.GOAL in self.entity_types, 'missing GOAL'

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
        assert Entity.TIMER_RESET in self.entity_types, 'missing TIMER_RESET'

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
        assert Entity.KEY in self.entity_types, 'missing KEY'

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
        assert Entity.FOG in self.entity_types, 'missing FOG'

        e = self.em.create()
        self.em.add_component(e, component.Identity(Entity.FOG))
        self.em.add_component(e, component.Active())
        self.em.add_component(e, component.Position(x, y))
        self.em.add_component(e, component.Fog())
        return e

    def add_wall(self, x: int, y: int) -> int:
        """Add a wall at the given position and return its id.

        Walls cannot be moved through by any entities."""
        assert Entity.WALL in self.entity_types, 'missing WALL'

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
        assert Entity.DOOR in self.entity_types, 'missing DOOR'

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
        assert Entity.BLOCK in self.entity_types, 'missing BLOCK'

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
        assert Entity.SPIKE in self.entity_types, 'missing SPIKE'

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
        assert Entity.ENEMY in self.entity_types, 'missing ENEMY'

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
        assert Entity.ENEMY in self.entity_types, 'missing ENEMY'

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
        assert Entity.ENEMY in self.entity_types, 'missing ENEMY'

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
        assert Entity.ENEMY in self.entity_types, 'missing ENEMY'

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
        assert Entity.ENEMY in self.entity_types, 'missing ENEMY'

        entities = [self.em.create() for _ in positions]
        head = entities[0]
        for i, (x, y) in enumerate(positions):
            e = entities[i]
            next = entities[i + 1] if i + 1 < len(entities) else None
            self.em.add_component(e, component.Identity(Entity.ENEMY))
            self.em.add_component(e, component.Active())
            self.em.add_component(e, component.Position(x, y))
            self.em.add_component(e, component.Solid(allow=(self.player,)))
            self.em.add_component(e, component.Deadly())
            self.em.add_component(e, component.SnakeAI(target=self.player, head=head, next=next, delta=delta))

        return tuple(entities)

    def add_switch(
            self,
            position: tuple[int, int],
            active_switchable_positions: list[tuple[int, int]] | None = None,
            inactive_switchable_positions: list[tuple[int, int]] | None = None,
    ):
        assert Entity.SWITCH_PRESSABLE in self.entity_types, 'missing SWITCH_PRESSABLE'

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
    ):
        assert Entity.SWITCH_PRESSABLE in self.entity_types, 'missing SWITCH_PRESSABLE'
        assert Entity.SWITCH_UNPRESSABLE in self.entity_types, 'missing SWITCH_UNPRESSABLE'

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

    def _preprocess_build_layer(self, text: str):
        layer = Layer(text)
        if self._grid is None:
            self.create_grid(layer.width, layer.height)
        else:
            assert layer.width == self.grid.width
            assert layer.height == self.grid.height

        return layer

    def populate(self, text: str, initializers: dict[str, Callable[[int, int], int]]):
        layer = self._preprocess_build_layer(text)
        processed_chars: set[str] = set()
        for char, method in initializers.items():
            processed_chars.add(char)
            if method is None:
                continue

            for x, y in layer.positions_map.get(char, []):
                method(x, y)

        skipped_chars = [c for c in layer.positions_map.keys() if c not in processed_chars]
        if skipped_chars:
            raise ValueError(f"unprocessed chars: {', '.join(skipped_chars)}")

    def populate_switches(self, text: str):
        layer = self._preprocess_build_layer(text)
        processed_chars: set[str] = set()

        switch_chars = [str(i) for i in range(1, 10)]
        active_chars = string.ascii_uppercase[:len(switch_chars)]
        inactive_chars = string.ascii_lowercase[:len(switch_chars)]

        for i, c_switch in enumerate(switch_chars):
            switch_positions = layer.positions_map.get(c_switch)
            if not switch_positions:
                break

            switch_position, = switch_positions

            c_active = active_chars[i]
            active_positions = layer.positions_map.get(c_active, [])

            c_inactive = inactive_chars[i]
            inactive_positions = layer.positions_map.get(c_inactive, [])

            self.add_switch(
                position=switch_position,
                active_switchable_positions=active_positions,
                inactive_switchable_positions=inactive_positions,
            )

            processed_chars.update([c_switch, c_active, c_inactive])

        def is_skipped_char(c: str):
            if c in processed_chars:
                return False

            return (
                c in switch_chars or
                c in active_chars or
                c in inactive_chars
            )

        skipped_chars = [c for c in layer.positions_map.keys() if is_skipped_char(c)]
        if skipped_chars:
            raise ValueError(f"unprocessed chars: {', '.join(skipped_chars)}")
