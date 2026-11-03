#!/usr/bin/env python3
"""Validate the SKY130 fact registry and, when available, its local source deck."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FACTS = ROOT / "pdk/sky130/facts.json"
DEFAULT_SOURCE = ROOT / "out/refs/sky130.lydrc"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = ap.parse_args()
    facts = json.loads(FACTS.read_text())
    required = {
        "difftap_min_width_um": 0.15,
        "difftap_min_space_um": 0.27,
        "nwell_min_width_um": 0.84,
        "nwell_min_space_um": 1.27,
        "dnwell_min_width_um": 3.0,
        "dnwell_min_space_um": 6.3,
        "diff_enclosing_licon_um": 0.04,
        "tap_enclosing_licon_one_edge_um": 0.12,
    }
    errors = []
    for key, expected in required.items():
        got = facts["rules"].get(key, {}).get("value")
        if got != expected:
            errors.append(f"{key}: expected {expected}, got {got}")
    ring = facts.get("ring", {})
    if ring.get("pdk_defined") is not False:
        errors.append("ring.pdk_defined must be false")
    if "No." not in ring.get("answer", ""):
        errors.append("ring.answer must state that the PDK does not define 1.0 um")
    source = args.source
    if source.exists():
        raw = source.read_bytes()
        got = hashlib.sha256(raw).hexdigest()
        if got != facts["source"]["sha256"]:
            errors.append(f"source sha256 mismatch: {got}")
        lines = raw.decode("utf-8", errors="replace").splitlines()
        for key, rec in facts["rules"].items():
            n = rec.get("source_line")
            if n and 1 <= n <= len(lines):
                if str(rec["value"]) not in lines[n-1]:
                    errors.append(f"{key}: value not found at source line {n}")
            elif n:
                errors.append(f"{key}: source line {n} out of range")
        print(f"source: {source} {len(raw)} bytes sha256={got}")
    else:
        print(f"source: {source} not present (hash not checked)", file=sys.stderr)
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print(f"OK: {len(facts['rules'])} facts; ring.pdk_defined=false")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
