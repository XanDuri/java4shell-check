"""Find Java installations and read their version and vendor."""

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import os
import shutil
import sys

JAVA_EXE = "java.exe" if sys.platform == "win32" else "java"

@dataclass
class JavaInstall:
    path: Path            # folder with bin/java(.exe)
    vendor: str           # e.g. "Temurin", "Oracle", "Corretto", "unknown"
    version: str          # raw string, e.g. "17.0.12"
    major: int | None     # 17
    update: tuple[int, ...] | None  # (0, 12) — everything after the major number


# Typical places where Java gets installed.
COMMON_DIRS = [
    r"C:\Program Files\Java",
    r"C:\Program Files\Eclipse Adoptium",
    r"C:\Program Files\Amazon Corretto",
    r"C:\Program Files\Zulu",
    "/usr/lib/jvm",
    "/Library/Java/JavaVirtualMachines",
]

VENDORS = [
    ("Temurin", "Temurin"),
    ("Corretto", "Corretto"),
    ("Zulu", "Zulu"),
    ("Microsoft", "Microsoft"),
    ("Red_Hat", "Red Hat"),
    ("SapMachine", "SapMachine"),
    ("BellSoft", "Liberica"),
    ("GraalVM", "GraalVM"),
    ("Java(TM) SE", "Oracle"),
]


def parse_java_output(text: str) -> tuple[str, str | None]:
    """Return (vendor, version) from `java -version` output."""
    match = re.search(r'version "([^"]+)"', text)
    version = match.group(1) if match else None

    for keyword, name in VENDORS:
        if keyword in text:
            return name, version

    if "OpenJDK" in text:
        return "OpenJDK", version
    return "unknown", version



def _java_in(home: Path) -> Path | None:
    """Return home/bin/java(.exe) if it exists."""
    candidate = home / "bin" / JAVA_EXE
    return candidate if candidate.is_file() else None


def find_java_binaries(extra_path: str | None = None, common_dirs: list[str] = COMMON_DIRS) -> list[Path]:
    """Return paths to java executables, without duplicates."""
    if extra_path:
        found = _java_in(Path(extra_path))
        return [found] if found else []

    candidates: list[Path | None] = []
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        candidates.append(_java_in(Path(java_home)))
    on_path = shutil.which("java")
    if on_path:
        candidates.append(Path(on_path))
    for folder in common_dirs:
        base = Path(folder)
        if base.is_dir():
            for child in base.iterdir():
                candidates.append(_java_in(child))

    unique: dict[Path, Path] = {}
    for c in candidates:
        if c is not None:
            unique.setdefault(c.resolve(), c)
    return list(unique.values())


def find_java_installs(extra_path: str | None = None) -> list[JavaInstall]:
    """Find every Java and read its vendor and version."""
    installs = []
    for java_bin in find_java_binaries(extra_path):
        try:
            vendor, version = read_version(java_bin)
        except (OSError, subprocess.TimeoutExpired):
            vendor, version = "unknown", None
        major, update = None, None
        if version:
            try:
                major, update = parse_version(version)
            except ValueError:
                pass
        installs.append(JavaInstall(java_bin.parent.parent, vendor, version or "unknown", major, update))
    return installs


def read_version(java_bin: Path) -> tuple[str, str]:
    result = subprocess.run([str(java_bin), "-version"], capture_output=True, text=True, timeout=10)
    return parse_java_output(result.stderr or result.stdout)


def parse_version(version: str) -> tuple[int, tuple[int, ...]]:
    """'17.0.12' -> (17, (0, 12)).  '1.8.0_411' -> (8, (0, 411))."""
    
    version = version.split("+", 1)[0].replace("_", ".")
    parts = [int(x) for x in version.split(".")]
    if parts[0] == 1:
        # Java 8 and older: 1.8.0_411 -> 8, (0, 411)
        return parts[1], tuple(parts[2:])
    else:
        # Java 9 and newer: 17.0.12 -> 17, (0, 12)
        return parts[0], tuple(parts[1:])