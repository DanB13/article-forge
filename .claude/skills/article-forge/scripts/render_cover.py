#!/usr/bin/env python3
"""
Render an HTML cover template to a platform-exact PNG.

Pipeline: self-contained HTML (images embedded as base64 data URIs)
  -> wkhtmltoimage (--load-error-handling ignore, for blocked font CDNs)
  -> Pillow crop/resize to exact dimensions.

Usage:
  python render_cover.py cover.html out.png --width 1200 --height 627
  python render_cover.py cover.html out.png --embed photo.jpg=PHOTO_URI

--embed replaces the placeholder token in the HTML with a base64 data URI
for the given image file, so templates never rely on external fetches.

Requires: wkhtmltoimage (apt: wkhtmltopdf), Pillow (pip install pillow --break-system-packages)
"""
import argparse
import base64
import mimetypes
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# wkhtmltoimage's old WebKit ignores these, and the layout silently collapses.
_UNSUPPORTED_LAYOUT = re.compile(r"display\s*:\s*(inline-)?(flex|grid)\b", re.I)


def lint_html(html: str) -> list[str]:
    """Return warnings for CSS that wkhtmltoimage will not render."""
    found = sorted({m.group(0).lower().replace(" ", "") for m in _UNSUPPORTED_LAYOUT.finditer(html)})
    return [f"'{f}' is not supported by wkhtmltoimage; use table/table-cell layout" for f in found]


def keep_source(html_path: Path, output_path: Path) -> Path | None:
    """Copy the input HTML into <output dir>/html/ so the image can be re-rendered later.

    Returns the copy's path, or None when the input already lives there.
    """
    dest_dir = output_path.parent / "html"
    dest = dest_dir / html_path.name
    if dest.resolve() == html_path.resolve():
        return None
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(html_path, dest)
    return dest


def embed_images(html: str, embeds: list[str]) -> str:
    for spec in embeds:
        try:
            img_path, token = spec.split("=", 1)
        except ValueError:
            sys.exit(f"--embed expects file=TOKEN, got: {spec}")
        p = Path(img_path)
        if not p.exists():
            sys.exit(f"embed image not found: {p}")
        mime = mimetypes.guess_type(p.name)[0] or "image/png"
        data = base64.b64encode(p.read_bytes()).decode()
        html = html.replace(token, f"data:{mime};base64,{data}")
    return html


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("html", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--width", type=int, default=1200)
    ap.add_argument("--height", type=int, default=627)
    ap.add_argument("--render-width", type=int, default=None,
                    help="viewport width for wkhtmltoimage (default: --width)")
    ap.add_argument("--embed", action="append", default=[],
                    help="image.jpg=PLACEHOLDER_TOKEN (repeatable)")
    ap.add_argument("--no-keep-source", action="store_true",
                    help="do not copy the input HTML into <output dir>/html/")
    args = ap.parse_args()

    html = args.html.read_text()
    for warning in lint_html(html):
        print(f"WARNING: {warning}", file=sys.stderr)
    if args.embed:
        html = embed_images(html, args.embed)

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as tmp:
        tmp.write(html)
        tmp_path = tmp.name

    render_w = args.render_width or args.width
    raw = args.output.with_suffix(".raw.png")
    cmd = [
        "wkhtmltoimage",
        "--load-error-handling", "ignore",
        "--enable-local-file-access",
        "--width", str(render_w),
        "--quality", "95",
        tmp_path, str(raw),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 and not raw.exists():
        sys.exit(f"wkhtmltoimage failed:\n{res.stderr}")

    from PIL import Image  # noqa: import after render so failure msg is clearer
    img = Image.open(raw)
    # Scale to target width, then centre-crop to exact height.
    scale = args.width / img.width
    img = img.resize((args.width, round(img.height * scale)), Image.LANCZOS)
    if img.height < args.height:
        sys.exit(f"rendered height {img.height}px < target {args.height}px; "
                 "add content or reduce --height")
    top = (img.height - args.height) // 2
    img = img.crop((0, top, args.width, top + args.height))
    img.save(args.output, "PNG")
    raw.unlink(missing_ok=True)
    print(f"wrote {args.output} ({args.width}x{args.height})")
    if not args.no_keep_source:
        kept = keep_source(args.html, args.output)
        if kept:
            print(f"kept source {kept}")


if __name__ == "__main__":
    main()
