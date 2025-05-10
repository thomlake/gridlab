from dataclasses import dataclass


@dataclass
class Grid:
    width: int
    height: int

    def inbounds(self, x, y):
        return (0 <= x < self.width and 0 <= y < self.height)
