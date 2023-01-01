# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import argparse
from collections.abc import Sequence

from fedrq.cli.base import CheckConfig, Command
from fedrq.cli.commands.pkgs import Pkgs
from fedrq.cli.commands.subpkgs import Subpkgs
from fedrq.cli.commands.whatrequires import (
    WhatCommand,
    Whatenhances,
    Whatrecommends,
    Whatrequires,
    Whatsuggests,
    Whatsupplements,
)

__all__ = (
    "Command",
    "Pkgs",
    "Subpkgs",
    "WhatCommand",
    "Whatenhances",
    "Whatrecommends",
    "Whatrequires",
    "Whatrequires",
    "Whatsuggests",
    "Whatsupplements",
)


def main(argv: Sequence | None = None, **kwargs) -> None:
    parser = argparse.ArgumentParser(
        description="fedrq is a tool for querying the Fedora and EPEL repositories.",
        **kwargs,
    )
    subparsers = parser.add_subparsers(
        title="Subcommands", dest="action", required=True
    )
    for name, cls in COMMANDS.items():
        cls.make_parser(subparsers.add_parser, name=name, add_help=True)
    _argv = (argv,) if argv else ()
    args = parser.parse_args(*_argv)
    return COMMANDS[args.action](args).run()


COMMANDS: dict[str, type[Command]] = {
    "check-config": CheckConfig,
    "pkgs": Pkgs,
    "subpkgs": Subpkgs,
    "whatenhances": Whatenhances,
    "whatrecommends": Whatrecommends,
    "whatrequires": Whatrequires,
    "whatsuggests": Whatsuggests,
    "whatsupplements": Whatsupplements,
}
