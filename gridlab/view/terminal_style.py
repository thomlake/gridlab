from gridlab.view.theme import Symbol


COLORIST_AVAILABLE = True
try:
    import colorist
except ImportError:
    COLORIST_AVAILABLE = False

_MISSING_COLORIST = 'terminal styling require the colorist package (pip install colorist)'


def color_foreground(value: str, color: str):
    if not COLORIST_AVAILABLE:
        raise ValueError(_MISSING_COLORIST)

    fg = colorist.ColorHex(color)
    return f'{fg}{value}{fg.OFF}'


def color_background(value: str, color: str):
    bg = colorist.BgColorHex(color)
    return f'{bg}{value}{bg.OFF}'


def make_bold(value: str):
    if not COLORIST_AVAILABLE:
        raise ValueError(_MISSING_COLORIST)

    return f'{colorist.Effect.BOLD}{value}{colorist.Effect.OFF}'


def format_symbol(symbol: Symbol):
    if not COLORIST_AVAILABLE:
        raise ValueError(_MISSING_COLORIST)

    value = symbol.char
    if symbol.color:
        value = color_foreground(value, symbol.color)

    if symbol.background:
        value = color_background(value, symbol.background)

    if symbol.bold:
        value = make_bold(value)

    return value
