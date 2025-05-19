from dataclasses import dataclass


@dataclass
class Grid:
    width: int
    height: int

    def inbounds(self, x, y):
        return (0 <= x < self.width and 0 <= y < self.height)

    # entity_grid: list[list[set[int]]]
    # entity_positions: dict[int, tuple[int, int]]

    # def _update_position(self, ent: int, x_new: int, y_new: int):
    #     x_old, y_old = self.entity_positions[ent]
    #     self.entity_grid[x_old][y_old].remove(ent)
    #     self.entity_grid[x_new][y_new].add(ent)
    #     self.entity_positions[ent] = x_new, y_new

    # def move(self, ent: int, dx: int, dy: int) -> bool:
    #     x_old, y_old = self.entity_positions[ent]
    #     x_new, y_new = x_old + dx, y_old + dy

    #     # 1) Out of bounds?
    #     if not self.inbounds(x_new, y_new):
    #         return False

    #     others = self.entity_grid[x_new, y_new] - {ent}

    #     # 2) Find obstacles
    #     if not others:
    #         self.update_position(ent, x_new, y_new)
    #         return True

    #     for other in others:

    #     # 2) Find obstacles
    #     for other, position in position_map.items():
    #         if position != target:
    #             continue

    #         # If pushable, try to push it
    #         if other in pushable_map:
    #             if ent not in pusher_map:
    #                 return False  # ent isn't a pusher
    #             elif not move(em, grid, other, dx, dy):
    #                 return False  # pushable couldn't be pushed

    #         # Otherwise, block movement
    #         solid = solid_map.get(other)
    #         if solid and ent not in solid.allow:
    #             return False

    #     # 3) Nothing blocking (all pushable blockers moved), so we move
    #     position_map[ent] = target
    #     em.add_component(ent, PositionDelta(dx, dy))
    #     return True
