# SPDX-FileCopyrightText: 2023 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import abc
import importlib.resources
import logging
from collections.abc import Callable, Collection, Iterable, Iterator
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable
from warnings import warn

if TYPE_CHECKING:
    from _typeshed import StrPath

    from fedrq.config import Release

_QueryT = TypeVar("_QueryT", bound="PackageQueryCompat")
LOG = logging.getLogger("fedrq.backends")


@runtime_checkable
class PackageCompat(Protocol):
    @property
    def name(self) -> str:
        ...

    @property
    def arch(self) -> str:
        ...

    @property
    def a(self) -> str:
        ...

    @property
    def epoch(self) -> int:
        ...

    @property
    def e(self) -> int:
        ...

    @property
    def version(self) -> str:
        ...

    @property
    def v(self) -> str:
        ...

    @property
    def release(self) -> str:
        ...

    @property
    def r(self) -> str:
        ...

    @property
    def from_repo(self) -> str:
        ...

    @property
    def evr(self) -> str:
        ...

    @property
    def debug_name(self) -> str:
        ...

    @property
    def source_name(self) -> str | None:
        ...

    @property
    def source_debug_name(self) -> str:
        ...

    @property
    def installtime(self) -> int:
        ...

    @property
    def buildtime(self) -> int:
        ...

    @property
    def size(self) -> int:
        ...

    @property
    def downloadsize(self) -> int:
        ...

    @property
    def installsize(self) -> int:
        ...

    @property
    def provides(self) -> Iterable:
        ...

    @property
    def requires(self) -> Iterable:
        ...

    @property
    def recommends(self) -> Iterable:
        ...

    @property
    def suggests(self) -> Iterable:
        ...

    @property
    def supplements(self) -> Iterable:
        ...

    @property
    def enhances(self) -> Iterable:
        ...

    @property
    def obsoletes(self) -> Iterable:
        ...

    @property
    def conflicts(self) -> Iterable:
        ...

    @property
    def sourcerpm(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...

    @property
    def summary(self) -> str:
        ...

    @property
    def license(self) -> str:
        ...

    @property
    def url(self) -> str:
        ...

    @property
    def reason(self) -> str | None:
        ...

    @property
    def files(self) -> Iterable[str]:
        ...

    @property
    def reponame(self) -> str:
        ...

    @property
    def repoid(self) -> str:
        ...

    @property
    def vendor(self) -> str:
        ...

    @property
    def packager(self) -> str:
        ...


@runtime_checkable
class PackageQueryCompat(Protocol):
    def filter(self, **kwargs) -> PackageQueryCompat:
        ...

    def filterm(self, **kwargs) -> PackageQueryCompat:
        ...

    def union(self: _QueryT, other: _QueryT) -> _QueryT:
        ...

    def __len__(self) -> int:
        ...

    def __iter__(self) -> Iterator[PackageCompat]:
        ...


class BaseMakerBase(abc.ABC):
    """
    Create a Base object and load repos
    """

    base: Any

    def __init__(self, base=None) -> None:
        ...

    @abc.abstractmethod
    def fill_sack(
        self,
        *,
        from_cache: bool = False,
        load_system_repo: bool = False,
    ):
        """
        Fill the sack and returns the Base object.
        The repository configuration shouldn't be manipulated after this.

        Note that the `_cachedir` arg is private and subject to removal.
        """

    @abc.abstractmethod
    def read_system_repos(self, disable: bool = True) -> None:
        """
        Load system repositories into the base object.
        By default, they are all disabled even if 'enabled=1' is in the
        repository configuration.
        """

    @abc.abstractmethod
    def enable_repos(self, repos: Collection[str]) -> None:
        """
        Enable a list of repositories by their repoid.
        Raise a ValueError if the repoid is not in `self.base`'s configuration.
        """

    @abc.abstractmethod
    def enable_repo(self, repo: str) -> None:
        """
        Enable a repo by its id.
        Raise a ValueError if the repoid is not in `self.base`'s configuration.
        """

    @abc.abstractmethod
    def read_repofile(self, file: StrPath) -> None:
        """
        Load repositories from a repo file
        """

    @abc.abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration options.
        Must be called before set_var() and before reading repos.
        """
        ...

    @abc.abstractmethod
    def set_var(self, key: str, value: Any) -> None:
        """
        Set substitutions (e.g. arch, basearch, releasever).
        Needs to be called after all options have been set() (if any)
        and before reading repos.
        """
        ...

    def load_filelists(self) -> None:
        # Can be overriden by subclasses. Purposely isn't an @abstractmethod.
        pass

    def load_release_repos(self, release: Release) -> None:
        if release.release_config.system_repos:
            self.read_system_repos()
        for path in release.release_config.full_def_paths:
            with importlib.resources.as_file(path) as fp:
                LOG.debug("Reading %s", fp)
                self.read_repofile((str(fp)))
        LOG.debug("Enabling repos: %s", release.repos)
        self.enable_repos(release.repos)


class RepoqueryBase(abc.ABC):
    """
    Helpers to query a repository.
    Provides a unified interface for different backends.
    """

    def __init__(self, base) -> None:
        self.base = base

    @property
    @abc.abstractmethod
    def base_arches(self) -> set[str]:
        ...

    @abc.abstractmethod
    def resolve_pkg_specs(
        self,
        specs: Collection[str],
        resolve: bool = False,
        latest: int | None = None,
        with_src: bool = True,
    ) -> PackageQueryCompat:
        ...

    def arch_filterm(
        self, query: PackageQueryCompat, arch: str | Iterable[str] | None = None
    ) -> PackageQueryCompat:
        if not arch:
            return query
        if arch == "notsrc":
            return query.filterm(arch=(*self.base_arches, "noarch"))  # type: ignore
        elif arch == "arched":
            return query.filterm(arch=self.base.conf.basearch)
        else:
            return query.filterm(arch=arch)

    def arch_filter(
        self, query: PackageQueryCompat, arch: str | Iterable[str] | None = None
    ) -> PackageQueryCompat:
        if not arch:
            return query
        if arch == "notsrc":
            return query.filter(arch=(*self.base_arches, "noarch"))  # type: ignore
        if arch == "arched":
            return query.filter(arch=list(self.base_arches))
        return query.filter(arch=arch)

    @abc.abstractmethod
    def _query(self) -> PackageQueryCompat:
        return self.base.sack.query()

    def query(
        self, *, arch: str | Iterable[str] | None = None, **kwargs
    ) -> PackageQueryCompat:
        if kwargs.get("latest", "UNDEFINED") is None:
            kwargs.pop("latest")
        query = self._query()
        query.filterm(**kwargs)
        self.arch_filterm(query, arch)
        return query

    def get_package(
        self,
        name: str,
        arch: str | Iterable[str] | None = None,
    ) -> PackageCompat:
        query = self.query(name=name, arch=arch, latest=1)
        if len(query) < 1:
            raise RuntimeError(f"Zero packages found for {name} on {arch}")
        return next(iter(query))

    def get_subpackages(
        self, packages: Iterable[PackageCompat], **kwargs
    ) -> PackageQueryCompat:
        """
        Return a hawkey.Query containing the binary RPMS/subpackages produced
        by {packages}.

        :param package: A :class:`PackageQueryCompat` containing source packages
        :arch package: Set this to filter out subpackages with a specific arch
        """
        arch = kwargs.get("arch")
        if arch == "src":
            raise ValueError("{arch} cannot be 'src'")
        elif not arch:
            kwargs.setdefault("arch__neq", "src")
        if val := kwargs.pop("sourcerpm", None):
            warn(f"Removing invalid kwarg: 'sourcerpm={val}")

        for package in packages:
            if package.arch != "src":
                raise ValueError(f"{package} must be a source package.")

        sourcerpms = [
            f"{package.name}-{package.version}-{package.release}.src.rpm"
            for package in packages
        ]
        query = self.query(sourcerpm=sourcerpms, **kwargs)
        return query


class BackendMod(Protocol):
    """
    Protocol for a backend module
    """

    get_releasever: Callable[[], str]
    BaseMaker: type[BaseMakerBase]
    Repoquery: type[RepoqueryBase]
    BACKEND: str
