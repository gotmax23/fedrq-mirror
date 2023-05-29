# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from collections.abc import Callable, Sequence

import pytest

import fedrq.backends
import fedrq.cli
from fedrq.backends.base import BackendMod


def test_disablerepo_wildcard(patch_config_dirs, capsys):
    fedrq.cli.main(["pkgs", "--disablerepo=*", "*"])
    out, err = capsys.readouterr()
    assert not out and not err


@pytest.mark.parametrize(
    "args",
    [
        pytest.param(["-r", "testrepo1"]),
        pytest.param(["--disablerepo=*", "-e", "testrepo1"]),
        pytest.param(["--disablerepo=*", "--enablerepo", "base"]),
        pytest.param(["--disablerepo=*", "--enablerepo", "@base"]),
    ],
)
def test_repo_by_real_name(patch_config_dirs, capsys, args):
    fedrq.cli.main(["pkgs", *args, "-F", "repoid", "*"])
    out, err = capsys.readouterr()
    assert set(out.splitlines()) == {"testrepo1"}
    assert not err


@pytest.mark.no_rpm_mock
@pytest.mark.parametrize(
    ["args", "releasever"],
    [
        pytest.param(
            ["-b", "local", "ansible"], lambda backend: backend.get_releasever()
        ),
        pytest.param(["-b", "local:34", "ansible"], lambda _: "34"),
    ],
)
def test_local_release(
    monkeypatch: pytest.MonkeyPatch,
    args: Sequence[str],
    releasever: Callable[[BackendMod], str],
):
    backend = fedrq.backends.get_default_backend()
    base_maker = backend.BaseMaker()
    base_maker.read_system_repos(False)
    repolist = base_maker.repolist()
    del base_maker

    parser = fedrq.cli.Pkgs.make_parser()
    namespace = parser.parse_args(args)
    # Calling fill_sack() is expensive and not necessary here
    monkeypatch.setattr(backend.BaseMaker, "fill_sack", lambda self: self.base)
    obj = fedrq.cli.Pkgs(namespace)
    base_maker = backend.BaseMaker(obj.rq.base)
    assert sorted(base_maker.repolist()) == sorted(repolist)
    # TODO: Add a proper API for this
    if backend.BACKEND == "dnf":
        assert releasever(backend) == base_maker.base.conf.substitutions["releasever"]
    else:
        assert releasever(backend) == base_maker.base.get_vars().get_value("releasever")
