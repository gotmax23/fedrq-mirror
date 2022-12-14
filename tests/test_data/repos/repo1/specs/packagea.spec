# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

Name:           packagea
Version:        1
Release:        1%{?dist}
Summary:        %{name} is a test package

License:        Unlicense
URL:            ...

BuildArch:      noarch
BuildRequires:  vpackage(b) > 0

Provides:       package(a)
Provides:       vpackage(a) = %{version}-%{release}
Requires:       vpackage(b)


%description
%{summary}.

%package        sub
Summary:        %{name}-sub is a subpackage of %{name}
Provides:       subpackage(a)
Provides:       vsubpackage(a) = %{version}-%{release}
Requires:       %{name} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       /usr/share/packageb-sub

%description    sub
%{name}-sub is a subpackage of %{name}.

%prep


%build


%install
echo '%{name}' | install -Dpm 0644 /dev/stdin %{buildroot}%{_datadir}/%{name}
echo '%{name}-sub' | install -Dpm 0644 /dev/stdin %{buildroot}%{_datadir}/%{name}-sub


%check


%files
%{_datadir}/%{name}

%files sub
%{_datadir}/%{name}-sub


%changelog

