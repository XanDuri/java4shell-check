"""Combine Java version, CPU and mitigation into one verdict."""

import json
from enum import Enum
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "fixed_versions.json"

AFFECTED_MAJORS = {17, 21, 25, 27}
MIN_AFFECTED_17 = (0, 6)  # per Calif: 17.0.6 and newer


class Verdict(str, Enum):
    NOT_AFFECTED = "NOT AFFECTED"
    PATCHED = "PATCHED"
    MITIGATED = "MITIGATED"
    VULNERABLE = "VULNERABLE"
    UNKNOWN = "UNKNOWN"


EXIT_CODES = {
    Verdict.NOT_AFFECTED: 0,
    Verdict.PATCHED: 0,
    Verdict.MITIGATED: 0,
    Verdict.UNKNOWN: 1,
    Verdict.VULNERABLE: 2,
}


def load_fixed_versions() -> dict:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def decide(
    vendor: str,
    major: int | None,
    update: tuple[int, ...] | None,
    cpu_affected: bool,
    mitigated: bool,
) -> Verdict:
    """Return the verdict for one Java install.

    Order of checks (write them as if-statements, top to bottom):
    1. version unknown                           -> UNKNOWN
    2. major not in AFFECTED_MAJORS              -> NOT_AFFECTED
    3. major == 17 and update < MIN_AFFECTED_17  -> NOT_AFFECTED
    4. version >= fixed version for this vendor  -> PATCHED
       (vendor not in fixed_versions.json        -> continue, can't tell)
    5. not cpu_affected (ARM or no VBMI)         -> NOT_AFFECTED
    6. mitigated                                 -> MITIGATED
    7. otherwise                                 -> VULNERABLE
    """
    if major is None or update is None:
        return Verdict.UNKNOWN

    if major not in AFFECTED_MAJORS:
        return Verdict.NOT_AFFECTED
    
    if major == 17 and update < MIN_AFFECTED_17:
        return Verdict.NOT_AFFECTED
    
    fixed = load_fixed_versions()
    if vendor in fixed and str(major) in fixed[vendor]:
        if (major, *update) >= tuple(fixed[vendor][str(major)]):
            return Verdict.PATCHED

    if not cpu_affected:
        return Verdict.NOT_AFFECTED

    if mitigated:
        return Verdict.MITIGATED

    return Verdict.VULNERABLE
