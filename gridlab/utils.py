
def grid_distance(a: tuple[int, int], b: tuple[int, int], diagonal: bool = False) -> int:
    x1, y1 = a
    x2, y2 = b
    if diagonal:
        return max(abs(x1 - x2), abs(y1 - y2))

    return abs(x1 - x2) + abs(y1 - y2)


def grid_neighbors(
        position: tuple[int, int],
        diagonal: bool = False,
) -> list[tuple[int, int]]:
    x, y = position
    neighbors = [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]
    if diagonal:
        neighbors = [(x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1), *neighbors]

    return neighbors
