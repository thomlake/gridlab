from gridlab.action import Action
from gridlab.component import (
    ChaseAI,
    Deadly,
    Door,
    Key,
    KeyCollector,
    FixedAI,
    Goal,
    MirrorAI,
    PatrolAI,
    Position,
    PositionDelta,
    Pushable,
    Pusher,
    Solid,
    Timer,
    TimerReset,
)
from gridlab.entity import EntityManager
from gridlab.grid import Grid
from gridlab.state import State
from gridlab import a_star


# class MovementSystem:
#     def __init__(self, em: EntityManager, state: State, grid: Grid):
#         self.em = em
#         self.state = state
#         self.grid = grid

#     def __call__(self):
#         if self.state.is_finished:
#             return

#         position_delta_map: dict[int, PositionDelta] = self.em.get(PositionDelta)
#         position_delta_map.clear()

#         movement_request_map: dict[int, MovementRequest] = self.em.get(MovementRequest)
#         for ent, move in movement_request_map.items():
#             self.move(ent, dx=move.x, dy=move.y)

#         movement_request_map.clear()


def move(em: EntityManager, grid: Grid, ent: int, dx: int, dy: int) -> bool:
    old_position_delta = em.get(PositionDelta).get(ent)
    if old_position_delta:
        em.remove_component(ent, old_position_delta)

    position_map: dict[int, Position] = em.get(Position)
    pusher_map: dict[int, Pusher] = em.get(Pusher)
    pushable_map: dict[int, Pushable] = em.get(Pushable)
    solid_map: dict[int, Solid] = em.get(Solid)

    current = position_map[ent]
    target = Position(current.x + dx, current.y + dy)

    # 1) Out of bounds?
    if not grid.inbounds(target.x, target.y):
        return False

    # 2) Find obstacles
    for other, position in position_map.items():
        if position != target:
            continue

        # If pushable, try to push it
        if other in pushable_map:
            if ent not in pusher_map:
                return False  # ent isn't a pusher
            elif not move(em, grid, other, dx, dy):
                return False  # pushable couldn't be pushed

        # Otherwise, block movement
        solid = solid_map.get(other)
        if solid and ent not in solid.allow:
            return False

    # 3) Nothing blocking (all pushable blockers moved), so we move
    position_map[ent] = target
    em.add_component(ent, PositionDelta(dx, dy))
    return True


class ActionSystem:
    def __init__(self, em: EntityManager, state: State, grid: Grid):
        self.em = em
        self.state = state
        self.grid = grid
        self.action_queue: list[tuple[str, Action]] = []

    def add_actions(self, actions: list[tuple[str, Action]]):
        self.action_queue.extend(actions)

    def __call__(self):
        if self.state.is_finished:
            return

        for ent, action in self.action_queue:
            dx, dy = action.move_delta
            move(self.em, self.grid, ent, dx, dy)

        self.action_queue.clear()


class ChaseAISystem:
    def __init__(self, em: EntityManager, state: State, grid: Grid):
        self.em = em
        self.state = state
        self.grid = grid

    def __call__(self):
        if self.state.is_finished:
            return

        ai_map: dict[int, ChaseAI] = self.em.get(ChaseAI)
        position_map: dict[int, Position] = self.em.get(Position)
        solid_map: dict[int, Solid] = self.em.get(Solid)

        grid = [[True for _ in range(self.grid.width)] for _ in range(self.grid.height)]
        for ent in solid_map.keys():
            pos = position_map[ent]
            grid[pos.y][pos.x] = False

        for ent, ai in ai_map.items():
            entity_pos = position_map.get(ent)
            target_pos = position_map.get(ai.target)
            if not (entity_pos and target_pos):
                continue

            dx, dy = a_star.search(
                grid,
                start=(entity_pos.x, entity_pos.y),
                goal=(target_pos.x, target_pos.y),
            )
            move(self.em, self.grid, ent, dx, dy)


class MirrorAISystem:
    def __init__(self, em: EntityManager, state: State, grid: Grid):
        self.em = em
        self.state = state
        self.grid = grid

    def __call__(self):
        if self.state.is_finished:
            return

        ai_map: dict[int, MirrorAI] = self.em.get(MirrorAI)
        position_delta_map: dict[int, PositionDelta] = self.em.get(PositionDelta)

        for ent, ai in ai_map.items():
            delta = position_delta_map.get(ai.target)
            if not delta:
                continue

            move(self.em, self.grid, ent, delta.x, -delta.y)


