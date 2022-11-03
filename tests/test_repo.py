import glob

import pytest

import fedrq.cli.formatters as formatters

TEST_REPO = "repo1"


def formatter(query, formatter_name="plain", *args, attr=False, **kwargs):
    result = sorted(
        (
            str(i)
            for i in formatters.FormatterContainer().format(
                query, formatter_name, *args, **kwargs
            )
        )
    )
    if attr:
        assert result == sorted(
            (
                str(i)
                for i in formatters.FormatterContainer().format(
                    query, f"attr:{formatter_name}", *args, **kwargs
                )
            )
        )
    return result


def test_repo_package_count(repo_test_rq, data_path):
    dir = data_path / "repos" / "repo1"
    count_specs = len(glob.glob("specs/**/*.spec", root_dir=dir, recursive=True))
    assert count_specs == len(repo_test_rq.query(arch="src"))
    assert count_specs == 3


# @pytest.mark.parametrize("special_repos", ("repo1",), indirect=["special_repos"])
def test_plain_formatter(repo_test_rq):
    expected = sorted(
        (
            "packagea-1-1.fc36.noarch",
            "packagea-1-1.fc36.src",
            "packagea-sub-1-1.fc36.noarch",
            "packageb-1-1.fc36.src",
            "packageb-1-1.fc36.x86_64",
            "packageb-11111:2-1.fc36.src",
            "packageb-11111:2-1.fc36.x86_64",
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
    result = formatter(query, "repo", attr=True)
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
