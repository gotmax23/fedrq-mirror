# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

outdir ::= results_fedrq

srpm:
	command -v fclogr || $(SUDO) dnf install -y python3-pygit2
	command -v fclogr || pip install --user fclogr
	command -v nox || $(SUDO) dnf install -y nox
	nox --no-venv -e srpm -- -o $(outdir)
