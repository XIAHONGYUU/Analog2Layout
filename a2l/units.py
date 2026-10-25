"""Engineering-unit parsing for SPICE-like values.

The rest of the code works in a small set of canonical units:

* lengths: micrometres (um)
* capacitance: picofarads (pF)
* area: square micrometres (um^2)

SPICE values are accepted in the usual forms: ``10u``, ``500n``, ``1.5p``,
``2.2k``, ``1e-6``, and suffixes may carry trailing unit letters such as
``10um`` or ``1.5pF``.
"""

from __future__ import annotations

import math
import re

_ENG = {
    "f": 1e-15,
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "m": 1e-3,
    "k": 1e3,
    "g": 1e9,
    "t": 1e12,
}

_NUMBER_RE = re.compile(
    r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([a-zA-Z]*)\s*$"
)


def parse_eng(value: str | int | float, *, what: str = "value") -> float:
    """Parse an engineering-notation number into its base SI value.

    >>> parse_eng("10u")
    1e-05
    >>> parse_eng("1.5pF")
    1.5e-12
    >>> parse_eng("2.2k")
    2200.0
    """

    if isinstance(value, bool):
        raise ValueError(f"cannot parse {what} from a boolean")
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace("\u00b5", "u").replace("\u03bc", "u")
    if not text:
        raise ValueError(f"empty {what}")

    match = _NUMBER_RE.match(text)
    if not match:
        raise ValueError(f"cannot parse {what}: {value!r}")

    number = float(match.group(1))
    suffix = match.group(2).lower()
    if not suffix:
        return number

    # ``meg`` must be checked before the single-letter ``m`` (milli).
    if suffix.startswith("meg"):
        return number * 1e6

    first = suffix[0]
    if first in _ENG:
        return number * _ENG[first]

    # A trailing unit that is not an engineering prefix (e.g. ``10V``) is
    # tolerated because the numeric part is still unambiguous.
    if len(suffix) >= 2 and suffix[1] in _ENG:
        return number * _ENG[suffix[1]]

    raise ValueError(f"unknown engineering suffix in {what}: {value!r}")


def _number_and_suffix(value: str | int | float, *, what: str) -> tuple[float, str]:
    if isinstance(value, bool):
        raise ValueError(f"cannot parse {what} from a boolean")
    if isinstance(value, (int, float)):
        return float(value), ""
    text = str(value).strip().replace("\u00b5", "u").replace("\u03bc", "u")
    match = _NUMBER_RE.match(text)
    if not match:
        raise ValueError(f"cannot parse {what}: {value!r}")
    return float(match.group(1)), match.group(2).lower()


def parse_length_um(value: str | int | float, *, what: str = "length") -> float:
    """Parse a length and return micrometres.

    A unitless value is interpreted as micrometres, which is the convention
    used by this project's netlists and rule packs.  Use ``n``, ``u`` or ``m``
    when a different scale is intended.
    """

    number, suffix = _number_and_suffix(value, what=what)
    if not suffix:
        return number
    return parse_eng(value, what=what) * 1e6


def parse_cap_pf(value: str | int | float, *, what: str = "capacitance") -> float:
    """Parse a capacitance and return picofarads.

    A unitless value is interpreted as picofarads.
    """

    number, suffix = _number_and_suffix(value, what=what)
    if not suffix:
        return number
    return parse_eng(value, what=what) * 1e12


def parse_positive_int(value: str | int | float, *, what: str = "count") -> int:
    number = parse_eng(value, what=what)
    if number <= 0 or not math.isfinite(number):
        raise ValueError(f"{what} must be a positive number, got {value!r}")
    if abs(number - round(number)) > 1e-9:
        raise ValueError(f"{what} must be an integer, got {value!r}")
    return int(round(number))


def fmt_um(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f} um"


def fmt_area(value_um2: float, digits: int = 1) -> str:
    if value_um2 >= 1e6:
        return f"{value_um2 / 1e6:.{digits}f} mm2"
    return f"{value_um2:.{digits}f} um2"


def fmt_pf(value_pf: float, digits: int = 2) -> str:
    return f"{value_pf:.{digits}f} pF"
