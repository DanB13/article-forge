"""Builds docs/images/how-it-works-{light,dark}.svg for the README.

Run from the repo root: python docs/images/make_how_it_works.py docs/images
Edit COLS or THEMES, then re-run; commit both SVGs."""
import sys
from pathlib import Path
from xml.sax.saxutils import escape as esc

OUT = Path(sys.argv[1])
W, H = 880, 404
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

THEMES = {
    "light": dict(fg="#1f2328", muted="#59636e", line="#d1d9e0", card="#ffffff", edge="#8c959f",
                  accents=["#8250df", "#0969da", "#1a7f37"], tints=["#fbefff", "#ddf4ff", "#dafbe1"],
                  prof="#fff8c5", profedge="#d4a72c", profink="#7d4e00"),
    "dark": dict(fg="#f0f6fc", muted="#9198a1", line="#3d444d", card="#151b23", edge="#656c76",
                 accents=["#a371f7", "#4493f8", "#3fb950"], tints=["#2a1f3d", "#102a46", "#12301b"],
                 prof="#2e2a10", profedge="#bb8009", profink="#e3b341"),
}

COLS = [
    ("Write", [("1", "Brief", "argument, audience, outcome"),
               ("2", "Research", "every stat marked unverified"),
               ("3", "Draft", "a complete first draft, kept"),
               ("you", "Your edit rounds", "options, never silent edits")]),
    ("Check", [("4", "Provenance", "every stat traced to source"),
               ("5", "Voice edit", "scorecard, then your voice"),
               ("6", "Imagery", "real material first"),
               ("7", "Publish pack", "ready for the platform")]),
    ("Publish and learn", [("pub", "Published", "you press the button"),
                           ("8", "Retro", "what you changed, and how much"),
                           ("you", "Profile updates", "proposed; you approve each")]),
]

def svg(t):
    cw, gap, top, ch = 268, 38, 54, 262
    xs = [0, cw + gap, 2 * (cw + gap)]
    a = []
    a.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             f'role="img" aria-label="How Article Forge works: write, check, publish and learn, with your profile read before every phase" '
             f'font-family="{FONT}">')
    a.append(f'<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
             f'<path d="M0 0L10 5L0 10z" fill="{t["edge"]}"/></marker></defs>')
    # Your idea pill
    ix = xs[0] + cw / 2
    a.append(f'<rect x="{ix-56}" y="2" width="112" height="28" rx="14" fill="{t["card"]}" stroke="{t["edge"]}"/>')
    a.append(f'<text x="{ix}" y="21" text-anchor="middle" font-size="13" font-weight="600" fill="{t["fg"]}">Your idea</text>')
    a.append(f'<line x1="{ix}" y1="30" x2="{ix}" y2="{top-3}" stroke="{t["edge"]}" stroke-width="1.5" marker-end="url(#arr)"/>')
    for i, (title, rows) in enumerate(COLS):
        x, acc, tint = xs[i], t["accents"][i], t["tints"][i]
        a.append(f'<rect x="{x+0.5}" y="{top+0.5}" width="{cw-1}" height="{ch}" rx="10" fill="{t["card"]}" stroke="{acc}" stroke-width="1.5"/>')
        a.append(f'<path d="M{x+0.5} {top+38} V{top+10.5} a10 10 0 0 1 10 -10 H{x+cw-10.5} a10 10 0 0 1 10 10 V{top+38} Z" fill="{tint}"/>')
        a.append(f'<line x1="{x+1}" y1="{top+38}" x2="{x+cw-1}" y2="{top+38}" stroke="{acc}" stroke-opacity="0.5"/>')
        a.append(f'<text x="{x+16}" y="{top+25}" font-size="15" font-weight="700" fill="{t["fg"]}">{esc(title)}</text>')
        for r, (num, name, desc) in enumerate(rows):
            ry = top + 56 + r * 52
            cx = x + 30
            if num == "you":
                a.append(f'<rect x="{cx-14}" y="{ry-1}" width="28" height="20" rx="10" fill="{acc}"/>')
                a.append(f'<text x="{cx}" y="{ry+13}" text-anchor="middle" font-size="10.5" font-weight="700" fill="{t["card"]}">YOU</text>')
            elif num == "pub":
                a.append(f'<circle cx="{cx}" cy="{ry+9}" r="10" fill="none" stroke="{acc}" stroke-width="1.5"/>')
                a.append(f'<path d="M{cx-4.5} {ry+9} l3 3.5 l6 -7" fill="none" stroke="{acc}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
            else:
                a.append(f'<circle cx="{cx}" cy="{ry+9}" r="10" fill="{tint}" stroke="{acc}" stroke-width="1.5"/>')
                a.append(f'<text x="{cx}" y="{ry+13.5}" text-anchor="middle" font-size="12" font-weight="700" fill="{acc}">{num}</text>')
            a.append(f'<text x="{x+52}" y="{ry+8}" font-size="14" font-weight="600" fill="{t["fg"]}">{esc(name)}</text>')
            a.append(f'<text x="{x+52}" y="{ry+26}" font-size="12.5" fill="{t["muted"]}">{esc(desc)}</text>')
        if i < 2:
            y = top + ch / 2
            a.append(f'<line x1="{x+cw+4}" y1="{y}" x2="{xs[i+1]-4}" y2="{y}" stroke="{t["edge"]}" stroke-width="1.5" marker-end="url(#arr)"/>')
    # profile bar
    py = top + ch + 46
    a.append(f'<rect x="0.5" y="{py+0.5}" width="{W-1}" height="{H-py-2}" rx="10" fill="{t["prof"]}" stroke="{t["profedge"]}" stroke-width="1.2"/>')
    a.append(f'<text x="18" y="{py+23}" font-size="14" font-weight="700" fill="{t["fg"]}">Your profile</text>')
    a.append(f'<text x="116" y="{py+23}" font-size="12.5" fill="{t["muted"]}">voice, context, writing samples, settings</text>')
    a.append(f'<text x="{W-18}" y="{py+23}" text-anchor="end" font-size="12.5" fill="{t["profink"]}">0 Onboarding builds it from your own writing</text>')
    # read-before-every-phase connectors (profile up into Write and Check), retro down into profile
    for i in (0, 1):
        cx = xs[i] + cw / 2
        a.append(f'<line x1="{cx}" y1="{py-2}" x2="{cx}" y2="{top+ch+4}" stroke="{t["profedge"]}" stroke-width="1.4" stroke-dasharray="4 3" marker-end="url(#arr)"/>')
    a.append(f'<text x="{xs[0]+cw/2+10}" y="{top+ch+28}" font-size="12" fill="{t["profink"]}">read before every phase</text>')
    cx = xs[2] + cw / 2
    a.append(f'<line x1="{cx}" y1="{top+ch+4}" x2="{cx}" y2="{py-2}" stroke="{t["profedge"]}" stroke-width="1.4" stroke-dasharray="4 3" marker-end="url(#arr)"/>')
    a.append(f'<text x="{cx-10}" y="{top+ch+28}" text-anchor="end" font-size="12" fill="{t["profink"]}">learns from what you changed</text>')
    a.append('</svg>')
    return "\n".join(a) + "\n"

OUT.mkdir(parents=True, exist_ok=True)
for name, theme in THEMES.items():
    (OUT / f"how-it-works-{name}.svg").write_text(svg(theme), encoding="utf-8")
print("ok")
