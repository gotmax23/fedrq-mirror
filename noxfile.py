# SPDX-FileCopyrightText: 2023 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later OR MIT

from __future__ import annotations

import itertools
import os
import subprocess
from collections.abc import Collection, Iterable
from pathlib import Path
from shutil import copy2, rmtree

import nox
import nox.command
import nox.virtualenv

IN_CI = "JOB_ID" in os.environ
ALLOW_EDITABLE = os.environ.get("ALLOW_EDITABLE", str(not IN_CI)).lower() in (
    "1",
    "true",
)
LINT_SESSIONS = ("formatters", "codeql", "typing", "reuse")
PROJECT = "fedrq"

nox.options.sessions = (*LINT_SESSIONS, "test", "libdnf5_test")


def install(session: nox.Session, *args, editable=False, **kwargs):
    if isinstance(session.virtualenv, nox.virtualenv.PassthroughEnv):
        session.warn(f"No venv. Skipping installation of {args}")
        return
    if editable and ALLOW_EDITABLE:
        args = ("-e", *args)
    session.install(*args, "-U", **kwargs)


def run_silent(*args, return_stdout: bool = False, **kwargs):
    kwargs.setdefault("text", True)
    kwargs.setdefault("stdout", subprocess.PIPE)
    kwargs.setdefault("check", True)
    proc = subprocess.run(args, **kwargs)
    return proc.stdout if return_stdout else proc


def git(session: nox.Session, *args, **kwargs):
    return session.run("git", *args, **kwargs, external=True)


