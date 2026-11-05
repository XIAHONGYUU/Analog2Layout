#!/usr/bin/env python3
"""Deterministic verification for the LDO layout-intent baseline.

Checks:
  1. regenerate white-line SVG/manifest from the deterministic compiler;
  2. compare canonical artifact hashes with artifact-lock.json;
  3. check manifest geometry invariants;
  4. check the frozen XR_GROUP hash and the NMOS selected-rule report.

This is not DRC/LVS/PEX. It prevents stale artifacts and accidental geometry
drift; it does not prove manufacturing correctness.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LDO = ROOT / "examples/sky130_ldo_01v8"
LOCK = LDO / "artifact-lock.json"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rebuild() -> None:
    subprocess.run([sys.executable, str(LDO / "make_white_line.py")], cwd=ROOT, check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true", help="regenerate SVG/manifest first")
    args = ap.parse_args()
    if args.rebuild:
        rebuild()

    errors: list[str] = []
    lock = json.loads(LOCK.read_text())
    for rel, expected in lock["artifacts"].items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing artifact: {rel}")
            continue
        actual = sha(path)
        if actual != expected:
            errors.append(f"hash mismatch: {rel}\n  expected {expected}\n  actual   {actual}")

    man = json.loads((LDO / "white-line-manifest.json").read_text())
    checks = man.get("checks", {})
    geom = man.get("checks_geometry", {})
    must_true = {
        "checks.all_devices_placed": checks.get("all_devices_placed"),
        "checks.dnw2_only_xm61": checks.get("dnw2_only_xm61"),
        "checks.passives_inside_dnw1": checks.get("passives_inside_dnw1"),
        "checks.x1_x2_inside_dnw1": checks.get("x1_x2_inside_dnw1"),
        "geometry.dnw1_contains_blocks": geom.get("dnw1_contains_blocks"),
        "geometry.dnw2_contains_pass": geom.get("dnw2_contains_pass"),
    }
    must_false = {
        "checks.fake_fill": checks.get("fake_fill"),
        "geometry.block_overlap": geom.get("block_overlap"),
    }
    for k, v in must_true.items():
        if v is not True:
            errors.append(f"{k} must be True (got {v!r})")
    for k, v in must_false.items():
        if v is not False:
            errors.append(f"{k} must be False (got {v!r})")
    if man.get("pass", {}).get("arrangement") != [3, 2]:
        errors.append("XM61 arrangement changed from [3,2]")
    if len(man.get("pass", {}).get("subs", [])) != 6:
        errors.append("XM61 must have six sub-banks")
    if len(man.get("device_clusters", [])) != 11:
        errors.append("expected 11 MOS bank clusters")

    nmos = json.loads((LDO / "banks/NMOS_2X0.5_BANK-drc.json").read_text())
    if not nmos.get("all_pass"):
        errors.append("NMOS_2X0.5 selected-rule report is not all_pass")
    xr = json.loads((LDO / "passive-banks/XR_GROUP_FROZEN.json").read_text())
    if xr.get("status") != "frozen_for_now":
        errors.append("XR_GROUP is not frozen_for_now")
    xr_png = LDO / "passive-banks/XR_GROUP_COMPACT2.png"
    if sha(xr_png) != xr["source"]["png_sha256"]:
        errors.append("XR_GROUP frozen PNG hash mismatch")

    if errors:
        print("VERIFY LDO: FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("VERIFY LDO: PASS")
    print(f" artifacts: {len(lock['artifacts'])}")
    print(f" bbox: {man['bbox_um']}  area: {man['area_um2']:.1f}  util: {man['utilization']:.4f}")
    print(" note: selected checks / hash consistency only; no DRC/LVS/PEX")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
