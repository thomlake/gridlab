from gridlab.view.base import View
from gridlab.view.theme import Theme, load_theme
from gridlab.world import World


class ViewPipeline:
    def __init__(
            self,
            views: dict[str, View],
            theme: Theme | str = 'ascii',
            templates: dict[int | None, str] | None = None,
            separator: str = '\n\n',
    ):
        if not isinstance(theme, Theme):
            theme = load_theme(theme)

        self.views = views
        self.theme = theme
        self.templates = templates or {}
        self.separator = separator

    def render_views(self, world: World, player: int | None = None):
        if player is None:
            player = world.player

        sections: dict[str, str] = {}
        for name, view in self.views.items():
            sections[name] = view(world, player, theme=self.theme)

        return sections

    def render(self, world: World, player: int | None = None):
        views = self.render_views(world, player)

        template = self.templates.get(world.turn, self.templates.get(None))
        if template:
            return template.format(**views)

        return self.separator.join(views.values())
