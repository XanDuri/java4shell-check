
# java4shell-check
 
A small, **read-only** command-line tool that tells you in seconds whether a machine is affected by
**Java4Shell (CVE-2026-114938)** — and what to do about it.
 
> No exploit or trigger code is included or run. The tool only reads Java versions, CPU flags and
> JVM settings, so it is safe to run on production hosts.
 
## Why
 
Java4Shell is a memory-corruption bug in OpenJDK's x86-64 Base64 intrinsic, disclosed on 17 Nov 2026.
A host is affected only when **three conditions** are met at once:
 
1. an affected Java version (17 from 17.0.6, 21, 25, 27),
2. an x86-64 CPU with **AVX-512 VBMI** (`avx512f`, `avx512bw`, `avx512vbmi`, `bmi2`) — ARM is not affected,
3. the workaround is not active (`-XX:-UseBASE64Intrinsics` or `-XX:UseAVX=2`).
A scanner that only looks at the Java version will flag every Java 17+ host. This tool also checks the
CPU and the JVM settings, so you know which hosts really need attention first.
 
## How it works
 
| Step | Module | What it checks |
| --- | --- | --- |
| 1 | `cpu.py` | CPU model, architecture and AVX-512 flags (`/proc/cpuinfo` on Linux, `py-cpuinfo` elsewhere) |
| 2 | `java_finder.py` | Java on `JAVA_HOME`, `PATH` and common install folders; vendor + version from `java -version` |
| 3 | `mitigation.py` | `java -XX:+PrintFlagsFinal` (Base64 intrinsic, `UseAVX`) and flags of running Java processes |
| 4 | `verdict.py` | Combines everything into one verdict per Java installation |
 
## Install
 
```bash
git clone https://github.com/XanDuri/java4shell-check.git
cd java4shell-check
pip install .
```
 
Requires Python 3.11+.
 
## Usage
 
```bash
java4shell-check                     # check every Java found on this machine
java4shell-check --path "C:\path\to\jdk-17"   # check one installation (the folder above bin\)
java4shell-check --json              # machine-readable output
java4shell-check --quiet             # verdict only
```
 
| Verdict | Meaning | Exit code |
| --- | --- | --- |
| NOT AFFECTED | version not affected, or CPU without AVX-512 VBMI | 0 |
| PATCHED | version is at or above the vendor's fixed build | 0 |
| MITIGATED | vulnerable version and CPU, but the workaround is active | 0 |
| UNKNOWN | version or vendor could not be read | 1 |
| VULNERABLE | affected version + affected CPU + no workaround | 2 |
 
Exit codes make it easy to use in scripts or CI: `java4shell-check --quiet || echo "check this host"`.
 
## Example output
 
**Lab host (Linux, Intel Xeon with AVX-512 VBMI, Temurin 17.0.12):**
 
```
CPU    Intel(R) Xeon(R) Processor @ 2.10GHz (x86_64)   AVX-512 VBMI: yes
┏━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Vendor  ┃ Version ┃ Workaround ┃ Verdict    ┃ Path            ┃
┡━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ Temurin │ 17.0.12 │ off        │ VULNERABLE │ /opt/jdk-17     │
└─────────┴─────────┴────────────┴────────────┴─────────────────┘
 
VERDICT  VULNERABLE
Update Java to a patched build from your vendor and restart all Java processes.
Temporary workaround: start Java with -XX:-UseBASE64Intrinsics
```
 
**My Windows gaming PC (AMD Ryzen 5 3600):**
 
```
CPU    AMD Ryzen 5 3600 6-Core Processor (AMD64)   AVX-512 VBMI: no
Java   none found (use --path to point at a specific installation)
 
VERDICT  NOT AFFECTED
```
 
## Real-world finding: "shadow" Java
 
On my PC, `java4shell-check` found **no Java** on `PATH` or `JAVA_HOME`. A full disk search found
**three Java runtimes bundled with the Minecraft launcher** (CurseForge) — Temurin 17.0.8, 21.0.4 and
21.0.12.1. All three versions are in the affected range:
 
```
java4shell-check --path "C:\Users\...\curseforge\minecraft\Install\java\java-runtime-gamma"
 
│ Temurin │ 17.0.8  │ n/a        │ NOT AFFECTED │ ...\java-runtime-gamma │
```
 
They are safe here only because the CPU has no AVX-512. On a Zen 4 desktop or a Xeon server, the same
runtimes would be **VULNERABLE** — and IT asset inventories usually miss them, because they are not
"installed" Java. The same problem made Log4Shell hard to find in 2021.
 
## Limitations
 
- Fixed versions differ per vendor; `java4shell_check/data/fixed_versions.json` currently lists Oracle only
  and must be kept up to date. For other vendors the tool can't confirm PATCHED and judges by CPU and workaround.
- The default search covers `JAVA_HOME`, `PATH` and common install folders — bundled runtimes need `--path`
  (see roadmap).
- Vendor detection relies on `java -version` output.
## Roadmap
 
- [ ] `--deep`: search the whole disk for bundled Java runtimes (like the Minecraft example above)
- [ ] Fixed versions for Temurin, Corretto, Zulu, Microsoft and Red Hat builds
- [ ] Release on PyPI (`pip install java4shell-check`)
- [ ] GitHub Actions: run tests on every push (Windows + Linux)
## Testing
 
```bash
pip install -e ".[dev]"
pytest
```
 
24 tests cover version parsing, vendor detection, Java discovery, workaround detection and the verdict
logic — without needing Java installed.
 
## References
 
- [Tenable — Java4Shell FAQ](https://www.tenable.com/blog/java4shell-cve-2026-114938-frequently-asked-questions-about-openjdk-rce-vulnerability)
- [Calif — Java4Shell write-up](https://calif.io/java4shell/)
## Author
 
**Łukasz Moszczyński** — Junior SOC / Security Analyst
[LinkedIn](https://linkedin.com/in/lukasz-moszczynski-soc) · [GitHub](https://github.com/XanDuri) · [TryHackMe](https://tryhackme.com/p/XanDuri)
 
## License
 
MIT
 
