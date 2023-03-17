# SPDX-FileCopyrightText: 2023 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import abc
import importlib.resources
import logging
from collections.abc import Callable, Collection, Iterable, Iterator
from typing import TYPE_CHECKING, Any, Optional, Protocol, TypeVar, runtime_checkable
from warnings import warn

if TYPE_CHECKING:
    from _typeshed import StrPath

    from fedrq.config import Release

_QueryT = TypeVar("_QueryT", bound="PackageQueryCompat")
LOG = logging.getLogger("fedrq.backends")


@runtime_checkable
class PackageCompat(Protocol):
    """
    Common interface provided by dnf.package.Package and other backends
    """

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
    def source_name(self) -> Optional[str]:
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
    def sourcerpm(self) -> Optional[str]:
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
    def reason(self) -> Optional[str]:
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

    @property
    def location(self) -> str:
        ...

    def __hash__(self) -> int:
        ...

    def __lt__(self, other) -> bool:
        ...

    def __le__(self, other) -> bool:
        ...

    def __gt__(self, other) -> bool:
        ...

    def __ge__(self, other) -> bool:
        ...


@runtime_checkable
class PackageQueryCompat(Protocol):
    """
    Common PackageQuery interface provided by hawkey.Query and other backends.
    """

    def filter(self, **kwargs) -> PackageQueryCompat:
        """
        Filter the PackageQuery.
        Depending on the backend, this either modifies 'self' in place and
        return 'self' or return a new PackageQuery object.
        See https://dnf.readthedocs.io/en/latest/api_queries.html#dnf.query.Query.filter
        for the allowed kwargs.
        """
        ...

    def filterm(self, **kwargs) -> PackageQueryCompat:
        """
        Filter the PackageQuery in place and return 'self'.
        See https://dnf.readthedocs.io/en/latest/api_queries.html#dnf.query.Query.filter
        for the allowed kwargs.
        """
        ...

    def union(self: _QueryT, other: _QueryT) -> _QueryT:
        """
        Combine two PackageQuery objects.
        Depending on the backend, this either modifies 'self' in place and
        returns 'self' or returns a new PackageQuery object.
        """
        ...

    def __len__(self) -> int:
        ...

    def __iter__(self) -> Iterator[PackageCompat]:
        ...


class BaseMakerBase(abc.ABC):
    """
    Create a Base object, set configuration, and load repos
    """

    base: Any

    def __init__(self, base=None) -> None:
        self.base = base

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
        'from_cache' isn't currently supported by the libdnf5 backend.
        """
        ...

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
    def disable_repo(self, repo: str, ignore_missing: bool = True) -> None:
        """
        Disable a repo by its id.
        Raise a ValueError if the repoid is not in `self.base`'s configuration
        when ignore_missing is False.
        """

    @abc.abstractmethod
    def read_repofile(self, file: StrPath) -> None:
        """
        Load repositories from a repo file
        """

    @abc.abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration options. Must be called before reading repos.
        """
        ...

    @abc.abstractmethod
    def set_var(self, key: str, value: Any) -> None:
        """
        Set substitutions (e.g. arch, basearch, releasever).
        Needs to be called before reading repos.
        """
        ...

    # Private for now
    @abc.abstractmethod
    def _read_repofile_new(self, file: StrPath, ensure_enabled: bool = False) -> None:
        """
        Load repositories from a repo file if they're not already in the
        configuration.
        """

    def sets(self, conf: dict[str, Any], substitutions: dict[str, Any]) -> None:
        """
        :param conf: A dict of configuration options. Call self.set() for each
        k-v pair.
        :param substitutions: A dict of substitutions/vars options. Call self.set_var()
        for each k-v pair.
        """
        for opt in conf.items():
            self.set(*opt)
        for opt in substitutions.items():
            self.set_var(*opt)

    def load_filelists(self) -> None:
        # Can be overriden by subclasses. Purposely isn't an @abstractmethod.
        """
        Load the filelists if they're not already enabled default
        """
        return None

    def load_release_repos(self, release: Release, set_releasever: bool = True) -> None:
        """
        Load the repositories from a fedrq.config.Release object
        """
        if set_releasever:
            self.set_var("releasever", release.version)
        if release.release_config.system_repos:
            self.read_system_repos()
        for path in release.release_config.full_def_paths:
            with importlib.resources.as_file(path) as fp:
                LOG.debug("Reading %s", fp)
                self._read_repofile_new(fp)
        LOG.debug("Enabling repos: %s", release.repos)
        self.enable_repos(release.repos)

    @abc.abstractmethod
    def create_repo(self, repoid: str, **kwargs) -> None:
        """
        Add a Repo object to the repo sack and configure it.
        :param kwargs: key-values options that should be set on the Repo object
                       values (like $basearch) will be substituted automatically.
        """
        ...

    @property
    @abc.abstractmethod
    def backend(self) -> BackendMod:
        ...


