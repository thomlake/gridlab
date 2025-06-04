from enum import StrEnum

from gridlab.view import legend, status, grid
from gridlab.view.base import View
from gridlab.view.pipeline import ViewPipeline
from gridlab.view.theme import Theme


class Mode(StrEnum):
    TEXT = 'text'
    TERMINAL = 'terminal'


def build_view_pipeline(
        *,
        theme: Theme | str | None = None,
        mode: Mode = Mode.TEXT,
        full_legend: bool = False,
        template: str | None = None,
        templates: dict[int | None, str] | None = None,
):
    if theme is None:
        theme = {
            Mode.TEXT: 'ascii',
            Mode.TERMINAL: 'desert',
        }[mode]

    templates = templates or {}
    if template:
        if None in templates:
            raise ValueError('multiple default templates specified')

        templates[None] = template

    views: dict[str, View]
    if mode == Mode.TEXT:
        views = {
            'legend': legend.TextLegendView(full=full_legend),
            'status': status.TextStatusView(),
            'grid': grid.TextGridView(),
        }
    elif mode == Mode.TERMINAL:
        views = {
            'legend': legend.TerminalLegendView(full=full_legend),
            'status': status.TerminalStatusView(),
            'grid': grid.TerminalGridView(),
        }
    else:
        raise ValueError(f'unknown mode {mode}')

    return ViewPipeline(views=views, theme=theme, templates=templates)
