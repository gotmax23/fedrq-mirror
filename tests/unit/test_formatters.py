# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import json
from collections.abc import Callable, Collection
from functools import cache
from pathlib import Path

import pytest

from fedrq import config as rqconfig
from fedrq.backends.base import PackageQueryCompat, RepoqueryBase
from fedrq.cli import formatters


@cache
def get_rq():
    return rqconfig.get_config(load_filelists="always").get_rq("tester", "base")


def formatter(
    query,
    formatter_name="plain",
    *args,
    attr=False,
    sort=True,
    repoquery: RepoqueryBase | None = None,
    **kwargs,
):
    result = [
        str(i)
        for i in formatters.DefaultFormatters.get_formatter(
            formatter_name, repoquery=repoquery
        ).format(query, *args, **kwargs)
    ]
    if sort:
        result.sort()
    if attr:
        result2 = [
            str(i)
            for i in formatters.DefaultFormatters.get_formatter(
                f"attr:{formatter_name}"
            ).format(query, *args, **kwargs)
        ]
        if sort:
            result2.sort()
        assert result == result2
    return result


# @pytest.mark.parametrize("special_repos", ("repo1",), indirect=["special_repos"])
def test_plain_formatter(patch_config_dirs, target_cpu):
    repo_test_rq = get_rq()
    expected = sorted(
        (
            "packagea-1-1.fc36.noarch",
            "packagea-1-1.fc36.src",
            "packagea-sub-1-1.fc36.noarch",
            "packageb-1-1.fc36.src",
            f"packageb-1-1.fc36.{target_cpu}",
            "packageb-11111:2-1.fc36.src",
            f"packageb-11111:2-1.fc36.{target_cpu}",
            "packageb-sub-1-1.fc36.noarch",
            "packageb-sub-11111:2-1.fc36.noarch",
        )
    )
    query = repo_test_rq.query()
    assert formatter(query) == expected
    assert formatter(query, "plain") == expected


def test_plainwithrepo_formatter(patch_config_dirs, repo_test_rq, target_cpu):
    repo_test_rq = get_rq()
    expected = sorted(
        (
            "packagea-1-1.fc36.noarch testrepo1",
            "packagea-1-1.fc36.src testrepo1",
            "packagea-sub-1-1.fc36.noarch testrepo1",
            "packageb-1-1.fc36.src testrepo1",
            f"packageb-1-1.fc36.{target_cpu} testrepo1",
            "packageb-11111:2-1.fc36.src testrepo1",
            f"packageb-11111:2-1.fc36.{target_cpu} testrepo1",
            "packageb-sub-1-1.fc36.noarch testrepo1",
            "packageb-sub-11111:2-1.fc36.noarch testrepo1",
        )
    )
    query = repo_test_rq.query()
    assert formatter(query, "plainwithrepo") == expected
    assert formatter(query, "nevrr") == expected


def test_name_formatter(patch_config_dirs):
    repo_test_rq = get_rq()
    expected = sorted(
        (
            "packagea",
            "packagea",
            "packagea-sub",
            "packageb",
            "packageb",
            "packageb",
            "packageb",
            "packageb-sub",
            "packageb-sub",
        )
    )
    query = repo_test_rq.query()
    assert formatter(query, "name") == expected
    assert formatter(query, "attr:name") == expected


def test_evr_formatter(patch_config_dirs):
    repo_test_rq = get_rq()
    query = repo_test_rq.query(name__glob="packageb*")
    result = sorted(
        (
            "11111:2-1.fc36",
            "11111:2-1.fc36",
            "11111:2-1.fc36",
            "1-1.fc36",
            "1-1.fc36",
            "1-1.fc36",
        )
    )
    assert formatter(query, "evr") == result
    assert formatter(query, "attr:evr") == result


def test_nv_formatter(patch_config_dirs):
    repo_test_rq = get_rq()
    query = repo_test_rq.query(name__glob="packagea*")
    expected = sorted(("packagea-1", "packagea-1", "packagea-sub-1"))
    assert formatter(query, "nv") == expected


def test_source_formatter(patch_config_dirs):
    repo_test_rq = get_rq()
    query = repo_test_rq.query()
    assert formatter(query, "source") == ["packagea", "packageb"]


