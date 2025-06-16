from gridlab.component import Identity
from gridlab.entity import Entity
from gridlab.view import terminal_style
from gridlab.view.base import View
from gridlab.view.theme import Symbol, Theme
from gridlab.world import World


class TextLegendView(View):
    def __init__(self, full: bool = False):
        self.full = full

    def legend_items(self, world: World, theme: Theme) -> list[tuple[Entity, Symbol]]:
        if self.full:
            entity_types = list(Entity)
        elif world.entity_types:
            entity_types = world.entity_types
        else:
            identity_map: dict[int, Identity] = world.em.get(Identity)
            entity_types = set()
            for identity in identity_map.values():
                entity_types.add(identity.type)

        return [(e, theme.symbols[e]) for e in entity_types]

    def __call__(self, world: World, player: int, theme: Theme):
        items = self.legend_items(world, theme)
        return '\n'.join(f'- `{s.char}`: {e}' for e, s in items)


class TerminalLegendView(TextLegendView):
    def __call__(self, world: World, player: int, theme: Theme):
        items = self.legend_items(world, theme)
        return '\n'.join(f'{terminal_style.format_symbol(s)}: {e}' for e, s in items)


class HTMLLegendView(TextLegendView):
    def __call__(self, world: World, player: int, theme: Theme):
        items = self.legend_items(world, theme)
        elements = '\n'.join(f'<li><span class="entity {e}">{s.char}</span>: {e}</li>' for e, s in items)
        return f'<ul class="legend">\n{elements}\n</ul>'


class HTMLTableLegendView(TextLegendView):
    def __call__(self, world: World, player: int, theme: Theme):
        items = self.legend_items(world, theme)
        rows = '\n'.join(f'<tr><td class="entity {e}">{s.char}</td><td>{e}</td></tr>' for e, s in items)
        return f'<table class="legend">\n{rows}\n</table>'
