# SPDX-FileCopyrightText: 2023 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later OR MIT

from __future__ import annotations

import os
from collections.abc import Sequence
from glob import iglob
from pathlib import Path
from shutil import copy2

import nox

IN_CI = "JOB_ID" in os.environ or "CI" in os.environ
ALLOW_EDITABLE = os.environ.get("ALLOW_EDITABLE", str(not IN_CI)).lower() in (
    "1",
    "true",
)
PINNED = os.environ.get("PINNED", "true").lower() in (
    "1",
    "true",
)

PROJECT = "fedrq"
SPECFILE = "fedrq.spec"
LINT_SESSIONS = ("formatters", "codeqa", "typing")
LINT_FILES = (f"src/{PROJECT}", "tests/", "noxfile.py")
RELEASERR = "releaserr @ git+https://git.sr.ht/~gotmax23/releaserr"
# RELEASERR = "-e../releaserr"

nox.options.sessions = ("lint", "covtest")
nox.options.reuse_existing_virtualenvs = True


# Helpers


def install(
    session: nox.Session, *args, editable=False, constraint: str | None = None, **kwargs
):
    largs = []
    if constraint and PINNED:
        largs.extend(("-c", f"requirements/{constraint}.txt"))
    if editable and ALLOW_EDITABLE:
        largs.append("-e")
    session.install(*largs, *args, **kwargs)


def git(session: nox.Session, *args, **kwargs):
    return session.run("git", *args, **kwargs, external=True)


# General


@nox.session(venv_params=["--system-site-packages"])
def test(
    session: nox.Session,
    backend: str | None = None,
    posargs: Sequence[str] | None = None,
):
    if not backend:
        # Make sure pytest is updated, as using the version from system
        # site-packages causes problems with plugins.
        install(session, ".[test]", constraint="test", editable=True)
    tmp = Path(session.create_tmp())
    env = {"FEDRQ_BACKEND": backend} if backend else {}
    if any(i.startswith("--cov") for i in session.posargs):
        install(session, "coverage[toml]", "pytest-cov")
        env |= {"COVERAGE_FILE": str(tmp / ".coverage")}
    session.run(
        "pytest", *(posargs if posargs is not None else session.posargs), env=env
    )


@nox.session
def coverage(session: nox.Session):
    install(session, "coverage[toml]")
    session.run("coverage", "combine", "--keep", *iglob(".nox/*test/tmp/.coverage"))
    session.run("coverage", "html")
    session.run("coverage", "report", "--fail-under=90")


@nox.session
def covtest(session: nox.Session):
    session.run("rm", "-f", *iglob(".nox/*/tmp/.coverage"), external=True)
    for name in ("dnf_test", "libdnf5_test", "pydanticv1_test", "coverage"):
        session.notify(name, [*session.posargs, "--cov"])


@nox.session(venv_backend="none")
def lint(session: nox.Session):
    """
    Run formatters, codeql, typing, and reuse sessions
    """
    for notify in LINT_SESSIONS:
        session.notify(notify)


@nox.session()
def codeqa(session: nox.Session):
    install(session, ".[codeqa]", constraint="codeqa")
    session.run("ruff", *session.posargs, *LINT_FILES)
    session.run("reuse", "lint")


@nox.session
def formatters(session: nox.Session):
    install(session, ".[formatters]", constraint="formatters")
    posargs = session.posargs
    if IN_CI:
        posargs.append("--check")
    session.run("black", *posargs, *LINT_FILES)
    session.run("isort", *posargs, *LINT_FILES)


@nox.session
def typing(session: nox.Session):
    install(session, ".[typing]", editable=True, constraint="typing")
    session.run("mypy", "--enable-incomplete-feature=Unpack", "src/fedrq/")


@nox.session
def bump(session: nox.Session):
    version = session.posargs[0]

    install(session, RELEASERR, "flit", "fclogr")

    session.run("releaserr", "check-tag", version)
    session.run("releaserr", "ensure-clean")
    session.run("releaserr", "set-version", "-s", "file", version)

    install(session, ".")

    # Bump specfile
    # fmt: off
    session.run(
        "fclogr", "bump",
        "--new", version,
        "--comment", f"Release {version}.",
        SPECFILE,
    )
    # fmt: on

    # Bump changelog, commit, and tag
    git(session, "add", SPECFILE, f"src/{PROJECT}/__init__.py")
    session.run("releaserr", "clog", version, "--tag")
    session.run("releaserr", "build", "--sign", "--backend", "flit_core")


