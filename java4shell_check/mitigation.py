"""Check whether the Java4Shell workaround is active."""

import re
import subprocess
from pathlib import Path

import psutil

WORKAROUND_FLAGS = ("-XX:-UseBASE64Intrinsics", "-XX:UseAVX=2", "-XX:UseAVX=1", "-XX:UseAVX=0")
JAVA_PROCESS_NAMES = {"java", "java.exe", "javaw", "javaw.exe"}

def parse_flags_output(text: str) -> bool | None:
    """Read `java -XX:+PrintFlagsFinal` output.

    True  -> workaround active (Base64 intrinsic off, or UseAVX below 3)
    False -> workaround not active
    None  -> flags not found, can't tell
    """
    intrinsic = re.search(r"\bUseBASE64Intrinsics\s*=\s*(true|false)", text)
    avx = re.search(r"\bUseAVX\s*=\s*(\d+)", text)
    if intrinsic is None and avx is None:
        return None
    if intrinsic and intrinsic.group(1) == "false":
        return True
    if avx and int(avx.group(1)) < 3:
        return True
    return False


def workaround_active(java_bin: Path) -> bool | None:
    """Run `java -XX:+PrintFlagsFinal -version` and check the workaround flags."""
    try:
        result = subprocess.run(
            [str(java_bin), "-XX:+PrintFlagsFinal", "-version"],
            capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return parse_flags_output(result.stdout)


def has_workaround_flag(cmdline: str) -> bool:
    return any(flag in cmdline for flag in WORKAROUND_FLAGS)


def running_java_processes() -> list[dict]:
    """List running Java processes and whether each one uses a workaround flag."""
    procs = []
    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        name = (p.info["name"] or "").lower()
        if name not in JAVA_PROCESS_NAMES:
            continue
        cmdline = " ".join(p.info["cmdline"] or [])
        procs.append({"pid": p.info["pid"], "cmdline": cmdline, "mitigated": has_workaround_flag(cmdline)})
    return procs