"""Command-line interface."""

import argparse
import json

from rich.console import Console
from rich.table import Table

from . import CVE_ID, __version__
from .cpu import get_cpu_info
from .java_finder import JAVA_EXE, find_java_installs
from .mitigation import running_java_processes, workaround_active
from .verdict import EXIT_CODES, Verdict, decide

# Worst first: used to pick the overall verdict.
SEVERITY = [Verdict.VULNERABLE, Verdict.UNKNOWN, Verdict.MITIGATED, Verdict.PATCHED, Verdict.NOT_AFFECTED]

COLORS = {
    Verdict.VULNERABLE: "bold red",
    Verdict.UNKNOWN: "yellow",
    Verdict.MITIGATED: "cyan",
    Verdict.PATCHED: "green",
    Verdict.NOT_AFFECTED: "green",
}

ADVICE = {
    Verdict.VULNERABLE: "Update Java to a patched build from your vendor and restart all Java processes.\n"
                        "Temporary workaround: start Java with -XX:-UseBASE64Intrinsics",
    Verdict.UNKNOWN: "Could not read the Java version or vendor - check this installation manually.",
    Verdict.MITIGATED: "Workaround is active. Still plan the update to a patched build.",
}


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


def run_checks(path: str | None) -> dict:
    """Run every check and return the results as a plain dict."""
    cpu = get_cpu_info()
    cpu_affected = cpu.is_x86_64 and cpu.has_required_flags

    java = []
    for inst in find_java_installs(path):
        workaround = workaround_active(inst.path / "bin" / JAVA_EXE) if cpu_affected else None
        verdict = decide(inst.vendor, inst.major, inst.update, cpu_affected, workaround is True)
        java.append({
            "path": str(inst.path),
            "vendor": inst.vendor,
            "version": inst.version,
            "workaround": workaround,
            "verdict": verdict,
        })

    verdicts = [j["verdict"] for j in java] or [Verdict.NOT_AFFECTED]
    overall = min(verdicts, key=SEVERITY.index)

    return {
        "tool": "java4shell-check",
        "version": __version__,
        "cve": CVE_ID,
        "cpu": {
            "model": cpu.model,
            "arch": cpu.arch,
            "avx512_vbmi": cpu.has_required_flags,
            "affected": cpu_affected,
        },
        "java": java,
        "processes": running_java_processes(),
        "verdict": overall,
    }


def print_report(result: dict, console: Console) -> None:
    cpu = result["cpu"]
    console.print(f"[bold]java4shell-check {result['version']}[/bold]  -  {result['cve']}\n")
    console.print(f"CPU    {cpu['model']} ({cpu['arch']})   AVX-512 VBMI: {'yes' if cpu['avx512_vbmi'] else 'no'}")

    if not result["java"]:
        console.print("Java   none found (use --path to point at a specific installation)")
    else:
        table = Table(show_header=True, header_style="bold")
        for col in ("Vendor", "Version", "Workaround", "Verdict", "Path"):
            table.add_column(col)
        for j in result["java"]:
            if not cpu["affected"]:
                workaround = "n/a"
            else:
                workaround = {True: "on", False: "off", None: "?"}[j["workaround"]]
            v = j["verdict"]
            table.add_row(j["vendor"], j["version"], workaround, f"[{COLORS[v]}]{v.value}[/]", j["path"])
        console.print(table)

    if result["processes"]:
        unmitigated = [p for p in result["processes"] if not p["mitigated"]]
        console.print(f"Running Java processes: {len(result['processes'])} "
                      f"({len(unmitigated)} without the workaround flag)")

    overall = result["verdict"]
    console.print(f"\nVERDICT  [{COLORS[overall]}]{overall.value}[/]")
    if overall in ADVICE:
        console.print(ADVICE[overall])


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_checks(args.path)

    if args.json:
        print(json.dumps(result, indent=2, default=lambda v: v.value if isinstance(v, Verdict) else str(v)))
    elif args.quiet:
        print(result["verdict"].value)
    else:
        print_report(result, Console())

    return EXIT_CODES[result["verdict"]]