@pytest.mark.parametrize(
    "latest,expected",
    (
        (None, ["1", "1", "2", "2"]),
        (1, ["2", "2"]),
    ),
)
def test_version_formatter(patch_config_dirs, latest, expected):
    repo_test_rq = get_rq()
    query = repo_test_rq.query(name="packageb", latest=latest)
    assert formatter(query, "version") == expected
    assert formatter(query, "attr:version") == expected


def test_epoch_formatter(patch_config_dirs):
    repo_test_rq = get_rq()
    query = repo_test_rq.query(name="packageb-sub")
    assert formatter(query, "epoch") == ["0", "11111"]
    assert formatter(query, "attr:epoch") == ["0", "11111"]


def test_requires_formatter(patch_config_dirs):
    repo_test_rq = get_rq()
    query = repo_test_rq.query(name=("packagea-sub", "packageb-sub"))
    assert len(query) == 3
    expected = [
        "/usr/share/packageb-sub",
        "package(b)",
        "packagea = 1-1.fc36",
        "vpackage(b) = 1-1.fc36",
    ]
    assert formatter(query, "requires", attr=True) == expected


def test_repo_formatter(patch_config_dirs):
    repo_test_rq = get_rq()
    query = repo_test_rq.query()
    result = formatter(query, "reponame", attr=True)
    assert len(query) == len(result)
    assert {"testrepo1"} == set(result)


def test_repo_license_formatter(patch_config_dirs):
    repo_test_rq = get_rq()
    query = repo_test_rq.query(name__glob="packagea*")
    result = formatter(query, "license", attr=True)
    assert result == ["Unlicense"] * 3


def test_debug_name_formatter(patch_config_dirs):
    repo_test_rq = get_rq()
    query = repo_test_rq.query(name="packageb")
    result = formatter(query, "debug_name", attr=True)
    assert result == ["packageb-debuginfo"] * len(query)


def test_repo_files_formatter(patch_config_dirs):
    repo_test_rq = get_rq()
    query = repo_test_rq.query(name=["packagea", "packageb"], arch="notsrc", latest=1)
    result = formatter(query, "files", attr=True)
    assert result == ["/usr/share/packagea", "/usr/share/packageb"]


@pytest.mark.parametrize(
    "args, expected_call",
    [
        pytest.param([], lambda x: x),
        pytest.param([None], lambda x: x),
        pytest.param([{"file"}], lambda x: x),
        pytest.param([{"ftp"}], lambda _: None),
    ],
)
def test_remote_location(
    patch_config_dirs,
    data_path: Path,
    args: list[Collection[str] | None],
    expected_call: Callable[[str], str | None],
):
    path = (
        data_path
        / "repos"
        / "repo1"
        / "repo"
        / "SRPMS"
        / "specs"
        / "packagea-1-1.fc36.src.rpm"
    )
    expected = expected_call(f"file://{path}")

    repo_test_rq = get_rq()
    package = repo_test_rq.get_package("packagea", "src")
    result = package.remote_location(*args)
    assert result == expected


def test_formatter_remote_location(patch_config_dirs, data_path: Path):
    path = (
        data_path
        / "repos"
        / "repo1"
        / "repo"
        / "SRPMS"
        / "specs"
        / "packagea-1-1.fc36.src.rpm"
    )
    expected = f"file://{path}"

    repo_test_rq = get_rq()
    package = repo_test_rq.get_package("packagea", "src")
    result = formatter([package], "remote_location")
    assert result == [expected]


@pytest.mark.parametrize("attr", formatters._ATTRS)
def test_formatter_sanity(patch_config_dirs, attr):
    """
    Sanity test to ensure that supported formatters work at all
    """
    repo_test_rq = get_rq()
    query = repo_test_rq.query(
        name=["packagea", "packagea-sub", "packageb", "packageb-sub"], latest=1
    )
    result = formatter(query, attr)
    if attr not in (
        "provides",
        "requires",
        "obsoletes",
        "conflicts",
        "recommends",
        "suggests",
        "enhances",
        "supplements",
    ):
        assert len(result) == len(query)


