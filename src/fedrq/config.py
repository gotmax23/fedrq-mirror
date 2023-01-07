# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import itertools
import logging
import re
import sys
import typing as t
import zipfile
from collections.abc import Callable
from getpass import getuser
from pathlib import Path

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

if sys.version_info < (3, 10):
    import importlib_resources
    from importlib_resources.abc import Traversable
else:
    import importlib.resources as importlib_resources
    from importlib.abc import Traversable


from pydantic import BaseModel, Field, validator

from fedrq._dnf import dnf, needs_dnf
from fedrq._utils import make_cachedir, mklog
from fedrq.repoquery import BaseMaker, Repoquery, get_releasever

if t.TYPE_CHECKING:
    from _typeshed import StrPath

CONFIG_DIRS = (Path.home() / ".config/fedrq", Path("/etc/fedrq"))
SMARTCACHE_BASEDIR = "/var/tmp/fedrq-of-{user}"
logger = logging.getLogger(__name__)


class ConfigError(ValueError):
    pass


class ReleaseConfig(BaseModel):
    name: str = Field(exclude=True)
    defs: dict[str, list[str]]
    matcher: t.Pattern
    repo_dirs: list[Path] = Field(
        default_factory=lambda: [dir.joinpath("repos") for dir in CONFIG_DIRS]
    )
    defpaths: set[str] = Field(default_factory=set)
    system_repos: bool = True

    koschei_collection: t.Optional[str] = None
    copr_chroot_fmt: t.Optional[str] = None

    full_def_paths: t.ClassVar[list[Traversable]] = []

    @validator("defpaths")
    def v_defpaths(cls, value, values) -> dict[str, t.Any]:
        flog = mklog(__name__, "ReleaseConfig", "_get_full_defpaths")
        flog.debug(f"Getting defpaths for {values['name']}: {value}")
        values["full_def_paths"] = cls._get_full_defpaths(
            values["name"], value, values["repo_dirs"]
        )
        return value

    @validator("matcher")
    def v_matcher(cls, value: t.Pattern) -> t.Pattern:
        if value.groups != 1:
            raise ValueError("'matcher' must have exactly one capture group")
        return value

    @validator("repo_dirs", pre=True)
    def v_repo_dirs(cls, value: str | list[Path]) -> list[Path]:
        if not isinstance(value, str):
            return value
        return [Path(dir) for dir in value.split(":")]

    def is_match(self, val: str) -> bool:
        return bool(re.match(self.matcher, val))

    def is_valid_repo(self, val: str) -> bool:
        return val in self.defs

    def release(self, branch: str, repo_name: str = "base") -> Release:
        return Release(self, branch, repo_name)

    @staticmethod
    def _repo_dir_iterator(
        repo_dirs: list[Path],
    ) -> t.Iterator[Traversable]:
        flog = mklog(__name__, "ReleaseConfig", "_repo_dir_iterator")
        topdirs = (*repo_dirs, importlib_resources.files("fedrq.data.repos"))
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
    ) -> list[Traversable]:
        missing_absolute: list[Traversable] = []
        full_defpaths: list[Traversable] = []
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

    def get_release(self, branch: str, repo_name: str = "base") -> Release:
        return Release(release_config=self, branch=branch, repo_name=repo_name)


class Release:
    def __init__(
        self, release_config: ReleaseConfig, branch: str, repo_name: str = "base"
    ) -> None:
        self.release_config = release_config
        if not self.release_config.is_match(branch):
            raise ConfigError(
                f"Branch {branch} does not match {self.release_config.name}"
            )
        if not self.release_config.is_valid_repo(repo_name):
            raise ConfigError(
                "{repo} is not a valid repo type for {name}".format(
                    repo=repo_name, name=self.release_config.name
                )
                + " Valid repos are: {}".format(tuple(release_config.defs))
            )
        self.branch = branch
        self.repo_name = repo_name

    @property
    def version(self) -> str:
        if match := re.match(self.release_config.matcher, self.branch):
            return match.group(1)
        raise ValueError(f"{self.branch} does not match {self.release_config.name}")

    @property
    def repos(self) -> tuple[str, ...]:
        return tuple(self.release_config.defs[self.repo_name])

    @property
    def copr_chroot_fmt(self) -> str | None:
        return self.release_config.copr_chroot_fmt

    @property
    def koschei_collection(self) -> str | None:
        return self.release_config.koschei_collection

    def make_base(
        self,
        base: dnf.Base | None = None,
        fill_sack: bool = True,
        *,
        _cachedir: StrPath | None = None,
    ) -> dnf.Base:
        """
        Return a dnf.Base object based on the releases's configuration

        Note that the `_cachedir` arg is private and subject to removal.
        """
        needs_dnf()
        flog = mklog(__name__, self.__class__.__name__, "make_base")
        base_maker = BaseMaker(base)
        base = base_maker.base
        base_maker.base.conf.substitutions["releasever"] = self.version
        if self.release_config.system_repos:
            base_maker.read_system_repos()
        # flog.debug("full_def_paths: %s", self.release_config.full_def_paths)
        for path in self.release_config.full_def_paths:
            with importlib_resources.as_file(path) as fp:
                flog.debug("Reading %s", fp)
                base_maker._read_repofile((str(fp)))
        flog.debug("Enabling repos: %s", self.repos)
        base_maker.enable_repos(self.repos)
        if fill_sack:
            base_maker.fill_sack(_cachedir=_cachedir)
        return base_maker.base


