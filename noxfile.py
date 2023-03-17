# SPDX-FileCopyrightText: 2023 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import itertools
import os
import subprocess
from pathlib import Path

import nox
import nox.command
import nox.virtualenv

nox.options.sessions = ("lint", "test", "libdnf5_test")

IN_CI = "JOB_ID" in os.environ
ALLOW_EDITABLE = os.environ.get("ALLOW_EDITABLE", str(not IN_CI)).lower() in (
    "1",
    "true",
)


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


def _to_install_system(session, *packages: str):
    for package in packages:
        for whatprovides in [(), ("-whatprovides",), "yield"]:
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
    test.func(session, "libdnf5")


@nox.session(venv_backend="none")
def lint(session: nox.Session):
    """
    Run format, codeql, typing, and reuse sessions
    """
    for notify in ("formatters", "codeql", "typing", "reuse"):
        session.notify(notify)


@nox.session(venv_params=["--system-site-packages"])
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


@nox.session(venv_params=["--system-site-packages"])
def typing(session: nox.Session):
    install(session, ".[lint]", editable=True)
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


def install_fclogr(session: nox.Session):
    install_system(session, "rpm-build", "python3-rpm")
    if Path("../fclogr").exists():
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
    last_ref = run_silent("git", "describe", "--abbrev=0", "HEAD").stdout.strip()
    session.run("fclogr", "--debug", "dev-srpm", "-r", last_ref, *posargs)


@nox.session
def mockbuild(session: nox.Session):
    install_system(session, "mock", "mock-core-configs")
    tmp = Path(session.create_tmp())
    srpm.func(session, ("-o", tmp, "--keep"))
    spec_path = tmp / "fedrq.spec"
    margs = [
        "mock",
        "--spec",
        spec_path,
        "--source",
        tmp,
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


@nox.session(venv_backend="none")
def bump(session: nox.Session):
    session.run("bash", "-x", "contrib/bump.sh", *session.posargs)


@nox.session
def publish(session: nox.Session):
    install(session, "flit")
    session.run("bash", "-x", "contrib/publish.sh", *session.posargs)
