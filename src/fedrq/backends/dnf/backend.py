# SPDX-FileCopyrightText: 2023 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import logging
import typing as t
from collections.abc import Collection

from fedrq._utils import filter_latest
from fedrq.backends import MissingBackendError
from fedrq.backends.base import (
    BaseMakerBase,
    PackageCompat,
    PackageQueryCompat,
    RepoqueryBase,
)
from fedrq.backends.dnf import BACKEND

try:
    import dnf
    import hawkey
except ImportError:
    raise MissingBackendError from None

if t.TYPE_CHECKING:
    from _typeshed import StrPath

LOG = logging.getLogger(__name__)


class BaseMaker(BaseMakerBase):
    """
    Create a Base object and load repos
    """

    base: dnf.Base

    def __init__(self, base: dnf.Base | None = None) -> None:
        """
        Initialize and configure the base object.
        """
        self.base: dnf.Base = base or dnf.Base()

    @property
    def conf(self) -> dnf.conf.MainConf:
        return self.base.conf

    def set(self, key: str, value: t.Any) -> None:
        setattr(self.conf, key, value)

    def set_var(self, key: str, value: t.Any) -> None:
        if key not in self.base.conf.substitutions:
            raise KeyError(f"{key} is not a valid substituion")
        self.set(key, value)

    def fill_sack(
        self,
        *,
        from_cache: bool = False,
        load_system_repo: bool = False,
    ) -> dnf.Base:
        """
        Fill the sack and returns the dnf.Base object.
        The repository configuration shouldn't be manipulated after this.

        Note that the `_cachedir` arg is private and subject to removal.
        """
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

    def read_repofile(self, file: StrPath) -> None:
        rr = dnf.conf.read.RepoReader(self.base.conf, None)
        for repo in rr._get_repos(str(file)):
            self.base.repos.add(repo)


class Repoquery(RepoqueryBase):
    def __init__(self, base: dnf.Base) -> None:
        self.base: dnf.Base = base

    @property
    def base_arches(self) -> set[str]:
        return {self.base.conf.arch, self.base.conf.basearch}

    def _query(self) -> dnf.query.Query:
        return self.base.sack.query()

    def resolve_pkg_specs(
        self,
        specs: Collection[str],
        resolve: bool = False,
        latest: int | None = None,
        with_src: bool = True,
    ) -> dnf.query.Query:
        ...
        LOG.debug(f"specs={specs}, resolve={resolve}, latest={latest}")
        query = self.query(empty=True)
        for p in specs:
            subject = dnf.subject.Subject(p).get_best_query(
                self.base.sack,
                with_provides=resolve,
                with_filenames=resolve,
                with_src=with_src,
            )
            query = query.union(subject)
            # LOG.debug(f"subject query: {tuple(subject)}")
        filter_latest(query, latest)
        return query


def get_releasever():
    """
    Return the system releasever
    """
    return dnf.rpm.detect_releasever("/")


Package: PackageCompat = dnf.package.Package
PackageQuery: PackageQueryCompat = dnf.query.Query

__all__ = (
    "BACKEND",
    "BaseMaker",
    "Package",
    "PackageQuery",
    "Repoquery",
    "get_releasever",
    #
    "dnf",
    "hawkey",
)
