import heapq

from gridlab.utils import grid_distance, grid_neighbors


class PriorityQueue:
    def __init__(self):
        # now storing priorities that can be tuples
        self.elements: list[tuple[tuple[int, int], tuple[int, int]]] = []

    def empty(self) -> bool:
        return not self.elements

    def put(self, item: tuple[int, int], priority: tuple[int, int]):
        # priority is now (f_cost, tie_breaker)
        heapq.heappush(self.elements, (priority, item))

    def get(self) -> tuple[int, int]:
        return heapq.heappop(self.elements)[1]


def heuristic_cost(a: tuple[int, int], b: tuple[int, int], diagonal: bool = False) -> int:
    x1, y1 = a
    x2, y2 = b
    if diagonal:
        return max(abs(x1 - x2), abs(y1 - y2))

    return abs(x1 - x2) + abs(y1 - y2)


def in_bounds(grid: list[list[bool]], position: tuple[int, int]) -> bool:
    width = len(grid[0])
    height = len(grid)
    x, y = position
    return 0 <= x < width and 0 <= y < height


def is_passable(grid: list[list[bool]], position: tuple[int, int]) -> bool:
    (x, y) = position
    return grid[y][x]


def search(
    grid: list[list[bool]],
    start: tuple[int, int],
    goal: tuple[int, int],
    diagonal: bool = False,
    fallback: bool = False,
) -> list[tuple[int, int]] | None:

    frontier = PriorityQueue()
    # initial priority is (0, 0): zero cost, zero tie-breaker
    frontier.put(start, (0, 0))

    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    cost_so_far: dict[tuple[int, int], int] = {start: 0}

    while not frontier.empty():
        current = frontier.get()
        if current == goal:
            break

        new_cost = cost_so_far[current] + 1
        neighbors = grid_neighbors(current, diagonal=diagonal)
        neighbors = [
            n for n in neighbors
            if in_bounds(grid, n) and is_passable(grid, n)
        ]

        # figure out which axis has the larger gap right now
        dx = abs(current[0] - goal[0])
        dy = abs(current[1] - goal[1])
        prefer_horizontal = (dx >= dy)

        for neighbor in neighbors:
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost

                # standard A* score
                score = new_cost + grid_distance(neighbor, goal, diagonal=diagonal)

                # tie-breaker: 0 if this step moves along the preferred axis
                if prefer_horizontal:
                    axis_move = (neighbor[0] != current[0])
                else:
                    axis_move = (neighbor[1] != current[1])

                tie = 0 if axis_move else 1

                frontier.put(neighbor, (score, tie))
                came_from[neighbor] = current

    if goal not in came_from:
        if not fallback:
            return None

        closest = min(came_from.keys(), key=lambda other: grid_distance(other, goal, diagonal=diagonal))
        if closest == start:
            return None  # no moves

        goal = closest

    path: list[tuple[int, int]] = [goal]
    while True:
        prev = came_from[path[-1]]
        if prev == start:
            path.reverse()
            return path

        path.append(prev)
