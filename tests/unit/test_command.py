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


# @pytest.mark.parametrize("subcommand", SUBCOMMANDS)
# def test_no_dnf_clean_failure(subcommand, capsys, monkeypatch):
#     monkeypatch.setattr(fedrq.cli.base, "HAS_DNF", False)
#     monkeypatch.setattr(fedrq.cli.base, "dnf", None)
#     monkeypatch.setattr(fedrq.cli.base, "hawkey", None)

#     with pytest.raises(SystemExit, match=r"^1$") as exc:
#         fedrq.cli.main([subcommand, "dummy"])
#     assert exc.value.code == 1
#     stdout, stderr = capsys.readouterr()
#     assert not stdout
#     assert stderr == "FATAL ERROR: " + fedrq.cli.base.NO_DNF_ERROR + "\n"


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
def test_smartcache_used(
    subcommand, mocker, monkeypatch, patch_config_dirs, temp_smartcache: Path
):
    """
    Ensure that the smartcache is used when the requested
    branch's releasever is different the the system's releasever
    """
    assert not list(temp_smartcache.iterdir())

    mocks = {}

    def _set_config(self, key: str) -> None:
        arg = getattr(self.args, key, None)
        if arg is not None:
            setattr(self.config, key, arg)
        if key == "backend":
            mocks["get_releasever"] = mocker.patch.object(
                self.config.backend_mod, "get_releasever", return_value="rawhide"
            )
            mocks["bm_set"] = mocker.spy(self.config.backend_mod.BaseMaker, "set")

    cls = fedrq.cli.COMMANDS[subcommand]
    monkeypatch.setattr(cls, "_set_config", _set_config)

    parser = cls.make_parser()
    args = parser.parse_args(["--sc", "packageb"])
    obj = cls(args)

    mocks["get_releasever"].assert_called_once()

    expected_cachedir = temp_smartcache / "fedrq" / "tester"

    assert any(
        call.args[1:] == ("cachedir", str(expected_cachedir))
        for call in mocks["bm_set"].call_args_list
    )

    assert obj.args.smartcache

    assert list(temp_smartcache.iterdir())


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
def test_smartcache_not_used(
    subcommand, mocker, monkeypatch, patch_config_dirs, temp_smartcache
):
    """
    Ensure that the smartcache is not used when the requested branch's
    releasever matches the the system's releasever
    """
    assert not list(temp_smartcache.iterdir())

    mocks = {}

    def _set_config(self, key: str) -> None:
        arg = getattr(self.args, key, None)
        if arg is not None:
            setattr(self.config, key, arg)
        if key == "backend":
            mocks["get_releasever"] = mocker.patch.object(
                self.config.backend_mod, "get_releasever", return_value="tester"
            )
            mocks["bm_set"] = mocker.spy(self.config.backend_mod.BaseMaker, "set")

    cls = fedrq.cli.COMMANDS[subcommand]
    monkeypatch.setattr(cls, "_set_config", _set_config)
    parser = cls.make_parser()
    args = parser.parse_args(["--sc", "packageb"])
    cls(args)

    mocks["get_releasever"].assert_called_once()
    assert all(call.args[1] != "cachedir" for call in mocks["bm_set"].call_args_list)
    # assert not list(temp_smartcache.iterdir())


@pytest.mark.parametrize(
    "args, config_smartcache, cachedir",
    (
        # smartcache is specified in the config file (default)
        ([], True, lambda d: d / "tester"),
        # smartcache is specified in the config file and on the cli (redundant)
        (["--sc"], True, lambda d: d / "tester"),
        # smartcache is only specified on the cli
        (["--sc"], False, lambda d: d / "tester"),
        # --system-cache is used to override the config file's 'smartcache = true'
        (["--system-cache"], False, lambda _: None),
        # --system-cache is used when smartcache is disabled in the config
        ([], False, lambda _: None),
        # --system-cache is used when smartcache is disabled in the config (redundant)
        (["--system-cache"], False, lambda _: None),
        # --cachedir trumps smartcache
        (["--cachedir=blah"], True, lambda _: Path("blah")),
        (["--cachedir=blah"], False, lambda _: Path("blah")),
    ),
)
def test_smartcache_config(
    args,
    config_smartcache,
    cachedir,
    patch_config_dirs,
    temp_smartcache,
    mocker,
    default_backend,
):
    assert os.environ["XDG_CACHE_HOME"] == str(temp_smartcache)
    bm_set = mocker.spy(default_backend.BaseMaker, "set")

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
            parser = fedrq.cli.Pkgs.make_parser()
            pargs = parser.parse_args([*args, "packagea"])
            fedrq.cli.Pkgs(pargs)
            expected_cachedir = cachedir(temp_smartcache / "fedrq")
            if expected_cachedir:
                assert any(
                    call.args[1:] == ("cachedir", str(expected_cachedir))
                    for call in bm_set.call_args_list
                )
            else:
                assert all(call.args[1] != "cachedir" for call in bm_set.call_args_list)

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
        f"ERROR: '{formatter}' FormatterError: received less than 1 argument",
        fedrq.cli.base.FORMATTER_ERROR_SUFFIX,
    ]


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
def test_json_formatter_invalid_args(subcommand, patch_config_dirs, capsys):
    with pytest.raises(SystemExit, match=r"^1$"):
        fedrq.cli.main([subcommand, "-F", "json:abc,name,requires,xyz", "*"])
    stdout, stderr = capsys.readouterr()
    assert not stdout
    assert stderr.splitlines() == [
        "ERROR: 'json' FormatterError: invalid argument 'abc'",
        fedrq.cli.base.FORMATTER_ERROR_SUFFIX,
    ]
