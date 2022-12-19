# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import typing as t
from collections.abc import Collection, Iterable
from warnings import warn

from fedrq._dnf import dnf, hawkey, needs_dnf
from fedrq._utils import mklog


def base_read_system_repos(base: dnf.Base | None = None) -> dnf.Base:
    needs_dnf()
    base = base or dnf.Base()
    # Read all repository definitions from the local system and then disable them.
    base.read_all_repos()
    for repo in base.repos.iter_enabled():
        repo.disable()
    return base


def base_read_repofiles(base: dnf.Base | None = None) -> dnf.Base:
    needs_dnf()
    base = base or dnf.Base()


def base_enable_repos(repos: Collection[str], base: dnf.Base | None = None) -> dnf.Base:
    needs_dnf()
    flog = mklog(__name__, "base_enable_repos")
    flog.debug("base = %s", base)
    base = base or dnf.Base()
    flog.debug("base = %s", base)
    flog.debug("Repos: %s", base.repos)
    for repo in repos:
        if repo_obj := base.repos.get_matching(repo):
            repo_obj.enable()
        else:
            raise ValueError(f"{repo} repo definition was not found.")
    return base


class Repoquery:
    base: dnf.Base

    def __init__(
        self,
        base: dnf.Base,
    ) -> None:
        self.base = base

    @property
    def sack(self) -> dnf.sack.Sack:
        return self.base.sack

    def arch_filter(
        self, query: hawkey.Query, arch: t.Union[str, Iterable[str], None] = None
    ) -> hawkey.Query:
        if not arch:
            return query
        if arch == "notsrc":
            return query.filter(arch=(self.base.conf.basearch, "noarch"))
        if arch == "arched":
            return query.filter(arch=self.base.conf.basearch)
        return query.filter(arch=arch)

    def query(
        self, *, arch: t.Union[str, Iterable[str], None] = None, **kwargs
    ) -> hawkey.Query:
        if kwargs.get("latest", "UNDEFINED") is None:
            kwargs.pop("latest")
        query = self.base.sack.query().filter(**kwargs)
        return self.arch_filter(query, arch)

    def get_package(
        self,
        name: str,
        arch: t.Union[str, Iterable[str], None] = None,
    ) -> dnf.package.Package:

        query = self.query(name=name, latest=1, arch=arch)
        # if len(query) > 1:
        #     raise RuntimeError(
        #         f"Multiple packages found for {name} on {arch}"
        #     ) from None
        if len(query) < 1:
            raise RuntimeError(f"Zero packages found for {name} on {arch}")
        return query[0]

    def get_subpackages(
        self,
        packages: hawkey.Query | dnf.package.Package,
        **kwargs,
    ) -> hawkey.Query:
        """
        Return a hawkey.Query containing the binary RPMS/subpackages produced
        by {packages}.

        :param package: A :class:`hawkey.Query` containing source packages
                        or a single :class:`dnf.package.Package`.
        :arch package: Set this to filter out subpackages with a specific arch
        """
        arch = kwargs.get("arch")
        if arch == "src":
            raise ValueError("{arch} cannot be 'src'")
        elif not arch:
            kwargs.setdefault("arch__neq", "src")
        if val := kwargs.pop("sourcerpm", None):
            warn(f"Removing invalid kwarg: 'sourcerpm={val}")

        if isinstance(packages, dnf.package.Package):
            packages = self.query(pkg=[packages])
        for package in packages:
            if package.arch != "src":
                raise ValueError(f"{package} must be a source package.")

        query = self.query(empty=True)
        for srpm in (
            f"{package.name}-{package.version}-{package.release}.src.rpm"
            for package in packages
        ):
            query = query.union(self.query(sourcerpm=srpm, **kwargs))
        return query
