# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from pytest import CaptureFixture

import fedrq.cli


def test_cli_make_cache(capsys: CaptureFixture):
    fedrq.cli.main(["make-cache", "-b", "f38"])
    out, err = capsys.readouterr()
    assert out == "Loaded 4 repos\n"
    assert not err
