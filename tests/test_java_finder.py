import pytest

from java4shell_check.java_finder import parse_version


@pytest.mark.parametrize(
    "text, expected",
    [
        ("17.0.12", (17, (0, 12))),
        ("21.0.13.1", (21, (0, 13, 1))),
        ("1.8.0_411", (8, (0, 411))),
        ("21", (21, ())),
        ("17.0.12+7", (17, (0, 12))),
    ],
)
def test_parse_version(text, expected):
    assert parse_version(text) == expected

from java4shell_check.java_finder import parse_java_output

TEMURIN = """openjdk version "17.0.12" 2024-07-16
OpenJDK Runtime Environment Temurin-17.0.12+7 (build 17.0.12+7)
OpenJDK 64-Bit Server VM Temurin-17.0.12+7 (build 17.0.12+7, mixed mode, sharing)"""

ORACLE = """java version "21.0.13" 2026-10-20 LTS
Java(TM) SE Runtime Environment (build 21.0.13+8-LTS-123)
Java HotSpot(TM) 64-Bit Server VM (build 21.0.13+8-LTS-123, mixed mode)"""

CORRETTO_8 = """openjdk version "1.8.0_412"
OpenJDK Runtime Environment Corretto-8.412.08.1 (build 1.8.0_412-b08)
OpenJDK 64-Bit Server VM Corretto-8.412.08.1 (build 25.412-b08, mixed mode)"""


@pytest.mark.parametrize(
    "text, expected",
    [
        (TEMURIN, ("Temurin", "17.0.12")),
        (ORACLE, ("Oracle", "21.0.13")),
        (CORRETTO_8, ("Corretto", "1.8.0_412")),
        ("garbage", ("unknown", None)),
    ],
)
def test_parse_java_output(text, expected):
    assert parse_java_output(text) == expected