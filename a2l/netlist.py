"""A deliberately small SPICE-like netlist reader.

The prototype supports the subset needed for schematic-level handoff:

* MOS devices: ``M1 d g s b model w=... l=... nf=... m=...``
* Spectre-style node lists: ``M1 (d g s b) model w=...``
* capacitors: ``C1 n1 n2 1.5p`` or ``C1 n1 n2 c=1.5p``
* ``.subckt`` / ``.ends``
* line continuation with ``+``
* annotations in the parameter list: ``role=``, ``match=``, ``group=``,
  ``layout=``

It is not a full SPICE parser.  In particular it does not expand device
models, evaluate ``.param`` expressions, or flatten hierarchical subcircuits.
That limitation is intentional: the input to the handoff layer should be a
clean, flattened netlist exported by the schematic tool.
"""

from __future__ import annotations

import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .roles import annotate_devices
from .units import parse_cap_pf, parse_eng, parse_length_um, parse_positive_int


@dataclass
class Device:
    name: str
    kind: str  # "mos", "cap" or "other"
    nodes: list[str]
    model: str
    params: dict[str, str] = field(default_factory=dict)
    line_no: int = 0
    subckt: str = ""
    role: str | None = None
    role_source: str = "unknown"
    match: str | None = None
    group: str | None = None
    layout: str | None = None

    @property
    def mos_type(self) -> str | None:
        if self.kind != "mos":
            return None
        model = self.model.lower()
        if model.startswith("n") or "nch" in model or "nmos" in model:
            return "nmos"
        if model.startswith("p") or "pch" in model or "pmos" in model:
            return "pmos"
        return "unknown"

    @property
    def w_um(self) -> float:
        return parse_length_um(self.params.get("w", "0"), what=f"{self.name} W")

    @property
    def l_um(self) -> float:
        return parse_length_um(self.params.get("l", "0"), what=f"{self.name} L")

    @property
    def nf(self) -> int:
        return parse_positive_int(self.params.get("nf", "1"), what=f"{self.name} nf")

    @property
    def m(self) -> int:
        return parse_positive_int(self.params.get("m", "1"), what=f"{self.name} m")

    @property
    def c_pf(self) -> float:
        raw = self.params.get("c", self.params.get("value", "0"))
        return parse_cap_pf(raw, what=f"{self.name} C")

    def total_width_um(self, width_convention: str = "per_finger") -> float:
        """Return the total drawn channel width.

        ``per_finger`` (default): SPICE ``w`` is one finger, so
        ``W_total = w * nf * m``.

        ``total``: ``w`` already includes all fingers and only ``m`` multiplies.
        """

        w = self.w_um
        if width_convention == "total":
            return w * self.m
        return w * self.nf * self.m

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "nodes": self.nodes,
            "model": self.model,
            "params": self.params,
            "line_no": self.line_no,
            "subckt": self.subckt,
            "role": self.role,
            "role_source": self.role_source,
            "match": self.match,
            "group": self.group,
            "layout": self.layout,
            "mos_type": self.mos_type,
        }


@dataclass
class Netlist:
    path: str
    name: str
    subckt: str
    ports: list[str]
    devices: list[Device]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "name": self.name,
            "subckt": self.subckt,
            "ports": self.ports,
            "devices": [device.to_dict() for device in self.devices],
            "warnings": self.warnings,
        }

    def device_by_name(self) -> dict[str, Device]:
        return {device.name: device for device in self.devices}


def _strip_comment(line: str) -> str:
    text = line.rstrip("\n\r")
    for marker in ("//", ";"):
        index = text.find(marker)
        if index >= 0:
            text = text[:index]
    if text.lstrip().startswith("*"):
        return ""
    return text.rstrip()


def _logical_lines(text: str) -> list[tuple[int, str]]:
    """Join SPICE continuation lines, preserving the first line number."""

    result: list[tuple[int, str]] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        line = _strip_comment(raw)
        if not line.strip():
            continue
        if line.lstrip().startswith("+"):
            if not result:
                result.append((number, line.lstrip()[1:].strip()))
            else:
                first_number, previous = result[-1]
                result[-1] = (first_number, f"{previous} {line.lstrip()[1:].strip()}")
        else:
            result.append((number, line.strip()))
    return result


