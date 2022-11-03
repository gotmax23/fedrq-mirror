# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import argparse
from collections import abc as cabc

from fedrq._utils import filter_latest, mklog
from fedrq.cli import Command
from fedrq.cli.base import get_packages


class Pkgs(Command):
    """
    Find the packages that match NAMES.
    NAMES can be package package name globs or NEVRs.
    """

    # -P: Resolve packages when given a filepath or a virtual Provide.
    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__(args)
        self.v_default()

    @classmethod
    def make_parser(
        cls,
        parser_func: cabc.Callable = argparse.ArgumentParser,
        *,
        add_help: bool,
        **kwargs,
    ) -> argparse.ArgumentParser:
        pargs = dict(description=Pkgs.__doc__, parents=[cls.parent_parser()])
        if add_help:
            pargs["help"] = "Find the packages that match a list of package specs"
        parser = parser_func("pkgs", **pargs)

        parser.add_argument("names", metavar="NAME", nargs="+")
        parser.add_argument(
            "-P",
            "--resolve-packages",
            action="store_true",
            help="Resolve the correct Package when given a virtual Provide."
            " For instance, /usr/bin/yt-dlp would resolve to yt-dlp",
        )

        arch_group = parser.add_mutually_exclusive_group()
        arch_group.add_argument(
            "-A",
            "--arch",
            help="Only include packages that match ARCH",
        )
        arch_group.add_argument(
            "--notsrc",
            dest="arch",
            action="store_const",
            const="notsrc",
            help="This includes all binary RPMs. Multilib is excluded on x86_64. "
            "Equivalent to --arch=notsrc",
        )
        arch_group.add_argument(
            "--src",
            dest="arch",
            action="store_const",
            const="src",
            help="Query for BuildRequires of NAME. "
            "This is equivalent to --arch=src.",
        )
        return parser

    def run(self) -> None:
        flog = mklog(__name__, self.__class__.__name__, "run")
        self.query = self.rq.query(empty=True)
        flog.debug("self.query = %s", tuple(self.query))

        resolved_packages = get_packages(
            self.rq.sack, self.args.names, self.args.resolve_packages
        )
        flog.debug("resolved_packages = %s", tuple(resolved_packages))
        self.query = self.query.union(resolved_packages)

        flog.debug("self.query = %s", tuple(self.query))
        glob_packages = self.rq.query(name__glob=self.args.names)
        flog.debug("glob_packages = %s", tuple(glob_packages))
        self.query = self.query.union(glob_packages)

        flog.debug("self.query = %s", tuple(self.query))
        self.query = self.rq.arch_filter(self.query, self.args.arch)
        flog.debug("self.query = %s", tuple(self.query))
        filter_latest(self.query, self.args.latest)
        flog.debug("self.query = %s", tuple(self.query))

        for p in sorted(self.formatter.format(self.query, self.args.formatter)):
            print(p)