class RepoqueryBase(abc.ABC):
    """
    Helpers to query a repository.
    Provides a unified repoquery interface for different backends.
    """

    def __init__(self, base) -> None:
        self.base = base

    @property
    @abc.abstractmethod
    def base_arches(self) -> set[str]:
        """
        Return a set of the system's arch and basearch.
        """
        ...

    @abc.abstractmethod
    def resolve_pkg_specs(
        self,
        specs: Collection[str],
        resolve: bool = False,
        latest: int | None = None,
        with_src: bool = True,
    ) -> PackageQueryCompat:
        """
        Resolve pkg specs.
        See
        https://dnf.readthedocs.io/en/latest/command_ref.html?highlight=spec#specifying-packages
        or
        https://dnf5.readthedocs.io/en/latest/misc/specs.7.html
        for valid forms.

        :param specs: Package specs to resolve.
        :param resolve: Whether to resolve file paths or virtual Provides in
                        addition to package specs
        :param latest: Limit packages with the same name and arch.
        """
        ...

    def arch_filterm(
        self, query: PackageQueryCompat, arch: str | Iterable[str] | None = None
    ) -> PackageQueryCompat:
        """
        Filter a query's architectures in place and return it.
        It includes a little more functionality than query.filterm(arch=...).
            - When arch is None, the query is left untouched.
            - If arch equals 'notsrc', all src and multilib packages are
              excluded.
            - If arch equals 'arched', all noarch, multilib, and source
              packages are excluded.
            - Otherwise, arch is passed to query.filterm(arch=...) and no other
              validation is preformed.
        """
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
        """
        Filter a query's architectures and return it.
        It includes a little more functionality than query.filter(arch=...).
            - When arch is None, the query is left untouched.
            - If arch equals 'notsrc', all src and multilib packages are
              excluded.
            - If arch equals 'arched', all noarch, multilib, and source
              packages are excluded.
            - Otherwise, arch is passed to query.filterm(arch=...) and no other
              validation is preformed.
        """
        if not arch:
            return query
        if arch == "notsrc":
            return query.filter(arch=(*self.base_arches, "noarch"))  # type: ignore
        if arch == "arched":
            return query.filter(arch=list(self.base_arches))
        return query.filter(arch=arch)

    @abc.abstractmethod
    def _query(self) -> PackageQueryCompat:
        """
        Return the PackageQuery object for this backend
        """
        return self.base.sack.query()

    def query(
        self, *, arch: str | Iterable[str] | None = None, **kwargs
    ) -> PackageQueryCompat:
        """
        Return an inital PackageQuery that's filtered with **kwargs.
        Further filtering can be applied with the PackageQuery's filter and
        filterm methods.
        """
        if kwargs.get("latest") is None:
            kwargs.pop("latest", None)
        query = self._query()
        query.filterm(**kwargs)
        self.arch_filterm(query, arch)
        return query

    def get_package(
        self,
        name: str,
        arch: str | Iterable[str] | None = None,
    ) -> PackageCompat:
        """
        Return the latest Package that matches the 'name' and 'arch'.
        A ValueError is raised when no matches are found.
        """
        query = self.query(name=name, arch=arch, latest=1)
        if len(query) < 1:
            raise ValueError(f"Zero packages found for {name} on {arch}")
        return next(iter(query))

    def get_subpackages(
        self, packages: Iterable[PackageCompat], **kwargs
    ) -> PackageQueryCompat:
        """
        Return a PackageQuery containing the binary RPMS/subpackages produced
        by {packages}.

        :param package: A :class:`PackageQueryCompat` containing source packages
        :param package: Set this to filter out subpackages with a specific arch
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

    @property
    @abc.abstractmethod
    def backend(self) -> BackendMod:
        ...


class BackendMod(Protocol):
    """
    Protocol for a backend module
    """

    BACKEND: str
    BaseMaker: type[BaseMakerBase]
    Package: type[PackageCompat]
    PackageQuery: type[PackageQueryCompat]
    Repoquery: type[RepoqueryBase]
    RepoError: Exception
    get_releasever: Callable[[], str]
