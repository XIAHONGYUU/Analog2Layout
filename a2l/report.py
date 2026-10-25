"""Human-readable reports and the one-page HTML review bundle."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from .area import AreaReport
from .delta import LayoutDelta
from .floorplan import Floorplan
from .roles import get_role

VERSION = "0.1.0"


def write_json(path: str | Path, data: Any) -> Path:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return file_path


def write_text(path: str | Path, text: str) -> Path:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(text, encoding="utf-8")
    return file_path


def area_str(area_um2: float) -> str:
    if area_um2 >= 1e6:
        return f"{area_um2 / 1e6:.3f} mm²"
    return f"{area_um2:.0f} µm²"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def area_markdown(report: AreaReport) -> str:
    summary = report.summary
    lines: list[str] = []
    lines.append(f"# Area report — {report.design}")
    lines.append("")
    lines.append(
        f"> Early planning estimate using **{report.rules_name}** "
        f"({report.rules_confidence}); owner: **{report.rules_owner}**. "
        f"Approval: {report.rules_approval}. Not a signoff area."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | ---: |")
    lines.append(f"| Devices | {summary['device_count']} ({summary['mos_count']} MOS, {summary['cap_count']} cap) |")
    lines.append(f"| Functional groups | {summary['group_count']} |")
    lines.append(f"| Device core (OD/cap) | {area_str(summary['area_core_um2'])} |")
    lines.append(f"| Active area (+ guard ring + device routing) | {area_str(summary['area_active_um2'])} |")
    lines.append(f"| Matched area (+ dummy + matching overhead) | {area_str(summary['area_matched_um2'])} |")
    lines.append(f"| Block area (+ periphery + block routing) | **{area_str(summary['area_block_um2'])}** |")
    lines.append(f"| PEX-fix reserve | {area_str(summary['area_reserved_um2'])} |")
    lines.append(f"| Total envelope (block + reserve) | {area_str(summary['area_envelope_um2'])} |")
    lines.append(f"| Dummy area | {area_str(summary['area_dummy_um2'])} |")
    lines.append(f"| Estimate range | {area_str(summary['area_low_um2'])} – {area_str(summary['area_high_um2'])} |")
    gate = summary.get("area_gate", {})
    if gate.get("status") and gate["status"] != "UNSET":
        lines.append(
            f"| Area gate | **{gate['status']}** (budget {area_str(gate['budget_um2'])}) |"
        )
    lines.append(f"| Width convention | `{report.width_convention}` |")
    lines.append("")
    lines.append(
        "**Area hierarchy:** device core (OD/cap only) < active (+ring/routing) < matched "
        "(+dummy/matching) < block (+periphery) < envelope (+reserve). "
        "Fractions below are relative to the block area."
    )
    lines.append("")
    lines.append("### Breakdown")
    lines.append("")
    lines.append("| Bucket | Area | Share of block |")
    lines.append("| --- | ---: | ---: |")
    for label, area_key, fraction_key in (
        ("Device core", "area_core_um2", "area_core_fraction"),
        ("Guard ring", "area_ring_um2", "area_ring_fraction"),
        ("Device routing", "area_device_routing_um2", "area_device_routing_fraction"),
        ("Dummy", "area_dummy_um2", "area_dummy_fraction"),
        ("Matching overhead", "area_matching_overhead_um2", "area_matching_fraction"),
        ("Periphery + block routing", "area_periphery_um2", "area_periphery_fraction"),
        ("PEX-fix reserve", "area_reserved_um2", "area_reserve_fraction"),
    ):
        fraction = f"{pct(summary[fraction_key])}" if fraction_key else "—"
        lines.append(f"| {label} | {area_str(summary[area_key])} | {fraction} |")
    lines.append("")
    sources = summary.get("role_sources", {})
    lines.append("### Annotation provenance")
    lines.append("")
    lines.append("| Source | Devices |")
    lines.append("| --- | ---: |")
    lines.append(f"| Name (primary source) | {sources.get('name', 0)} |")
    lines.append(f"| Explicit `role=` override | {sources.get('explicit', 0)} |")
    lines.append(f"| Other / invalid | {sources.get('other', 0)} |")
    lines.append(f"| Unknown role | {sources.get('unknown', 0)} |")
    lines.append("")

    lines.append("## Area by role")
    lines.append("")
    lines.append("| Role | Area | Share of device area |")
    lines.append("| --- | ---: | ---: |")
    total_role_area = sum(report.by_role.values()) or 1.0
    for role, area in sorted(report.by_role.items(), key=lambda item: -item[1]):
        spec = get_role(role)
        lines.append(f"| {spec.label_zh} (`{role}`) | {area_str(area)} | {pct(area / total_role_area)} |")
    lines.append("")

    lines.append("## Groups")
    lines.append("")
    lines.append("| Group | Role | Devices | Dummies | Area (with overhead) |")
    lines.append("| --- | --- | ---: | ---: | ---: |")
    for group in report.groups:
        names = ", ".join(device.name for device in group.devices)
        lines.append(
            f"| `{group.key}` | {group.role} | {len(group.devices)} | {group.dummy_count} | "
            f"{area_str(group.area_with_dummy_um2)} |"
        )
        _ = names
    lines.append("")

    lines.append("## Devices")
    lines.append("")
    lines.append("| Device | Role | Group | W/L (µm) | nf×m | Total W (µm) | Layout (µm) | Area |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for device in report.devices:
        if device.kind == "cap":
            wl = "—"
            nfm = "—"
            total_w = "—"
        else:
            geometry = ""
            wl = f"{device.w_um:g}/{device.l_um:g}"
            nfm = f"{device.nf}×{device.m}"
            total_w = f"{device.total_w_um:g}"
        lines.append(
            f"| `{device.name}` | {device.role} | `{device.group}` | {wl} | {nfm} | {total_w} | "
            f"{device.w_layout_um:.1f} × {device.h_layout_um:.1f} | {area_str(device.area_total_um2)} |"
        )
    lines.append("")

    if report.warnings:
        lines.append("## Warnings")
        lines.append("")
        for warning in report.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    lines.append("## Model notes")
    lines.append("")
    for note in summary.get("notes", []):
        lines.append(f"- {note}")
    lines.append("- MOS area = OD footprint (fingers × pitch × finger height) + guard ring + routing overhead.")
    lines.append("- Capacitor area = C / density; the generic density is a placeholder, not a PDK value.")
    lines.append("- Block area adds a periphery and a global routing factor around the sum of group areas.")
    lines.append("")
    return "\n".join(lines)


def handoff_markdown(
    report: AreaReport,
    floorplan: Floorplan,
    delta: LayoutDelta,
    *,
    svg_rel: str = "floorplan.svg",
) -> str:
    summary = report.summary
    lines: list[str] = []
    lines.append(f"# Handoff — {report.design}")
    lines.append("")
    lines.append(
        "> Floorplan sketch intent generated from a role-annotated schematic. "
        "Use this as the agenda for the schematic/layout review, not as a signoff document."
    )
    lines.append("")
    lines.append(f"![floorplan]({svg_rel})")
    lines.append("")
    lines.append("## 1. Block summary")
    lines.append("")
    reserve = summary["area_reserved_um2"]
    stats = floorplan.stats
    sources = summary.get("role_sources", {})
    shape = (
        f"{stats.get('block_width_um', 0):.1f} × {stats.get('block_height_um', 0):.1f} µm; "
        f"aspect {stats.get('aspect_ratio', 0):.2f}; squareness {stats.get('squareness', 0):.2f}; "
        f"{stats.get('orientation', 'unknown')}"
    )
    lines.append("| Metric | Value |")
    lines.append("| --- | ---: |")
    lines.append(f"| Device core | {area_str(summary['area_core_um2'])} |")
    lines.append(f"| Active area (+ ring/routing) | {area_str(summary['area_active_um2'])} |")
    lines.append(f"| Matched area (+ dummy/matching) | {area_str(summary['area_matched_um2'])} |")
    lines.append(f"| **Block area** | **{area_str(summary['area_block_um2'])}** |")
    lines.append(f"| PEX-fix reserve | {area_str(reserve)} |")
    lines.append(f"| Total envelope | {area_str(summary['area_envelope_um2'])} |")
    lines.append(f"| Dummy area | {area_str(summary['area_dummy_um2'])} |")
    lines.append(f"| Estimate range | {area_str(summary['area_low_um2'])} – {area_str(summary['area_high_um2'])} |")
    gate = summary.get("area_gate", {})
    if gate.get("status") and gate["status"] != "UNSET":
        lines.append(f"| Area gate | **{gate['status']}** (budget {area_str(gate['budget_um2'])}) |")
    lines.append(f"| Shape | {shape} |")
    lines.append(f"| Arrangement | {stats.get('arrangement', '—')} |")
    lines.append(f"| Devices / groups | {summary['device_count']} / {summary['group_count']} |")
    lines.append(f"| Rules | `{report.rules_name}` ({report.rules_confidence}); owner: {report.rules_owner} |")
    lines.append(f"| Width convention | `{report.width_convention}` |")
    lines.append(
        f"| Role sources | name {sources.get('name', 0)}, explicit override {sources.get('explicit', 0)}, "
        f"unknown {sources.get('unknown', 0)} |"
    )
    lines.append("")
    lines.append(
        "> Area hierarchy: **core** (OD/cap) < **active** (+guard ring/routing) < "
        "**matched** (+dummy/matching) < **block** (+periphery) < **envelope** (+reserve)."
    )
    lines.append("")

    lines.append("## 2. What layout must preserve")
    lines.append("")
    lines.append("- Input pair: symmetry, common-centroid/interdigitated pattern, clean gate routing, substrate isolation.")
    lines.append("- Current mirror / tail: identical environment for all ratio devices; boundary dummies as proposed.")
    lines.append("- Cascode stack: source-drain routing kept short; dummy stack at the boundary if proposed.")
    lines.append("- Output stage: current density, wide metal, multiple vias, EM/IR review.")
    lines.append("- Reserve the hatched PEX-fix strip; do not consume it for unrelated routing.")
    lines.append("")

    lines.append("## 3. Groups and devices")
    lines.append("")
    lines.append("| Group | Role | Devices | Match | Layout intent | Area |")
    lines.append("| --- | --- | --- | --- | --- | ---: |")
    for group in report.groups:
        names = ", ".join(f"`{device.name}`" for device in group.devices)
        layout = ", ".join(sorted({device.layout for device in group.devices if device.layout})) or "—"
        lines.append(
            f"| `{group.key}` | {group.role} | {names} | `{group.match or '—'}` | {layout} | "
            f"{area_str(group.area_with_dummy_um2)} |"
        )
    lines.append("")

    lines.append("## 4. Proposed layout-induced schematic deltas")
    lines.append("")
    lines.append(
        "These are the predictable changes that otherwise show up late in PEX. "
        "Accept or reject each item **before** the layout is frozen."
    )
    lines.append("")
    delta_total = delta.summary["area_delta_um2"]
    reserve = delta.summary["reserve_um2"]
    shortfall = delta.summary["reserve_shortfall_um2"]
    if shortfall > 0:
        lines.append(
            f"> **Reserve check:** proposed deltas total {area_str(delta_total)}, "
            f"but the PEX-fix reserve is {area_str(reserve)} — shortfall {area_str(shortfall)}. "
            "Increase the reserve or reduce/relocate deltas before freezing the floorplan."
        )
    else:
        lines.append(
            f"> **Reserve check:** proposed deltas total {area_str(delta_total)}, "
            f"within the {area_str(reserve)} PEX-fix reserve."
        )
    lines.append("")
    lines.append("| ID | Kind | Target | Action | Owner | Area impact | Status |")
    lines.append("| --- | --- | --- | --- | --- | ---: | --- |")
    for item in delta.items:
        lines.append(
            f"| `{item.id}` | {item.kind} | {item.target} | {item.action} | {item.owner} | "
            f"{area_str(item.area_delta_um2)} | {item.status} |"
        )
    lines.append("")

    lines.append("## 5. PEX re-simulation scope")
    lines.append("")
    for scope in delta.pex_resim_scope:
        lines.append(f"- {scope}")
    lines.append("")

    lines.append("## 6. Review questions")
    lines.append("")
    lines.append("- Are the role annotations complete and correct, especially for switches and dummies?")
    lines.append("- Is the input-pair symmetry axis where the designer expects it?")
    lines.append("- Are the proposed boundary dummies and dummy branches wanted, or should they be removed?")
    lines.append("- Is the decap value / location acceptable, or should it be split between supplies?")
    lines.append("- Does the reserved PEX-fix area match the team's risk tolerance for this block?")
    if float(stats.get("squareness", 1.0)) < 0.5:
        lines.append(
            f"- The block is elongated (aspect {stats.get('aspect_ratio', 0):.2f}, "
            f"squareness {stats.get('squareness', 0):.2f}); is this shape compatible with "
            "the parent block and the intended pin locations?"
        )
    gate = summary.get("area_gate", {})
    if gate.get("status") in ("UNCERTAIN", "REJECT"):
        lines.append(
            f"- The area gate is **{gate['status']}** at budget {area_str(gate.get('budget_um2', 0))}; "
            "should we refine the rule pack, reduce area, or renegotiate the budget?"
        )
    lines.append("")

    lines.append("## 7. Warnings")
    lines.append("")
    if report.warnings:
        for warning in report.warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def _area_gate_callout(summary: dict[str, Any]) -> str:
    gate = summary.get("area_gate", {})
    status = gate.get("status", "UNSET")
    if status == "UNSET":
        return ""
    budget = area_str(gate.get("budget_um2", 0.0))
    low = area_str(summary["area_low_um2"])
    high = area_str(summary["area_high_um2"])
    if status == "PASS":
        return (
            "<div class='callout ok'><b>Area gate passed.</b> "
            f"Budget {budget}; high estimate {high}; headroom {area_str(gate.get('headroom_um2', 0.0))}.</div>"
        )
    if status == "REJECT":
        return (
            "<div class='callout warn'><b>Area gate rejected.</b> "
            f"Budget {budget}; low estimate {low}; shortfall {area_str(gate.get('shortfall_um2', 0.0))}.</div>"
        )
    return (
        "<div class='callout warn'><b>Area gate uncertain.</b> "
        f"Budget {budget}; estimate range {low} – {high} overlaps the budget. "
        "Refine the estimate or do a layout check.</div>"
    )


def _reserve_callout(delta: LayoutDelta) -> str:
    shortfall = float(delta.summary.get("reserve_shortfall_um2", 0.0))
    reserve = float(delta.summary.get("reserve_um2", 0.0))
    total = float(delta.summary.get("area_delta_um2", 0.0))
    if shortfall > 0:
        return (
            "<div class='callout warn'><b>Reserve check failed.</b> "
            f"Proposed deltas total {area_str(total)}; reserve is {area_str(reserve)}; "
            f"shortfall {area_str(shortfall)}. Increase the reserve or reduce/relocate deltas.</div>"
        )
    return (
        "<div class='callout ok'><b>Reserve check passed.</b> "
        f"Proposed deltas total {area_str(total)}; reserve is {area_str(reserve)}.</div>"
    )


def index_html(
    report: AreaReport,
    floorplan: Floorplan,
    delta: LayoutDelta,
    *,
    svg_markup: str,
) -> str:
    summary = report.summary
    stats = floorplan.stats
    sources = summary.get("role_sources", {})

    hierarchy_rows = "\n".join(
        f"<tr><td>{label}</td><td>{desc}</td><td class='num'>{area_str(summary[area_key])}</td>"
        f"<td class='num'>{pct(summary[fraction_key])}</td></tr>"
        for label, desc, area_key, fraction_key in (
            ("Device core", "OD / capacitor only", "area_core_um2", "area_core_fraction"),
            ("Active", "+ guard ring, device routing", "area_active_um2", "area_active_fraction"),
            ("Matched", "+ dummy, matching overhead", "area_matched_um2", "area_matched_fraction"),
            ("Block", "+ periphery, block routing", "area_block_um2", "area_block_fraction"),
            ("Envelope", "+ PEX-fix reserve", "area_envelope_um2", "area_envelope_fraction"),
        )
    )
    breakdown_rows = "\n".join(
        f"<tr><td>{label}</td><td class='num'>{area_str(summary[area_key])}</td>"
        f"<td class='num'>{pct(summary[fraction_key])}</td></tr>"
        for label, area_key, fraction_key in (
            ("Guard ring", "area_ring_um2", "area_ring_fraction"),
            ("Device routing", "area_device_routing_um2", "area_device_routing_fraction"),
            ("Dummy", "area_dummy_um2", "area_dummy_fraction"),
            ("Matching overhead", "area_matching_overhead_um2", "area_matching_fraction"),
            ("Periphery + block routing", "area_periphery_um2", "area_periphery_fraction"),
            ("PEX-fix reserve", "area_reserved_um2", "area_reserve_fraction"),
        )
    )
    shape_items = "\n".join(
        [
            f"<li><b>Block bbox:</b> {stats.get('block_width_um', 0):.1f} × {stats.get('block_height_um', 0):.1f} µm</li>",
            f"<li><b>Aspect ratio:</b> {stats.get('aspect_ratio', 0):.2f} (W/H)</li>",
            f"<li><b>Squareness:</b> {stats.get('squareness', 0):.2f} (1.0 = square)</li>",
            f"<li><b>Orientation:</b> {stats.get('orientation', 'unknown')}</li>",
            f"<li><b>Arrangement:</b> {html.escape(str(stats.get('arrangement', '—')))}</li>",
        ]
    )
    role_rows = "\n".join(
        f"<tr><td><code>{html.escape(role)}</code></td><td>{html.escape(get_role(role).label_zh)}</td>"
        f"<td class='num'>{area_str(area)}</td>"
        f"<td class='num'>{pct(area / max(sum(report.by_role.values()), 1e-9))}</td></tr>"
        for role, area in sorted(report.by_role.items(), key=lambda item: -item[1])
    )
    group_rows = "\n".join(
        f"<tr><td><code>{html.escape(group.key)}</code></td><td>{html.escape(group.role)}</td>"
        f"<td>{html.escape(', '.join(device.name for device in group.devices))}</td>"
        f"<td class='num'>{group.dummy_count}</td><td class='num'>{area_str(group.area_with_dummy_um2)}</td></tr>"
        for group in report.groups
    )
    delta_rows = "\n".join(
        f"<tr><td><code>{html.escape(item.id)}</code></td><td>{html.escape(item.kind)}</td>"
        f"<td>{html.escape(item.target)}</td><td>{html.escape(item.action)}</td>"
        f"<td>{html.escape(item.owner)}</td><td class='num'>{area_str(item.area_delta_um2)}</td>"
        f"<td><span class='pill'>{html.escape(item.status)}</span></td></tr>"
        for item in delta.items
    )
    warning_items = "\n".join(f"<li>{html.escape(warning)}</li>" for warning in report.warnings) or "<li>None.</li>"
    scope_items = "\n".join(f"<li>{html.escape(scope)}</li>" for scope in delta.pex_resim_scope)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(report.design)} — Analog2Layout handoff</title>
<style>
  :root {{
    --ink: #0f172a; --muted: #64748b; --line: #e2e8f0; --paper: #ffffff;
    --bg: #f8fafc; --accent: #0f766e; --warn: #b45309;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--ink);
    font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width: 1440px; margin: 0 auto; padding: 32px 24px 64px; }}
  header {{ display: flex; justify-content: space-between; gap: 24px; align-items: flex-end;
    border-bottom: 1px solid var(--line); padding-bottom: 20px; margin-bottom: 24px; }}
  h1 {{ font-size: 28px; margin: 0 0 6px; letter-spacing: -0.02em; }}
  h2 {{ font-size: 18px; margin: 32px 0 12px; letter-spacing: -0.01em; }}
  p {{ line-height: 1.6; }}
  .sub {{ color: var(--muted); margin: 0; }}
  .badge {{ display: inline-block; font: 12px/1.4 ui-monospace, monospace; color: var(--muted);
    border: 1px solid var(--line); border-radius: 999px; padding: 4px 10px; background: var(--paper); }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; }}
  .card {{ background: var(--paper); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; }}
  .card .k {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .06em; }}
  .card .v {{ font-size: 20px; font-weight: 650; margin-top: 4px; }}
  .card .s {{ color: var(--muted); font-size: 12px; margin-top: 2px; }}
  .panel {{ background: var(--paper); border: 1px solid var(--line); border-radius: 14px; padding: 16px; overflow: auto; }}
  .svg-wrap {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 8px; overflow: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }}
  th {{ color: var(--muted); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }}
  td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  code {{ font: 12px ui-monospace, SFMono-Regular, Menlo, monospace; background: #f1f5f9; padding: 1px 5px; border-radius: 4px; }}
  .pill {{ display: inline-block; font-size: 11px; border: 1px solid #a7f3d0; background: #ecfdf5;
    color: #065f46; border-radius: 999px; padding: 1px 8px; }}
  .cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .note {{ color: var(--muted); font-size: 13px; }}
  .callout {{ border-radius: 10px; padding: 10px 14px; font-size: 13px; margin: 8px 0 12px; }}
  .callout.warn {{ background: #fffbeb; border: 1px solid #fde68a; color: #92400e; }}
  .callout.ok {{ background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; }}
  ul {{ margin: 8px 0 0 20px; padding: 0; }}
  li {{ margin: 4px 0; line-height: 1.5; }}
  footer {{ margin-top: 40px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--line); padding-top: 12px; }}
  @media (max-width: 900px) {{ .cols {{ grid-template-columns: 1fr; }} header {{ flex-direction: column; align-items: flex-start; }} }}
</style>
</head>
<body>
<main>
<header>
  <div>
    <h1>{html.escape(report.design)} — schematic → layout handoff</h1>
    <p class="sub">Role-aware area estimate and floorplan sketch intent. Generated by Analog2Layout v{VERSION}. Role taxonomy and rule values are owned by {html.escape(report.rules_owner)}.</p>
  </div>
  <div><span class="badge">{html.escape(report.rules_name)} · {html.escape(report.rules_confidence)}</span> <span class="badge">owner: analog</span></div>
</header>

<section class="cards">
  <div class="card"><div class="k">Device core</div><div class="v">{area_str(summary['area_core_um2'])}</div><div class="s">OD / capacitor only</div></div>
  <div class="card"><div class="k">Block area</div><div class="v">{area_str(summary['area_block_um2'])}</div><div class="s">matched + periphery + routing</div></div>
  <div class="card"><div class="k">Total envelope</div><div class="v">{area_str(summary['area_envelope_um2'])}</div><div class="s">block + PEX-fix reserve</div></div>
  <div class="card"><div class="k">Shape</div><div class="v">{stats.get('block_width_um', 0):.0f} × {stats.get('block_height_um', 0):.0f} µm</div><div class="s">aspect {stats.get('aspect_ratio', 0):.2f} · squareness {stats.get('squareness', 0):.2f}</div></div>
  <div class="card"><div class="k">Proposed deltas</div><div class="v">{delta.summary['item_count']}</div><div class="s">review before layout freeze</div></div>
</section>
<p class="note">{summary['device_count']} devices · {summary['group_count']} groups · estimate range {area_str(summary['area_low_um2'])} – {area_str(summary['area_high_um2'])} · dummy {area_str(summary['area_dummy_um2'])} · reserve {area_str(summary['area_reserved_um2'])} · role sources: name {sources.get('name', 0)} / explicit override {sources.get('explicit', 0)} / unknown {sources.get('unknown', 0)} · owner: {html.escape(report.rules_owner)}</p>
{_area_gate_callout(summary)}

<h2>Floorplan intent</h2>
<div class="svg-wrap">{svg_markup}</div>
<p class="note">Solid = existing device; dashed = proposed dummy/decap; hatched strip = reserved PEX-fix area. This is a floorplan sketch, not a legal layout.</p>

<h2>Area hierarchy</h2>
<div class="panel"><table>
  <thead><tr><th>Level</th><th>What it adds</th><th class="num">Area</th><th class="num">Relative to block</th></tr></thead>
  <tbody>{hierarchy_rows}</tbody>
</table></div>

<div class="cols">
  <section>
    <h2>Breakdown</h2>
    <div class="panel"><table>
      <thead><tr><th>Bucket</th><th class="num">Area</th><th class="num">Share</th></tr></thead>
      <tbody>{breakdown_rows}</tbody>
    </table></div>
  </section>
  <section>
    <h2>Shape &amp; arrangement</h2>
    <div class="panel"><ul>{shape_items}</ul></div>
  </section>
</div>

<div class="cols">
  <section>
    <h2>Area by role</h2>
    <div class="panel"><table>
      <thead><tr><th>Role</th><th>Meaning</th><th class="num">Area</th><th class="num">Share</th></tr></thead>
      <tbody>{role_rows}</tbody>
    </table></div>
  </section>
  <section>
    <h2>Warnings</h2>
    <div class="panel"><ul>{warning_items}</ul></div>
  </section>
</div>

<h2>Groups</h2>
<div class="panel"><table>
  <thead><tr><th>Group</th><th>Role</th><th>Devices</th><th class="num">Dummies</th><th class="num">Area</th></tr></thead>
  <tbody>{group_rows}</tbody>
</table></div>

<h2>Proposed layout-induced schematic deltas</h2>
{_reserve_callout(delta)}
<div class="panel"><table>
  <thead><tr><th>ID</th><th>Kind</th><th>Target</th><th>Action</th><th>Owner</th><th class="num">Area</th><th>Status</th></tr></thead>
  <tbody>{delta_rows}</tbody>
</table></div>

<h2>PEX re-simulation scope</h2>
<div class="panel"><ul>{scope_items}</ul></div>

<footer>
Generated by <code>a2l build</code>. Area is an early planning estimate; replace the generic rule pack with a company-validated one before production.
Links: <a href="area_report.md">area_report.md</a> · <a href="floorplan.json">floorplan.json</a> · <a href="layout_delta.json">layout_delta.json</a> · <a href="HANDOFF.md">HANDOFF.md</a>
</footer>
</main>
</body>
</html>
"""