class RQConfig(BaseModel):
    releases: dict[str, ReleaseConfig]
    default_branch: str = "rawhide"
    smartcache: bool = True

    class Config:
        json_encoders: dict[t.Any, Callable[[t.Any], str]] = {
            re.Pattern: lambda pattern: pattern.pattern,
            zipfile.Path: lambda path: str(path),
        }

    def get_release(
        self, branch: str | None = None, repo_name: str = "base"
    ) -> Release:
        flog = mklog(__name__, "RQConfig", "get_releases")
        branch = branch or self.default_branch
        pair = (branch, repo_name)
        for release in sorted(
            self.releases.values(), key=lambda r: r.name, reverse=True
        ):
            try:
                r = release.get_release(branch=branch, repo_name=repo_name)
            except ConfigError as exc:
                logger.debug(
                    f"{release.name} does not match {pair}: {exc}",
                    # exc_info=exc,
                )
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


def get_smartcache_basedir() -> Path:
    return Path(SMARTCACHE_BASEDIR.format(user=getuser()))


def _get_files(
    dir: Traversable, suffix: str, reverse: bool = True
) -> list[Traversable]:
    files: list[Traversable] = []
    if not dir.is_dir():
        return files
    for file in dir.iterdir():
        if file.name.endswith(suffix) and file.is_file():
            files.append(file)
    return sorted(files, key=lambda f: f.name, reverse=reverse)


def _process_config(
    data: dict[str, t.Any], config: dict[str, t.Any], releases: dict[str, t.Any]
) -> None:
    if r := data.pop("releases", None):
        releases.update(r)
    config.update(data)


def get_config() -> RQConfig:
    """
    Retrieve config files from CONFIG_DIRS and fedrq.data.
    Perform naive top-level merging of the 'releases' table.
    """
    flog = mklog(__name__, "get_config")
    flog.debug(f"CONFIG_DIRS = {CONFIG_DIRS}")
    config: dict[str, t.Any] = {}
    releases: dict[str, t.Any] = {}
    all_files: list[list[Traversable]] = [
        _get_files(importlib_resources.files("fedrq.data"), ".toml"),
        *(_get_files(p, ".toml") for p in reversed(CONFIG_DIRS)),
    ]
    flog.debug("all_files = %s", all_files)
    for path in itertools.chain.from_iterable(all_files):
        flog.debug("Loading config file: %s", path)
        with path.open("rb") as fp:
            data = tomllib.load(fp)
        _process_config(data, config, releases)
    config["releases"] = _get_releases(releases)
    flog.debug("Final config: %s", config)
    return RQConfig(**config)


def _get_releases(rdict: dict[str, dict[str, t.Any]]) -> dict[str, t.Any]:
    releases: dict[str, t.Any] = {}
    for name, data in rdict.items():
        releases[name] = dict(name=name, **data)
    return releases


def get_rq(
    branch: str | None = None, repo: str = "base", *, smart_cache: bool = False
) -> Repoquery:
    """
    Higher level interface that creates an RQConfig object, finds the Release
    object that mathces {branch} and {repo}, creates a dnf.Base, and finally
    returns a Repoquery object.
    """
    needs_dnf()
    config = get_config()
    branch = branch or config.default_branch
    release = config.get_release(branch, repo)
    cachedir = None
    if release.version != get_releasever():
        base_cachedir = get_smartcache_basedir()
        cachedir = base_cachedir / branch
        for dir in (base_cachedir, cachedir):
            if err := make_cachedir(dir):
                raise RuntimeError(err)
    rq = Repoquery(release.make_base(_cachedir=cachedir))
    return rq
