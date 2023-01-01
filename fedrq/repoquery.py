# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import typing as t
from collections.abc import Collection, Iterable
from warnings import warn

from fedrq._dnf import dnf, hawkey, needs_dnf
from fedrq._utils import filter_latest, mklog

if t.TYPE_CHECKING:
    from _typeshed import StrPath


class BaseMaker:
    """
    Create a dnf.Base object and load repos
    """

    def __init__(self, base: dnf.Base | None = None) -> None:
        needs_dnf()
        self.base: dnf.Base = base or dnf.Base()

    def fill_sack(
        self,
        *,
        from_cache: bool = False,
        load_system_repo: bool = False,
        _cachedir: StrPath | None = None,
    ) -> dnf.Base:
        """
        Fill the sack and returns the dnf.Base object.
        The repository configuration shouldn't be manipulated after this.

        Note that the `_cachedir` arg is private and subject to removal.
        """
        if _cachedir:
            self.base.conf.cachedir = str(_cachedir)
        if from_cache:
            self.base.fill_sack_from_repos_in_cache(load_system_repo=load_system_repo)
        else:
            self.base.fill_sack(load_system_repo=load_system_repo)
        return self.base

    def read_system_repos(self, disable: bool = True) -> None:
        """
        Load system repositories into the base object.
        By default, they are all disabled even if 'enabled=1' is in the
        repository configuration.
        """
        self.base.read_all_repos()
        if not disable:
            return None
        for repo in self.base.repos.iter_enabled():
            repo.disable()

    def enable_repos(self, repos: Collection[str]) -> None:
        """
        Enable a list of repositories by their repoid.
        Raise a ValueError if the repoid is not in `self.base`'s configuration.
        """
        for repo in repos:
            self.enable_repo(repo)

    def enable_repo(self, repo: str) -> None:
        """
        Enable a repo by its id.
        Raise a ValueError if the repoid is not in `self.base`'s configuration.
        """
        if repo_obj := self.base.repos.get_matching(repo):
            repo_obj.enable()
        else:
            raise ValueError(f"{repo} repo definition was not found.")

    def _read_repofile(self, file: str) -> None:
        rr = dnf.conf.read.RepoReader(self.base.conf, None)
        for repo in rr._get_repos(file):
            self.base.repos.add(repo)


class Repoquery:
    base: dnf.Base

    def __init__(
        self,
        base: dnf.Base,
    ) -> None:
        needs_dnf()
        self.base = base

    @property
    def sack(self) -> dnf.sack.Sack:
        return self.base.sack

    def arch_filter(
        self, query: hawkey.Query, arch: str | Iterable[str] | None = None
    ) -> hawkey.Query:
        if not arch:
            return query
        if arch == "notsrc":
            return query.filter(
                arch=(*{self.base.conf.basearch, self.base.conf.arch}, "noarch")
            )
        if arch == "arched":
            return query.filter(arch=self.base.conf.basearch)
        return query.filter(arch=arch)

    def query(
        self, *, arch: str | Iterable[str] | None = None, **kwargs
    ) -> hawkey.Query:
        if kwargs.get("latest", "UNDEFINED") is None:
            kwargs.pop("latest")
        query = self.base.sack.query().filter(**kwargs)
        return self.arch_filter(query, arch)

    def get_package(
        self,
        name: str,
        arch: str | Iterable[str] | None = None,
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

    def resolve_pkg_specs(
        self,
        specs: Collection[str],
        resolve: bool = False,
        latest: int | None = None,
    ) -> hawkey.Query:
        flog = mklog(__name__, self.__class__.__name__, "resolve_pkg_spec")
        flog.debug(f"specs={specs}, resolve={resolve}, latest={latest}")
        query = self.query(empty=True)
        for p in specs:
            subject = dnf.subject.Subject(p).get_best_query(
                self.sack, with_provides=resolve, with_filenames=resolve
            )
            query = query.union(subject)
            flog.debug(f"subject query: {tuple(subject)}")
        filter_latest(query, latest)
        return query


def get_releasever() -> str:
    needs_dnf()
    return dnf.rpm.detect_releasever("/")
