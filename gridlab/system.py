from gridlab import a_star
from gridlab.action import Action
from gridlab.component import (
    Active,
    ChaseAI,
    Deadly,
    Door,
    Key,
    KeyCollector,
    Goal,
    Identity,
    MirrorAI,
    PatrolAI,
    Position,
    PositionDelta,
    Pushable,
    Pusher,
    SnakeAI,
    Solid,
    Switch,
    SwitchPresser,
    Switchable,
    Timer,
    TimerReset,
)
from gridlab.entity import Entity, EntityManager
from gridlab.grid import Grid
from gridlab.state import State


def move(em: EntityManager, grid: Grid, ent: int, dx: int, dy: int) -> bool:
    active_map = em.get(Active)
    position_map = em.get(Position)
    pusher_map = em.get(Pusher)
    pushable_map = em.get(Pushable)
    solid_map = em.get(Solid)

    current = position_map[ent]
    target = Position(current.x + dx, current.y + dy)

    # 1) Out of bounds?
    if not grid.inbounds(target.x, target.y):
        return False

    # 2) Find obstacles
    for other, solid in solid_map.items():
        if other not in active_map:
            continue

        position = position_map[other]
        if position != target:
            continue

        # If pushable, try to push it
        if other in pushable_map:
            if ent not in pusher_map:
                return False  # ent isn't a pusher
            elif not move(em, grid, other, dx, dy):
                return False  # pushable couldn't be pushed
        elif solid.is_blocked(ent):
            return False

    # 3) Nothing blocking
    position_map[ent] = target
    em.add_component(ent, PositionDelta(dx, dy))
    return True


def teleport(em: EntityManager, grid: Grid, ent: int, x: int, y: int) -> bool:
    position_map = em.get(Position)
    current = position_map[ent]

    # 1) Out of bounds?
    if not grid.inbounds(x, y):
        return False

    dx = x - current.x
    dy = y - current.y
    position_map[ent] = Position(x, y)
    em.add_component(ent, PositionDelta(dx, dy))
    return True


class PositionDeltaSystem:
    def __init__(self, em: EntityManager, state: State,):
        self.em = em
        self.state = state

    def __call__(self):
        if self.state.is_finished:
            return

        position_delta_map = self.em.get(PositionDelta)
        position_delta_map.clear()


class ActionSystem:
    def __init__(self, em: EntityManager, state: State, grid: Grid):
        self.em = em
        self.state = state
        self.grid = grid
        self.action_queue: list[tuple[int, Action]] = []

    def add_actions(self, actions: list[tuple[int, Action]]):
        self.action_queue.extend(actions)

    def __call__(self):
        if self.state.is_finished:
            return

        for ent, action in self.action_queue:
            if action == Action.NONE:
                continue

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

        active_map = self.em.get(Active)
        ai_map = self.em.get(ChaseAI)
        position_map = self.em.get(Position)
        solid_map = self.em.get(Solid)

        def make_grid(ent: int):
            grid = [[True for _ in range(self.grid.width)] for _ in range(self.grid.height)]
            for other in solid_map.keys():
                if other != ent and other in active_map:
                    pos = position_map[other]
                    grid[pos.y][pos.x] = False

            return grid

        for ent, ai in ai_map.items():
            if ent not in active_map:
                continue

            ai.tick += 1
            if ai.tick % ai.stagger != 0:
                continue

            entity_pos = position_map[ent]
            target_pos = position_map[ai.target]

            grid = make_grid(ent)
            x, y = entity_pos.x, entity_pos.y
            path = a_star.search(
                grid,
                start=(x, y),
                goal=(target_pos.x, target_pos.y),
                diagonal=ai.diagonal,
            )
            remain = ai.steps
            while path and remain > 0:
                (x_new, y_new), *path = path
                dx = x_new - x
                dy = y_new - y
                if not move(self.em, self.grid, ent, dx, dy):
                    break

                remain -= 1
                x, y = x_new, y_new


class MirrorAISystem:
    def __init__(self, em: EntityManager, state: State, grid: Grid):
        self.em = em
        self.state = state
        self.grid = grid

    def __call__(self):
        if self.state.is_finished:
            return

        active_map = self.em.get(Active)
        ai_map = self.em.get(MirrorAI)
        position_delta_map = self.em.get(PositionDelta)

        for ent, ai in ai_map.items():
            if ent not in active_map:
                continue

            delta = position_delta_map.get(ai.target)
            if not delta:
                continue

            dx, dy = ai.reflect(delta.x, delta.y)
            move(self.em, self.grid, ent, dx, dy)


