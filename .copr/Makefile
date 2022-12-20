# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

outdir ::= results_fedrq
srpm:
	dnf install -y git-core fedpkg rpmdevtools --setopt=install_weak_deps=False
	./srpm.sh $(outdir)
