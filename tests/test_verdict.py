"""Run with:  pytest"""

import pytest

from java4shell_check.verdict import Verdict, decide


@pytest.mark.parametrize(
    "vendor, major, update, cpu_affected, mitigated, expected",
    [
        ("Temurin", 17, (0, 12), True, False, Verdict.VULNERABLE),
        ("Temurin", 17, (0, 12), False, False, Verdict.NOT_AFFECTED),  # ARM / no VBMI
        ("Temurin", 17, (0, 12), True, True, Verdict.MITIGATED),
        ("Oracle", 17, (0, 21, 1), True, False, Verdict.PATCHED),
        ("Temurin", 11, (0, 25), True, False, Verdict.NOT_AFFECTED),
        ("Temurin", 17, (0, 5), True, False, Verdict.NOT_AFFECTED),   # before 17.0.6
        ("unknown", None, None, True, False, Verdict.UNKNOWN),
    ],
)
def test_decide(vendor, major, update, cpu_affected, mitigated, expected):
    assert decide(vendor, major, update, cpu_affected, mitigated) == expected
