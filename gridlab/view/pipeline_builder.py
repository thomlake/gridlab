from enum import StrEnum

from gridlab.view import legend, status, grid
from gridlab.view.base import View
from gridlab.view.pipeline import ViewPipeline
from gridlab.view.theme import Theme


class Mode(StrEnum):
    TEXT = 'text'
    TERMINAL = 'terminal'
    HTML = 'html'
    HTML_TABLE = 'html_table'


def build_view_pipeline(
        *,
        theme: Theme | str | None = None,
        mode: Mode = Mode.TEXT,
        full_legend: bool = False,
):
    if theme is None:
        theme = {
            Mode.TEXT: 'ascii',
            Mode.TERMINAL: 'desert',
            Mode.HTML: 'desert',
            Mode.HTML_TABLE: 'desert',
        }[mode]

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
    elif mode == Mode.HTML:
        views = {
            'legend': legend.HTMLLegendView(full=full_legend),
            'status': status.HTMLStatusView(),
            'grid': grid.HTMLGridView(),
        }
    elif mode == Mode.HTML_TABLE:
        views = {
            'legend': legend.HTMLTableLegendView(full=full_legend),
            'status': status.HTMLTableStatusView(),
            'grid': grid.HTMLTableGridView(),
        }
    else:
        raise ValueError(f'unknown mode {mode}')

    return ViewPipeline(views=views, theme=theme)
