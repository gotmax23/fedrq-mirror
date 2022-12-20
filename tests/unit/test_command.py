# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Generic tests for fedrq.cli.Command
"""
from textwrap import dedent

import pytest

import fedrq.cli

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
