# java4shell-check

A small, **read-only** command-line tool that tells you in seconds whether a machine is affected by
**Java4Shell (CVE-2026-114938)** — and what to do about it.

> ⚠️ Work in progress (v0.1). No exploit or trigger code is included or run — the tool only reads
> Java versions, CPU flags and JVM settings, so it is safe to run on production hosts.

## Why

Java4Shell is a memory-corruption bug in OpenJDK's x86-64 Base64 intrinsic. A host is affected only
when **three conditions** are met at once:

1. an affected Java version (17 from 17.0.6, 21, 25, 27),
2. an x86-64 CPU with **AVX-512 VBMI** (`avx512f`, `avx512bw`, `avx512vbmi`, `bmi2`) — ARM is not affected,
3. the Base64 intrinsic is not disabled (`-XX:-UseBASE64Intrinsics`).

Checking that by hand on many servers is tedious. This tool does it in one command.

## Install

```bash
pip install .            # from a clone (PyPI release planned)
```

## Usage

```bash
java4shell-check                 # check every Java found on this machine
java4shell-check --path "C:\Program Files\Eclipse Adoptium\jdk-17"
java4shell-check --json          # machine-readable output
java4shell-check --quiet         # verdict only
```

| Verdict | Exit code |
| --- | --- |
| NOT AFFECTED / PATCHED / MITIGATED | 0 |
| UNKNOWN | 1 |
| VULNERABLE | 2 |

## Example output

<!-- TODO: paste real output once implemented -->

## Limitations

- Fixed versions differ per vendor; `java4shell_check/data/fixed_versions.json` must be kept up to date.
- Vendor detection relies on `java -version` output.

## References

- [Tenable — Java4Shell FAQ](https://www.tenable.com/blog/java4shell-cve-2026-114938-frequently-asked-questions-about-openjdk-rce-vulnerability)
- [Calif — Java4Shell write-up](https://calif.io/java4shell/)

## Author

**Łukasz Moszczyński** — [LinkedIn](https://linkedin.com/in/lukasz-moszczynski-soc) · [GitHub](https://github.com/XanDuri)

## License

MIT
