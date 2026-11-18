"""CPU architecture and the AVX-512 flags Java4Shell needs."""

import platform
from dataclasses import dataclass
from pathlib import Path

# All four must be present for the vulnerable Base64 intrinsic to be used.
REQUIRED_FLAGS = {"avx512f", "avx512bw", "avx512vbmi", "bmi2"}


@dataclass
class CpuInfo:
    model: str
    arch: str               # "x86_64", "arm64", ...
    flags: set[str]

    @property
    def is_x86_64(self) -> bool:
        return self.arch.lower() in {"x86_64", "amd64"}

    @property
    def has_required_flags(self) -> bool:
        return REQUIRED_FLAGS.issubset(self.flags)


def get_cpu_info() -> CpuInfo:
    """Read CPU model, architecture and flags (Linux: /proc/cpuinfo, else py-cpuinfo)."""
    arch = platform.machine()
    model = "unknown"
    flags: set[str] = set()

    proc = Path("/proc/cpuinfo")
    if proc.exists():
        for line in proc.read_text().splitlines():
            key, _, value = line.partition(":")
            key = key.strip()
            if key == "model name" and model == "unknown":
                model = value.strip()
            if key == "flags" and not flags:
                flags = set(value.split())
    else:
        import cpuinfo
        info = cpuinfo.get_cpu_info()
        model = info.get("brand_raw", "unknown")
        flags = set(info.get("flags", []))

    return CpuInfo(model=model, arch=arch, flags={f.lower() for f in flags})
