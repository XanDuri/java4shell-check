"""CPU architecture and the AVX-512 flags Java4Shell needs."""

from dataclasses import dataclass

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
    """Read CPU model, architecture and flags.

    TODO:
    - arch: platform.machine()
    - Linux: read the first 'flags' line from /proc/cpuinfo
    - Windows / macOS: `import cpuinfo; cpuinfo.get_cpu_info()` -> 'brand_raw', 'flags'
    - lowercase all flags
    """
    raise NotImplementedError
