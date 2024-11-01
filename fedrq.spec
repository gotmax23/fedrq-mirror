# This specfile is licensed under:
#
# Copyright (C) 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: MIT
# License text: https://spdx.org/licenses/MIT.html

%bcond libdnf5 %[0%{?fedora} >= 38]

Name:           fedrq
Version:        1.4.0
Release:        1%{?dist}
Summary:        A tool to query the Fedora and EPEL repositories

# - code is GPL-2.0-or-later
# - the data and config files in fedrq/data are UNLICENSEed
# - Embeded repo defs are MIT.
# - PSF-2.0 code copied from Cpython 3.11 for older Python versions
License:        GPL-2.0-or-later AND Unlicense AND MIT AND PSF-2.0
URL:            https://fedrq.gtmx.me
%global furl    https://git.sr.ht/~gotmax23/fedrq
Source0:        %{furl}/refs/download/v%{version}/fedrq-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
# Test deps
BuildRequires:  createrepo_c
BuildRequires:  distribution-gpg-keys
BuildRequires:  python3-argcomplete
BuildRequires:  python3-dnf
%if %{with libdnf5}
BuildRequires:  python3-libdnf5
%endif
# Manpage
BuildRequires:  scdoc

Requires:       (python3-dnf or python3-libdnf5)
Suggests:       (python3-libdnf5 if dnf5)
Requires:       distribution-gpg-keys
Recommends:     fedora-repos-rawhide
Recommends:     python3-argcomplete

# fedrq config --dump
Recommends:     python3-tomli-w


%description
fedrq is a tool to query the Fedora and EPEL repositories.


%prep
%autosetup -p1


%generate_buildrequires
%pyproject_buildrequires -x test


%build
%py3_shebang_fix contrib/api_examples/*.py

%pyproject_wheel
scdoc <doc/fedrq.1.scd >fedrq.1
scdoc <doc/fedrq.5.scd >fedrq.5
register-python-argcomplete --shell bash fedrq >fedrq.bash
register-python-argcomplete --shell fish fedrq >fedrq.fish


%install
%pyproject_install
%pyproject_save_files fedrq
install -Dpm 0644 fedrq.1 -t %{buildroot}%{_mandir}/man1/
install -Dpm 0644 fedrq.5 -t %{buildroot}%{_mandir}/man5/
install -Dpm 0644 fedrq.bash %{buildroot}%{bash_completions_dir}/fedrq
install -Dpm 0644 fedrq.fish %{buildroot}%{fish_completions_dir}/fedrq.fish


%check
bash -x ./tests/test_data/build.sh

# Use python3 -m to ensure the current directory is part of sys.path so the
# tests can import from its own package.

FEDRQ_BACKEND=dnf %{py3_test_envvars} \
    %{python3} -m pytest -v -m "not no_rpm_mock"

%if %{with libdnf5}
# Some tests are failing only in mock and only with Python 3.12
#   RuntimeError: Failed to download metadata
%if v"0%{?python3_version}" >= v"3.12"
%global skips %{shrink:
    not test_smartcache_not_used
    and not test_smartcache_config
    and not test_baseurl_repog
}
%endif
FEDRQ_BACKEND=libdnf5 %{py3_test_envvars} \
    %{python3} -m pytest -v -m "not no_rpm_mock" %{?skips:-k '%{skips}'}
%endif


%files -f %{pyproject_files}
# Licenses are included in the wheel
%license %{_licensedir}/fedrq/
%doc README.md CONTRIBUTING.md NEWS.md contrib/api_examples
%{_bindir}/fedrq*
%{bash_completions_dir}/fedrq
%{fish_completions_dir}/fedrq.fish
%{_mandir}/man1/fedrq.1*
%{_mandir}/man5/fedrq.5*


%changelog
* Fri Nov 01 2024 Maxwell G <maxwell@gtmx.me> - 1.4.0-1
- Release 1.4.0.

* Tue Aug 27 2024 Maxwell G <maxwell@gtmx.me> - 1.3.0-1
- Release 1.3.0.

* Sat Aug 03 2024 Maxwell G <maxwell@gtmx.me> - 1.2.0-1
- Release 1.2.0.

* Wed May 01 2024 Maxwell G <maxwell@gtmx.me> - 1.1.0-1
- Release 1.1.0.

* Mon Apr 01 2024 Maxwell G <maxwell@gtmx.me> - 1.0.0-1
- Release 1.0.0.

* Tue Feb 13 2024 Maxwell G <maxwell@gtmx.me> - 0.15.0-1
- Release 0.15.0.

* Wed Feb 07 2024 Maxwell G <maxwell@gtmx.me> - 0.14.0-1
- Release 0.14.0.

* Mon Dec 18 2023 Maxwell G <maxwell@gtmx.me> - 0.13.0-1
- Release 0.13.0.

* Mon Sep 11 2023 Maxwell G <maxwell@gtmx.me> - 0.12.0-1
- Release 0.12.0.

* Thu Aug 31 2023 Maxwell G <maxwell@gtmx.me> - 0.11.0-1
- Release 0.11.0.

* Wed Jul 12 2023 Maxwell G <maxwell@gtmx.me> - 0.10.0-1
- Release 0.10.0.

* Thu Jun 29 2023 Maxwell G <maxwell@gtmx.me> - 0.9.0-1
- Release 0.9.0.

* Wed Jun 21 2023 Maxwell G <maxwell@gtmx.me> - 0.8.0-1
- Release 0.8.0.

* Wed May 31 2023 Maxwell G <maxwell@gtmx.me> - 0.7.1-1
- Release 0.7.1.

* Tue May 30 2023 Maxwell G <maxwell@gtmx.me> - 0.7.0-1
- Release 0.7.0.

* Sat Apr 08 2023 Maxwell G <maxwell@gtmx.me> - 0.6.0-1
- Release 0.6.0

* Sat Mar 18 2023 Maxwell G <maxwell@gtmx.me> - 0.5.0-1
- Release 0.5.0

* Tue Mar 14 2023 Maxwell G <maxwell@gtmx.me> - 0.4.1-1
- Release 0.4.1

* Tue Feb 21 2023 Maxwell G <maxwell@gtmx.me> - 0.4.0-1
- Release 0.4.0

* Mon Feb 13 2023 Maxwell G <gotmax@e.email> - 0.3.0-1
- Release 0.3.0

* Sat Jan 14 2023 Maxwell G <gotmax@e.email> - 0.2.0-1
- Release 0.2.0

* Tue Jan 03 2023 Maxwell G <gotmax@e.email> 0.1.0-1
- Release 0.1.0

* Tue Dec 20 2022 Maxwell G <gotmax@e.email> 0.0.2-1
- Release 0.0.2

* Tue Dec 20 2022 Maxwell G <gotmax@e.email> 0.0.1-1
- Release 0.0.1
