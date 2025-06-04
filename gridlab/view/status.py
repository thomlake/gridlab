from typing import Any

from gridlab.component import Door, KeyCollector, Key, Timer
from gridlab.view import terminal_style
from gridlab.view.base import View
from gridlab.view.theme import Theme
from gridlab.world import World


class TextStatusView(View):
    def status_dict(self, world: World, player: int) -> dict[str, Any]:
        status_dict: dict[str, Any] = {}
        status_dict['Turn'] = world.turn

        timer = world.em.get(Timer).get(player)
        if timer:
            status_dict['Moves'] = timer.remain

        key_collector = world.em.get(KeyCollector).get(player)
        if key_collector:
            key_map = world.em.get(Key)
            door_map = world.em.get(Door)
            if key_map or door_map or key_collector.count > 0:
                status_dict['Keys'] = key_collector.count

        return status_dict

    def __call__(self, world: World, player: int, theme: Theme):
        status_dict = self.status_dict(world, player)
        return '\n'.join(f'- {s}: {v}' for s, v in status_dict.items())


class TerminalStatusView(TextStatusView):
    def __call__(self, world: World, player: int, theme: Theme):
        status_dict = self.status_dict(world, player)
        if any(s.bold for s in theme.symbols.values()):
            status_dict = {terminal_style.make_bold(k): v for k, v in status_dict.items()}

        return '\n'.join(f'[{k}: {v}]' for k, v in status_dict.items())


class HTMLStatusView(TextStatusView):
    def __call__(self, world: World, player: int, theme: Theme):
        status_dict = self.status_dict(world, player)
        content = '\n'.join(f'<li><span class="status_item">{k}</span>: {v}</li>' for k, v in status_dict.items())
        return f'<ul class="status">\n{content}\n</ul>'


class HTMLTableStatusView(TextStatusView):
    def __call__(self, world: World, player: int, theme: Theme):
        status_dict = self.status_dict(world, player)
        content = '\n'.join(f'<tr><td class="status_item">{k}</td><td>{v}</td></tr>' for k, v in status_dict.items())
        return f'<table class="status">\n{content}\n</table>'
