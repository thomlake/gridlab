# // openSet is the nodes that have calculated cost
# // closedSet is the nodes that haven't calculated cost yet
import heapq


class PriorityQueue:
    def __init__(self):
        self.elements: list[tuple[int, tuple[int, int]]] = []

    def empty(self) -> bool:
        return not self.elements

    def put(self, item: tuple[int, int], priority: int):
        heapq.heappush(self.elements, (priority, item))

    def get(self) -> tuple[int, int]:
        return heapq.heappop(self.elements)[1]


def heuristic_cost(a: tuple[int, int], b: tuple[int, int]) -> int:
    x1, y1 = a
    x2, y2 = b
    return abs(x1 - x2) + abs(y1 - y2)


def in_bounds(grid: list[list[bool]], position: tuple[int, int]) -> bool:
    width = len(grid[0])
    height = len(grid)
    x, y = position
    return 0 <= x < width and 0 <= y < height


def is_passable(grid: list[list[bool]], position: tuple[int, int]) -> bool:
    (x, y) = position
    return grid[y][x]


def get_neighbors(grid: list[list[bool]], position: tuple[int, int]) -> list[tuple[int, int]]:
    x, y = position
    neighbors = [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]  # E W N S
    # make paths straight hack
    if (x + y) % 2 == 0:
        neighbors = reversed(neighbors)  # S N W E

    results = [n for n in neighbors if in_bounds(grid, n) and is_passable(grid, n)]
    return results


def search(
        grid: list[list[bool]],
        start: tuple[int, int],
        goal: tuple[int, int],
) -> tuple[int, int] | None:

    frontier = PriorityQueue()
    frontier.put(start, 0)

    came_from: dict[tuple[int, int], tuple[int, int] | None] = {}
    came_from[start] = None

    cost_so_far: dict[tuple[int, int], int] = {}
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()
        if current == goal:
            break

        for next in get_neighbors(grid, current):
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic_cost(next, goal)
                frontier.put(next, priority)
                came_from[next] = current

    if goal not in came_from:
        # no path was found
        return None

    current = goal
    while True:
        previous = came_from[current]
        if previous == start:
            x1, y1 = previous
            x2, y2 = current
            return x2 - x1, y2 - y1
        else:
            current = previous