def _to_install_system(session, *packages: str):
    for package in packages:
        for whatprovides in [(), ("--whatprovides",), "yield"]:
            if whatprovides == "yield":
                session.log(f"Installing RPM package {package!r}")
                yield package
            if not subprocess.run(
                ["rpm", "-q", *whatprovides, package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode:
                session.log(f"RPM package {package!r} is already installed.")
                break


def install_system(
    session: nox.Session, *packages: str, install_weak_deps: bool = False
):
    to_install = list(_to_install_system(session, *packages))
    if not to_install:
        return
    cmd = ["dnf", "install"]
    if not session.interactive:
        cmd.append("-y")
    if os.geteuid() != 0:
        cmd.insert(0, "sudo")
    if not install_weak_deps:
        cmd.append("--setopt=install_weak_deps=False")
    session.run_always(*cmd, *to_install, external=True)


@nox.session(venv_params=["--system-site-packages"])
def test(session: nox.Session, backend=None):
    install_system(session, "createrepo_c", "rpm-build", "python3-rpm")
    install(session, ".[test]", "pytest-xdist", editable=True)
    posargs = session.posargs
    if "--check" in posargs:
        posargs.remove("--check")
    session.run(
        "python",
        "-m",
        "pytest",
        *session.posargs,
        env={
            "PYTEST_PLUGINS": "xdist.plugin,pytest_mock",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        }
        | ({"FEDRQ_BACKEND": backend} if backend else {}),
    )


@nox.session(venv_backend="none")
def testa(session):
    session.notify("test")
    session.notify("libdnf5_test")


@nox.session(venv_params=["--system-site-packages"])
def libdnf5_test(session: nox.Session):
    install_system(session, "python3-libdnf5")
    test(session, "libdnf5")


@nox.session(venv_backend="none")
def lint(session: nox.Session):
    """
    Run format, codeql, typing, and reuse sessions
    """
    for notify in LINT_SESSIONS:
        session.notify(notify)


@nox.session()
def codeql(session: nox.Session):
    install(
        session,
        "ruff",
    )
    posargs = session.posargs
    if "--check" in posargs:
        posargs.remove("--check")
    session.run(
        "ruff",
        *session.posargs,
        "src/fedrq/",
        "tests/",
        "noxfile.py",
    )


@nox.session
def typing(session: nox.Session):
    install(session, ".[lint]", "-I", editable=True)
    session.run(
        "python", "-m", "mypy", "--enable-incomplete-feature=Unpack", "src/fedrq/"
    )


@nox.session
def formatters(session: nox.Session):
    install(session, "black", "isort")
    posargs = session.posargs
    if IN_CI:
        posargs = ["--check"]
    try:
        session.run(
            "python",
            "-m",
            "black",
            *posargs,
            "src/fedrq/",
            "tests/",
            "noxfile.py",
        )
    finally:
        try:
            session.run(
                "python",
                "-m",
                "isort",
                "--add-import",
                "from __future__ import annotations",
                *posargs,
                "src/fedrq/",
                "noxfile.py",
            )
        finally:
            session.run("python", "-m", "isort", *posargs, "tests/")


@nox.session
def reuse(session: nox.Session):
    install(session, "reuse")
    session.run("reuse", "lint")


def install_fclogr(session: nox.Session, allow_local: bool = True):
    install_system(session, "rpm-build", "python3-rpm")
    if allow_local and Path("../fclogr").exists():
        install(session, "-e", "../fclogr")
    else:
        install(session, "git+https://git.sr.ht/~gotmax23/fclogr#main")


def _spec_changed(session: nox.Session) -> bool:
    if "fedrq.spec" not in run_silent("git", "diff", "--name-only", return_stdout=True):
        return False
    if not session.interactive:
        return True
    session.run("git", "diff", "fedrq.spec", external=True, env=dict(PAGER=""))
    session.log(
        "fedrq.spec has changed in the working tree. Should we revert it? (y/N)"
    )
    return input().lower() == "y"


@nox.session(venv_backend="none")
def clean(session: nox.Session):
    exts = ("fedrq-*.tar.gz", "fedrq-*.src.rpm")
    for file in itertools.chain.from_iterable(Path().glob(ext) for ext in exts):
        session.log(f"Removing old artifact: {file}")
        file.unlink()
    if _spec_changed(session):
        session.run("git", "restore", "fedrq.spec")


@nox.session
def srpm(session: nox.Session, posargs=None):
    posargs = posargs or session.posargs
    install_fclogr(session)
    session.run("fclogr", "--debug", "dev-srpm", *posargs)


@nox.session
def mockbuild(session: nox.Session):
    install_system(session, "mock", "mock-core-configs")
    tmp = Path(session.create_tmp())
    srpm(session, ("-o", tmp, "--keep"))
    spec_path = tmp / "fedrq.spec"
    margs = [
        "mock",
        "--spec",
        str(spec_path),
        "--source",
        str(tmp),
        *session.posargs,
    ]
    if not session.interactive:
        margs.append("--verbose")
    if not {
        "--clean",
        "--no-clean",
        "--cleanup-after",
        "--no-cleanup-after",
        "-n",
        "-N",
    } & set(session.posargs):
        margs.insert(1, "-N")
    session.run(*margs, external=True)


def ensure_clean(session: nox.Session):
    if git(session, "status", "--porcelain", "--untracked-files", silent=True):
        msg = "There are untracked and/or modified files."
        session.error(msg)


def _check_git_tag(session: nox.Session, version: str):
    tag = "v" + version
    tags = git(session, "tag", "--list", silent=True).splitlines()
    if tag in tags:
        session.error(f"{tag} is already tagged")


@nox.session
def bump(session: nox.Session):
    version = session.posargs[0]
    _check_git_tag(session, version)
    ensure_clean(session)

    install(session, "flit>=3.9", "tomcli[tomlkit]", "twine")
    install_fclogr(session, False)

    # Download generate_changelog
    tmp = Path(session.create_tmp())
    with session.chdir(tmp):
        session.run_always(
            "wget",
            "https://git.sr.ht/~gotmax23/fedora-scripts/blob/main/generate_changelog.py",
            external=True,
        )

    # Update version
    session.run("tomcli-set", "pyproject.toml", "str", "project.version", version)

    install(session, ".")

    # Bump specfile
    session.run(
        "fclogr",
        "bump",
        "--new",
        version,
        "--comment",
        f"Release {version}.",
        f"{PROJECT}.spec",
    )

    # Bump changelog, commit, and tag
    git(session, "add", f"{PROJECT}.spec", "pyproject.toml")
    session.run(
        "python", str(tmp / "generate_changelog.py"), f"--version={version}", "--tag"
    )

    if Path("dist").is_dir():
        rmtree("dist")
    session.run("flit", "build", "--use-vcs")
    artifacts = _get_artifacts(("*.whl", "*.tar.gz"), expected_count=2)
    session.run("twine", "check", "--strict", *artifacts)
    _sign_artifacts(session)


def _sign_artifacts(session: nox.Session) -> None:
    uid = git(session, "config", "user.email", silent=True).strip()
    artifacts = _get_artifacts(["tar.gz", "whl"], expected_count=2)
    for path in artifacts:
        if Path(path + ".asc").exists():
            session.warn(f"{path}.asc already exists. Not signing it.")
            continue
        session.run(
            "gpg", "--local-user", uid, "--armor", "--detach-sign", path, external=True
        )


def _get_artifacts(
    exts: Collection[str] = ("whl", "tar.gz", "tar.gz.asc", "whl.asc"),
    required=True,
    extra_allowed=True,
    expected_count: int | None = None,
) -> Iterable[str]:
    count = 0
    all_files = set(Path("dist").iterdir())
    for ext in exts:
        found = tuple(Path("dist").glob(f"*.{ext}"))
        if not found and required:
            raise ValueError(f"No matches for {ext}")
        count += len(found)
        for file in found:
            all_files.remove(file)
        yield from map(str, found)
    if all_files and not extra_allowed:
        raise ValueError(f"Extra files found in dist: {all_files}")
    if expected_count is not None and count != expected_count:
        raise ValueError(f"Found {count} artifacts. Expected {expected_count}.")


@nox.session
def publish(session: nox.Session):
    # Setup
    ensure_clean(session)
    install(session, "twine", "tomcli[tomlkit]")

    # Upload to PyPI
    session.run(
        "twine",
        "upload",
        "--non-interactive",
        "--username",
        "__token__",
        *_get_artifacts(("*.whl", "*.tar.gz"), expected_count=2),
    )

    # Push to git, publish artifacts to sourcehut, and release to copr
    if not session.interactive or input(
        "Push to Sourcehut and copr build (Y/n)"
    ).lower() in ("", "y"):
        git(session, "push", "--follow-tags")
        srht_artifacts(session)
        copr_release(session)

    # Post-release bump
    version = session.run(  # type: ignore[union-attr]
        "tomcli-get", "pyproject.toml", "project.version", silent=True
    ).strip()
    session.run(
        "tomcli-set", "pyproject.toml", "str", "project.version", f"{version}.post0"
    )
    git(session, "add", "pyproject.toml")
    git(session, "commit", "-S", "-m", "Post release version bump")


@nox.session
def docgen(session: nox.Session):
    """
    Generate extra content for the docsite
    """
    for i in ("1", "5"):
        # Long, terrible pipeline to convert scdoc to markdown
        # fmt: off
        session.run(
            "sh", "-euo", "pipefail", "-c",
            # Convert scdoc to html
            f"scd2html < doc/fedrq.{i}.scd"
            # Remove aria-hidden attributes so pandoc doesn't try to convert them
            "| sed 's|aria-hidden=\"true\"||'"
            "| pandoc --from html "
            # mkdocs doesn't support most of the pandoc markdown extensions.
            # Use markdown_strict and only enable pipe_tables.
            "--to markdown_strict+pipe_tables"
            "| sed "
            # Remove anchors that scd2html inserts
            r"-e 's| \[¶\].*||' "
            f"> doc/fedrq{i}.md",
            external=True,
        )
        # fmt: on


@nox.session
def copr_release(session: nox.Session):
    install(session, "copr-cli", "requests-gssapi", "specfile")
    tmp = Path(session.create_tmp())
    dest = tmp / "tomcli.spec"
    copy2("tomcli.spec", dest)
    session.run("python", "contrib/fedoraify.py", str(dest))
    session.run("copr-cli", "build", "--nowait", "gotmax23/tomcli", str(dest))


@nox.session(python="none")
def srht_artifacts(session: nox.Session):
    artifacts = map(str, Path("dist").glob("*"))
    session.run("hut", "git", "artifact", "upload", *artifacts, external=True)


@nox.session
def mkdocs(session: nox.Session):
    install(session, "-e", ".[doc]")
    docgen(session)
    session.run("mkdocs", *session.posargs)
