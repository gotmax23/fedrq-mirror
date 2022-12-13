# This specfile is licensed under:
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
Name:           fedrq
Version:        0.0.1~1
Release:        %autorelease
Summary:        A tool to query the Fedora and EPEL repositories

# - code is GPL-2.0-or-later
# - the data and config files in fedrq/config are UNLICENSEed
License:        GPL-2.0-or-later AND Unlicense
URL:            https://git.sr.ht/~gotmax23/fedrq
Source:         %{url}/archive/%{version}.tar.gz#/fedrq-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  createrepo_c
BuildRequires:  fedora-repos-rawhide
BuildRequires:  python3-devel
BuildRequires:  python3-dnf
BuildRequires:  python3-tomli-w
BuildRequires:  rpmdevtools
BuildRequires:  scdoc

Requires:       python3-dnf
Requires:       fedora-repos-rawhide

# fedrq config --dump
Recommends:     python3-tomli-w


%description
fedrq is a tool to query the Fedora and EPEL repositories.


%prep
%autosetup -p1


%generate_buildrequires
%pyproject_buildrequires -x test


%build
%pyproject_wheel
scdoc < doc/fedrq.1.scd > fedrq.1


%install
%pyproject_install
%pyproject_save_files fedrq
install -Dpm 0644 fedrq.1 -t %{buildroot}%{_mandir}/man1/


%check
%pytest -v -m "not no_rpm_mock"


%files -f %{pyproject_files}
%license LICENSES/GPL-2.0-or-later.txt
%license LICENSES/Unlicense.txt
%{_bindir}/fedrq*
%{_mandir}/man1/fedrq.1*


%changelog
%autochangelog
