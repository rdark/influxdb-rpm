# InfluxDB spec for EL6
#
# NOTE: This spec repackages pre-built binaries from influxdb releases and does
# not build from source.

%define influxdb_group influxdb
%define influxdb_user  influxdb
%define influxdb_home  %{_sharedstatedir}/influxdb
%define  debug_package %{nil}

Summary:        An Open-Source, Distributed, Time Series Database
Name:           influxdb
Version:        0.9.4.2
ExclusiveArch:  x86_64
Release:        1
License:        MIT
Group:          Applications/Databases
URL:            https://influxdb.com
Source0:        https://s3.amazonaws.com/influxdb/influxdb_%{version}_x86_64.tar.gz
Patch0:         0001-influxdb.conf-dir-locations.patch
Patch1:         0002-init.sh-dir-locations.patch
Patch2:         0003-init.sh-runuser.patch
Requires:       coreutils
Requires:       openssl
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}.%{_arch}

%description
InfluxDB is an open source distributed time series database with no external
dependencies. It's useful for recording metrics, events, and performing
analytics.

%prep
%setup -q -n %{name}_%{version}_%{_arch}
# patch influxdb.conf for directory locations
%patch0 -p1
pushd ./
cd opt/influxdb/versions/%{version}
# patch init script for directory locations
%patch1 -p5 
# patch init script to use runuser rather than su
%patch2 -p5 
popd

%build
# nope

%install
%{__rm} -rf %{buildroot}
# setup base directories - install binaries to /usr/bin rather than /opt
install -d -m 0750 %{buildroot}%{_sharedstatedir}/%{name}
install -d -m 0750 %{buildroot}%{_localstatedir}/log/%{name}
install -d -m 0775 %{buildroot}%{_localstatedir}/run/%{name}
install -d -m 0755 %{buildroot}%{_sysconfdir}/logrotate.d
install -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}
install -d -m 0755 %{buildroot}%{_bindir}
install -d -m 0755 %{buildroot}%{_initddir}

# install logrotate config
install -p -m 0644 etc/logrotate.d/influxd %{buildroot}%{_sysconfdir}/logrotate.d/influxdb

# install main config file
install -p -m 0640 etc/opt/%{name}/%{name}.conf %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf

# install binaries
install -p -m 0755 opt/%{name}/versions/%{version}/influx %{buildroot}%{_bindir}/influx
install -p -m 0755 opt/%{name}/versions/%{version}/influxd %{buildroot}%{_bindir}/influxd

# install init script
install -p -m 0755 opt/%{name}/versions/%{version}/scripts/init.sh %{buildroot}%{_initddir}/%{name}

%clean
rm -rf %{buildroot}

%pre
# setup users
getent group %{influxdb_group} >/dev/null || groupadd -r %{influxdb_group}
getent passwd %{influxdb_user} >/dev/null || /usr/sbin/useradd --comment "InfluxDB Daemon User" --shell /sbin/nologin -M -r -g %{influxdb_group} --home %{influxdb_home} %{influxdb_user}

%preun
if [ $1 = 0 ]; then
  service %{name} stop > /dev/null 2>&1
  chkconfig --del %{name}
fi

%postun
if [ $1 -ge 1 ]; then
  service %{name} condrestart >/dev/null 2>&1
fi


%files
%defattr(-,%{influxdb_user},%{influxdb_group})
%{_sharedstatedir}/%{name}
%{_localstatedir}/log/%{name}
%{_localstatedir}/run/%{name}
%attr(-,root,%{influxdb_group}) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%defattr(-,root,root)
%{_bindir}/influx
%{_bindir}/influxd
%{_initddir}/%{name}
%{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

%changelog
* Fri Nov 13 2015 Richard Clark <richard@drkr.uk> 0.9.4.2-1
- Initial version
