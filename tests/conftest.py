# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

import subprocess
import logging
from pathlib import Path

# import pydantic
import pytest
from rpm import expandMacro

from fedrq import config as rqconfig

# from fedrq.releases import Config, FedoraRawhide, RELEASES
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


@pytest.fixture
def data_path():
    return TEST_DATA


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


@pytest.fixture(scope="session")
def repo_test_tmpdir(tmp_path_factory):
    b = tmp_path_factory.mktemp("testrepo")
    return str(b)


@pytest.fixture
def patch_config_dirs(monkeypatch):
    config_dirs = (FEDRQ_CONFIG_HOME,)
    monkeypatch.setattr(rqconfig, "CONFIG_DIRS", config_dirs)


@pytest.fixture
def repo_test_rq(repo_test_tmpdir, patch_config_dirs):
    config = rqconfig.get_config()
    release = config.get_release("tester", "base")
    base = release.make_base(fill_sack=False)
    base.cachedir = repo_test_tmpdir
    base.fill_sack(load_system_repo=False)
    rq = Repoquery(base)
    return rq


@pytest.fixture(scope="session")
def target_cpu():
    macro = expandMacro("%{_target_cpu}")
    assert macro != "%{_taget_cpu}"
    return macro
