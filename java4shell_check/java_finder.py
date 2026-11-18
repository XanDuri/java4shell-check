"""Find Java installations and read their version and vendor."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class JavaInstall:
    path: Path            # folder with bin/java(.exe)
    vendor: str           # e.g. "Temurin", "Oracle", "Corretto", "unknown"
    version: str          # raw string, e.g. "17.0.12"
    major: int            # 17
    update: tuple[int, ...]  # (0, 12) — everything after the major number


# Typical places where Java gets installed.
COMMON_DIRS = [
    r"C:\Program Files\Java",
    r"C:\Program Files\Eclipse Adoptium",
    r"C:\Program Files\Amazon Corretto",
    r"C:\Program Files\Zulu",
    "/usr/lib/jvm",
    "/Library/Java/JavaVirtualMachines",
]


def find_java_installs(extra_path: str | None = None) -> list[JavaInstall]:
    """Return every Java found on this machine.

    TODO:
    - check JAVA_HOME (os.environ)
    - check `java` on PATH (shutil.which)
    - check every folder in COMMON_DIRS (one level down)
    - if extra_path is given (--path), check only that one
    - remove duplicates (same resolved path)
    """
    raise NotImplementedError


def read_version(java_bin: Path) -> tuple[str, str]:
    """Run `<java_bin> -version` and return (vendor, version).

    Remember: `java -version` prints to STDERR, not stdout.
    Example output:
        openjdk version "17.0.12" 2024-07-16
        OpenJDK Runtime Environment Temurin-17.0.12+7 (build 17.0.12+7)

    TODO: subprocess.run(..., capture_output=True, text=True, timeout=10),
    then a regex on result.stderr for the version and vendor.
    """
    raise NotImplementedError


def parse_version(version: str) -> tuple[int, tuple[int, ...]]:
    """'17.0.12' -> (17, (0, 12)).  '1.8.0_411' -> (8, (0, 411)).

    TODO: handle the old '1.8.0_xxx' format for Java 8.
    """
    raise NotImplementedError