class PatrolAISystem:
    def __init__(self, em: EntityManager, state: State, grid: Grid):
        self.em = em
        self.state = state
        self.grid = grid

    def __call__(self):
        if self.state.is_finished:
            return

        active_map = self.em.get(Active)
        ai_map = self.em.get(PatrolAI)

        change_dir_map: dict[int, PatrolAI] = {}

        for ent, ai in ai_map.items():
            if ent not in active_map:
                continue

            dx, dy = ai.delta
            if not move(self.em, self.grid, ent, dx, dy):
                change_dir_map[ent] = ai

        for ent, ai in change_dir_map.items():
            dx, dy = ai.delta
            dx, dy = -dx, -dy
            move(self.em, self.grid, ent, dx, dy)
            ai.delta = dx, dy


class SnakeAISystem:
    def __init__(self, em: EntityManager, state: State, grid: Grid):
        self.em = em
        self.state = state
        self.grid = grid

    def __call__(self):
        if self.state.is_finished:
            return

        active_map = self.em.get(Active)
        ai_map = self.em.get(SnakeAI)
        position_map = self.em.get(Position)
        solid_map = self.em.get(Solid)

        def make_grid(ent: int):
            grid = [[True for _ in range(self.grid.width)] for _ in range(self.grid.height)]
            for other in solid_map.keys():
                if other != ent and other in active_map:
                    pos = position_map[other]
                    grid[pos.y][pos.x] = False

            return grid

        def shift(ent: int | None, x: int, y: int):
            while ent:
                ai = ai_map[ent]
                position = position_map[ent]
                teleport(self.em, self.grid, ent, x, y)
                x, y = position.x, position.y
                ent = ai.next

        for ent, ai in ai_map.items():
            if ent not in active_map:
                continue

            if ent != ai.head:
                continue

            entity_pos = position_map[ent]
            target_pos = position_map[ai.target]

            if not ai.delta:
                grid = make_grid(ent)
                path = a_star.search(
                    grid,
                    start=(entity_pos.x, entity_pos.y),
                    goal=(target_pos.x, target_pos.y),
                    diagonal=ai.diagonal,
                )
                remain = ai.steps
                x, y = entity_pos.x, entity_pos.y
                while path and remain > 0:
                    (x_new, y_new), *path = path
                    dx = x_new - x
                    dy = y_new - y
                    if not move(self.em, self.grid, ent, dx, dy):
                        break

                    shift(ai.next, x, y)
                    remain -= 1
                    x, y = x_new, y_new
            else:
                x, y = entity_pos.x, entity_pos.y
                dx, dy = ai.delta
                remain = ai.steps
                while remain > 0:
                    entity_pos = position_map[ent]
                    x, y = entity_pos.x, entity_pos.y
                    if move(self.em, self.grid, ent, dx, dy):
                        shift(ai.next, x, y)
                    else:
                        dx, dy = -dx, -dy
                        if move(self.em, self.grid, ent, dx, dy):
                            shift(ai.next, x, y)

                    remain -= 1

                ai.delta = dx, dy


class DoorSystem:
    def __init__(self, em: EntityManager, state: State):
        self.em = em
        self.state = state

    def __call__(self):
        if self.state.is_finished:
            return

        active_map = self.em.get(Active)
        door_map = self.em.get(Door)
        key_map = self.em.get(Key)
        collector_map = self.em.get(KeyCollector)
        position_map = self.em.get(Position)

        for collector_ent, collector in collector_map.items():
            if collector_ent not in active_map:
                continue

            collector_pos = position_map[collector_ent]
            keys_remove: list[int] = []
            for key_ent, _ in key_map.items():
                if key_ent not in active_map:
                    continue

                key_pos = position_map[key_ent]
                if key_pos == collector_pos:
                    keys_remove.append(key_ent)
                    collector.count += 1

            self.em.remove_all(keys_remove)

            if collector.count < 1:
                continue

            doors_remove: list[int] = []
            for door_ent, _ in door_map.items():
                if door_ent not in active_map:
                    continue

                door_pos = position_map[door_ent]
                if collector_pos.is_adjacent(door_pos):
                    collector.count -= 1
                    doors_remove.append(door_ent)

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
        timer_map = self.em.get(Timer)
        if not timer_map:
            return

        active_map = self.em.get(Active)
        timer_reset_map = self.em.get(TimerReset)
        position_map = self.em.get(Position)
        player_pos = position_map[self.player]

        timer_resets_remove: list[int] = []
        for ent, _ in timer_reset_map.items():
            if ent not in active_map:
                continue

            timer_reset_pos = position_map[ent]
            if player_pos == timer_reset_pos:
                timer_resets_remove.append(ent)

        self.em.remove_all(timer_resets_remove)

        expired_entities: list[int] = []
        for ent, timer in timer_map.items():
            if ent not in active_map:
                continue

            timer.tick += 1
            if timer_resets_remove:
                timer.tick = 0
            elif timer.tick >= timer.limit and not self.state.goal_reached:
                if ent == self.player:
                    self.state.player_dead = True
                else:
                    expired_entities.append(ent)

        self.em.remove_all(expired_entities)


