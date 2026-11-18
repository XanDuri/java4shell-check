import pytest

from java4shell_check.mitigation import has_workaround_flag, parse_flags_output

DEFAULT = """     bool UseBASE64Intrinsics                      = true                                   {ARCH product} {default}
     intx UseAVX                                   = 3                                   {ARCH product} {default}"""


@pytest.mark.parametrize(
    "text, expected",
    [
        (DEFAULT, False),
        (DEFAULT.replace("= true", "= false"), True),
        (DEFAULT.replace("= 3 ", "= 2 "), True),
        ("no flags here", None),
    ],
)
def test_parse_flags_output(text, expected):
    assert parse_flags_output(text) == expected


def test_has_workaround_flag():
    assert has_workaround_flag("java -XX:-UseBASE64Intrinsics -jar app.jar")
    assert not has_workaround_flag("java -jar app.jar")