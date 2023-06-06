# SPDX-FileCopyrightText: 2023 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later OR MIT

from __future__ import annotations

import os
from glob import iglob
from pathlib import Path
from shutil import copy2

import nox

IN_CI = "JOB_ID" in os.environ or "CI" in os.environ
ALLOW_EDITABLE = os.environ.get("ALLOW_EDITABLE", str(not IN_CI)).lower() in (
    "1",
    "true",
)

PROJECT = "fedrq"
SPECFILE = "fedrq.spec"
LINT_SESSIONS = ("formatters", "codeqa", "typing")
LINT_FILES = (f"src/{PROJECT}", "tests/", "noxfile.py")
RELEASERR = "releaserr @ git+https://git.sr.ht/~gotmax23/releaserr"
# RELEASERR = "-e../releaserr"

nox.options.sessions = (*LINT_SESSIONS, "dnf_test", "libdnf5_test")


# Helpers


def install(session: nox.Session, *args, editable=False, **kwargs):
    if editable and ALLOW_EDITABLE:
        args = ("-e", *args)
    session.install(*args, "-U", **kwargs)


def git(session: nox.Session, *args, **kwargs):
    return session.run("git", *args, **kwargs, external=True)


# General


@nox.session(venv_params=["--system-site-packages"])
def test(session: nox.Session, backend=None):
    install(session, ".[test]", "pytest", editable=True)
    session.run(
        "pytest", *session.posargs, env={"FEDRQ_BACKEND": backend} if backend else {}
    )


@nox.session(venv_backend="none")
def lint(session: nox.Session):
    """
    Run formatters, codeql, typing, and reuse sessions
    """
    for notify in LINT_SESSIONS:
        session.notify(notify)


@nox.session()
def codeqa(session: nox.Session):
    install(session, ".[codeqa]")
    session.run("ruff", *session.posargs, *LINT_FILES)
    session.run("reuse", "lint")


@nox.session
def formatters(session: nox.Session):
    install(session, ".[formatters]")
    posargs = session.posargs
    if IN_CI:
        posargs.append("--check")
    session.run("black", *posargs, *LINT_FILES)
    session.run("isort", *posargs, *LINT_FILES)


@nox.session
def typing(session: nox.Session):
    install(session, ".[typing]", editable=True)
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
    git(session, "add", "src/{PROJECT}/__init__.py")
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
    install(session, "fclogr")
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
    install(session, "-e", ".[doc]")
    docgen(session)
    session.run("mkdocs", *session.posargs)


@nox.session(venv_backend="none")
def testa(session):
    session.notify("dnf_test")
    session.notify("libdnf5_test")


@nox.session(venv_params=["--system-site-packages"])
def dnf_test(session: nox.Session):
    test(session, "dnf")


@nox.session(venv_params=["--system-site-packages"])
def libdnf5_test(session: nox.Session):
    test(session, "libdnf5")