def test_json_formatter(patch_config_dirs):
    expected = [
        {
            "name": "packagea",
            "evr": "1-1.fc36",
            "arch": "noarch",
            "requires": ["vpackage(b)"],
            "conflicts": [],
            "provides": ["package(a)", "packagea = 1-1.fc36", "vpackage(a) = 1-1.fc36"],
            "source_name": "packagea",
        },
        {
            "name": "packagea",
            "evr": "1-1.fc36",
            "arch": "src",
            "requires": ["vpackage(b) > 0"],
            "conflicts": [],
            "provides": ["packagea = 1-1.fc36", "packagea-sub = 1-1.fc36"],
            "source_name": None,
        },
        {
            "name": "packagea-sub",
            "evr": "1-1.fc36",
            "arch": "noarch",
            "requires": ["/usr/share/packageb-sub", "packagea = 1-1.fc36"],
            "conflicts": [],
            "provides": [
                "subpackage(a)",
                "packagea-sub = 1-1.fc36",
                "vsubpackage(a) = 1-1.fc36",
            ],
            "source_name": "packagea",
        },
    ]
    repo_test_rq = get_rq()
    query = repo_test_rq.resolve_pkg_specs(["packagea*"], latest=1)
    output = formatter(
        query, "json:name,evr,arch,requires,conflicts,provides,source_name"
    )
    assert len(output) == 1
    assert json.loads(output[0]) == expected


def test_multiline_formatter(patch_config_dirs):
    repo_test_rq = get_rq()
    query = repo_test_rq.resolve_pkg_specs(
        ["packagea-1", "packageb"], with_src=False, latest=1
    )
    output = formatter(query, "multiline:na,description", sort=False)
    assert output == [
        "packagea.noarch : packagea is a test package.",
        "packagea.noarch : This is another line of text.",
        "packagea.noarch : Another another.",
        "packagea.noarch : And another.",
        "packageb.x86_64 : ...",
    ]


@cache
def formatter_test_query() -> PackageQueryCompat:
    repo_test_rq = get_rq()
    return repo_test_rq.resolve_pkg_specs(
        ["packagea-1", "packageb"], with_src=False, latest=1
    )


@pytest.mark.parametrize(
    "formatter_,expected_output",
    [
        pytest.param(
            "multiline:na,description",
            [
                "packagea.noarch : packagea is a test package.",
                "packagea.noarch : This is another line of text.",
                "packagea.noarch : Another another.",
                "packagea.noarch : And another.",
                "packageb.x86_64 : ...",
            ],
            id="multiline",
        ),
        pytest.param(
            "line:na,repoid",
            [
                "packagea.noarch : testrepo1",
                "packageb.x86_64 : testrepo1",
            ],
            id="line-simple",
        ),
        pytest.param(
            "line:na,repoid:",
            [
                "packagea.noarch : testrepo1",
                "packageb.x86_64 : testrepo1",
            ],
            id="line-trailing",
        ),
        pytest.param(
            "line:na,repoid: | ",
            [
                "packagea.noarch | testrepo1",
                "packageb.x86_64 | testrepo1",
            ],
            id="line-custom-separator",
        ),
        pytest.param(
            "line:na,repoid,source: | ",
            [
                "packagea.noarch | testrepo1 | packagea",
                "packageb.x86_64 | testrepo1 | packageb",
            ],
            id="line-special-formatter",
        ),
        pytest.param(
            "line:line:na,repoid: | ",
            [
                "packagea.noarch | testrepo1",
                "packageb.x86_64 | testrepo1",
            ],
            id="line-stacked",
        ),
        pytest.param(
            "description",
            [
                "packagea is a test package.\n"
                "This is another line of text.\nAnother another.\nAnd another.\n---\n",
                "...",
            ],
            id="description",
        ),
        pytest.param(
            [
                "requiresmatch:packageb",
                "rm:packageb",
                "rmsrc:packageb",
                "requiresmatch-src:packageb",
            ],
            ["vpackage(b)"],
            id="rm",
        ),
        pytest.param(
            ["narm:packageb", "na-requiresmatch:packageb,packagea,jfjfjfj"],
            ["packagea.noarch : vpackage(b)"],
            id="narm",
        ),
    ],
)
def test_formatter_p(
    patch_config_dirs,
    formatter_: str | Collection[str],
    expected_output: Collection[str],
) -> None:
    formatters = [formatter_] if isinstance(formatter_, str) else formatter_
    query = formatter_test_query()
    for fmt in formatters:
        output = formatter(query, fmt, sort=False, repoquery=get_rq())
        assert output == expected_output, fmt
