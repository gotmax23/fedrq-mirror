# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import argparse
import collections.abc as cabc
import logging
import typing as t

from fedrq._utils import filter_latest, get_source_name
from fedrq.backends.base import PackageCompat, PackageQueryCompat
from fedrq.cli.base import Command
from fedrq.cli.formatters import DefaultFormatters, Formatter

logger = logging.getLogger(__name__)


class BreakdownFormatter(Formatter):
    def format(self, packages: cabc.Iterable[PackageCompat]) -> cabc.Iterable[str]:
        runtime = []
        buildtime = []
        for p in packages:
            if p.arch == "src":
                buildtime.append(p)
            else:
                runtime.append(p)
        if runtime:
            yield "Runtime:"
            for p in runtime:
                yield p.name
            yield f"    {len(runtime)} total runtime dependencies"
            if buildtime:
                yield ""
        if buildtime:
            yield "Buildtime:"
            for p in buildtime:
                yield p.name
            yield f"    {len(buildtime)} total buildtime dependencies"
        yield ""
        yield "All SRPM names:"
        yield from (all_pkgs := sorted({get_source_name(pkg) for pkg in packages}))
        yield f"    {len(all_pkgs)} total SRPMs"


class WhatFormatters(DefaultFormatters):
    _formatters = dict(breakdown=BreakdownFormatter)


