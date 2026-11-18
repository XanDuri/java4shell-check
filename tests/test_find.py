from java4shell_check.java_finder import JAVA_EXE, find_java_binaries


def make_jdk(base, name):
    bin_dir = base / name / "bin"
    bin_dir.mkdir(parents=True)
    exe = bin_dir / JAVA_EXE
    exe.write_text("")
    return exe


def test_finds_java_in_common_dir(tmp_path, monkeypatch):
    exe = make_jdk(tmp_path, "jdk-17")
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.setattr("shutil.which", lambda name: None)
    assert find_java_binaries(common_dirs=[str(tmp_path)]) == [exe]


def test_extra_path_checks_only_that_folder(tmp_path):
    make_jdk(tmp_path, "jdk-17")
    exe21 = make_jdk(tmp_path, "jdk-21")
    assert find_java_binaries(extra_path=str(tmp_path / "jdk-21")) == [exe21]


def test_java_home_and_common_dir_not_duplicated(tmp_path, monkeypatch):
    exe = make_jdk(tmp_path, "jdk-17")
    monkeypatch.setenv("JAVA_HOME", str(tmp_path / "jdk-17"))
    monkeypatch.setattr("shutil.which", lambda name: None)
    assert find_java_binaries(common_dirs=[str(tmp_path)]) == [exe]