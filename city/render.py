"""Draws the contribution calendar as an animated isometric city (SVG + CSS)."""
import math
from dataclasses import dataclass

from city.data import Day

W = (9.6, -3.4)  # screen offset of one week step
D = (3.8, 4.4)  # screen offset of one weekday step
G = 0.82  # building footprint, as a fraction of a grid cell
PAD = 24
PAD_TOP = 10
HEIGHT_CAP = 64  # one outlier day must not flatten the rest of the city
FONT = "Georgia, 'Times New Roman', serif"


@dataclass(frozen=True)
class Theme:
    bg: str
    tile: str
    levels: tuple[str, str, str, str]
    top: float
    front: float
    left: float
    glow: bool
    ink: str
    muted: str


DARK = Theme(
    bg="#0d1117", tile="#161b22", levels=("#0e4429", "#006d32", "#26a641", "#39d353"),
    top=0.18, front=-0.25, left=-0.50, glow=True, ink="#e6edf3", muted="#7d8590",
)
LIGHT = Theme(
    bg="#ffffff", tile="#ebedf0", levels=("#9be9a8", "#40c463", "#30a14e", "#216e39"),
    top=0.0, front=-0.14, left=-0.30, glow=False, ink="#1f2328", muted="#59636e",
)


def _point(w, d):
    return (w * W[0] + d * D[0], w * W[1] + d * D[1])


def _height(count):
    return 0 if count == 0 else 3 + math.sqrt(min(count, HEIGHT_CAP)) * 11


def _points(points, dx, dy):
    return " ".join(f"{x + dx:.1f},{y + dy:.1f}" for x, y in points)


def _shade(hex_color, f):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    if f < 0:
        r, g, b = (int(v * (1 + f)) for v in (r, g, b))
    else:
        r, g, b = (int(v + (255 - v) * f) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def render_svg(days: list[Day], theme: Theme) -> str:
    nonzero = sorted(d.count for d in days if d.count > 0)
    quartiles = [nonzero[int(len(nonzero) * f)] for f in (0.25, 0.5, 0.75)] if nonzero else []

    def level(count):
        return 0 if count == 0 else 1 + sum(count > q for q in quartiles)

    all_x, all_y = [], []
    for day in days:
        for cw, cd in ((day.week, day.weekday), (day.week + G, day.weekday),
                       (day.week + G, day.weekday + G), (day.week, day.weekday + G)):
            x, y = _point(cw, cd)
            all_x.append(x)
            all_y.extend([y, y - _height(day.count)])
    ox = -min(all_x) + PAD
    oy = -min(all_y) + PAD_TOP
    vb_w = max(all_x) - min(all_x) + PAD * 2
    vb_h = max(all_y) - min(all_y) + PAD + PAD_TOP

    total = sum(d.count for d in days)
    active = len(nonzero)
    order = sorted(enumerate(days), key=lambda t: (t[1].weekday * D[1] + t[1].week * W[1], t[1].week))

    parts = [
        f'<svg viewBox="0 0 {vb_w:.0f} {vb_h:.0f}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;height:auto;display:block;background:{theme.bg}">',
        "<style>",
        ".b{transform-box:fill-box;transform-origin:50% 100%;"
        "animation:rise 9s cubic-bezier(.2,.8,.2,1) infinite both}",
        "@keyframes rise{0%{transform:scaleY(0)}7%{transform:scaleY(1)}"
        "86%{transform:scaleY(1)}93%,100%{transform:scaleY(0)}}",
        "</style>",
    ]
    if theme.glow:
        parts.append(
            '<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
            '<feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/>'
            '<feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
        )

    for index, day in order:
        w, d = day.week, day.weekday
        base = [_point(w, d), _point(w + G, d), _point(w + G, d + G), _point(w, d + G)]
        if day.count == 0:
            parts.append(f'<polygon data-tile="" points="{_points(base, ox, oy)}" fill="{theme.tile}"/>')
            continue
        h = _height(day.count)
        lvl = level(day.count)
        color = theme.levels[lvl - 1]
        top = [(x, y - h) for x, y in base]
        front = [base[3], base[2], top[2], top[3]]
        left = [base[0], base[3], top[3], top[0]]
        delay = index / len(days) * 3.6
        top_extra = ' filter="url(#glow)"' if theme.glow and lvl == 4 else ""
        parts.append(
            f'<g class="b" style="animation-delay:{delay:.2f}s">'
            f'<polygon points="{_points(left, ox, oy)}" fill="{_shade(color, theme.left)}"/>'
            f'<polygon points="{_points(front, ox, oy)}" fill="{_shade(color, theme.front)}"/>'
            f'<polygon points="{_points(top, ox, oy)}" fill="{_shade(color, theme.top)}"{top_extra}/>'
            "</g>"
        )

    noun = "active day" if active == 1 else "active days"
    parts.append(
        f'<text x="{PAD - 2}" y="{PAD_TOP + 34}" font-family="{FONT}" font-size="46" fill="{theme.ink}">'
        f"{total:,}</text>"
        f'<text x="{PAD}" y="{PAD_TOP + 54}" font-family="{FONT}" font-size="11" fill="{theme.muted}">'
        f"contributions in the last year · {active} {noun}</text>"
    )
    parts.append("</svg>")
    return "".join(parts)
