# SPDX-FileCopyrightText: 2023 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import logging
import typing as t
from collections.abc import Collection, Iterable

from fedrq._utils import filter_latest
from fedrq.backends import MissingBackendError
from fedrq.backends.base import BaseMakerBase, RepoqueryBase
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


class QueryFilterKwargs(t.TypedDict, total=False):
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


class BaseMaker(BaseMakerBase):
    """
    Create a Base object and load repos
    """

    base: libdnf5.base.Base

    def __init__(
        self, base: libdnf5.base.Base | None = None, *, initialized=False
    ) -> None:
        """
        Initialize and configure the base object.
        :param base: Pass in a :class:`libdnf.base.Base object` to configure
        instead of creating a new one.
        :param initialized: Set to True if base.setup() has already been
        called.
        """
        self.base = base or libdnf5.base.Base()
        self.initialized = initialized if base else False
        if not base:
            self.base.load_config_from_file()

    def setup(self) -> None:
        if not self.initialized:
            self.base.setup()
            self.initialized = True

    @property
    def config(self) -> libdnf5.config.ConfigMain:
        return self.base.get_config()

    def set(self, key: str, value: t.Any) -> None:
        # if self.initialized:
        #     raise RuntimeError("The base object has already been initialized")
        LOG.debug("Setting config option %s=%r", key, value)
        option_obj = getattr(self.config, key, None)
        if not callable(option_obj):
            raise ValueError(f"{key!r} is not a valid option.")
        option_obj().set(Priority_RUNTIME, value)

    def set_var(self, key: str, value: t.Any) -> None:
        self.base.get_vars().set(key, value)

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

    def read_repofile(self, file: StrPath) -> None:
        """
        Load repositories from a repo file
        """
        self.rs.create_repos_from_file(str(file))

    def load_filelists(self) -> None:
        LOG.debug("Loading filelists")
        option: libdnf5.conf.OptionStringSet = self.config.optional_metadata_types()
        option.add_item(libdnf5.conf.METADATA_TYPE_FILELISTS)


class Package(libdnf5.rpm.Package):
    DEBUGINFO_SUFFIX = "-debuginfo"
    DEBUGSOURCE_SUFFIX = "-debugsource"

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
    def source_name(self) -> str | None:
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
        return self.get_package_size()

    @property
    def downloadsize(self) -> int:
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
    def sourcerpm(self) -> str:
        return self.get_sourcerpm()

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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<{str(self)}>"

    def __str__(self) -> str:
        return self.get_nevra()


libdnf5._rpm.Package_swigregister(Package)


class Reldep5(libdnf5.rpm.Reldep):
    def __str__(self) -> str:
        return self.to_string()


libdnf5._rpm.Reldep_swigregister(Reldep5)


class PackageQuery(libdnf5.rpm.PackageQuery):
    __rq__: Repoquery

    def _filter(  # type: ignore[override]
        self,
        **kwargs: Unpack[QueryFilterKwargs],
    ) -> None:
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
            if key not in QueryFilterKwargs.__annotations__:
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
        **kwargs: Unpack[QueryFilterKwargs],
    ) -> PackageQuery:
        self._filter(**kwargs)
        return self

    def filter(  # type: ignore[override]
        self,
        **kwargs: Unpack[QueryFilterKwargs],
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


ValT = t.TypeVar("ValT")


def _convert_value(key: str, value: ValT) -> t.Union[list[ValT], ValT]:
    d_annotations = t.get_type_hints(QueryFilterKwargs)
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
        filter_latest(r_query, latest)
        return r_query


def get_releasever() -> str:
    base = libdnf5.base.Base()
    base.load_config_from_file()
    base.setup()
    return base.get_vars().get_value("releasever")