class SwitchSystem:
    def __init__(self, em: EntityManager, state: State):
        self.em = em
        self.state = state

    def __call__(self):
        if self.state.is_finished:
            return

        active_map = self.em.get(Active)
        id_map = self.em.get(Identity)
        position_map = self.em.get(Position)
        switch_map = self.em.get(Switch)
        switchable_map = self.em.get(Switchable)
        switch_presser_map = self.em.get(SwitchPresser)

        # Collect switches that are overlapped by trigger entities this tick
        triggered_switches: dict[int, bool] = {}
        for switch_ent, switch in switch_map.items():
            switch_pos = position_map[switch_ent]
            overlap = any(
                True for e, p in position_map.items()
                if e in switch_presser_map and p == switch_pos
            )
            if overlap:
                triggered_switches[switch_ent] = switch.pressable

        # Handle solo and group switches
        for switch_ent, switch in switch_map.items():
            if switch.group is not None:
                # Only the pressable one can be triggered
                if triggered_switches.get(switch_ent):
                    group = switch.group
                    index = group.index(switch_ent)
                    switch.pressed = True
                    switch.pressable = False
                    id_map[switch_ent].type = Entity.SWITCH_UNPRESSABLE

                    # Find the next switch in the group (cycle order)
                    next_idx = (index + 1) % len(group)
                    next_ent = group[next_idx]
                    next_switch = switch_map[next_ent]
                    next_switch.pressable = True
                    next_switch.pressed = False
                    id_map[next_ent].type = Entity.SWITCH_PRESSABLE

                    # Set all other group switches to not pressable/pressed (optional but robust)
                    for other_ent in group:
                        if other_ent not in (switch_ent, next_ent):
                            other = switch_map[other_ent]
                            other.pressable = False
                            other.pressed = False
                            id_map[other_ent].type = Entity.SWITCH_UNPRESSABLE
                else:
                    switch.pressed = False

            else:
                if switch_ent not in triggered_switches:
                    switch.pressed = False
                    switch.pressable = True
                    id_map[switch_ent].type = Entity.SWITCH_PRESSABLE
                elif triggered_switches[switch_ent]:
                    switch.pressed = True
                    switch.pressable = False
                    id_map[switch_ent].type = Entity.SWITCH_UNPRESSABLE
                else:
                    switch.pressed = False
                    switch.pressable = False
                    id_map[switch_ent].type = Entity.SWITCH_UNPRESSABLE

        # Activate/deactivate Switchable entities
        for switchable_ent, switchable in switchable_map.items():
            # If any of the triggers are currently pressed, toggle active state
            if any(switch_map[s].pressed for s in switchable.triggers if s in switch_map):
                if switchable_ent in active_map:
                    active_map.pop(switchable_ent)
                else:
                    active_map[switchable_ent] = Active()


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

        active_map = self.em.get(Active)
        position_map = self.em.get(Position)
        deadly_map = self.em.get(Deadly)
        position = position_map[self.player]
        overlap = [
            e for e, p in position_map.items()
            if e != self.player and e in active_map and p == position
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

        active_map = self.em.get(Active)
        position_map = self.em.get(Position)
        goal_map = self.em.get(Goal)
        p1 = position_map[self.player]
        goal_positions = [position_map[e] for e in goal_map if e in active_map]
        if any((p1.x, p1.y) == (p2.x, p2.y) for p2 in goal_positions):
            self.state.goal_reached = True


class StatusSystem:
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
