# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import argparse
from collections.abc import Sequence

try:
    import argcomplete
except ImportError:
    HAS_ARGCOMPLETE = False
else:
    HAS_ARGCOMPLETE = True

from fedrq.cli.base import CheckConfig, Command
from fedrq.cli.commands.cache import MakeCacheCommand
from fedrq.cli.commands.changelogs import ChangelogCommand
from fedrq.cli.commands.download import DownloadCommand, DownloadSpecCommand
from fedrq.cli.commands.formatters import FormattersCommand
from fedrq.cli.commands.pkgs import Pkgs
from fedrq.cli.commands.repolist import Repolist
from fedrq.cli.commands.subpkgs import Subpkgs
from fedrq.cli.commands.whatrequires import (
    WhatCommand,
    Whatenhances,
    Whatobsoletes,
    Whatrecommends,
    Whatrequires,
    WhatrequiresSrc,
    Whatsuggests,
    Whatsupplements,
)

__all__ = (
    "Command",
    "Pkgs",
    "Repolist",
    "Subpkgs",
    "ChangelogCommand",
    "DownloadCommand",
    "DownloadSpecCommand",
    "FormattersCommand",
    "MakeCacheCommand",
    "WhatCommand",
    "Whatenhances",
    "Whatobsoletes",
    "Whatrecommends",
    "Whatrequires",
    "WhatrequiresSrc",
    "Whatsuggests",
    "Whatsupplements",
)


def version() -> str:
    from fedrq import __version__

    return __version__


def main(argv: Sequence | None = None, **kwargs) -> None:
    parser = argparse.ArgumentParser(
        description="fedrq is a tool for querying the Fedora and EPEL repositories.",
        **kwargs,
    )
    parser.add_argument("--version", action="version", version=version())
    subparsers = parser.add_subparsers(
        title="Subcommands", dest="action", required=True
    )
    for name, cls in COMMANDS.items():
        cls.make_parser(subparsers.add_parser, name=name, add_help=True)
    if HAS_ARGCOMPLETE:
        argcomplete.autocomplete(parser)
    args = parser.parse_args(argv)
    return COMMANDS[args.action](args).run()


COMMANDS: dict[str, type[Command]] = {
    "make-cache": MakeCacheCommand,
    "check-config": CheckConfig,
    "changelog": ChangelogCommand,
    "download": DownloadCommand,
    "download-spec": DownloadSpecCommand,
    "formatters": FormattersCommand,
    "pkgs": Pkgs,
    "subpkgs": Subpkgs,
    "repolist": Repolist,
    "whatenhances": Whatenhances,
    "whatobsoletes": Whatobsoletes,
    "whatrecommends": Whatrecommends,
    "whatrequires": Whatrequires,
    "wr": Whatrequires,
    "whatrequires-src": WhatrequiresSrc,
    "wrsrc": WhatrequiresSrc,
    "whatsuggests": Whatsuggests,
    "whatsupplements": Whatsupplements,
}