def _parse_key_values(tokens: list[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    for token in tokens:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        key = key.strip().lower()
        value = value.strip().strip("'\"")
        if key:
            params[key] = value
    return params


def _parse_nodes_and_model(tokens: list[str], line_no: int, warnings: list[str]) -> tuple[list[str], str, list[str]]:
    """Extract nodes, model and parameter tokens from a device line."""

    if len(tokens) < 2:
        warnings.append(f"line {line_no}: device line has no nodes")
        return [], "", []

    if tokens[1].startswith("("):
        # Spectre: M1 (d g s b) model w=... l=...
        joined = " ".join(tokens[1:])
        close = joined.find(")")
        if close < 0:
            warnings.append(f"line {line_no}: unterminated node list")
            return [], "", []
        node_text = joined[1:close]
        rest = joined[close + 1 :].strip()
        nodes = [part for part in re.split(r"[\s,]+", node_text) if part]
        rest_tokens = shlex.split(rest)
        if not rest_tokens:
            warnings.append(f"line {line_no}: missing model name")
            return nodes, "", []
        return nodes, rest_tokens[0], rest_tokens[1:]

    if len(tokens) < 6:
        warnings.append(f"line {line_no}: expected at least 4 nodes and a model")
        return tokens[1:-1], tokens[-1] if len(tokens) > 1 else "", []

    return tokens[1:5], tokens[5], tokens[6:]


def parse_text(text: str, *, path: str = "<memory>", name: str | None = None) -> Netlist:
    warnings: list[str] = []
    logical = _logical_lines(text)

    subckt = name or Path(path).stem
    ports: list[str] = []
    devices: list[Device] = []
    current_subckt = ""
    seen_names: set[str] = set()

    for line_no, line in logical:
        tokens = shlex.split(line)
        if not tokens:
            continue
        head = tokens[0].lower()

        if head == ".subckt":
            if len(tokens) < 2:
                warnings.append(f"line {line_no}: .subckt without a name")
                continue
            current_subckt = tokens[1]
            subckt = current_subckt
            ports = tokens[2:]
            continue

        if head in (".ends", ".end"):
            current_subckt = ""
            continue

        if head.startswith("."):
            # .model, .param, .include, .global, ... are not needed for the
            # handoff view.  Ignore them explicitly rather than guessing.
            continue

        if head.startswith("m"):
            nodes, model, param_tokens = _parse_nodes_and_model(tokens, line_no, warnings)
            params = _parse_key_values(param_tokens)
            device = Device(
                name=tokens[0],
                kind="mos",
                nodes=nodes,
                model=model,
                params=params,
                line_no=line_no,
                subckt=current_subckt,
            )
        elif head.startswith("c"):
            if len(tokens) < 4:
                warnings.append(f"line {line_no}: capacitor needs two nodes and a value")
                continue
            params = _parse_key_values(tokens[3:])
            if "c" not in params and "value" not in params:
                params["c"] = tokens[3]
            device = Device(
                name=tokens[0],
                kind="cap",
                nodes=tokens[1:3],
                model="cap",
                params=params,
                line_no=line_no,
                subckt=current_subckt,
            )
        else:
            # Resistors, inductors, sources, etc. are out of scope for v0.1.
            continue

        if device.name in seen_names:
            warnings.append(f"line {line_no}: duplicate device name {device.name!r}")
        seen_names.add(device.name)
        devices.append(device)

    if not devices:
        warnings.append("no MOS or capacitor devices found")

    netlist = Netlist(
        path=path,
        name=name or Path(path).stem,
        subckt=subckt,
        ports=ports,
        devices=devices,
        warnings=warnings,
    )
    warning = annotate_devices(netlist)
    netlist.warnings.extend(warning)
    return netlist


def parse_file(path: str | Path, *, name: str | None = None) -> Netlist:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    return parse_text(text, path=str(file_path), name=name or file_path.stem)


def validate_netlist(netlist: Netlist, *, min_l_um: float = 0.0) -> tuple[list[str], list[str]]:
    """Return ``(errors, warnings)`` for structural/annotation problems."""

    errors: list[str] = []
    warnings: list[str] = list(netlist.warnings)

    for device in netlist.devices:
        if device.kind == "mos":
            if "w" not in device.params:
                errors.append(f"{device.name}: missing w=")
            if "l" not in device.params:
                errors.append(f"{device.name}: missing l=")
            try:
                if device.w_um <= 0:
                    errors.append(f"{device.name}: w must be > 0")
                if device.l_um <= 0:
                    errors.append(f"{device.name}: l must be > 0")
                if min_l_um and device.l_um + 1e-12 < min_l_um:
                    warnings.append(
                        f"{device.name}: L={device.l_um:g} um is below the rule minimum {min_l_um:g} um"
                    )
                _ = device.nf
                _ = device.m
            except ValueError as exc:
                errors.append(f"{device.name}: {exc}")
        elif device.kind == "cap":
            try:
                if device.c_pf <= 0:
                    errors.append(f"{device.name}: capacitance must be > 0")
            except ValueError as exc:
                errors.append(f"{device.name}: {exc}")

    return errors, warnings


def known_value(value: str | None, default: float = 0.0) -> float:
    """Best-effort parse used by optional parameters."""

    if value is None or str(value).strip() == "":
        return default
    try:
        return parse_eng(value)
    except ValueError:
        return default
