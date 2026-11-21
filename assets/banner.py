"""Generate the tokenized banner SVGs (light/dark).

Usage: python assets/banner.py
Requires: pip install tiktoken
"""

from pathlib import Path
from xml.sax.saxutils import escape

import tiktoken

MOTTO = "let's make things work."
ACCENT = "work"  # token that turns green once the motto is "built"
NAME = "Yuan He"
ROLE = "AI Researcher & Engineer"

ENCODING = "o200k_base"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Helvetica, Arial, sans-serif"
FONT_SIZE = 44
CHAR_W = FONT_SIZE * 0.6  # monospace advance width
PAD_X, GAP = 7, 5
CHIP_H, CHIP_Y = 62, 34
WIDTH, HEIGHT = 860, 250
STEP = 0.12  # seconds between tokens

THEMES = {
    "light": {
        "chip": "#EEF1F4",
        "accent": "#CDF3D8",
        "ring": "#2DA44E",
        "text": "#1F2328",
        "muted": "#656D76",
        "faint": "#B6BDC5",
    },
    "dark": {
        "chip": "#1C2128",
        "accent": "#13391F",
        "ring": "#3FB950",
        "text": "#E6EDF3",
        "muted": "#8D96A0",
        "faint": "#484F58",
    },
}


def render(theme: dict) -> str:
    enc = tiktoken.get_encoding(ENCODING)
    tokens = [(enc.decode([i]), i) for i in enc.encode(MOTTO)]

    widths = [len(tok) * CHAR_W + 2 * PAD_X for tok, _ in tokens]
    total = sum(widths) + GAP * (len(tokens) - 1)
    x = (WIDTH - total) / 2

    built = len(tokens) * STEP + 0.25  # when the last token has landed
    chips = []
    for n, ((tok, tid), w) in enumerate(zip(tokens, widths)):
        is_accent = tok.strip() == ACCENT
        rect = (
            f'<rect x="{x:.1f}" y="{CHIP_Y}" width="{w:.1f}" height="{CHIP_H}" rx="9" '
            f'class="{"chip pass" if is_accent else "chip"}"/>'
        )
        if is_accent:
            rect += (
                f'<rect x="{x:.1f}" y="{CHIP_Y}" width="{w:.1f}" height="{CHIP_H}" rx="9" class="ring"/>'
            )
        chips.append(
            f'<g class="t" style="animation-delay:{n * STEP:.2f}s">{rect}'
            f'<text x="{x + PAD_X:.1f}" y="{CHIP_Y + CHIP_H / 2}" class="tok" xml:space="preserve" '
            f'textLength="{len(tok) * CHAR_W:.1f}" lengthAdjust="spacingAndGlyphs">{escape(tok)}</text>'
            f'<text x="{x + w / 2:.1f}" y="{CHIP_Y + CHIP_H + 20}" class="id">{tid}</text>'
            f"</g>"
        )
        x += w + GAP

    cursor_x = x - GAP + 3
    label = escape(f"{MOTTO} — {NAME}, {ROLE}")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="{label}">
<style>
  text {{ dominant-baseline: central; }}
  .tok {{ font: 600 {FONT_SIZE}px {MONO}; fill: {theme["text"]}; }}
  .id {{ font: 12px {MONO}; fill: {theme["faint"]}; text-anchor: middle; }}
  .name {{ font: 650 26px {SANS}; letter-spacing: -0.01em; fill: {theme["text"]}; text-anchor: middle; }}
  .role {{ font: 12.5px {MONO}; letter-spacing: 0.28em; fill: {theme["muted"]}; text-anchor: middle; }}
  .chip {{ fill: {theme["chip"]}; }}
  .pass {{ animation: pass 0.5s ease-out {built:.2f}s both; }}
  .ring {{ fill: none; stroke: {theme["ring"]}; stroke-width: 2; opacity: 0;
           transform-box: fill-box; transform-origin: center;
           animation: ring 0.9s ease-out {built:.2f}s both; }}
  .t {{ animation: in 0.45s cubic-bezier(.2,.7,.2,1) both; }}
  .sub {{ animation: in 0.7s {built:.2f}s cubic-bezier(.2,.7,.2,1) both; }}
  .cursor {{ fill: {theme["text"]}; animation: blink 1.1s steps(1) {built:.2f}s infinite both; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes pass {{ from {{ fill: {theme["chip"]}; }} to {{ fill: {theme["accent"]}; }} }}
  @keyframes ring {{ 0% {{ opacity: 0.9; transform: scale(1); }} 100% {{ opacity: 0; transform: scale(1.18, 1.35); }} }}
  @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{
    .t, .sub, .cursor, .ring {{ animation: none; }}
    .pass {{ animation: none; fill: {theme["accent"]}; }}
  }}
</style>
{"".join(chips)}
<rect class="cursor" x="{cursor_x:.1f}" y="{CHIP_Y + 10}" width="3" height="{CHIP_H - 20}" rx="1.5"/>
<g class="sub">
  <text class="name" x="{WIDTH / 2}" y="{HEIGHT - 62}">{escape(NAME)}</text>
  <text class="role" x="{WIDTH / 2}" y="{HEIGHT - 30}">{escape(ROLE.upper())}</text>
</g>
</svg>
"""


if __name__ == "__main__":
    out = Path(__file__).parent
    for name, theme in THEMES.items():
        (out / f"banner-{name}.svg").write_text(render(theme))