class PatrolAISystem:
    def __init__(self, em: EntityManager, state: State, grid: Grid):
        self.em = em
        self.state = state
        self.grid = grid

    def __call__(self):
        if self.state.is_finished:
            return

        ai_map: dict[int, PatrolAI] = self.em.get(PatrolAI)
        for ent, ai in ai_map.items():
            dx, dy = ai.delta
            if not move(self.em, self.grid, ent, dx, dy):
                dx, dy = -dx, -dy
                move(self.em, self.grid, ent, dx, dy)
                ai.delta = dx, dy


class FixedAISystem:
    def __init__(self, em: EntityManager, state: State, grid: Grid):
        self.em = em
        self.state = state
        self.grid = grid

    def __call__(self):
        if self.state.is_finished:
            return

        ai_map: dict[int, FixedAI] = self.em.get(FixedAI)
        for ent, ai in ai_map.items():
            dx, dy = ai.moves[ai.move_index]
            move(self.em, self.grid, ent, dx, dy)
            ai.move_index = (ai.move_index + 1) % len(ai.moves)


class DoorSystem:
    def __init__(self, em: EntityManager, state: State):
        self.em = em
        self.state = state

    def __call__(self):
        if self.state.is_finished:
            return

        door_map: dict[int, Door] = self.em.get(Door)
        key_map: dict[int, Key] = self.em.get(Key)
        collector_map: dict[int, KeyCollector] = self.em.get(KeyCollector)
        position_map: dict[int, Position] = self.em.get(Position)

        for collector_ent, collector in collector_map.items():
            collector_pos = position_map[collector_ent]
            keys_remove = set()
            for key_ent, _ in key_map.items():
                key_pos = position_map[key_ent]
                if key_pos == collector_pos:
                    keys_remove.add(key_ent)
                    collector.count += 1

            self.em.remove_all(keys_remove)

            if collector.count < 1:
                continue

            doors_remove = set()
            for door_ent, _ in door_map.items():
                door_pos = position_map[door_ent]
                if collector_pos.is_adjacent(door_pos):
                    collector.count -= 1
                    doors_remove.add(door_ent)

            self.em.remove_all(doors_remove)


class TimerSystem:
    def __init__(
            self,
            em: EntityManager,
            state: State,
            player: int,
    ):
        self.em = em
        self.state = state
        self.player = player

    def __call__(self):
        timer_map: dict[int, Timer] = self.em.get(Timer)
        if not timer_map:
            return

        timer_reset_map: dict[int, TimerReset] = self.em.get(TimerReset)
        position_map: dict[int, Position] = self.em.get(Position)
        player_pos = position_map[self.player]

        timer_resets_remove = set()
        for ent, _ in timer_reset_map.items():
            timer_reset_pos = position_map[ent]
            if player_pos == timer_reset_pos:
                timer_resets_remove.add(ent)

        self.em.remove_all(timer_resets_remove)

        for ent, timer in timer_map.items():
            timer.tick += 1
            if timer_resets_remove:
                timer.tick = 0
            elif timer.tick >= timer.limit and not self.state.goal_reached:
                self.state.player_dead = True


class DeathSystem:
    def __init__(
            self,
            em: EntityManager,
            state: State,
            player: int,
    ):
        self.em = em
        self.state = state
        self.player = player

    def __call__(self):
        if self.state.is_finished:
            return

        position_map: dict[int, Position] = self.em.get(Position)
        deadly_map: dict[int, Deadly] = self.em.get(Deadly)
        position = position_map[self.player]
        overlap = [
            e for e, p in position_map.items()
            if e != self.player and (p.x, p.y) == (position.x, position.y)
        ]
        if not any(e in deadly_map for e in overlap):
            return

        self.state.player_dead = True


class GoalSystem:
    def __init__(
            self,
            em: EntityManager,
            state: State,
            player: int,
    ):
        self.em = em
        self.state = state
        self.player = player

    def __call__(self):
        if self.state.is_finished:
            return

        position_map: dict[int, Position] = self.em.get(Position)
        goal_map: dict[int, Goal] = self.em.get(Goal)
        p1 = position_map[self.player]
        goal_positions = [position_map[e] for e in goal_map]
        if any((p1.x, p1.y) == (p2.x, p2.y) for p2 in goal_positions):
            self.state.goal_reached = True
