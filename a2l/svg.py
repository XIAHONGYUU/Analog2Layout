"""SVG renderer for the floorplan sketch.

The drawing style is intentionally restrained: white background, thin dark
outlines, dashed group boundaries, one red symmetry axis, and hatching only for
the reserved PEX-fix area.  It should look like something an engineer can mark
up in a design review, not a polished marketing illustration.
"""

from __future__ import annotations

import html
from .floorplan import Floorplan, FPDevice, FPGroup
from .roles import get_role

INK = "#111827"
MUTED = "#6b7280"
GUIDE = "#9ca3af"
FAINT = "#d1d5db"
PAPER = "#ffffff"
PROPOSED_FILL = "#f3f4f6"
CAP_FILL = "#fafafa"
AXIS = "#dc2626"


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


class SVGCanvas:
    def __init__(self, width: float, height: float, *, scale: float = 6.0) -> None:
        self.width = width
        self.height = height
        self.scale = scale
        self.parts: list[str] = []

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        *,
        fill: str = "none",
        stroke: str = INK,
        stroke_width: float = 0.35,
        dash: str | None = None,
        rx: float = 0.0,
        opacity: float = 1.0,
    ) -> None:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        opacity_attr = f' opacity="{opacity:g}"' if opacity < 1.0 else ""
        self.add(
            f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" '
            f'rx="{rx:g}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width:g}"'
            f'{dash_attr}{opacity_attr}/>'
        )

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        *,
        stroke: str = INK,
        stroke_width: float = 0.3,
        dash: str | None = None,
        opacity: float = 1.0,
        marker_start: bool = False,
        marker_end: bool = False,
    ) -> None:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        start = ' marker-start="url(#arrow)"' if marker_start else ""
        end = ' marker-end="url(#arrow)"' if marker_end else ""
        self.add(
            f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
            f'stroke="{stroke}" stroke-width="{stroke_width:g}" stroke-linecap="round"'
            f'{dash_attr}{start}{end} opacity="{opacity:g}"/>'
        )

    def text(
        self,
        x: float,
        y: float,
        text: str,
        *,
        size: float = 2.8,
        fill: str = INK,
        anchor: str = "start",
        weight: str = "normal",
        rotate: float = 0.0,
        opacity: float = 1.0,
        letter_spacing: float = 0.0,
    ) -> None:
        transform = f' transform="rotate({rotate:g} {x:.3f} {y:.3f})"' if rotate else ""
        spacing = f' letter-spacing="{letter_spacing:g}"' if letter_spacing else ""
        self.add(
            f'<text x="{x:.3f}" y="{y:.3f}" fill="{fill}" font-size="{size:g}" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
            f'font-weight="{weight}" text-anchor="{anchor}" dominant-baseline="middle"'
            f'{spacing}{transform} opacity="{opacity:g}">{_esc(text)}</text>'
        )

    def render(self, *, title: str, aria_label: str) -> str:
        px_w = self.width * self.scale
        px_h = self.height * self.scale
        defs = f"""
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="{MUTED}"/>
  </marker>
  <pattern id="hatch" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="4" stroke="{FAINT}" stroke-width="0.35"/>
  </pattern>
</defs>"""
        body = "\n".join(self.parts)
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width:.3f} {self.height:.3f}" width="{px_w:.0f}" height="{px_h:.0f}" role="img" aria-label="{_esc(aria_label)}" style="max-width:100%;background:{PAPER}">
<title>{_esc(title)}</title>
{defs}
<rect x="0" y="0" width="{self.width:.3f}" height="{self.height:.3f}" fill="{PAPER}"/>
{body}
<rect x="0.5" y="0.5" width="{self.width - 1:.3f}" height="{self.height - 1:.3f}" fill="none" stroke="{FAINT}" stroke-width="0.3"/>
</svg>
"""


def render_floorplan_svg(
    floorplan: Floorplan,
    *,
    title: str | None = None,
    subtitle: str | None = None,
) -> str:
    canvas = SVGCanvas(floorplan.width, floorplan.height)
    content_left = 16.0
    content_right = max((group.x + group.w for group in floorplan.groups), default=floorplan.width - 20.0)
    content_top = 34.0
    content_bottom = max((group.y + group.h for group in floorplan.groups), default=floorplan.height - 30.0)

    _draw_reserve(canvas, floorplan)
    _draw_bands(canvas, floorplan, content_left)
    _draw_channels(canvas, floorplan)
    _draw_groups(canvas, floorplan)
    _draw_symmetry_axis(canvas, floorplan, content_top, content_bottom)
    _draw_devices(canvas, floorplan)
    _draw_ports(canvas, floorplan, content_top, content_bottom)
    _draw_dimensions(canvas, floorplan, content_left, content_right, content_top, content_bottom)
    _draw_header(canvas, floorplan, title, subtitle)
    _draw_legend(canvas, floorplan)
    return canvas.render(
        title=title or f"{floorplan.design} — floorplan intent",
        aria_label=f"Floorplan sketch intent for {floorplan.design}",
    )


def _draw_reserve(canvas: SVGCanvas, floorplan: Floorplan) -> None:
    reserve = floorplan.reserve
    if not reserve:
        return
    x = float(reserve["x"])
    y = float(reserve["y"])
    w = float(reserve["w"])
    h = float(reserve["h"])
    canvas.rect(x, y, w, h, fill="url(#hatch)", stroke=GUIDE, stroke_width=0.3, dash="2.5,1.8")
    cx = x + w / 2.0
    cy = y + h / 2.0
    fraction = float(reserve.get("fraction", 0.08))
    canvas.text(
        cx,
        cy - 2.0,
        f"PEX-FIX RESERVE {fraction * 100:.0f}%",
        size=2.4,
        fill=MUTED,
        anchor="middle",
        rotate=-90,
        letter_spacing=0.15,
    )
    canvas.text(
        cx + 2.4,
        cy + 8.0,
        "keep uncommitted",
        size=1.8,
        fill=GUIDE,
        anchor="middle",
        rotate=-90,
    )


def _draw_bands(canvas: SVGCanvas, floorplan: Floorplan, left: float) -> None:
    for band in floorplan.bands:
        cy = (band.y0 + band.y1) / 2.0
        canvas.text(
            left - 7.0,
            cy,
            band.name.upper(),
            size=2.2,
            fill=GUIDE,
            anchor="middle",
            rotate=-90,
            letter_spacing=0.25,
        )


def _draw_channels(canvas: SVGCanvas, floorplan: Floorplan) -> None:
    for channel in floorplan.channels:
        canvas.line(
            channel.x1,
            channel.y1,
            channel.x2,
            channel.y2,
            stroke=FAINT,
            stroke_width=0.25,
            dash="2.0,2.0",
        )


def _draw_groups(canvas: SVGCanvas, floorplan: Floorplan) -> None:
    for group in floorplan.groups:
        canvas.rect(
            group.x,
            group.y,
            group.w,
            group.h,
            fill="none",
            stroke=GUIDE,
            stroke_width=0.3,
            dash="2.8,1.8",
            rx=0.8,
        )
        _group_label(canvas, group)


def _group_label(canvas: SVGCanvas, group: FPGroup) -> None:
    label = group.label
    width = max(3.0, len(label) * 1.25 + 1.5)
    x = group.x + 0.7
    # The top band has the VDD pin and the width dimension above it; put its
    # label below the group so it does not fight the header.
    if group.band == "top":
        y = group.y + group.h + 1.4
    else:
        y = group.y - 1.4
    canvas.rect(x - 0.4, y - 1.3, width, 2.6, fill=PAPER, stroke="none", stroke_width=0.0)
    canvas.text(x, y, label, size=2.1, fill=MUTED, weight="bold")


def _draw_symmetry_axis(
    canvas: SVGCanvas,
    floorplan: Floorplan,
    top: float,
    bottom: float,
) -> None:
    x = floorplan.symmetry_x
    canvas.line(x, top - 2.0, x, bottom + 2.0, stroke=AXIS, stroke_width=0.35, dash="3.0,2.0", opacity=0.55)
    canvas.text(x + 1.2, top - 2.8, "SYM AXIS", size=1.8, fill=AXIS, opacity=0.85)


def _draw_devices(canvas: SVGCanvas, floorplan: Floorplan) -> None:
    for device in floorplan.devices:
        _draw_device(canvas, device)


def _draw_device(canvas: SVGCanvas, device: FPDevice) -> None:
    if device.proposed:
        fill = PROPOSED_FILL
    elif device.kind == "cap":
        fill = CAP_FILL
    else:
        fill = PAPER

    canvas.rect(
        device.x,
        device.y,
        device.w,
        device.h,
        fill=fill,
        stroke=INK,
        stroke_width=0.32 if not device.proposed else 0.3,
        dash="2.2,1.4" if device.proposed else None,
    )

    role = get_role(device.role).short
    name = device.label or device.name
    cx = device.x + device.w / 2.0
    cy = device.y + device.h / 2.0

    if device.w >= 11.0 and device.h >= 7.0:
        canvas.text(cx, cy - 1.8, name, size=2.7, anchor="middle", weight="bold")
        canvas.text(cx, cy + 1.2, role, size=1.9, anchor="middle", fill=MUTED)
        if device.detail:
            canvas.text(cx, cy + 3.7, device.detail, size=1.6, anchor="middle", fill=GUIDE)
    elif device.w >= 4.6 and device.h >= 4.0:
        canvas.text(cx, cy - 0.7, name, size=2.2, anchor="middle", weight="bold")
        canvas.text(cx, cy + 1.8, role, size=1.5, anchor="middle", fill=MUTED)
    elif device.h >= 2.0:
        canvas.text(
            cx,
            cy,
            name,
            size=1.9,
            anchor="middle",
            weight="bold",
            rotate=-90,
        )
    else:
        canvas.text(cx, device.y - 0.9, name, size=1.7, anchor="middle", weight="bold")


def _draw_ports(
    canvas: SVGCanvas,
    floorplan: Floorplan,
    top: float,
    bottom: float,
) -> None:
    for port in floorplan.ports:
        size = 2.2
        canvas.rect(
            port.x - size / 2.0,
            port.y - size / 2.0,
            size,
            size,
            fill=INK,
            stroke=INK,
            stroke_width=0.2,
        )
        if port.side == "top":
            canvas.text(port.x, port.y - 3.0, port.name, size=2.5, anchor="middle", weight="bold")
            canvas.line(port.x, port.y + size / 2.0, port.x, top, stroke=FAINT, stroke_width=0.3)
        elif port.side == "bottom":
            canvas.text(port.x, port.y + 3.4, port.name, size=2.5, anchor="middle", weight="bold")
            canvas.line(port.x, port.y - size / 2.0, port.x, bottom, stroke=FAINT, stroke_width=0.3)
        elif port.side == "pin-top":
            canvas.text(port.x, port.y - 2.2, port.name, size=1.9, anchor="middle", weight="bold")
            canvas.line(port.x, port.y + size / 2.0, port.x, port.y + 2.8, stroke=FAINT, stroke_width=0.3)
        elif port.side == "pin-right":
            canvas.text(port.x + 2.0, port.y, port.name, size=1.6, anchor="middle", weight="bold", rotate=-90)
            canvas.line(port.x - size / 2.0, port.y, port.x - 2.8, port.y, stroke=FAINT, stroke_width=0.3)
        elif port.side == "left":
            canvas.text(port.x - 2.2, port.y, port.name, size=2.4, anchor="end", weight="bold")
        else:
            canvas.text(port.x + 2.2, port.y, port.name, size=2.4, anchor="start", weight="bold")


def _draw_dimensions(
    canvas: SVGCanvas,
    floorplan: Floorplan,
    left: float,
    right: float,
    top: float,
    bottom: float,
) -> None:
    y = 20.0
    canvas.line(left, y, right, y, stroke=MUTED, stroke_width=0.25, marker_start=True, marker_end=True)
    canvas.line(left, y - 1.4, left, y + 1.4, stroke=MUTED, stroke_width=0.25)
    canvas.line(right, y - 1.4, right, y + 1.4, stroke=MUTED, stroke_width=0.25)
    canvas.text((left + right) / 2.0, y - 1.7, f"W = {right - left:.1f} um", size=2.0, fill=MUTED, anchor="middle")

    x = floorplan.width - 5.0
    canvas.line(x, top, x, bottom, stroke=MUTED, stroke_width=0.25, marker_start=True, marker_end=True)
    canvas.line(x - 1.4, top, x + 1.4, top, stroke=MUTED, stroke_width=0.25)
    canvas.line(x - 1.4, bottom, x + 1.4, bottom, stroke=MUTED, stroke_width=0.25)
    canvas.text(
        x + 2.0,
        (top + bottom) / 2.0,
        f"H = {bottom - top:.1f} um",
        size=2.0,
        fill=MUTED,
        anchor="middle",
        rotate=-90,
    )


def _draw_header(
    canvas: SVGCanvas,
    floorplan: Floorplan,
    title: str | None,
    subtitle: str | None,
) -> None:
    canvas.text(16.0, 8.5, title or f"{floorplan.design} — floorplan intent", size=6.0, weight="bold")
    proposed = int(floorplan.stats.get("proposed_dummy_count", 0))
    device_text = f"{floorplan.stats.get('device_count', 0)} devices"
    if proposed:
        device_text += f" + {proposed} proposed dummies"
    sub = subtitle or (
        f"rules: {floorplan.rules_name}  ·  symmetry x={floorplan.symmetry_x:.1f} um  ·  "
        f"{device_text} / {floorplan.stats.get('group_count', 0)} groups"
    )
    canvas.text(16.0, 14.6, sub, size=2.7, fill=MUTED)


def _draw_legend(canvas: SVGCanvas, floorplan: Floorplan) -> None:
    y0 = floorplan.height - 20.0
    canvas.line(16.0, y0, floorplan.width - 16.0, y0, stroke=FAINT, stroke_width=0.25)
    canvas.text(
        16.0,
        y0 + 4.2,
        "SOLID existing · DASHED proposed · HATCH PEX reserve · grey dash = routing channel · um",
        size=1.9,
        fill=MUTED,
    )
    canvas.text(
        16.0,
        y0 + 8.6,
        "DP input pair   CM current mirror   CAS cascode   TAIL tail   OUT output   COMP cap   SW switch   DM dummy",
        size=1.9,
        fill=GUIDE,
    )
    canvas.text(
        16.0,
        floorplan.height - 4.0,
        "a2l v0.1  ·  early planning estimate, not DRC/LVS clean  ·  rules are educational, replace with a company rule pack",
        size=1.8,
        fill=GUIDE,
    )