def compare_markdown(reports: list[AreaReport]) -> str:
    lines: list[str] = ["# Architecture area comparison", ""]
    lines.append("| Design | Devices | Core | Matched | Block | Envelope | Range | Gate | Dominant role |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |")
    for report in reports:
        summary = report.summary
        dominant = summary.get("dominant_roles", [])
        dominant_text = ", ".join(f"{item['role']} ({pct(item['share'])})" for item in dominant[:2]) or "—"
        lines.append(
            f"| {report.design} | {summary['device_count']} | "
            f"{area_str(summary['area_core_um2'])} | {area_str(summary['area_matched_um2'])} | "
            f"{area_str(summary['area_block_um2'])} | {area_str(summary['area_envelope_um2'])} | "
            f"{area_str(summary['area_low_um2'])} – {area_str(summary['area_high_um2'])} | "
            f"{summary.get('area_gate', {}).get('status', 'UNSET')} | {dominant_text} |"
        )
    lines.append("")
    lines.append("> These are relative comparisons from the same rule pack. Do not compare numbers produced with different rule packs.")
    lines.append("")
    return "\n".join(lines)


def write_bundle(
    out_dir: str | Path,
    *,
    report: AreaReport,
    floorplan: Floorplan,
    delta: LayoutDelta,
    svg_markup: str,
) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "area_json": write_json(out / "area_report.json", report.to_dict()),
        "area_md": write_text(out / "area_report.md", area_markdown(report)),
        "floorplan_json": write_json(out / "floorplan.json", floorplan.to_dict()),
        "floorplan_svg": write_text(out / "floorplan.svg", svg_markup),
        "delta_json": write_json(out / "layout_delta.json", delta.to_dict()),
        "handoff_md": write_text(out / "HANDOFF.md", handoff_markdown(report, floorplan, delta)),
        "index_html": write_text(out / "index.html", index_html(report, floorplan, delta, svg_markup=svg_markup)),
    }
    return paths
