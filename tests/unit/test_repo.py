# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

import glob
import json

import pytest

import fedrq.cli.formatters as formatters

TEST_REPO = "repo1"


def formatter(query, formatter_name="plain", *args, attr=False, **kwargs):
    result = sorted(
        (
            str(i)
            for i in formatters.DefaultFormatters()
            .get_formatter(formatter_name)
            .format(query, *args, **kwargs)
        )
    )
    if attr:
        assert result == sorted(
            (
                str(i)
                for i in formatters.DefaultFormatters()
                .get_formatter(f"attr:{formatter_name}")
                .format(query, *args, **kwargs)
            )
        )
    return result


def test_repo_package_count(repo_test_rq, data_path):
    dir = data_path / "repos" / "repo1"
    count_specs = len(glob.glob("specs/**/*.spec", root_dir=dir, recursive=True))
    assert count_specs == len(repo_test_rq.query(arch="src"))
    assert count_specs == 3


# @pytest.mark.parametrize("special_repos", ("repo1",), indirect=["special_repos"])
def test_plain_formatter(repo_test_rq, target_cpu):
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


def test_name_formatter(repo_test_rq):
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


def test_evr_formatter(repo_test_rq):
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


def test_nv_formatter(repo_test_rq):
    query = repo_test_rq.query(name__glob="packagea*")
    expected = sorted(("packagea-1", "packagea-1", "packagea-sub-1"))
    assert formatter(query, "nv") == expected


def test_source_formatter(repo_test_rq):
    query = repo_test_rq.query()
    assert formatter(query, "source") == ["packagea", "packageb"]


@pytest.mark.parametrize(
    "latest,expected",
    (
        (None, ["1", "1", "2", "2"]),
        (1, ["2", "2"]),
    ),
)
def test_version_formatter(repo_test_rq, latest, expected):
    query = repo_test_rq.query(name="packageb", latest=latest)
    assert formatter(query, "version") == expected
    assert formatter(query, "attr:version") == expected


def test_epoch_formatter(repo_test_rq):
    query = repo_test_rq.query(name="packageb-sub")
    assert formatter(query, "epoch") == ["0", "11111"]
    assert formatter(query, "attr:epoch") == ["0", "11111"]


def test_requires_formatter(repo_test_rq):
    query = repo_test_rq.query(name=("packagea-sub", "packageb-sub"))
    assert len(query) == 3
    expected = [
        "/usr/share/packageb-sub",
        "package(b)",
        "packagea = 1-1.fc36",
        "vpackage(b) = 1-1.fc36",
    ]
    assert formatter(query, "requires", attr=True) == expected


def test_repo_formatter(repo_test_rq):
    query = repo_test_rq.query()
    result = formatter(query, "reponame", attr=True)
    assert len(query) == len(result)
    assert {"testrepo1"} == set(result)


def test_repo_license_formatter(repo_test_rq):
    query = repo_test_rq.query(name__glob="packagea*")
    result = formatter(query, "license", attr=True)
    assert result == ["Unlicense"] * 3


def test_debug_name_formatter(repo_test_rq):
    query = repo_test_rq.query(name="packageb")
    result = formatter(query, "debug_name", attr=True)
    assert result == ["packageb-debuginfo"] * len(query)


def test_repo_files_formatter(repo_test_rq):
    query = repo_test_rq.query(name=["packagea", "packageb"], arch="notsrc", latest=1)
    result = formatter(query, "files", attr=True)
    assert result == ["/usr/share/packagea", "/usr/share/packageb"]


@pytest.mark.parametrize("attr", formatters.ATTRS)
def test_formatter_sanity(repo_test_rq, attr):
    """
    Sanity test to ensure that supported formatters work at all
    """
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


def test_json_formatter(repo_test_rq):
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
    query = repo_test_rq.resolve_pkg_specs(["packagea*"], latest=1)
    output = formatter(
        query, "json:name,evr,arch,requires,conflicts,provides,source_name"
    )
    assert len(output) == 1
    assert json.loads(output[0]) == expected
