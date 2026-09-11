#!/usr/bin/env python3
"""Build the overview figure for the ExploitGym report.

Run from the repository root:

    python3 diagrams/build_overview.py

The figure is hand-laid-out rather than drawn by a diagram tool, so the type
sizes and spacing are chosen for the width the post actually renders at.  It
uses the same system font stack as the site, which keeps the figure in step
with the surrounding text.
"""

from __future__ import annotations

import math
import pathlib
import sys

OUT = pathlib.Path("static/images/onemind-overview.svg")

FONT = (
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
    "'Helvetica Neue', Arial, sans-serif"
)

# ColorBrewer Dark2 accents, plus neutrals for structure.
INK = "#2F3648"
GRAY = "#666666"
PERIWINKLE = "#7570B3"
TEAL = "#1B9E77"
ORANGE = "#D95F02"
MAGENTA = "#E7298A"
GOLD = "#E6AB02"
GOLD_INK = "#3E2C00"
PANEL_FILL = "#EFF2F8"
PANEL_SUB = "#5F6979"
STROKE = "#98A2B3"
CONTAINER = "#C4CBD7"
LABEL = "#6B7280"
WHITE = "#FFFFFF"

W, H = 560, 498


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rect(x, y, w, h, fill="none", rx=10, stroke=None, sw=1.5, dash=None):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"']
    if stroke:
        out.append(f' stroke="{stroke}" stroke-width="{sw}"')
    if dash:
        out.append(f' stroke-dasharray="{dash}"')
    return "".join(out) + "/>"


def text(x, y, s, size=12.5, weight=400, fill=WHITE, anchor="middle", opacity=None):
    out = [
        f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}"',
        f' fill="{fill}" text-anchor="{anchor}"',
    ]
    if opacity is not None:
        out.append(f' fill-opacity="{opacity}"')
    out.append(f">{esc(s)}</text>")
    return "".join(out)


def arrow(x1, y1, x2, y2, color=STROKE, sw=1.6, head=5.5, both=False, dash=None):
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    x2b, y2b = x2 - ux * head, y2 - uy * head
    x1b, y1b = (x1 + ux * head, y1 + uy * head) if both else (x1, y1)

    out = [
        f'<line x1="{x1b:.1f}" y1="{y1b:.1f}" x2="{x2b:.1f}" y2="{y2b:.1f}" '
        f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round"'
    ]
    if dash:
        out.append(f' stroke-dasharray="{dash}"')
    out.append("/>")

    def head_at(tip_x, tip_y, dir_x, dir_y):
        base_x, base_y = tip_x - dir_x * head, tip_y - dir_y * head
        half = head * 0.42
        return (
            f'<path d="M {tip_x:.1f} {tip_y:.1f} '
            f'L {base_x + px * half:.1f} {base_y + py * half:.1f} '
            f'L {base_x - px * half:.1f} {base_y - py * half:.1f} Z" '
            f'fill="{color}"/>'
        )

    out.append(head_at(x2, y2, ux, uy))
    if both:
        out.append(head_at(x1, y1, -ux, -uy))
    return "".join(out)


def build() -> str:
    p: list[str] = []
    p.append(rect(0, 0, W, H, fill=WHITE, rx=0))

    # --- Task input -------------------------------------------------------
    p.append(rect(120, 20, 320, 50, fill=GRAY, rx=10))
    p.append(text(280, 42, "Task Input", 15, 600))
    p.append(text(280, 61, "Vulnerability Information", 12.5, 400, opacity=0.9))
    p.append(arrow(280, 72, 280, 90))

    # --- The system: workflow, roles, memory ------------------------------
    p.append(rect(24, 92, 512, 272, rx=14, stroke=PERIWINKLE, sw=1.6))
    p.append(text(280, 122, "VARAS-OneMind", 15, 600, fill=PERIWINKLE))

    p.append(rect(44, 136, 472, 54, fill=PANEL_FILL, rx=10))
    p.append(text(280, 158, "Stage-Governed Workflow", 15, 600, fill=INK))
    p.append(text(280, 180, "Triage → Primitive → Chaining → Remote", 12.5, 400, fill=PANEL_SUB))

    p.append(rect(44, 208, 214, 70, fill=PERIWINKLE, rx=10))
    p.append(text(151, 233, "Operator", 15, 600))
    p.append(text(151, 255, "Plans and delegates", 11.5, 400, opacity=0.92))
    p.append(text(151, 271, "Integrates the results", 11.5, 400, opacity=0.92))

    p.append(rect(302, 208, 214, 70, fill=TEAL, rx=10))
    p.append(text(409, 233, "Executor", 15, 600))
    p.append(text(409, 255, "Runs bounded work", 11.5, 400, opacity=0.92))
    p.append(text(409, 271, "In a fresh context", 11.5, 400, opacity=0.92))

    p.append(arrow(262, 228, 298, 228, head=5.5))
    p.append(arrow(298, 248, 262, 248, head=5.5))

    p.append(rect(44, 294, 472, 54, fill=ORANGE, rx=10))
    p.append(text(280, 316, "Exploit Memory", 15, 600))
    p.append(text(280, 335, "Organized around Capabilities, Branches and Evidence", 12, 400, opacity=0.9))

    # --- The capability chain it builds -----------------------------------
    p.append(rect(24, 380, 512, 98, rx=14, stroke=CONTAINER, sw=1.5, dash="7 5"))
    p.append(text(280, 403, "Capability Chain", 13.5, 600, fill=LABEL))

    card_y, card_w, card_h = 414, 100, 48
    card_x = [44, 168, 292, 416]
    for x, fill in zip(card_x, [MAGENTA, MAGENTA, MAGENTA, GOLD]):
        p.append(rect(x, card_y, card_w, card_h, fill=fill, rx=9))

    p.append(text(card_x[0] + card_w / 2, 432, "C0", 13.5, 600))
    p.append(text(card_x[0] + card_w / 2, 448, "Initial Primitive", 10, 400, opacity=0.9))
    p.append(text(card_x[1] + card_w / 2, 441, "C1", 13.5, 600))
    p.append(text(card_x[2] + card_w / 2, 441, "C2 …", 13.5, 600))
    p.append(text(card_x[3] + card_w / 2, 441, "Flag", 14, 600, fill=GOLD_INK))

    for left, right in zip(card_x, card_x[1:]):
        p.append(arrow(left + card_w, card_y + card_h / 2, right, card_y + card_h / 2, head=5))

    body = "\n".join(f"  {line}" for line in p)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        'aria-label="VARAS-OneMind overview">\n'
        f"<style>text{{font-family:{FONT};}}</style>\n"
        f"{body}\n"
        "</svg>\n"
    )


if __name__ == "__main__":
    target = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    target.write_text(build())
    print(f"written {target}")
