"""Command-line interface."""

import argparse

from . import CVE_ID, __version__


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="java4shell-check",
        description=f"Read-only check for {CVE_ID} (Java4Shell). No exploit code is run.",
    )
    p.add_argument("--path", help="check only this Java installation folder")
    p.add_argument("--json", action="store_true", help="print the result as JSON")
    p.add_argument("--quiet", action="store_true", help="print only the verdict")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # TODO:
    # 1. cpu = get_cpu_info()
    # 2. installs = find_java_installs(args.path)
    # 3. for each install: check mitigation, call decide(...)
    # 4. print: rich table (default) / json.dumps (--json) / verdict only (--quiet)
    # 5. return the worst exit code (VULNERABLE=2 beats UNKNOWN=1 beats 0)
    print(f"java4shell-check {__version__} — not implemented yet (args: {vars(args)})")
    return 1
