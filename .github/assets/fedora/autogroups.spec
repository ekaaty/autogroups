Name:           autogroups
Version:        %autover
Release:        %autorelease
Summary:        A declarative system group synchronization engine

License:        GPLv2+
URL:            https://github.com/ekaaty/autogroups
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  systemd-rpm-macros

Requires:       python3-pyyaml
Requires:       shadow-utils
Recommends:     python3-samba

%description
Autogroups ensures that local system groups match a desired state defined 
in YAML files. It supports local and Active Directory (via Winbind) backends.

%prep
%autosetup

%build
%py3_build 

%install
%py3_install 

install -d -m 0755 %{buildroot}%{_sysconfdir}/autogroups/autogroup.d/ 

# Install Systemd units
install -D -m 0644 data/autogroups.service %{buildroot}%{_unitdir}/autogroups.service 
install -D -m 0644 data/autogroups.timer %{buildroot}%{_unitdir}/autogroups.timer 

%post
%systemd_post autogroups.timer 

%preun
%systemd_preun autogroups.timer 

%postun
%systemd_postun_with_restart autogroups.timer 

%files
%license LICENSE
%doc README.md
%{_bindir}/autogroups
%{python3_sitelib}/autogroups/
%{python3_sitelib}/autogroups-*.egg-info/ 
%{_unitdir}/autogroups.service 
%{_unitdir}/autogroups.timer 
%dir %{_sysconfdir}/autogroups/ 
%dir %{_sysconfdir}/autogroups/autogroup.d/ 

%changelog
%autochangelog
