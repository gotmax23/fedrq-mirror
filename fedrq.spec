# This specfile is licensed under:
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
Name:           fedrq
Version:        0.0.1~1
Release:        %autorelease
Summary:        A tool to query the Fedora and EPEL repositories

License:        GPL-2.0-or-later
URL:            https://git.sr.ht/~gotmax23/fedrq
Source:         %{url}/archive/%{version}.tar.gz#/fedrq-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  createrepo_c
BuildRequires:  fedora-repos-rawhide
BuildRequires:  python3-devel
BuildRequires:  python3-dnf
BuildRequires:  python3-tomli-w
BuildRequires:  rpmdevtools

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


%install
%pyproject_install
%pyproject_save_files fedrq


%check
%pytest -v -m "not no_rpm_mock"


%files -f %{pyproject_files}
%license LICENSES/GPL-2.0-or-later.txt
%{_bindir}/fedrq*


%changelog
%autochangelog
