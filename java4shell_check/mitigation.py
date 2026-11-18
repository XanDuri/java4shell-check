"""Check whether the Base64 intrinsic is disabled (the temporary workaround)."""

from pathlib import Path

WORKAROUND_FLAGS = ("-XX:-UseBASE64Intrinsics", "-XX:UseAVX=2")


def intrinsic_enabled_by_default(java_bin: Path) -> bool | None:
    """Run `java -XX:+PrintFlagsFinal -version` and read UseBASE64Intrinsics.

    The line looks like:
        bool UseBASE64Intrinsics   = true   {ARCH product} {default}

    Return True / False, or None if the flag is not listed.
    TODO: subprocess.run + search the output for 'UseBASE64Intrinsics'.
    """
    raise NotImplementedError


def running_java_processes() -> list[dict]:
    """List running Java processes and whether each one uses a workaround flag.

    Return items like: {"pid": 1234, "cmdline": "...", "mitigated": True}
    TODO: psutil.process_iter(["pid", "name", "cmdline"]),
    keep names starting with 'java', check cmdline for WORKAROUND_FLAGS.
    Catch psutil.AccessDenied — some processes can't be read without admin.
    """
    raise NotImplementedError
