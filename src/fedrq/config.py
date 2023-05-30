# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
This module houses code to load configuration from the filesystem and validate
it.
"""

from __future__ import annotations

import importlib.resources as importlib_resources
import itertools
import logging
import os
import re
import sys
import typing as t
import warnings
import zipfile
from collections.abc import Callable
from enum import auto as auto_enum
from importlib.abc import Traversable
from pathlib import Path

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

from pydantic import BaseModel, Field, PrivateAttr, validator

from fedrq._compat import StrEnum
from fedrq._config import ConfigError
from fedrq._utils import merge_dict, mklog
from fedrq.backends import BACKENDS, get_default_backend
from fedrq.backends.base import BaseMakerBase
from fedrq.release_repo import AliasRepoG, DefaultRepoGs, RepoG, Repos

if t.TYPE_CHECKING:
    import dnf
    import libdnf5

    from fedrq.backends.base import BackendMod, RepoqueryBase

CONFIG_DIRS = (Path.home() / ".config/fedrq", Path("/etc/fedrq"))
DEFAULT_REPO_CLASS = "base"
DEFAULT_COPR_BASEURL = "https://copr.fedoraproject.org"
logger = logging.getLogger(__name__)


class LoadFilelists(StrEnum):
    auto = auto_enum()
    always = auto_enum()
    never = auto_enum()

    @classmethod
    def from_bool(cls, /, boolean: bool) -> LoadFilelists:
        return cls.always if boolean else cls.never

    def __bool__(self) -> bool:
        return self == LoadFilelists.always


class ReleaseConfig(BaseModel):
    name: str = Field(exclude=True)
    defs: dict[str, list[str]]
    version: t.Optional[str] = None
    matcher: t.Pattern
    repo_dirs: list[Path] = Field(
        default_factory=lambda: [
            directory.joinpath("repos") for directory in CONFIG_DIRS
        ]
    )
    defpaths: set[str] = Field(default_factory=set)
    system_repos: bool = True
    append_system_repos: bool = False

    koschei_collection: t.Optional[str] = None
    copr_chroot_fmt: t.Optional[str] = None

    full_def_paths: t.ClassVar[list[t.Union[Traversable, Path]]] = []
    repo_aliases: dict[str, str] = {}
    _repogs = PrivateAttr()

    @property
    def repogs(self) -> Repos:
        return self._repogs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._repogs = DefaultRepoGs.new(
            self.defs | AliasRepoG.from_str_mapping(self.repo_aliases)
        )

    @validator("defpaths")
    def v_defpaths(cls, value, values) -> dict[str, t.Any]:
        flog = mklog(__name__, "ReleaseConfig", "_get_full_defpaths")
        flog.debug(f"Getting defpaths for {values['name']}: {value}")
        values["full_def_paths"] = cls._get_full_defpaths(
            values["name"], value.copy(), values["repo_dirs"]
        )
        return value

    @validator("matcher")
    def v_matcher(cls, value: t.Pattern, values: dict[str, t.Any]) -> t.Pattern:
        if not values["version"] and value.groups != 1:
            raise ValueError("'matcher' must have exactly one capture group")
        return value

    @validator("repo_dirs", pre=True)
    def v_repo_dirs(cls, value: str | list[Path]) -> list[Path]:
        if not isinstance(value, str):
            return value
        return [Path(directory) for directory in value.split(":")]

    @validator("append_system_repos", always=True)
    def v_append_system_repos(cls, value: bool, values: dict[str, t.Any]) -> bool:
        if value:
            values["system_repos"] = True
        return value

    def is_match(self, val: str) -> bool:
        return bool(re.fullmatch(self.matcher, val))

    def is_valid_repo(self, val: str) -> bool:
        try:
            self.repogs.get_repo(val)
        except ConfigError:
            return False
        else:
            return True

    @staticmethod
    def _repo_dir_iterator(
        repo_dirs: list[Path],
    ) -> t.Iterator[t.Union[Traversable, Path]]:
        flog = mklog(__name__, "ReleaseConfig", "_repo_dir_iterator")
        topdirs: tuple[t.Union[Traversable, Path], ...] = (
            *repo_dirs,
            importlib_resources.files("fedrq.data.repos"),
        )
        flog.debug("topdirs = %s", topdirs)
        for topdir in topdirs:
            if isinstance(topdir, Path):
                topdir = topdir.expanduser()
            if not topdir.is_dir():
                continue
            for file in topdir.iterdir():
                if file.is_file():
                    yield file

    @classmethod
    def _get_full_defpaths(
        cls, name: str, defpaths: set[str], repo_dirs: list[Path]
    ) -> list[t.Union[Traversable, Path]]:
        missing_absolute: list[t.Union[Traversable, Path]] = []
        full_defpaths: list[t.Union[Traversable, Path]] = []
        flog = mklog(__name__, cls.__name__, "_get_full_defpaths")
        flog.debug(f"Searching for absolute defpaths: {defpaths}")
        for defpath in defpaths.copy():
            if (path := Path(defpath).expanduser()).is_absolute():
                flog.debug(f"Is absolute: {path}")
                defpaths.discard(defpath)
                if path.is_file():
                    flog.debug(f"Exists: {path}")
                    full_defpaths.append(path)
                else:
                    flog.debug(f"Doesn't Exist: {path}")
                    missing_absolute.append(path)
        flog.debug(f"Getting relative defpaths: {defpaths}")
        files = cls._repo_dir_iterator(repo_dirs)
        while defpaths:
            try:
                file = next(files)
                flog.debug(f"file={file}")
            except StopIteration:
                flog.debug(msg="StopIteration")
                break
            if file.name in defpaths:
                flog.debug(f"{file.name} in {defpaths}")
                full_defpaths.append(file)
                defpaths.discard(file.name)
        if defpaths:
            _missing = ", ".join(
                sorted(str(p) for p in ((*defpaths, *missing_absolute)))
            )
            raise ConfigError(f"Missing defpaths in {name}: {_missing}")
        return full_defpaths

    def get_release(
        self, config: RQConfig, branch: str, repo_name: str = "base"
    ) -> Release:
        return Release(
            config=config, release_config=self, branch=branch, repo_name=repo_name
        )


class Release:
    """
    Encapsulates a ReleaseConfig with a specific version and repo name.
    This SHOULD NOT be instantiated directly.
    The __init__() has no stability promises.
    Use the [`RQConfig.get_release()`][fedrq.config.RQConfig.get_release]
    factory instead.
    """

    def __init__(
        self,
        config: RQConfig,
        release_config: ReleaseConfig,
        branch: str,
        repo_name: str = "base",
    ) -> None:
        self.config = config
        self.release_config = release_config
        if not self.release_config.is_match(branch):
            raise ConfigError(
                f"Branch {branch} does not match {self.release_config.name}"
            )
        self.branch = branch
        self.repo_name = repo_name
        self.repog: RepoG = self.get_repog(repo_name)

    def get_repog(self, key: str) -> RepoG:
        return self.release_config.repogs.get_repo(key)

    @property
    def version(self) -> str:
        v: str | None = None
        if self.release_config.version:
            v = self.release_config.version
        elif match := re.fullmatch(self.release_config.matcher, self.branch):
            v = match.group(1)
        if v is None:
            raise ValueError(f"{self.branch} does not match {self.release_config.name}")
        # Special case
        if v == "$releasever":
            v = self.config.backend_mod.get_releasever()
        return v

    @property
    def copr_chroot_fmt(self) -> str | None:
        return self.release_config.copr_chroot_fmt

    @property
    def koschei_collection(self) -> str | None:
        return self.release_config.koschei_collection

    def make_base(
        self,
        config: RQConfig | None = None,
        base_conf: dict[str, t.Any] | None = None,
        base_vars: dict[str, t.Any] | None = None,
        base_maker: BaseMakerBase | None = None,
        fill_sack: bool = True,
    ) -> dnf.Base | libdnf5.base.Base:
        """
        :param config: An RQConfig object. Not passing this argument is deprecated.
                       DEPRECATED since 0.4.0: A new RQConfig object will be
                                               created if this is None.
        :param base_conf: Base session configuration
        :param base_vars: Base session vars/substitutions (arch, basearch,
                                                           releasever, etc.)
        :param base_maker: Existing BaseMaker object to configure.
                           If base_maker is None, a new one will be created.
        :param fill_sack: Whether to fill the Base object's package sack or
                          just return the Base object after applying configuration.
        """
        if config is None:
            warnings.warn(
                "DEPRECATED since 0.4.0: Provide an RQConfig object for 'config'"
            )
            config = get_config()
        base_conf = base_conf or {}
        base_vars = base_vars or {}
        releasever = config.backend_mod.get_releasever()
        if (
            "cachedir" not in base_conf
            and config.smartcache
            and self.version != releasever
        ):
            logger.debug("Using smartcache")
            base_conf["cachedir"] = str(get_smartcache_basedir() / str(self.version))
        bm = base_maker or config.backend_mod.BaseMaker()
        bm.sets(base_conf, base_vars)
        if config.load_filelists:
            bm.load_filelists()
        bm.load_release_repos(self, "releasever" not in base_vars)
        return bm.fill_sack() if fill_sack else bm.base

    def _copr_repo(
        self, value: str, default_copr_baseurl: str = DEFAULT_COPR_BASEURL
    ) -> str:
        value = value.rstrip("/")
        if not self.copr_chroot_fmt:
            raise ValueError(
                f"{self.release_config.name} does not have 'copr_chroot_fmt' set"
            )
        chroot = re.sub("-{arch}$", "", self.copr_chroot_fmt).format(
            version=self.version
        )
        if value.startswith(("http://", "https://")):
            return value + "/" + chroot

        frag = "coprs/"
        if value.startswith("@"):
            frag += "g/"
            value = value[1:]
        value, sep, copr_baseurl = value.partition("@")
        if not sep:
            copr_baseurl = default_copr_baseurl.rstrip("/")
        elif not copr_baseurl.startswith(("http://", "https://")):
            copr_baseurl = "https://" + copr_baseurl
        frag += value
        return f"{copr_baseurl}/{frag}/repo/{chroot}"


class RQConfig(BaseModel):
    backend: t.Optional[str] = os.environ.get("FEDRQ_BACKEND")
    releases: dict[str, ReleaseConfig]
    default_branch: str = os.environ.get("FEDRQ_BRANCH", "rawhide")
    smartcache: bool = True
    load_filelists: LoadFilelists = LoadFilelists.auto
    _backend_mod = None
    copr_baseurl: str = DEFAULT_COPR_BASEURL

    class Config:
        json_encoders: dict[t.Any, Callable[[t.Any], str]] = {
            re.Pattern: lambda pattern: pattern.pattern,
            zipfile.Path: lambda path: str(path),
        }
        underscore_attrs_are_private = True
        validate_assignment = True

    @validator("backend")
    def v_backend(cls, value) -> str:
        assert (
            value is None or value in BACKENDS
        ), f"Valid backends are: {', '.join(BACKENDS)}"
        return value

    @property
    def backend_mod(self) -> BackendMod:
        if not self._backend_mod:
            self._backend_mod = get_default_backend(
                self.backend,
                # allow falling back to a non default backend
                # (i.e. not backends.DEFAULT_BACKEND)
                # when the user does not explicitly request a backend.
                fallback=not bool(self.backend),
            )
        return self._backend_mod

    def get_release(
        self, branch: str | None = None, repo_name: str | None = None
    ) -> Release:
        flog = mklog(__name__, "RQConfig", "get_releases")
        branch = branch or self.default_branch
        repo_name = repo_name or DEFAULT_REPO_CLASS
        pair = (branch, repo_name)
        for release in sorted(
            self.releases.values(), key=lambda r: r.name, reverse=True
        ):
            try:
                r = release.get_release(self, branch=branch, repo_name=repo_name)
            except ConfigError as exc:
                logger.debug(f"{release.name} does not match {pair}: {exc}")
            else:
                flog.debug("%s matches %s", release.name, pair)
                return r
        raise ConfigError(
            "{} does not much any of the configured releases: {}".format(
                pair, self.release_names
            )
        )

    @property
    def release_names(self) -> list[str]:
        return [rc.name for rc in self.releases.values()]

    def get_rq(
        self,
        branch: str | None = None,
        repo: str | None = None,
        base_conf: dict[str, t.Any] | None = None,
        base_vars: dict[str, t.Any] | None = None,
    ) -> RepoqueryBase:
        """
        Higher level interface that finds the Release object that mathces
        {branch} and {repo}, creates a (lib)dnf(5).base.Base session, and
        returns a Repoquery object.

        :param branch: branch name
        :param repo: repo class. defaults to 'base'.
        :param base_conf: Base session configuration
        :param base_vars: Base session vars/substitutions (arch, basearch,
                                                           releasever, etc.)
        """
        release = self.get_release(branch, repo)
        return self.backend_mod.Repoquery(release.make_base(self, base_conf, base_vars))


def get_smartcache_basedir() -> Path:
    basedir = Path(os.environ.get("XDG_CACHE_HOME", Path("~/.cache").expanduser()))
    return basedir.joinpath("fedrq").resolve()


def _get_files(
    directory: t.Union[Traversable, Path], suffix: str, reverse: bool = True
) -> list[t.Union[Traversable, Path]]:
    files: list[t.Union[Traversable, Path]] = []
    if not directory.is_dir():
        return files
    for file in directory.iterdir():
        if file.name.endswith(suffix) and file.is_file():
            files.append(file)
    return sorted(files, key=lambda f: f.name, reverse=reverse)


def get_config(**overrides: t.Any) -> RQConfig:
    """
    Retrieve config files from CONFIG_DIRS and fedrq.data.
    Perform naive top-level merging of the 'releases' table.
    """
    flog = mklog(__name__, "get_config")
    flog.debug(f"CONFIG_DIRS = {CONFIG_DIRS}")
    config: dict[str, t.Any] = {}
    all_files: list[list[t.Union[Traversable, Path]]] = [
        _get_files(importlib_resources.files("fedrq.data"), ".toml"),
        *(_get_files(p, ".toml") for p in reversed(CONFIG_DIRS)),
    ]
    flog.debug("all_files = %s", all_files)
    for path in itertools.chain.from_iterable(all_files):
        flog.debug("Loading config file: %s", path)
        with path.open("rb") as fp:
            data = tomllib.load(fp)
        merge_dict(data, config)
    merge_dict(overrides, config)
    config["releases"] = _get_releases(config["releases"])
    flog.debug("Final config: %s", config)
    return RQConfig(**config)


def _get_releases(rdict: dict[str, dict[str, t.Any]]) -> dict[str, t.Any]:
    releases: dict[str, t.Any] = {}
    for name, data in rdict.items():
        releases[name] = dict(name=name, **data)
    return releases


def get_rq(
    branch: str | None = None,
    repo: str = "base",
    *,
    smart_cache: bool | None = None,
    load_filelists: bool | None = None,
) -> RepoqueryBase:
    """
    **DEPRECATED since 0.4.0.** Use
    [`RQConfig.get_rq()`][fedrq.config.RQConfig.get_rq] instead.

    Higher level interface that creates an RQConfig object, finds the Release
    object that mathces {branch} and {repo}, creates a dnf.Base, and finally
    returns a Repoquery object.
    """
    warnings.warn("DEPRECATED since 0.4.0: use RQConfig.get_rq() instead.")
    config = get_config()
    if smart_cache is not None:
        config.smartcache = smart_cache
    if load_filelists is not None:
        config.load_filelists = LoadFilelists.from_bool(load_filelists)
    return config.get_rq(branch, repo)
