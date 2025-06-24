from gridlab.component import Identity
from gridlab.entity import Entity, describe_entity
from gridlab.view import terminal_style
from gridlab.view.base import View
from gridlab.view.theme import Symbol, Theme
from gridlab.world import World


class TextLegendView(View):
    def __init__(self, full: bool = False, verbose: bool = False):
        self.full = full
        self.verbose = verbose

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

    def _format_item(self, entity: Entity, symbol: Symbol):
        if self.verbose:
            desc = describe_entity(entity)
            return f'- `{symbol.char}` ({entity}): {desc}'

        return f'- `{symbol.char}`: {entity}'

    def __call__(self, world: World, player: int, theme: Theme):
        items = self.legend_items(world, theme)
        return '\n'.join(self._format_item(e, s) for e, s in items)


class TerminalLegendView(TextLegendView):
    def _format_item(self, entity: Entity, symbol: Symbol):
        s = terminal_style.format_symbol(symbol)
        if self.verbose:
            desc = describe_entity(entity)
            return f'- `{s}` ({entity}): {desc}'

        return f'- `{s}`: {entity}'

    def __call__(self, world: World, player: int, theme: Theme):
        items = self.legend_items(world, theme)
        return '\n'.join(self._format_item(e, s) for e, s in items)


class HTMLLegendView(TextLegendView):
    def _format_item(self, entity: Entity, symbol: Symbol):
        if self.verbose:
            desc = describe_entity(entity)
            return f'<li><span class="entity {entity}">{symbol.char}</span> ({entity}): {desc}</li>'

        return f'<li><span class="entity {entity}">{symbol.char}</span>: {entity}</li>'

    def __call__(self, world: World, player: int, theme: Theme):
        items = self.legend_items(world, theme)
        elements = '\n'.join(self._format_item(e, s) for e, s in items)
        return f'<ul class="legend">\n{elements}\n</ul>'


class HTMLTableLegendView(TextLegendView):
    def _format_item(self, entity: Entity, symbol: Symbol):
        if self.verbose:
            desc = describe_entity(entity)
            return f'<tr><td class="entity {entity}">{symbol.char}</td><td>{entity}</td><td>{desc}</td></tr>'

        return f'<tr><td class="entity {entity}">{symbol.char}</td><td>{entity}</td></tr>'

    def __call__(self, world: World, player: int, theme: Theme):
        items = self.legend_items(world, theme)
        rows = '\n'.join(f'<tr><td class="entity {e}">{s.char}</td><td>{e}</td></tr>' for e, s in items)
        return f'<table class="legend">\n{rows}\n</table>'