class WhatCommand(Command):
    formatters = WhatFormatters()
    _exclude_subpackages_opt: bool = False
    _operator: str
    operator: str

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
        pargs = dict(description=cls.__doc__, parents=[cls.parent_parser()], **kwargs)
        if add_help:
            pargs["help"] = f"Find reverse {cls.operator.title()} of a list of packages"
        parser = parser_func(**pargs)

        _rp_help = f"""
        Resolve the correct Package when given a virtual Provide. For instance,
        /usr/bin/yt-dlp would resolve to yt-dlp, and then any package that
        {cls.operator} python3dist(yt-dlp) would also be included.
        """
        resolve_group = parser.add_mutually_exclusive_group()
        resolve_group.add_argument(
            "-P", "--resolve-packages", action="store_true", help=_rp_help
        )
        resolve_group.add_argument(
            "-E",
            "--exact",
            action="store_true",
            help="This is the opposite extreme to --resolve-packages. "
            "E.g., yt-dlp would not match python3dist(yt-dlp) like it does by default.",
        )

        arch_group = parser.add_mutually_exclusive_group()
        arch_group.add_argument(
            "-A",
            "--arch",
            help=f"After finding the packages that {cls._operator} NAMES, "
            "filter out the resulting packages that don't match ARCH",
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
        if cls._exclude_subpackages_opt:
            parser.add_argument("-X", "--exclude-subpackages", action="store_true")
        return parser

    def exclude_subpackages(self, rpms: t.Optional[PackageQueryCompat]) -> None:
        import re

        rpms = rpms or self.rq.resolve_pkg_specs(self.args.names, resolve=True)
        brpms = self.rq.query(pkg=rpms, arch__neq="src")
        srpms = self.rq.query(pkg=rpms, arch="src")

        brpm_sourcerpms = [
            re.sub(r"\.rpm$", "", t.cast(str, pkg.sourcerpm)) for pkg in brpms
        ]
        brpm_srpm_query = self.rq.resolve_pkg_specs(brpm_sourcerpms)
        subpackages = self.rq.get_subpackages(brpm_srpm_query.union(srpms))
        self.query.filterm(pkg__neq=subpackages)
        return None

    def run(self) -> None:
        self.query = self.rq.query(empty=True)
        # Resolve self.args.names into Package objs.
        # This makes it so packages that depend on virtual Provides of the
        # names are included.
        if not self.args.exact:
            resolved_packages = self.rq.resolve_pkg_specs(
                self.args.names, self.args.resolve_packages, with_src=False
            )
            self._logq(resolved_packages, "resolved_packages")
            operator_kwargs = {self.operator: resolved_packages}
            rp_rdeps = self.rq.query(**operator_kwargs, arch=self.args.arch)
            self._logq(rp_rdeps, "rp_rdeps")

            self.query = self.query.union(rp_rdeps)

        operator_kwargs = {f"{self.operator}__glob": self.args.names}
        glob_rdeps = self.rq.query(**operator_kwargs, arch=self.args.arch)
        self._logq(glob_rdeps, "glob_rdeps")

        self.query = self.query.union(glob_rdeps)
        filter_latest(self.query, self.args.latest)

        if getattr(self.args, "exclude_subpackages", None):
            self.exclude_subpackages(
                resolved_packages if self.args.resolve_packages else None
            )

        for p in self.format():
            print(p)


class Whatrequires(WhatCommand):
    """
    By default, fedrq-whatrequires takes one or more valid package names. Then,
    it finds the packages' reverse dependencies, including dependents of their
    virtual Provides. Use the options below to modify fedrq-whatrequires exact
    search strategy.
    """

    _operator = "Require"
    operator = "requires"
    _exclude_subpackages_opt = True


class Whatrecommends(WhatCommand):
    """
    By default, fedrq-whatrecommends takes one or more valid package names. Then,
    it finds the packages' reverse dependencies, including dependents of their
    virtual Provides. Use the options below to modify fedrq-whatrecommends exact
    search strategy.
    """

    _operator = "Recommend"
    operator = "recommend"
    _exclude_subpackages_opt = True


class Whatsuggests(WhatCommand):
    """
    By default, fedrq-whatsuggests takes one or more valid package names. Then,
    it finds the packages' reverse dependencies, including dependents of their
    virtual Provides. Use the options below to modify fedrq-whatsuggests exact
    search strategy.
    """

    _operator = "Suggest"
    operator = "suggests"
    _exclude_subpackages_opt = True


class Whatsupplements(WhatCommand):
    """
    By default, fedrq-whatsupplements takes one or more valid package names. Then,
    it finds the packages' reverse dependencies, including dependents of their
    virtual Provides. Use the options below to modify fedrq-whatsupplements exact
    search strategy.
    """

    _operator = "Supplement"
    operator = "supplements"
    _exclude_subpackages_opt = False


class Whatenhances(WhatCommand):
    """
    By default, fedrq-whatsuggests takes one or more valid package names. Then,
    it finds the packages' reverse dependencies, including dependents of their
    virtual Provides. Use the options below to modify fedrq-whatsuggests exact
    search strategy.
    """

    _operator = "Enhance"
    operator = "enhances"
    _exclude_subpackages_opt = False


class WhatrequiresSrc(WhatCommand):
    """
    By default, fedrq whatrequires-src takes one or more valid source package
    names. Then, it finds the reverse dependencies of the binary RPMs that they
    produce. Use the options below to modify fedrq whatrequires-src's exact
    search strategy.
    This command is a shortcut for `fedrq whatrequires $(fedrq subpkgs ...)`.
    """

    _exclude_subpackages_opt = True
    _operator = "Require"
    operator = "requires"

    @classmethod
    def make_parser(
        cls,
        parser_func: cabc.Callable = argparse.ArgumentParser,
        *,
        add_help: bool = False,
        **kwargs,
    ) -> argparse.ArgumentParser:
        kwargs.update(dict(description=cls.__doc__, parents=[cls.parent_parser()]))
        if add_help:
            _help = (
                f"Find reverse {cls.operator.title()} of a list of"
                " source packages' subpackages."
            )
            kwargs["help"] = _help
        parser = parser_func(**kwargs)
        parser.add_argument(
            "-X",
            "--exclude-subpackages",
            action="store_true",
        )
        arch_group = parser.add_mutually_exclusive_group()
        arch_group.add_argument(
            "-A",
            "--arch",
            help=f"After finding the packages that {cls._operator} NAMES' subpackages, "
            "filter out the resulting packages that don't match ARCH",
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
            help="This is equivalent to --arch=src.",
        )
        return parser

    def run(self) -> None:
        srpms = self.rq.resolve_pkg_specs(self.args.names, with_src=True).filterm(
            arch="src"
        )
        subpackages = self.rq.get_subpackages(srpms)
        qkwargs = {
            self.operator: subpackages,
            "arch": self.args.arch,
            "latest": self.args.latest,
        }
        if self.args.exclude_subpackages:
            qkwargs["pkg__neq"] = subpackages
        self.query = self.rq.query(**qkwargs)
        for p in self.format():
            print(p)
