# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

import subprocess
from pathlib import Path
from shutil import rmtree

import pytest
from rpm import expandMacro

import fedrq.cli
from fedrq import config as rqconfig
from fedrq.repoquery import Repoquery

TEST_DATA = Path(__file__).parent.resolve() / "test_data"
CONFIG_HOME = TEST_DATA / "config_home"
FEDRQ_CONFIG_HOME = CONFIG_HOME / ".config" / "fedrq"
TEST_REPO_DIR = FEDRQ_CONFIG_HOME / "repos"
TEST_REPO_1 = f"""
[testrepo1]
name = testrepo1
baseurl = file://{TEST_DATA / 'repos' / 'repo1' / 'repo'}/
gpgcheck = False
"""


@pytest.fixture(scope="session", autouse=True)
def clear_cache():
    path = rqconfig.get_smartcache_basedir() / "tester"
    rmtree(path, ignore_errors=True)
    try:
        yield
    finally:
        rmtree(path, ignore_errors=True)


@pytest.fixture
def temp_smartcache(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    return tmp_path


@pytest.fixture
def data_path():
    return TEST_DATA


@pytest.fixture
def fedrq_config_home():
    return FEDRQ_CONFIG_HOME


@pytest.fixture(scope="session", autouse=True)
def repo_test_repo():
    assert TEST_DATA.is_dir()
    assert (buildsh := TEST_DATA / "build.sh").exists()
    subprocess.run(("bash", buildsh), check=True)


@pytest.fixture(scope="session", autouse=True)
def repo_test_config():
    try:
        path = TEST_REPO_DIR / "testrepo1.repo"
        path.write_text(TEST_REPO_1)
        yield
    finally:
        path.unlink()


@pytest.fixture(autouse=True)
def clear_config(monkeypatch):
    monkeypatch.setattr(rqconfig, "CONFIG_DIRS", ())


@pytest.fixture
def patch_config_dirs(monkeypatch, tmp_path):
    config_dirs = (
        tmp_path,
        FEDRQ_CONFIG_HOME,
    )
    monkeypatch.setattr(rqconfig, "CONFIG_DIRS", config_dirs)
    return tmp_path


@pytest.fixture
def repo_test_rq(patch_config_dirs):
    config = rqconfig.get_config()
    release = config.get_release("tester", "base")
    base = release.make_base(fill_sack=False)
    base.cachedir = rqconfig.get_smartcache_basedir()
    base.fill_sack(load_system_repo=False)
    rq = Repoquery(base)
    return rq


@pytest.fixture(scope="session")
def target_cpu():
    macro = expandMacro("%{_target_cpu}")
    assert macro != "%{_target_cpu}"
    return macro


@pytest.fixture
def run_command2(capsys, patch_config_dirs):
    def runner(args):
        fedrq.cli.main(args)
        stdout, stderr = capsys.readouterr()
        result = stdout.splitlines(), stderr.splitlines(), stdout
        return result

    return runner
