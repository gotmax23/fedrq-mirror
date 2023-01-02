# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Generic tests for fedrq.cli.Command
"""
import stat
import shutil
from textwrap import dedent
from pathlib import Path
from unittest.mock import call

import pytest
import tomli_w

import fedrq.cli
import fedrq.config

SUBCOMMANDS = ("pkgs", "whatrequires", "subpkgs")


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
def test_no_dnf_clean_failure(subcommand, capsys, monkeypatch):
    error = dedent(
        """
        FATAL ERROR: The dnf and hawkey modules are not available in the current context.
        These modules are only available for the default system Python interpreter.
        """
    ).lstrip()
    monkeypatch.setattr(fedrq.cli.base, "HAS_DNF", False)
    monkeypatch.setattr(fedrq.cli.base, "dnf", None)
    monkeypatch.setattr(fedrq.cli.base, "hawkey", None)

    with pytest.raises(SystemExit, match=r"^1$") as exc:
        fedrq.cli.main([subcommand, "pkgs", "dummy"])
    assert exc.value.code == 1
    stdout, stderr = capsys.readouterr()
    assert not stdout
    assert stderr == error


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
def test_smartcache_used(subcommand, mocker, patch_config_dirs, cleanup_smartcache):
    """
    Ensure that the smartcache is used when the requested
    branch's releasever is different the the system's releasever
    """
    paths = (
        Path("/var/tmp/fedrq-of-testuser"),
        Path("/var/tmp/fedrq-of-testuser/tester"),
    )
    get_releasever = mocker.patch(
        "fedrq.cli.base.get_releasever", return_value="rawhide"
    )
    mocker.patch("fedrq.cli.base.getuser", return_value="testuser")
    _make_cachedir = mocker.patch(
        "fedrq.cli.base.make_cachedir", wraps=fedrq.cli.base.make_cachedir
    )
    bm_fill_sack = mocker.spy(fedrq.config.BaseMaker, "fill_sack")

    cls = fedrq.cli.COMMANDS[subcommand]
    parser = cls.make_parser()
    args = parser.parse_args(["--sc", "packageb"])
    obj = cls(args)

    bm_fill_sack.assert_called_once()
    assert bm_fill_sack.call_args.kwargs == dict(_cachedir=paths[1])

    get_releasever.assert_called_once()

    calls = [call(p) for p in paths]
    assert _make_cachedir.call_args_list == calls

    for p in paths:
        assert p.is_dir()
        assert stat.S_IMODE(p.stat().st_mode) == 0o700

    assert obj.args.smartcache


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
def test_smartcache_not_used(subcommand, mocker, patch_config_dirs):
    """
    Ensure that the smartcache is not used when the requested branch's
    releasever matches the the system's releasever
    """
    get_releasever = mocker.patch(
        "fedrq.cli.base.get_releasever", return_value="tester"
    )
    mocker.patch("fedrq.cli.base.getuser", return_value="testuser")
    _make_cachedir = mocker.patch(
        "fedrq.cli.base.make_cachedir", wraps=fedrq.cli.base.make_cachedir
    )
    bm_fill_sack = mocker.spy(fedrq.config.BaseMaker, "fill_sack")

    cls = fedrq.cli.COMMANDS[subcommand]
    parser = cls.make_parser()
    args = parser.parse_args(["--sc", "packageb"])
    obj = cls(args)

    bm_fill_sack.assert_called_once()
    assert bm_fill_sack.call_args.kwargs == {"_cachedir": None}

    get_releasever.assert_called_once()

    _make_cachedir.assert_not_called()

    assert not obj.args.smartcache


@pytest.mark.parametrize(
    "args, config_smartcache, final_smartcache, cachedir",
    (
        # smartcache is specified in the config file
        ([], True, True, Path("/var/tmp/fedrq-of-testuser/tester")),
        # smartcache is specified in the config file and on the cli (redundant)
        (["--sc"], True, True, Path("/var/tmp/fedrq-of-testuser/tester")),
        # smartcache is only specified on the cli
        (["--sc"], False, True, Path("/var/tmp/fedrq-of-testuser/tester")),
        # --system-cache is used to override the config file's 'smartcache = true'
        (["--system-cache"], True, False, None),
        # --system-cache is used (default)
        ([], False, False, None),
        # --system-cache is used (default, redundant)
        (["--system-cache"], False, False, None),
        # --cachedir trumps smartcache
        (["--cachedir=blah"], True, False, Path("blah")),
        (["--cachedir=blah"], False, False, Path("blah")),
    ),
)
def test_smartcache_config(
    args, config_smartcache, final_smartcache, cachedir, patch_config_dirs, mocker
):
    write_config = [True]
    if not config_smartcache:
        # Check that False is the default
        write_config.append(False)
    dest = patch_config_dirs / "smartcache.toml"
    assert not dest.exists()
    for w in write_config:
        try:
            if w:
                data = {"smartcache": config_smartcache}
                with dest.open("wb") as fp:
                    tomli_w.dump(data, fp)
            mocker.patch("fedrq.cli.base.getuser", return_value="testuser")

            Pkgs = fedrq.cli.Pkgs
            parser = Pkgs.make_parser()
            pargs = parser.parse_args([*args, "packagea"])
            obj = Pkgs(pargs)
            assert obj.args.smartcache is final_smartcache
            assert obj.args.cachedir == cachedir

        finally:
            shutil.rmtree("blah", ignore_errors=True)
            dest.unlink(True)


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
def test_nonexistant_formatter(subcommand, patch_config_dirs, capsys):
    with pytest.raises(SystemExit, match=r"^1$"):
        fedrq.cli.main([subcommand, "--formatter=blahblah", "*"])
    stdout, stderr = capsys.readouterr()
    assert not stdout
    assert stderr.splitlines() == [
        "ERROR: 'blahblah' is not a valid formatter",
        fedrq.cli.base.FORMATTER_ERROR_SUFFIX,
    ]


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
@pytest.mark.parametrize("formatter", (("json"), ("attr")))
def test_formatter_0_args(subcommand, formatter, patch_config_dirs, capsys):
    with pytest.raises(SystemExit, match=r"^1$"):
        fedrq.cli.main([subcommand, "--formatter", formatter + ":", "*"])
    stdout, stderr = capsys.readouterr()
    assert not stdout
    assert stderr.splitlines() == [
        f"ERROR: The '{formatter}' formatter recieved 0 arguments",
        fedrq.cli.base.FORMATTER_ERROR_SUFFIX,
    ]


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
def test_json_formatter_invalid_args(subcommand, patch_config_dirs, capsys):
    with pytest.raises(SystemExit, match=r"^1$"):
        fedrq.cli.main([subcommand, "-F", "json:abc,name,requires,xyz", "*"])
    stdout, stderr = capsys.readouterr()
    assert not stdout
    assert stderr.splitlines() == [
        "ERROR: The 'json' formatter recieved invalid arguments: abc,xyz",
        fedrq.cli.base.FORMATTER_ERROR_SUFFIX,
    ]