@nox.session
def publish(session: nox.Session):
    # Setup
    install(session, RELEASERR, "twine")
    session.run("releaserr", "ensure-clean")

    # Upload to PyPI
    session.run("releaserr", "upload")

    # Push to git, publish artifacts to sourcehut, and release to copr
    if not session.interactive or input(
        "Push to Sourcehut and copr build (Y/n)"
    ).lower() in ("", "y"):
        git(session, "push", "--follow-tags")
        session.run("hut", "git", "artifact", "upload", *iglob("dist/*"), external=True)
        copr_release(session)

    # Post-release bump
    session.run("releaserr", "post-version", "-s", "file")
    git(session, "add", f"src/{PROJECT}/__init__.py")
    git(session, "commit", "-S", "-m", "Post release version bump")


@nox.session
def copr_release(session: nox.Session):
    install(session, "copr-cli", "requests-gssapi", "specfile")
    tmp = Path(session.create_tmp())
    dest = tmp / SPECFILE
    copy2(SPECFILE, dest)
    session.run("python", "contrib/fedoraify.py", str(dest))
    session.run("copr-cli", "build", "--nowait", f"gotmax23/{PROJECT}", str(dest))


@nox.session
def srpm(session: nox.Session, posargs=None):
    install(session, "-r", "requirements/srpm.in", constraint="srpm")
    posargs = posargs or session.posargs
    session.run("fclogr", "--debug", "dev-srpm", *posargs)


@nox.session
def mockbuild(session: nox.Session):
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
    session.run(*margs, external=True)


# fedrq specific


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
def mkdocs(session: nox.Session):
    install(session, "-e", ".[doc]", constraint="doc")
    docgen(session)
    session.run("mkdocs", *session.posargs)


@nox.session(venv_backend="none")
def testa(session: nox.Session):
    session.notify("dnf_test", ["--cov"])
    session.notify("libdnf5_test", ["--cov"])
    session.notify("pydanticv1_test")
    session.notify("coverage")


@nox.session(venv_params=["--system-site-packages"])
def dnf_test(session: nox.Session):
    install(session, ".[test]", constraint="test", editable=True)
    test(session, "dnf")


@nox.session
def libdnf5_test(session: nox.Session):
    install(session, ".[test]", "libdnf5-shim", constraint="test", editable=True)
    test(session, "libdnf5")


@nox.session(venv_params=["--system-site-packages"])
def pydanticv1_test(session: nox.Session):
    install(session, ".[test]", constraint="pydanticv1_test")
    test(session, "dnf", ["tests/unit"])


@nox.session(name="pip-compile", python=["3.9"], venv_params=["--download"])
def pip_compile(session: nox.Session):
    session.install("pip-tools")
    Path("requirements").mkdir(exist_ok=True)

    # Use --upgrade by default unless a user passes -P.
    args = list(session.posargs)
    if not any(
        arg.startswith("-P") or arg.startswith("--upgrade-package") for arg in args
    ):
        args.append("--upgrade")

    # fmt: off
    session.run(
        "pip-compile",
        "-o", "requirements/requirements.txt",
        *args,
    )

    extras = (
        "codeqa",
        "doc",
        "formatters",
        "typing",
        "test",
    )
    for extra in extras:
        session.run(
            "pip-compile",
            "-o", f"requirements/{extra}.txt",
            f"--extra={extra}",
            *args,
        )

    extras_a = [f"--extra={extra}" for extra in extras]
    session.run("pip-compile", "-o", "requirements/all.txt", *extras_a, *args)

    session.run(
        "pip-compile", "-o", "requirements/srpm.txt", *args, "requirements/srpm.in"
    )

    session.run(
        "pip-compile",
        "-o", "requirements/pydanticv1_test.txt",
        "-c", "requirements/pydanticv1.in",
        "--extra=test",
        *args,
    )
    # fmt: on
