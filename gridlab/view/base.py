from gridlab.view.theme import Theme
from gridlab.world import World


class View:
    def __call__(self, world: World, player: int, theme: Theme) -> str:
        raise NotImplementedError()
