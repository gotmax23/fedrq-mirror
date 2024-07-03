# SPDX-FileCopyrightText: 2023 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
This module contains a fedrq backend (i.e. an implementation of the
[`fedrq.backends.base.BackendMod`][fedrq.backends.base.BackendMod] interface)
that uses the dnf Python bindings.
"""

from __future__ import annotations

import logging
import sys
import typing as t
from collections.abc import Collection, Iterator
from enum import Enum
from functools import cache

from fedrq._utils import filter_latest
from fedrq.backends import MissingBackendError
from fedrq.backends.base import (
    BackendMod,
    BaseMakerBase,
    ChangelogEntry,
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

PackageCompat.register(dnf.package.Package)
Package: type[PackageCompat] = dnf.package.Package
PackageQueryCompat.register(dnf.query.Query)
PackageQuery: type[PackageQueryCompat] = dnf.query.Query
RepoError = dnf.exceptions.RepoError


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
            raise KeyError(f"{key} is not a valid substitution")
        self.set(key, value)

    def load_filelists(self, enable: bool = True) -> None:
        # Old versions of dnf always load filelists
        try:
            types: list[str] = self.conf.optional_metadata_types
        except AttributeError:
            return
        if enable:
            types.append("filelists")
            return
        while "filelists" in types:
            types.remove("filelists")

    def load_changelogs(self, enable: bool = True) -> None:
        for repo in self.base.repos.iter_enabled():
            repo.load_metadata_other = enable

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

    def disable_repo(self, repo: str, ignore_missing: bool = True) -> None:
        """
        Disable a repo by its id.
        Raise a ValueError if the repoid is not in `self.base`'s configuration
        when ignore_missing is False.
        """
        if repo_obj := self.base.repos.get_matching(repo):
            repo_obj.disable()
        elif not ignore_missing:
            raise ValueError(f"{repo} repo definition was not found.")

    def read_repofile(self, file: StrPath) -> None:
        rr = dnf.conf.read.RepoReader(self.base.conf, None)
        for repo in rr._get_repos(str(file)):
            LOG.debug("Adding %s from %s", repo.id, file)
            self.base.repos.add(repo)

    # This is private for now
    def _read_repofile_new(self, file: StrPath, ensure_enabled: bool = False) -> None:
        """
        Load repositories from a repo file if they're not already in the
        configuration.
        """
        rr = dnf.conf.read.RepoReader(self.base.conf, None)
        for repo in rr._get_repos(str(file)):
            if repo.id in self.base.repos:
                LOG.debug("Not adding %s. It's already in the config.", repo.id)
            else:
                LOG.debug("Adding %s from %s", repo.id, file)
                self.base.repos.add(repo)
            if ensure_enabled:
                LOG.debug("Ensuring that %s is enabled.", repo.id)
                self.base.repos[repo.id].enable()

    def create_repo(self, repoid: str, **kwargs: t.Any) -> None:
        """
        Add a Repo object to the repo sack and configure it.

        Args:
            kwargs:
                key-values options that should be set on the Repo object values
                (like `$basearch`) will be substituted automatically.
        """
        self.base.repos.add_new_repo(repoid, self.conf, **kwargs)

    @property
    def backend(self) -> BackendMod:
        return sys.modules[__name__]

    def repolist(self, enabled: bool | None = None) -> list[str]:
        if enabled is None:
            return list(self.base.repos)
        return [r.id for r in self.base.repos.values() if r.enabled is bool(enabled)]

    def enable_source_repos(self) -> None:
        self.base.repos.enable_source_repos()


class NEVRAForms(int, Enum):
    NEVRA = hawkey.FORM_NEVRA
    NEVR = hawkey.FORM_NEVR
    NEV = hawkey.FORM_NEV
    NA = hawkey.FORM_NA
    NAME = hawkey.FORM_NAME


# Use PackageCompat and PackageQueryCompat as the TypeVar, as the the native dnf objects
# don't provide typing.
class Repoquery(RepoqueryBase[PackageQueryCompat[PackageCompat]]):
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
        *,
        with_filenames: bool | None = None,
        with_provides: bool | None = None,
        resolve_provides: bool | None = None,
        nevra_forms: list[NEVRAForms] | None = None,
    ) -> dnf.query.Query:
        opts = self._get_resolve_options(
            resolve, with_filenames, with_provides, resolve_provides
        )
        resolve_provides = opts.pop("resolve_provides")
        opts["with_src"] = with_src
        if nevra_forms:
            opts["forms"] = nevra_forms

        query = self.query(empty=True)
        for p in specs:
            subject = dnf.subject.Subject(p).get_best_query(self.base.sack, **opts)
            query = query.union(subject)
        if opts["with_provides"]:
            query = query.union(self.query(provides=specs))
        if opts["with_filenames"]:
            query = query.union(self.query(file=specs))
        filter_latest(query, latest)
        return query

    @property
    def backend(self) -> BackendMod:
        return sys.modules[__name__]


@cache
def get_releasever():
    """
    Return the system releasever
    """
    return dnf.rpm.detect_releasever("/")


def get_changelogs(package: t.Any) -> Iterator[ChangelogEntry]:
    for entry in package.changelogs:
        yield ChangelogEntry(
            text=entry["text"], author=entry["author"], date=entry["timestamp"]
        )


__all__ = (
    "BACKEND",
    "BaseMaker",
    "Package",
    "NEVRAForms",
    "PackageQuery",
    "RepoError",
    "Repoquery",
    "get_releasever",
    "get_changelogs",
    #
    "dnf",
    "hawkey",
)
