# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import argparse
from collections import abc as cabc

from fedrq._utils import filter_latest, mklog
from fedrq.cli import Command


class Pkgs(Command):
    """
    Find the packages that match NAMES.
    NAMES can be package package name globs or NEVRs.
    """

    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__(args)
        self.v_default()

    @classmethod
    def make_parser(
        cls,
        parser_func: cabc.Callable = argparse.ArgumentParser,
        *,
        add_help: bool = False,
        **kwargs,
    ) -> argparse.ArgumentParser:
        pargs = dict(description=Pkgs.__doc__, parents=[cls.parent_parser()])
        if add_help:
            pargs["help"] = "Find the packages that match a list of package specs"
        parser = parser_func("pkgs", **pargs)

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
            "-S",
            "--notsrc",
            dest="arch",
            action="store_const",
            const="notsrc",
            help="This includes all binary RPMs. Multilib is excluded on x86_64. "
            "Equivalent to --arch=notsrc",
        )
        arch_group.add_argument(
            "-s",
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
        # flog.debug("self.query = %s", tuple(self.query))

        resolved_packages = self.rq.resolve_pkg_specs(
            self.args.names, self.args.resolve_packages
        )
        self._logq(resolved_packages, "resolved_packages")
        self.query = self.query.union(resolved_packages)

        glob_packages = self.rq.query(name__glob=self.args.names)
        self._logq(glob_packages, "glob_packages")
        self.query = self.query.union(glob_packages)

        self.query = self.rq.arch_filter(self.query, self.args.arch)
        filter_latest(self.query, self.args.latest)
        flog.debug("self.query = %s", tuple(self.query))

        for p in self.format():
            print(p)
