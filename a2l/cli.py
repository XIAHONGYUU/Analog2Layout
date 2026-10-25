"""Command-line interface for analog2layout."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .area import AreaReport, estimate_area
from .delta import plan_layout_delta
from .floorplan import build_floorplan
from .netlist import Netlist, parse_file, validate_netlist
from .report import (
    area_markdown,
    area_str,
    compare_markdown,
    write_bundle,
    write_json,
    write_text,
)
from .roles import ROLES, ROLE_OWNER, ROLE_POLICY
from .rules import Rules, default_rules_path, load_rules
from .svg import render_floorplan_svg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="a2l",
        description="Role-aware area estimation and white-line floorplan handoff for analog circuits.",
    )
    parser.add_argument("--version", action="version", version=f"a2l {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("netlist", help="SPICE-like netlist exported from the schematic")
    common.add_argument(
        "--rules",
        default=None,
        help="rule pack JSON (default: rules/generic_180.json)",
    )
    common.add_argument("--out", default=None, help="output directory")
    common.add_argument(
        "--area-budget-mm2",
        type=float,
        default=None,
        help="optional area budget in mm2; reports PASS/REJECT/UNCERTAIN using area_low/high",
    )
    common.add_argument("--quiet", action="store_true", help="only print warnings/errors")
    common.add_argument(
        "--fail-on-gate",
        action="store_true",
        help="exit non-zero unless the area gate is PASS (requires --area-budget-mm2)",
    )

    analyze = sub.add_parser("analyze", parents=[common], help="estimate area from role annotations")
    analyze.add_argument("--json", action="store_true", help="print the JSON report to stdout")

    floorplan = sub.add_parser("floorplan", parents=[common], help="generate the white-line floorplan")
    floorplan.add_argument("--title", default=None, help="SVG title override")

    handoff = sub.add_parser("handoff", parents=[common], help="generate the full review bundle")

    build = sub.add_parser("build", parents=[common], help="alias for handoff")
    build.add_argument("--title", default=None, help="SVG title override")

    compare = sub.add_parser("compare", help="compare area of several architectures")
    compare.add_argument("netlists", nargs="+", help="two or more netlists")
    compare.add_argument("--rules", default=None)
    compare.add_argument("--out", default=None, help="write compare.md to this directory")
    compare.add_argument(
        "--area-budget-mm2",
        type=float,
        default=None,
        help="optional area budget in mm2 applied to every design",
    )
    compare.add_argument("--quiet", action="store_true", help="only write output, do not print the table")
    compare.add_argument("--fail-on-gate", action="store_true", help="exit non-zero unless every design is PASS")

    validate = sub.add_parser("validate", help="validate annotations and geometry")
    validate.add_argument("netlist")
    validate.add_argument("--rules", default=None)
    validate.add_argument("--quiet", action="store_true")
    validate.add_argument(
        "--require-explicit-roles",
        action="store_true",
        help="fail if any device relies on name fallback instead of an explicit role=",
    )

    sub.add_parser("roles", help="print the device-role taxonomy")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "roles":
        _print_roles()
        return 0

    if args.command == "compare":
        return _cmd_compare(args)

    if args.command == "validate":
        return _cmd_validate(args)

    try:
        rules = load_rules(args.rules or default_rules_path())
        netlist = parse_file(args.netlist)
        errors, validation_warnings = validate_netlist(
            netlist, min_l_um=float(rules.mos("min_l_um", 0.0))
        )
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1

        budget = args.area_budget_mm2
        report = estimate_area(
            netlist,
            rules,
            area_budget_um2=(budget * 1e6) if budget is not None else None,
        )
        report.warnings = _dedupe(list(netlist.warnings) + report.warnings)

        if getattr(args, "fail_on_gate", False):
            gate = report.summary.get("area_gate", {})
            status = gate.get("status", "UNSET")
            if status != "PASS":
                print(
                    f"ERROR: area gate is {status}; pass --area-budget-mm2 and refine the estimate",
                    file=sys.stderr,
                )
                return 1

        if args.command == "analyze":
            return _cmd_analyze(args, report, netlist, rules)
        if args.command == "floorplan":
            return _cmd_floorplan(args, report, rules)
        if args.command in ("handoff", "build"):
            return _cmd_bundle(args, report, rules)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _print_summary(report: AreaReport) -> None:
    summary = report.summary
    print(f"Design:   {report.design}")
    print(f"Role owner: {ROLE_OWNER}")
    print(f"Rules:    {report.rules_name} ({report.rules_confidence})")
    print(
        f"Devices:  {summary['device_count']} ({summary['mos_count']} MOS, "
        f"{summary['cap_count']} cap) in {summary['group_count']} groups"
    )
    print(f"Core:     {area_str(summary['area_core_um2'])}")
    print(f"Area:     {area_str(summary['area_block_um2'])} block (committed)")
    print(f"Envelope: {area_str(summary['area_envelope_um2'])} (block + reserve)")
    print(f"Range:    {area_str(summary['area_low_um2'])} – {area_str(summary['area_high_um2'])}")
    print(f"Reserve:  {area_str(summary['area_reserved_um2'])}")
    gate = summary.get("area_gate", {})
    if gate.get("status") and gate["status"] != "UNSET":
        line = f"Area gate: {gate['status']:<9} budget {area_str(gate['budget_um2'])}"
        if gate["status"] == "PASS":
            line += f"  headroom {area_str(gate['headroom_um2'])}"
        elif gate["status"] == "REJECT":
            line += f"  shortfall {area_str(gate['shortfall_um2'])}"
        else:
            line += "  range overlaps budget; refine / layout check"
        print(line)
    dominant = summary.get("dominant_roles", [])
    if dominant:
        text = ", ".join(f"{item['role']} {item['share'] * 100:.0f}%" for item in dominant[:3])
        print(f"Dominant: {text}")
    sources = summary.get("role_sources", {})
    if not summary.get("all_roles_explicit", True):
        print(
            f"Roles:    explicit {sources.get('explicit', 0)}, "
            f"name fallback {sources.get('name', 0)}, other {sources.get('other', 0)}, "
            f"unknown {sources.get('unknown_role', 0)}"
        )
    if report.warnings:
        print(f"Warnings: {len(report.warnings)}")
        for warning in report.warnings:
            print(f"  - {warning}")


def _cmd_analyze(
    args: argparse.Namespace,
    report: AreaReport,
    netlist: Netlist,
    rules: Rules,
) -> int:
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    elif not args.quiet:
        _print_summary(report)

    if args.out:
        out = Path(args.out)
        write_json(out / "area_report.json", report.to_dict())
        write_text(out / "area_report.md", area_markdown(report))
        if not args.quiet:
            print(f"Wrote {out / 'area_report.json'}")
            print(f"Wrote {out / 'area_report.md'}")
    return 0


def _cmd_floorplan(args: argparse.Namespace, report: AreaReport, rules: Rules) -> int:
    floorplan = build_floorplan(report.design, report, rules)
    svg = render_floorplan_svg(floorplan, title=getattr(args, "title", None))
    out = Path(args.out or (Path("out") / report.design))
    write_json(out / "floorplan.json", floorplan.to_dict())
    write_text(out / "floorplan.svg", svg)
    if not args.quiet:
        _print_summary(report)
        print(f"Wrote {out / 'floorplan.svg'}")
        print(f"Wrote {out / 'floorplan.json'}")
    return 0


def _cmd_bundle(args: argparse.Namespace, report: AreaReport, rules: Rules) -> int:
    floorplan = build_floorplan(report.design, report, rules)
    delta = plan_layout_delta(report, floorplan, rules)
    svg = render_floorplan_svg(floorplan, title=getattr(args, "title", None))
    out = Path(args.out or (Path("out") / report.design))
    paths = write_bundle(
        out,
        report=report,
        floorplan=floorplan,
        delta=delta,
        svg_markup=svg,
    )
    if not args.quiet:
        _print_summary(report)
        print(f"Deltas:   {delta.summary['item_count']} proposed")
        print(f"Wrote {out}/")
        for key in ("index_html", "floorplan_svg", "handoff_md"):
            print(f"  - {paths[key]}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    rules_path = args.rules or default_rules_path()
    rules = load_rules(rules_path)
    netlist = parse_file(args.netlist)
    errors, warnings = validate_netlist(netlist, min_l_um=float(rules.mos("min_l_um", 0.0)))

    if args.require_explicit_roles:
        for device in netlist.devices:
            if device.role_source != "explicit":
                errors.append(
                    f"{device.name}: role must be explicit (source={device.role_source}); "
                    "name fallback is only a suggestion"
                )

    if not args.quiet:
        print(f"Netlist: {netlist.path}")
        print(f"Subckt:  {netlist.subckt} ({len(netlist.ports)} ports)")
        print(f"Devices: {len(netlist.devices)}")
        print(f"Rules:   {rules.name} (owner: {rules.owner})")
        print(f"Role owner: {ROLE_OWNER}")

    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        return 1
    if not args.quiet:
        print("OK: no structural errors")
    return 0


def _cmd_compare(args: argparse.Namespace) -> int:
    rules = load_rules(args.rules or default_rules_path())
    reports: list[AreaReport] = []
    for path in args.netlists:
        netlist = parse_file(path)
        errors, _ = validate_netlist(netlist, min_l_um=float(rules.mos("min_l_um", 0.0)))
        if errors:
            for error in errors:
                print(f"ERROR: {path}: {error}", file=sys.stderr)
            return 1
        budget = args.area_budget_mm2
        report = estimate_area(
            netlist,
            rules,
            area_budget_um2=(budget * 1e6) if budget is not None else None,
        )
        report.warnings = _dedupe(list(netlist.warnings) + report.warnings)
        reports.append(report)

    if getattr(args, "fail_on_gate", False):
        bad = [
            report.design
            for report in reports
            if report.summary.get("area_gate", {}).get("status") != "PASS"
        ]
        if bad:
            print(f"ERROR: area gate is not PASS for: {', '.join(bad)}", file=sys.stderr)
            return 1

    if not args.quiet:
        print(compare_markdown(reports))
    if args.out:
        out = Path(args.out)
        write_text(out / "compare.md", compare_markdown(reports))
        write_json(out / "compare.json", [report.to_dict() for report in reports])
        if not args.quiet:
            print(f"Wrote {out / 'compare.md'}")
    return 0


def _print_roles() -> None:
    print(f"Owner: {ROLE_OWNER}")
    print(ROLE_POLICY)
    print()
    print(f"{'role':<18} {'short':<6} {'band':<10} {'critical':<9} description")
    print("-" * 100)
    for spec in ROLES.values():
        print(
            f"{spec.id:<18} {spec.short:<6} {spec.band:<10} "
            f"{'yes' if spec.critical else 'no':<9} {spec.description}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
