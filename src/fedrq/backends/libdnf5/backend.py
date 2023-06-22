# SPDX-FileCopyrightText: 2023 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
This module contains a fedrq backend (i.e. an implementation of the
[`fedrq.backends.base.BackendMod`][fedrq.backends.base.BackendMod] interface)
that uses the libdnf5 Python bindings.
"""

from __future__ import annotations

import functools
import inspect
import logging
import sys
import typing as t
from collections.abc import Collection, Iterable
from os.path import join as path_join
from urllib.parse import urlparse

from fedrq._utils import filter_latest
from fedrq.backends import MissingBackendError
from fedrq.backends.base import BackendMod, BaseMakerBase, RepoqueryBase
from fedrq.backends.libdnf5 import BACKEND  # noqa: F401

if t.TYPE_CHECKING:
    from _typeshed import StrPath
    from typing_extensions import TypeAlias, Unpack


try:
    import libdnf5
    import rpm
except ImportError as exc:
    raise MissingBackendError(str(exc)) from None

LOG = logging.getLogger(__name__)
Priority_RUNTIME = libdnf5.conf.Option.Priority_RUNTIME
StrIter = t.Union[list[str], tuple[str], str]
IntIter = t.Union[list[int], tuple[int], int]
CONVERT_TO_LIST = (str, int)


class _QueryFilterKwargs(t.TypedDict, total=False):
    name: t.Union[StrIter, libdnf5.rpm.PackageSet]
    name__eq: t.Union[StrIter, libdnf5.rpm.PackageSet]
    name__neq: t.Union[StrIter, libdnf5.rpm.PackageSet]
    name__glob: StrIter
    name__contains: StrIter

    epoch: t.Union[StrIter, IntIter]
    epoch__eq: t.Union[StrIter, IntIter]
    epoch__neq: t.Union[StrIter, IntIter]
    epoch__glob: StrIter
    epoch__gt: IntIter
    epoch__lt: IntIter
    epoch__lte: IntIter

    epoch__gte: IntIter
    version: StrIter
    version__eq: StrIter
    version__neq: StrIter
    version__glob: StrIter
    version__gt: StrIter
    version__lt: StrIter
    version__gte: StrIter
    version__lte: StrIter

    release: StrIter
    release__eq: StrIter
    release__neq: StrIter
    release__glob: StrIter
    release__gt: StrIter
    release__lt: StrIter
    release__gte: StrIter
    release__lte: StrIter

    arch: StrIter
    arch__eq: StrIter
    arch__neq: StrIter
    arch__glob: StrIter

    sourcerpm: StrIter
    sourcerpm__eq: StrIter
    sourcerpm__neq: StrIter
    sourcerpm__glob: StrIter

    url: StrIter
    url__eq: StrIter
    url__neq: StrIter
    url__glob: StrIter
    url__contains: StrIter

    summary: StrIter
    summary__eq: StrIter
    summary__neq: StrIter
    summary__glob: StrIter
    summary__contains: StrIter

    description: StrIter
    description__eq: StrIter
    description__neq: StrIter
    description__glob: StrIter
    description__contains: StrIter

    provides: t.Union[StrIter, libdnf5.rpm.ReldepList]
    provides__eq: t.Union[StrIter, libdnf5.rpm.ReldepList]
    provides__neq: t.Union[StrIter, libdnf5.rpm.ReldepList]
    provides__glob: StrIter

    requires: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    requires__eq: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    requires__neq: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    requires__glob: StrIter

    conflicts: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    conflicts__eq: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    conflicts__neq: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    conflicts__glob: StrIter

    obsoletes: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    obsoletes__eq: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    obsoletes__neq: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    obsoletes__glob: StrIter

    recommends: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    recommends__eq: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    recommends__neq: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    recommends__glob: StrIter

    suggests: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    suggests__eq: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    suggests__neq: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    suggests__glob: StrIter

    enhances: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    enhances__eq: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    enhances__neq: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    enhances__glob: StrIter

    supplements: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    supplements__eq: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    supplements__neq: t.Union[StrIter, libdnf5.rpm.ReldepList, libdnf5.rpm.PackageSet]
    supplements__glob: StrIter

    file: StrIter
    file__eq: StrIter
    file__neq: StrIter
    file__glob: StrIter
    file__contains: StrIter

    latest: int
    latest_per_arch: int

    downgrades: bool

    empty: bool

    reponame: StrIter
    reponame__eq: StrIter
    reponame__neq: StrIter
    reponame__glob: StrIter
    reponame__contains: StrIter

    pkg: Iterable[libdnf5.rpm.Package]
    pkg__eq: Iterable[libdnf5.rpm.Package]
    pkg__neq: Iterable[libdnf5.rpm.Package]


def _get_option(config: libdnf5.conf.Config, key: str) -> libdnf5.conf.Option:
    """
    Get an Option object from a libdnf5 Config object.
    Maintains compatability with dnf5 versions before
    https://github.com/rpm-software-management/dnf5/pull/327
    """
    LOG.debug("Getting option %s", key)
    # dnf5 > 5.0.7
    if option := getattr(config, f"get_{key}_option", None):
        LOG.debug(f"option = get_{key}_options")
        return option()
    # dnf5 <= 5.0.7
    # TODO: Add warning and deprecate
    elif option := getattr(config, key, None):
        return option()
    else:
        raise ValueError(f"{key!r} is not a valid option.")


class BaseMaker(BaseMakerBase):
    """
    Create a Base object and load repos
    """

    base: libdnf5.base.Base

    def __init__(
        self,
        base: libdnf5.base.Base | None = None,
        *,
        initialized: bool = False,
        config_loaded: bool = False,
    ) -> None:
        """
        Initialize and configure the base object.
        :param base: Pass in a :class:`libdnf.base.Base object` to configure
        instead of creating a new one.
        :param initialized: Set to True if base.setup() has already been
        called. Only applies when `base` is passed.
        :param config_loaded: Set to True if base.load_config_from_file()
        has already been called. Only applies when `base` is passed.
        """
        self.base = base or libdnf5.base.Base()
        self.initialized = initialized if base else False
        if not base or not config_loaded:
            self.base.load_config_from_file()

    def setup(self) -> None:
        if not self.initialized:
            self.base.setup()
            self.initialized = True

    # Not part of the BaseMakerBase interface
    @property
    def config(self) -> libdnf5.config.ConfigMain:
        return self.base.get_config()

    # Not part of the BaseMakerBase interface
    @property
    def vars(self) -> libdnf5.conf.Vars:
        return self.base.get_vars()

    # Not part of the BaseMakerBase interface
    def _set(self, config, key: str, value: t.Any) -> None:
        self._get_option(config, key).set(Priority_RUNTIME, value)

    def set(self, key: str, value: t.Any) -> None:
        # if self.initialized:
        #     raise RuntimeError("The base object has already been initialized")
        LOG.debug("Setting config option %s=%r", key, value)
        self._set(self.config, key, value)

    def set_var(self, key: str, value: t.Any) -> None:
        self.vars.set(key, value)

    # Not part of the BaseMakerBase interface
    @property
    def rs(self) -> libdnf5.repo.RepoSackWeakPtr:
        self.setup()
        return self.base.get_repo_sack()

    def fill_sack(
        self,
        *,
        from_cache: bool = False,
        load_system_repo: bool = False,
    ) -> libdnf5.base.Base:
        """
        Fill the sack and returns the Base object.
        The repository configuration shouldn't be manipulated after this.

        Note that the `_cachedir` arg is private and subject to removal.
        """
        if from_cache:
            raise NotImplementedError
        self.rs.update_and_load_enabled_repos(load_system_repo)
        return self.base

    def read_system_repos(self, disable: bool = True) -> None:
        """
        Load system repositories into the base object.
        By default, they are all disabled even if 'enabled=1' is in the
        repository configuration.
        """
        self.rs.create_repos_from_system_configuration()
        if disable:
            repoq = libdnf5.repo.RepoQuery(self.base)
            repoq.filter_enabled(True)
            for repo in repoq:
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
        repoq = libdnf5.repo.RepoQuery(self.base)
        repoq.filter_id(repo, libdnf5.common.QueryCmp_GLOB)
        if not repoq:
            raise ValueError(f"{repo} repo definition was not found.")
        for repo in repoq:
            repo.enable()  # type: ignore

    def disable_repo(self, repo: str, ignore_missing: bool = True) -> None:
        """
        Disable a repo by its id.
        Raise a ValueError if the repoid is not in `self.base`'s configuration
        when ignore_missing is False.
        """
        repoq = libdnf5.repo.RepoQuery(self.base)
        repoq.filter_id(repo, libdnf5.common.QueryCmp_GLOB)
        if not ignore_missing and not repoq:
            raise ValueError(f"{repo} repo definition was not found.")
        for repo in repoq:
            repo.disable()  # type: ignore

    def read_repofile(self, file: StrPath) -> None:
        """
        Load repositories from a repo file
        """
        self.rs.create_repos_from_file(str(file))

    def _get_option(self, config: libdnf5.conf.Config, key: str) -> libdnf5.conf.Option:
        """
        Get an Option object from a libdnf5 Config object.
        Maintains compatability with dnf5 versions before
        https://github.com/rpm-software-management/dnf5/pull/327
        """
        return _get_option(config, key)

    # This is private for now
    def _read_repofile_new(self, file: StrPath, ensure_enabled: bool = False) -> None:
        """
        Load repositories from a repo file if they're not already in the
        configuration.
        """
        parser = libdnf5.conf.ConfigParser()
        parser.read(str(file))
        sections = parser.get_data()
        for name, _ in sections:
            expanded_id = self.vars.substitute(name)
            if expanded_id == "main":
                LOG.debug("Not reading main section.")
                continue
            if repo := self._get_repo(expanded_id):
                LOG.debug("Not adding %s. It's already in the config.", expanded_id)
            else:
                LOG.debug("Adding %s from %s", expanded_id, file)
                repo = self.rs.create_repo(expanded_id)
                repo_config: libdnf5.repo.ConfigRepo = repo.get_config()
                repo_config.load_from_parser(
                    parser,
                    expanded_id,
                    # base.get_vars() returns a WeakPtr, hence the .get()
                    self.base.get_vars().get(),
                    # base.get_logger() returns a WeakPtr, hence the .get()
                    self.base.get_logger().get(),
                    Priority_RUNTIME,
                )
                nameop = self._get_option(repo_config, "name")
                if nameop.get_priority() == libdnf5.conf.Option.Priority_DEFAULT:
                    nameop.set(Priority_RUNTIME, expanded_id)
            if ensure_enabled:
                repo.enable()

    def _get_repo(self, name: str) -> libdnf5.repo.Repo | None:
        """
        Get a repository. Returns None if the repository doesn't exist.
        """
        repoq = libdnf5.repo.RepoQuery(self.base)
        repoq.filter_id([name])
        return next(iter(repoq), None)

    def load_filelists(self) -> None:
        LOG.debug("Loading filelists")
        option = self._get_option(self.config, "optional_metadata_types")
        func = option.add_item
        # https://github.com/rpm-software-management/dnf5/commit/ba011ff
        if "priority" in inspect.signature(func).parameters:
            func(Priority_RUNTIME, libdnf5.conf.METADATA_TYPE_FILELISTS)
        else:
            func(libdnf5.conf.METADATA_TYPE_FILELISTS)

    def create_repo(self, repoid: str, **kwargs) -> None:
        """
        Add a Repo object to the repo sack and configure it.
        :param kwargs: key-values options that should be set on the Repo object
                       values (like $basearch) will be substituted automatically.
        """
        repo = self.rs.create_repo(repoid)
        config = repo.get_config()
        for key, value in kwargs.items():
            value = self._substitute(value)
            self._set(config, key, value)

    # https://github.com/rpm-software-management/dnf5/issues/306
    # https://github.com/rpm-software-management/dnf/blob/276ade38231f3f4120f442e5c3d214f37b66379b/dnf/repodict.py#L73
    def _substitute(self, values):
        if isinstance(values, str):
            return self.vars.substitute(values)
        if isinstance(values, (list, tuple)):
            new = []
            for value in values:
                if isinstance(value, str):
                    new.append(self.vars.substitute(value))
                else:
                    new.append(value)
            return new
        return values

    @property
    def backend(self) -> BackendMod:
        return sys.modules[__name__]

    def repolist(self, enabled: bool | None = None) -> list[str]:
        repoq = libdnf5.repo.RepoQuery(self.base)
        if enabled is not None:
            repoq.filter_enabled(enabled)
        return [r.get_id() for r in repoq]


@functools.total_ordering
class Package(libdnf5.rpm.Package):
    DEBUGINFO_SUFFIX = "-debuginfo"
    DEBUGSOURCE_SUFFIX = "-debugsource"
    """
    libdnf5.rpm.Package subclass with strong dnf.package.Package compatability
    """

    def __hash__(self) -> int:
        return hash(self.get_id().id)

    def __gt__(self, other) -> bool:
        if not isinstance(other, libdnf5.rpm.Package):
            raise TypeError
        if self.name != other.name:
            return self.name > other.name
        evrcmp = libdnf5.rpm.rpmvercmp(self.get_evr(), other.get_evr())
        if evrcmp != 0:
            return evrcmp > 0
        return self.get_arch() > other.get_arch()

    def __lt__(self, other) -> bool:
        return not (self > other)

    @property
    def name(self) -> str:
        return self.get_name()

    @property
    def arch(self) -> str:
        return self.get_arch()

    @property
    def a(self) -> str:
        return self.get_arch()

    @property
    def epoch(self) -> int:
        return int(self.get_epoch())

    @property
    def e(self) -> int:
        return self.epoch

    @property
    def version(self) -> str:
        return self.get_version()

    @property
    def v(self) -> str:
        return self.version

    @property
    def release(self) -> str:
        return self.get_release()

    @property
    def r(self) -> str:
        return self.release

    @property
    def from_repo(self) -> str:
        return self.get_from_repo_id()

    @property
    def evr(self) -> str:
        return self.get_evr()

    @property
    def debug_name(self) -> str:
        # Taken from dnf.package.Package
        # Copyright (C) 2012-2016 Red Hat, Inc.
        # SPDX-License-Identifier: GPL-2.0-or-later
        """
        Returns name of the debuginfo package for this package.
        If this package is a debuginfo package, returns its name.
        If this package is a debugsource package, returns the debuginfo package
        for the base package.
        e.g. kernel-PAE -> kernel-PAE-debuginfo
        """
        if self.name.endswith(self.DEBUGINFO_SUFFIX):
            return self.name

        name = self.name
        if self.name.endswith(self.DEBUGSOURCE_SUFFIX):
            name = name[: -len(self.DEBUGSOURCE_SUFFIX)]

        return name + self.DEBUGINFO_SUFFIX

    @property
    def source_name(self) -> t.Optional[str]:
        # def source_name(self) -> str:
        return None if self.arch == "src" else self.get_source_name()
        # return self.get_source_name()

    @property
    def source_debug_name(self) -> str:
        source_name = self.name if self.arch == "src" else self.source_name
        return source_name + self.DEBUGSOURCE_SUFFIX  # type: ignore[operator]

    @property
    def installtime(self) -> int:
        return self.get_install_time()

    @property
    def buildtime(self) -> int:
        return self.get_build_time()

    @property
    def size(self) -> int:
        return self.downloadsize

    @property
    def downloadsize(self) -> int:
        # https://github.com/rpm-software-management/dnf5/pull/558
        try:
            return self.get_download_size()
        except AttributeError:
            return self.get_package_size()

    @property
    def installsize(self) -> int:
        return self.get_install_size()

    @property
    def provides(self) -> Iterable[Reldep5]:
        return self.get_provides()

    @property
    def requires(self) -> Iterable[Reldep5]:
        return self.get_requires()

    @property
    def recommends(self) -> Iterable[Reldep5]:
        return self.get_recommends()

    @property
    def suggests(self) -> Iterable[Reldep5]:
        return self.get_suggests()

    @property
    def supplements(self) -> Iterable[Reldep5]:
        return self.get_supplements()

    @property
    def enhances(self) -> Iterable[Reldep5]:
        return self.get_enhances()

    @property
    def obsoletes(self) -> Iterable[Reldep5]:
        return self.get_obsoletes()

    @property
    def conflicts(self) -> Iterable[Reldep5]:
        return self.get_conflicts()

    @property
    def sourcerpm(self) -> t.Optional[str]:
        return self.get_sourcerpm() or None

    @property
    def description(self) -> str:
        return self.get_description()

    @property
    def summary(self) -> str:
        return self.get_summary()

    @property
    def license(self) -> str:
        return self.get_license()

    @property
    def url(self) -> str:
        return self.get_url()

    @property
    def reason(self) -> str:
        reason = self.get_reason()
        reason_str = libdnf5.transaction.transaction_item_reason_to_string(reason)
        return reason_str

    @property
    def files(self) -> Iterable[str]:
        return self.get_files()

    @property
    def reponame(self) -> str:
        return self.get_repo_id()

    @property
    def repoid(self) -> str:
        return self.get_repo_id()

    @property
    def vendor(self) -> str:
        return self.get_vendor()

    @property
    def packager(self) -> str:
        return self.get_packager()

    @property
    def location(self) -> str:
        return self.get_location()

    def remote_location(
        self, schemes: Collection[str] | None = ("http", "ftp", "file", "https")
    ) -> str | None:
        location = self.location
        if not location:  # pragma: no cover
            return None
        repo_obj: libdnf5.repo.RepoWeakPtr = self.get_repo()
        mirrors = (
            repo_obj.get_mirrors()
            or _get_option(repo_obj.get_config(), "baseurl").get_value()
        )
        if not mirrors:  # pragma: no cover
            return None

        for url in mirrors:
            if not schemes:
                return path_join(url, location)
            scheme = urlparse(url).scheme
            if scheme in schemes:
                return path_join(url, location)
        return None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<{str(self)}>"

    def __str__(self) -> str:
        return self.get_nevra()


libdnf5._rpm.Package_swigregister(Package)


class Reldep5(libdnf5.rpm.Reldep):
    """
    Subclass of libdnf5.rpm.Reldep with a useful __str__() method
    """

    def __str__(self) -> str:
        return self.to_string()


libdnf5._rpm.Reldep_swigregister(Reldep5)


class PackageQuery(libdnf5.rpm.PackageQuery):
    __rq__: Repoquery

    """
    Subclass of libdnf5.rpm.PackageQuery with hawkey.Query compatability
    """

    def _filter(  # type: ignore[override]
        self,
        **kwargs: Unpack[_QueryFilterKwargs],
    ) -> None:
        if not kwargs:
            return None
        filter_mapping = {
            "latest": "latest_evr",
            "latest_per_arch": "latest_evr",
            "reponame": "repo_id",
        }
        comp_mapping: dict[str, int] = {
            "eq": libdnf5.common.QueryCmp_EQ,
            "neq": libdnf5.common.QueryCmp_NEQ,
            "glob": libdnf5.common.QueryCmp_GLOB,
            "contains": libdnf5.common.QueryCmp_NOT_CONTAINS,
            "gt": libdnf5.common.QueryCmp_GT,
            "gte": libdnf5.common.QueryCmp_GTE,
            "lt": libdnf5.common.QueryCmp_LT,
            "lte": libdnf5.common.QueryCmp_LTE,
        }
        invalid = []
        for key in kwargs:
            if key not in _QueryFilterKwargs.__annotations__:
                invalid.append(key)
        if invalid:
            raise TypeError(f"Invalid keyword arguments: {invalid}")
        if kwargs.pop("empty", None):
            self.clear()
            return None
        if kwargs.pop("downgrades", None):
            self.filter_downgrades()
        for key, value in kwargs.items():
            split = key.rsplit("__", 1)
            name = "filter_" + filter_mapping.get(split[0], split[0])
            args = [_convert_value(key, value)]
            if len(split) == 2:
                args.append(comp_mapping[split[1]])
            getattr(self, name)(*args)

    def filterm(  # type: ignore[override]
        self,
        **kwargs: Unpack[_QueryFilterKwargs],
    ) -> PackageQuery:
        self._filter(**kwargs)
        return self

    def filter(  # type: ignore[override]
        self,
        **kwargs: Unpack[_QueryFilterKwargs],
    ) -> PackageQuery:
        self._filter(**kwargs)
        return self

    def __len__(self) -> int:
        return self.size()

    def union(self, other: PackageQuery) -> PackageQuery:
        self.update(other)
        return self

    def __ior__(self, other: PackageQuery) -> PackageQuery:
        return self.union(other)

    _pkg_comps: TypeAlias = (
        "t.Union[libdnf5.common.QueryCmp_EQ, libdnf5.common.QueryCmp_NEQ]"
    )

    def filter_pkg(
        self,
        pkgs: Iterable[libdnf5.rpm.Package],
        comp: _pkg_comps = libdnf5.common.QueryCmp_EQ,
        /,
    ):
        if isinstance(pkgs, (libdnf5.rpm.PackageSet, libdnf5.rpm.PackageQuery)):
            newquery = pkgs
        else:
            if hasattr(self, "__rq__"):
                base = self.__rq__.base
            else:
                base = self.get_base()
            newquery = libdnf5.rpm.PackageSet(base)
            newquery.clear()
            for p in pkgs:
                newquery.add(p)
        if comp == libdnf5.common.QueryCmp_EQ:
            self.intersection(newquery)
        elif comp == libdnf5.common.QueryCmp_NEQ:
            self.difference(newquery)
        else:
            raise ValueError()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}<{tuple(self)}>"


_ValT = t.TypeVar("_ValT")


def _convert_value(key: str, value: _ValT) -> t.Union[list[_ValT], _ValT]:
    """
    Overkill code to normalize single strings or ints that libdnf5 requires to
    be a list based on type annotations.
    """
    d_annotations = t.get_type_hints(_QueryFilterKwargs)
    annotation = d_annotations[key]
    if t.get_origin(annotation) is not t.Union or not any(
        isinstance(value, typ) for typ in CONVERT_TO_LIST
    ):
        return value
    union_types = t.get_args(annotation)
    pairs = [(t.get_origin(arg), t.get_args(arg)) for arg in union_types]
    for origin, sargs in pairs:
        assert isinstance(origin, type)
        if not issubclass(origin, list):
            continue
        if t.get_origin(sargs[0]) is t.Union:
            pairs = [(t.get_origin(arg), t.get_args(arg)) for arg in union_types]
            for origin, sargs in pairs:
                assert isinstance(origin, type)
                if issubclass(origin, list) and isinstance(value, sargs[0]):
                    return [value]
        if isinstance(value, sargs[0]):
            return [value]
    return value


class Repoquery(RepoqueryBase):
    def __init__(self, base: libdnf5.base.Base) -> None:
        self.base: libdnf5.base.Base = base

    @property
    def base_arches(self) -> set[str]:
        base_vars = self.base.get_vars()
        return {base_vars.get_value("arch"), base_vars.get_value("basearch")}

    def _query(self) -> PackageQuery:
        obj = PackageQuery(self.base)
        obj.__rq__ = self
        return obj

    def query(
        self, *, arch: str | Iterable[str] | None = None, **kwargs
    ) -> PackageQuery:
        return t.cast(PackageQuery, super().query(arch=arch, **kwargs))

    def resolve_pkg_specs(
        self,
        specs: Collection[str],
        resolve: bool = False,
        latest: int | None = None,
        with_src: bool = True,
    ) -> PackageQuery:
        settings = libdnf5.base.ResolveSpecSettings()
        settings.with_filenames = resolve
        settings.with_provides = resolve

        r_query = self.query(empty=True)
        for spec in specs:
            query = self._query()
            query.resolve_pkg_spec(spec, settings, with_src)
            r_query.union(query)
        if resolve:
            r_query = r_query.union(self.query(provides=specs))
        filter_latest(r_query, latest)
        return r_query

    @property
    def backend(self) -> BackendMod:
        return sys.modules[__name__]


def _dnf_getreleasever() -> str:  # pragma: no cover
    # This is taken from dnf and slightly modified
    #
    # SPDX-License-Identifier: GPL-2.0-or-later
    # Copyright (C) 2012-2015  Red Hat, Inc.
    DISTROVERPKG = (
        "system-release(releasever)",
        "system-release",
        "distribution-release(releasever)",
        "distribution-release",
        "redhat-release",
        "suse-release",
    )
    ts = rpm.TransactionSet("/")
    try:
        ts.setVSFlags(~(rpm._RPMVSF_NOSIGNATURES | rpm._RPMVSF_NODIGESTS))
        for distroverpkg in map(lambda p: p.encode("utf-8"), DISTROVERPKG):
            idx = ts.dbMatch("provides", distroverpkg)
            if not len(idx):
                continue
            try:
                hdr = next(idx)
            except StopIteration:
                raise RuntimeError(
                    "Error: rpmdb failed to list provides. Try: rpm --rebuilddb"
                ) from None
            releasever = hdr["version"]
            try:
                try:
                    # header returns bytes -> look for bytes
                    # it may fail because rpm returns a decoded string since 10 Apr 2019
                    off = hdr[rpm.RPMTAG_PROVIDENAME].index(distroverpkg)
                except ValueError:
                    # header returns a string -> look for a string
                    off = hdr[rpm.RPMTAG_PROVIDENAME].index(distroverpkg.decode("utf8"))
                flag = hdr[rpm.RPMTAG_PROVIDEFLAGS][off]
                ver = hdr[rpm.RPMTAG_PROVIDEVERSION][off]
                if flag == rpm.RPMSENSE_EQUAL and ver:
                    if hdr["name"] not in (distroverpkg, distroverpkg.decode("utf8")):
                        # override the package version
                        releasever = ver
            except (ValueError, KeyError, IndexError):
                pass
            if isinstance(releasever, bytes):
                releasever = releasever.decode("utf-8")
            return releasever
        return ""
    finally:
        ts.closeDB()


@functools.cache
def get_releasever() -> str:
    """
    Return the system releasever
    """
    # libdnf5 > 5.0.10
    if hasattr(libdnf5.conf.Vars, "detect_release"):
        base = libdnf5.base.Base()
        return libdnf5.conf.Vars.detect_release(base.get_weak_ptr(), "/").get()
    # Fall back to our copy of dnf4's code
    else:  # pragma: no cover
        return _dnf_getreleasever()


RepoError = RuntimeError

__all__ = (
    "BACKEND",
    "BaseMaker",
    "Package",
    "PackageQuery",
    "Repoquery",
    "RepoError",
    "get_releasever",
    #
    "libdnf5",
)
