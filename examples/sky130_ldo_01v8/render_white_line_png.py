#!/usr/bin/env python3
"""Render the LDO white-line SVG to PNG (optional dev dependency: cairosvg)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SVG = ROOT / "examples/sky130_ldo_01v8/white-line.svg"
PNG = ROOT / "examples/sky130_ldo_01v8/white-line.png"

def main() -> int:
    try:
        import cairosvg
    except ImportError:
        print("cairosvg not installed; install the local .tools dependency first", file=sys.stderr)
        return 1
    cairosvg.svg2png(url=str(SVG), write_to=str(PNG), scale=1.4)
    print(f"wrote {PNG} {PNG.stat().st_size} bytes")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
