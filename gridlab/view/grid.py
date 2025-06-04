from gridlab.component import Active, Identity, Position
from gridlab.entity import Entity
from gridlab.view import terminal_style
from gridlab.view.base import View
from gridlab.view.theme import Symbol, Theme
from gridlab.world import World


RENDER_ORDER = [
    Entity.GOAL_REACHED,
    Entity.PLAYER_DIED,
    Entity.FOG,
    Entity.PLAYER,
    Entity.BLOCK,
    Entity.DOOR,
    Entity.WALL,
    Entity.ENEMY,
    Entity.SPIKE,
    Entity.GOAL,
    Entity.KEY,
    Entity.TIMER_RESET,
    Entity.SWITCH_PRESSABLE,
    Entity.SWITCH_UNPRESSABLE,
]


def _create_render_order_map():
    return {e_type: i for i, e_type in enumerate(reversed(RENDER_ORDER))}


RENDER_PRIORITY = _create_render_order_map()


class TextGridView(View):
    def entity_symbol_grid(self, world: World, theme: Theme) -> list[list[tuple[Entity, Symbol]]]:
        width, height = world.grid.width, world.grid.height
        id_map = world.em.get(Identity)
        pos_map = world.em.get(Position)
        active_map = world.em.get(Active)

        grid = [[(Entity.EMPTY, theme.symbols[Entity.EMPTY]) for _ in range(width)] for _ in range(height)]
        render_priority = [[-1 for _ in range(width)] for _ in range(height)]

        for e, id in id_map.items():
            if e not in active_map:
                continue

            p = pos_map.get(e)
            if not p:
                continue

            x, y = p.x, p.y
            curr_priority = render_priority[y][x]
            this_priority = RENDER_PRIORITY[id.type]
            if curr_priority > this_priority:
                continue

            grid[y][x] = (id.type, theme.symbols[id.type])
            render_priority[y][x] = this_priority

        return grid

    def __call__(self, world: World, player: int, theme: Theme):
        grid = self.entity_symbol_grid(world, theme)
        return '\n'.join(''.join(s.char for _, s in row) for row in grid)


class TerminalGridView(TextGridView):
    def __call__(self, world: World, player: int, theme: Theme):
        grid = self.entity_symbol_grid(world, theme)
        return '\n'.join(''.join(terminal_style.format_symbol(s) for _, s in row) for row in grid)


class HTMLGridView(TextGridView):
    def __call__(self, world: World, player: int, theme: Theme):
        grid = self.entity_symbol_grid(world, theme)
        content = '\n'.join(''.join(f'<span class="{e}">{s.char}</span>' for e, s in row) for row in grid)
        return f'<pre class="grid">\n{content}\n</pre>'


class HTMLTableGridView(TextGridView):
    def __call__(self, world: World, player: int, theme: Theme):
        grid = self.entity_symbol_grid(world, theme)
        rows = (''.join(f'<td class="{e}">{s.char}</td>' for e, s in row) for row in grid)
        content = '\n'.join(f'<tr>{row}</tr>' for row in rows)
        return f'<table class="grid">\n{content}\n</table>'
