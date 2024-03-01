# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

outdir ::= results_fedrq

srpm:
	command -v repoquery || $(SUDO) dnf install -y dnf-plugins-core
	command -v fclogr || $(SUDO) dnf copr enable -y gotmax23/fclogr
	command -v fclogr || $(SUDO) dnf install -y fclogr
	command -v nox || $(SUDO) dnf install -y nox
	nox --no-venv -e srpm -- -o $(outdir)
