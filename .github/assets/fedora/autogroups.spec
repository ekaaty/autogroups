%global upstream_version 0.2.0

Name:           autogroups
Version:        %{upstream_version}
Release:        %autorelease
Summary:        A declarative system group synchronization engine

License:        GPLv2+
URL:            https://github.com/ekaaty/autogroups
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
BuildRequires:  python3-setuptools
BuildRequires:  systemd-rpm-macros

Requires:       python3-pyyaml
Requires:       shadow-utils
Recommends:     samba-winbind

%description
Autogroups ensures that local system groups match a desired state defined 
in YAML files. It supports local and Active Directory (via Winbind) backends.

%prep
%autosetup

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files autogroups

# Config directory
install -d -m 0755 %{buildroot}%{_sysconfdir}/autogroups/groups.d/ 

# Install Systemd units
install -D -m 0644 data/autogroups.service %{buildroot}%{_unitdir}/autogroups.service 
install -D -m 0644 data/autogroups.timer %{buildroot}%{_unitdir}/autogroups.timer 

%post
%systemd_post autogroups.timer 

%preun
%systemd_preun autogroups.timer 

%postun
%systemd_postun_with_restart autogroups.timer 

%files -f %{pyproject_files}
#license LICENSE
#doc README.md
%{_bindir}/autogroups
%{_unitdir}/autogroups.service 
%{_unitdir}/autogroups.timer 
%dir %{_sysconfdir}/autogroups/ 
%dir %{_sysconfdir}/autogroups/autogroup.d/ 

%changelog
%autochangelog
