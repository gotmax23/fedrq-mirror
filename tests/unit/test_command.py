# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Generic tests for fedrq.cli.Command
"""
import os
import shutil
from pathlib import Path

import pytest
import tomli_w

import fedrq.cli
import fedrq.config

SUBCOMMANDS = ("pkgs", "whatrequires", "subpkgs")


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
def test_no_dnf_clean_failure(subcommand, capsys, monkeypatch):
    monkeypatch.setattr(fedrq.cli.base, "HAS_DNF", False)
    monkeypatch.setattr(fedrq.cli.base, "dnf", None)
    monkeypatch.setattr(fedrq.cli.base, "hawkey", None)

    with pytest.raises(SystemExit, match=r"^1$") as exc:
        fedrq.cli.main([subcommand, "dummy"])
    assert exc.value.code == 1
    stdout, stderr = capsys.readouterr()
    assert not stdout
    assert stderr == "FATAL ERROR: " + fedrq.cli.base.NO_DNF_ERROR + "\n"


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
def test_smartcache_used(subcommand, mocker, patch_config_dirs, temp_smartcache: Path):
    """
    Ensure that the smartcache is used when the requested
    branch's releasever is different the the system's releasever
    """
    assert not list(temp_smartcache.iterdir())
    get_releasever = mocker.patch(
        "fedrq.cli.base.get_releasever", return_value="rawhide"
    )
    bm_fill_sack = mocker.spy(fedrq.config.BaseMaker, "fill_sack")

    cls = fedrq.cli.COMMANDS[subcommand]
    parser = cls.make_parser()
    args = parser.parse_args(["--sc", "packageb"])
    obj = cls(args)

    get_releasever.assert_called_once()

    bm_fill_sack.assert_called_once()
    assert bm_fill_sack.call_args.kwargs == dict(
        _cachedir=temp_smartcache / "fedrq" / "tester"
    )

    assert obj.args.smartcache

    assert list(temp_smartcache.iterdir())


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
def test_smartcache_not_used(subcommand, mocker, patch_config_dirs, temp_smartcache):
    """
    Ensure that the smartcache is not used when the requested branch's
    releasever matches the the system's releasever
    """
    assert not list(temp_smartcache.iterdir())
    get_releasever = mocker.patch(
        "fedrq.cli.base.get_releasever", return_value="tester"
    )
    bm_fill_sack = mocker.spy(fedrq.config.BaseMaker, "fill_sack")

    cls = fedrq.cli.COMMANDS[subcommand]
    parser = cls.make_parser()
    args = parser.parse_args(["--sc", "packageb"])
    obj = cls(args)

    get_releasever.assert_called_once()

    bm_fill_sack.assert_called_once()
    assert bm_fill_sack.call_args.kwargs == {"_cachedir": None}

    assert not obj.args.smartcache

    assert not list(temp_smartcache.iterdir())


@pytest.mark.parametrize(
    "args, config_smartcache, final_smartcache, cachedir",
    (
        # smartcache is specified in the config file (default)
        ([], True, True, lambda d: d / "tester"),
        # smartcache is specified in the config file and on the cli (redundant)
        (["--sc"], True, True, lambda d: d / "tester"),
        # smartcache is only specified on the cli
        (["--sc"], False, True, lambda d: d / "tester"),
        # --system-cache is used to override the config file's 'smartcache = true'
        (["--system-cache"], True, False, lambda _: None),
        # --system-cache is used when smartcache is disabled in the config
        ([], False, False, lambda _: None),
        # --system-cache is used when smartcache is disabled in the config (redundant)
        (["--system-cache"], False, False, lambda _: None),
        # --cachedir trumps smartcache
        (["--cachedir=blah"], True, False, lambda _: Path("blah")),
        (["--cachedir=blah"], False, False, lambda _: Path("blah")),
    ),
)
def test_smartcache_config(
    args,
    config_smartcache,
    final_smartcache,
    cachedir,
    patch_config_dirs,
    mocker,
    temp_smartcache,
):
    assert os.environ["XDG_CACHE_HOME"] == str(temp_smartcache)
    write_config = [True]
    # Check that True is the default
    if config_smartcache:
        write_config.append(False)
    dest = patch_config_dirs / "smartcache.toml"
    assert not dest.exists()
    for w in write_config:
        try:
            if w:
                data = {"smartcache": config_smartcache}
                with dest.open("wb") as fp:
                    tomli_w.dump(data, fp)
            Pkgs = fedrq.cli.Pkgs
            parser = Pkgs.make_parser()
            pargs = parser.parse_args([*args, "packagea"])
            obj = Pkgs(pargs)
            assert obj.args.smartcache is final_smartcache
            assert obj.args.cachedir == cachedir(temp_smartcache / "fedrq")

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


# @pytest.mark.parametrize("subcommand", SUBCOMMANDS)
# def test_multiple_errors
