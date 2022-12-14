# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

try:
    import tomllib
except ImportError:
    import tomli as tomllib

import pytest

import fedrq.cli


@pytest.fixture
def run_command(capsys, patch_config_dirs):
    def runner(args):
        fedrq.cli.main(args)
        stdout, stderr = capsys.readouterr()
        result = stdout.splitlines(), stderr.splitlines(), stdout
        return result

    return runner

@pytest.fixture
def no_tomli_w(monkeypatch, mocker):
    monkeypatch.setattr(fedrq.cli.base, "HAS_TOMLI_W", False)
    mock = mocker.patch("fedrq.cli.base.tomli_w")
    mock.dump.side_effect = NameError

def test_checkconfig_basic(run_command):
    out = run_command(["check-config"])
    assert "No validation errors found!" in out[0]
    assert not out[1]


def test_checkconfig_dump(run_command):
    defs = {"base": ["testrepo1"]}
    expected = {
        "matcher": "^(tester)$",
        "defpaths": [],
        "system_repos": False,
        "defs": defs,
    }

    out = run_command(["check-config", "--dump"])
    data = tomllib.loads(out[2])

    testrepo1 = data["releases"]["testrepo1"]
    del testrepo1["full_def_paths"]
    assert testrepo1 == expected
    assert not out[1]


def test_checkconfig_dump_error(capsys, no_tomli_w):
    with pytest.raises(SystemExit, match="tomli-w is required for --dump"):
        fedrq.cli.main(["check-config", "--dump"])
    stdout = capsys.readouterr()[0]
    assert not stdout
