#
%define nginx_home %{_localstatedir}/cache/zstor-nginx
%define nginx_user zstor-nginx
%define nginx_group zstor-nginx
%define nginx_loggroup adm

# distribution specific definitions
%define use_systemd (0%{?fedora} && 0%{?fedora} >= 18) || (0%{?rhel} && 0%{?rhel} >= 7) || (0%{?suse_version} == 1315)

%if 0%{?rhel} == 6
%define _group System Environment/Daemons
Requires(pre): shadow-utils
Requires: initscripts >= 8.36
Requires(post): chkconfig
#Requires: openssl >= 1.0.1
#BuildRequires: openssl-devel >= 1.0.1
%endif

%if 0%{?rhel} == 7
BuildRequires: redhat-lsb-core
%define _group System Environment/Daemons
%define epoch 1
Epoch: %{epoch}
Requires(pre): shadow-utils
Requires: systemd
BuildRequires: systemd
%define os_minor %(lsb_release -rs | cut -d '.' -f 2)
%if %{os_minor} >= 4
#Requires: openssl >= 1.0.2
#BuildRequires: openssl-devel >= 1.0.2
%define dist .el7
%else
#Requires: openssl >= 1.0.1
#BuildRequires: openssl-devel >= 1.0.1
%define dist .el7
%endif
%endif

%if 0%{?suse_version} == 1315
%define _group Productivity/Networking/Web/Servers
%define nginx_loggroup trusted
Requires(pre): shadow
Requires: systemd
#BuildRequires: libopenssl-devel
BuildRequires: systemd
%endif

# end of distribution specific definitions

%define main_version @VERSION@
%define main_release @RELEASE@%{?dist}

%define bdir %{_builddir}/%{name}-%{main_version}

%define WITH_CC_OPT $(echo %{optflags} $(pcre-config --cflags)) -fPIC
%define WITH_LD_OPT -Wl,-z,relro -Wl,-z,now -pie

%define BASE_CONFIGURE_ARGS $(echo "--prefix=%{_sysconfdir}/zstor-nginx --sbin-path=%{_sbindir}/zstor-nginx --modules-path=%{_libdir}/zstor-nginx/modules --conf-path=%{_sysconfdir}/zstor-nginx/zstor-nginx.conf --error-log-path=%{_localstatedir}/log/zstor-nginx/error.log --http-log-path=%{_localstatedir}/log/zstor-nginx/access.log --pid-path=%{_localstatedir}/run/zstor-nginx.pid --lock-path=%{_localstatedir}/run/zstor-nginx.lock --http-client-body-temp-path=%{_localstatedir}/cache/zstor-nginx/client_temp --http-proxy-temp-path=%{_localstatedir}/cache/zstor-nginx/proxy_temp --http-fastcgi-temp-path=%{_localstatedir}/cache/zstor-nginx/fastcgi_temp --http-uwsgi-temp-path=%{_localstatedir}/cache/zstor-nginx/uwsgi_temp --http-scgi-temp-path=%{_localstatedir}/cache/zstor-nginx/scgi_temp --user=%{nginx_user} --group=%{nginx_group} --with-compat --with-file-aio --with-threads --with-http_addition_module --with-http_auth_request_module --with-http_dav_module --with-http_flv_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_mp4_module --with-http_random_index_module --with-http_realip_module --with-http_secure_link_module --with-http_slice_module --with-http_ssl_module --with-http_stub_status_module --with-http_sub_module --with-http_v2_module --with-mail --with-mail_ssl_module --with-stream --with-stream_realip_module --with-stream_ssl_module --with-stream_ssl_preread_module")

Summary: High performance web server
Name: zstor-nginx
Version: %{main_version}
Release: %{main_release}
Vendor: Nginx, Inc.
URL: http://nginx.org/
Group: %{_group}

Source0: http://nginx.org/download/%{name}-%{version}.tar.gz
Source1: logrotate
Source2: zstor-nginx.init.in
Source3: zstor-nginx.sysconf
Source4: zstor-nginx.conf
#Source5: zstor-nginx.vh.default.conf
Source7: zstor-nginx-debug.sysconf
Source8: zstor-nginx.service
Source9: zstor-nginx.upgrade.sh
Source10: zstor-nginx.suse.logrotate
Source11: zstor-nginx-debug.service
Source12: COPYRIGHT
Source13: zstor-nginx.check-reload.sh

License: 2-clause BSD-like license

BuildRoot: %{_tmppath}/%{name}-%{main_version}-%{main_release}-root
BuildRequires: zlib-devel
BuildRequires: pcre-devel

Provides: webserver

%description
zstor-nginx [engine x] is an HTTP and reverse proxy server, as well as
a mail proxy server.

%if 0%{?suse_version} == 1315
%debug_package
%endif

%prep
%setup -q
cp %{SOURCE2} .
sed -e 's|%%DEFAULTSTART%%|2 3 4 5|g' -e 's|%%DEFAULTSTOP%%|0 1 6|g' \
    -e 's|%%PROVIDES%%|zstor-nginx|g' < %{SOURCE2} > zstor-nginx.init
sed -e 's|%%DEFAULTSTART%%||g' -e 's|%%DEFAULTSTOP%%|0 1 2 3 4 5 6|g' \
    -e 's|%%PROVIDES%%|zstor-nginx-debug|g' < %{SOURCE2} > zstor-nginx-debug.init

%build
./configure %{BASE_CONFIGURE_ARGS} \
    --with-cc-opt="%{WITH_CC_OPT}" \
    --with-ld-opt="%{WITH_LD_OPT}" \
    --with-debug \
    --with-openssl=./openssl-1.0.2n \
    --with-openssl-opt=-fPIC
make %{?_smp_mflags}
%{__mv} %{bdir}/objs/nginx \
    %{bdir}/objs/zstor-nginx-debug
./configure %{BASE_CONFIGURE_ARGS} \
    --with-cc-opt="%{WITH_CC_OPT}" \
    --with-ld-opt="%{WITH_LD_OPT}" \
    --with-openssl=./openssl-1.0.2n \
    --with-openssl-opt=-fPIC
make %{?_smp_mflags}

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__make} DESTDIR=$RPM_BUILD_ROOT INSTALLDIRS=vendor install

%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/zstor-nginx
%{__mv} $RPM_BUILD_ROOT%{_sysconfdir}/zstor-nginx/html $RPM_BUILD_ROOT%{_datadir}/zstor-nginx/

%{__rm} -f $RPM_BUILD_ROOT%{_sysconfdir}/zstor-nginx/*.default
%{__rm} -f $RPM_BUILD_ROOT%{_sysconfdir}/zstor-nginx/fastcgi.conf

%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/log/zstor-nginx
%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/run/zstor-nginx
%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/cache/zstor-nginx

%{__mkdir} -p $RPM_BUILD_ROOT%{_libdir}/zstor-nginx/modules
cd $RPM_BUILD_ROOT%{_sysconfdir}/zstor-nginx && \
    %{__ln_s} ../..%{_libdir}/zstor-nginx/modules modules && cd -

%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/doc/%{name}-%{main_version}
%{__install} -m 644 -p %{SOURCE12} \
    $RPM_BUILD_ROOT%{_datadir}/doc/%{name}-%{main_version}/

%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/zstor-nginx/conf.d
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/zstor-nginx/zstor-nginx.conf
%{__install} -m 644 -p %{SOURCE4} \
    $RPM_BUILD_ROOT%{_sysconfdir}/zstor-nginx/zstor-nginx.conf
#%{__install} -m 644 -p %{SOURCE5} \
#    $RPM_BUILD_ROOT%{_sysconfdir}/zstor-nginx/conf.d/default.conf

%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
%{__install} -m 644 -p %{SOURCE3} \
    $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/zstor-nginx
%{__install} -m 644 -p %{SOURCE7} \
    $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/zstor-nginx-debug

%{__install} -p -D -m 0644 %{bdir}/objs/nginx.8 \
    $RPM_BUILD_ROOT%{_mandir}/man8/zstor-nginx.8

%if %{use_systemd}
# install systemd-specific files
%{__mkdir} -p $RPM_BUILD_ROOT%{_unitdir}
%{__install} -m644 %SOURCE8 \
    $RPM_BUILD_ROOT%{_unitdir}/zstor-nginx.service
%{__install} -m644 %SOURCE11 \
    $RPM_BUILD_ROOT%{_unitdir}/zstor-nginx-debug.service
%{__mkdir} -p $RPM_BUILD_ROOT%{_libexecdir}/initscripts/legacy-actions/zstor-nginx
%{__install} -m755 %SOURCE9 \
    $RPM_BUILD_ROOT%{_libexecdir}/initscripts/legacy-actions/zstor-nginx/upgrade
%{__install} -m755 %SOURCE13 \
    $RPM_BUILD_ROOT%{_libexecdir}/initscripts/legacy-actions/zstor-nginx/check-reload
%else
# install SYSV init stuff
%{__mkdir} -p $RPM_BUILD_ROOT%{_initrddir}
%{__install} -m755 zstor-nginx.init $RPM_BUILD_ROOT%{_initrddir}/zstor-nginx
%{__install} -m755 zstor-nginx-debug.init $RPM_BUILD_ROOT%{_initrddir}/zstor-nginx-debug
%endif

# install log rotation stuff
%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
%if 0%{?suse_version}
%{__install} -m 644 -p %{SOURCE10} \
    $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/zstor-nginx
%else
%{__install} -m 644 -p %{SOURCE1} \
    $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/zstor-nginx
%endif

%{__install} -m755 %{bdir}/objs/zstor-nginx-debug \
    $RPM_BUILD_ROOT%{_sbindir}/zstor-nginx-debug

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)

%{_sbindir}/zstor-nginx
%{_sbindir}/zstor-nginx-debug

%dir %{_sysconfdir}/zstor-nginx
%dir %{_sysconfdir}/zstor-nginx/conf.d
%{_sysconfdir}/zstor-nginx/modules

%config(noreplace) %{_sysconfdir}/zstor-nginx/zstor-nginx.conf
#%config(noreplace) %{_sysconfdir}/zstor-nginx/conf.d/default.conf
%config(noreplace) %{_sysconfdir}/zstor-nginx/mime.types
%config(noreplace) %{_sysconfdir}/zstor-nginx/fastcgi_params
%config(noreplace) %{_sysconfdir}/zstor-nginx/scgi_params
%config(noreplace) %{_sysconfdir}/zstor-nginx/uwsgi_params
%config(noreplace) %{_sysconfdir}/zstor-nginx/koi-utf
%config(noreplace) %{_sysconfdir}/zstor-nginx/koi-win
%config(noreplace) %{_sysconfdir}/zstor-nginx/win-utf

%config(noreplace) %{_sysconfdir}/logrotate.d/zstor-nginx
%config(noreplace) %{_sysconfdir}/sysconfig/zstor-nginx
%config(noreplace) %{_sysconfdir}/sysconfig/zstor-nginx-debug
%if %{use_systemd}
%{_unitdir}/zstor-nginx.service
%{_unitdir}/zstor-nginx-debug.service
%dir %{_libexecdir}/initscripts/legacy-actions/zstor-nginx
%{_libexecdir}/initscripts/legacy-actions/zstor-nginx/*
%else
%{_initrddir}/zstor-nginx
%{_initrddir}/zstor-nginx-debug
%endif

%attr(0755,root,root) %dir %{_libdir}/zstor-nginx
%attr(0755,root,root) %dir %{_libdir}/zstor-nginx/modules
%dir %{_datadir}/zstor-nginx
%dir %{_datadir}/zstor-nginx/html
%{_datadir}/zstor-nginx/html/*

%attr(0755,root,root) %dir %{_localstatedir}/cache/zstor-nginx
%attr(0755,root,root) %dir %{_localstatedir}/log/zstor-nginx

%dir %{_datadir}/doc/%{name}-%{main_version}
%doc %{_datadir}/doc/%{name}-%{main_version}/COPYRIGHT
%{_mandir}/man8/zstor-nginx.8*

%pre
# Add the "zstor-nginx" user
getent group %{nginx_group} >/dev/null || groupadd -r %{nginx_group}
getent passwd %{nginx_user} >/dev/null || \
    useradd -r -g %{nginx_group} -s /sbin/nologin \
    -d %{nginx_home} -c "zstor-nginx user"  %{nginx_user}
exit 0

%post
# Register the zstor-nginx service
if [ $1 -eq 1 ]; then
%if %{use_systemd}
    /usr/bin/systemctl preset zstor-nginx.service >/dev/null 2>&1 ||:
    /usr/bin/systemctl preset zstor-nginx-debug.service >/dev/null 2>&1 ||:
%else
    /sbin/chkconfig --add zstor-nginx
    /sbin/chkconfig --add zstor-nginx-debug
%endif
    # print site info
    cat <<BANNER
----------------------------------------------------------------------

Thanks for using zstor-nginx!

----------------------------------------------------------------------
BANNER

    # Touch and set permisions on default log files on installation

    if [ -d %{_localstatedir}/log/zstor-nginx ]; then
        if [ ! -e %{_localstatedir}/log/zstor-nginx/access.log ]; then
            touch %{_localstatedir}/log/zstor-nginx/access.log
            %{__chmod} 640 %{_localstatedir}/log/zstor-nginx/access.log
            %{__chown} zstor-nginx:%{nginx_loggroup} %{_localstatedir}/log/zstor-nginx/access.log
        fi

        if [ ! -e %{_localstatedir}/log/zstor-nginx/error.log ]; then
            touch %{_localstatedir}/log/zstor-nginx/error.log
            %{__chmod} 640 %{_localstatedir}/log/zstor-nginx/error.log
            %{__chown} zstor-nginx:%{nginx_loggroup} %{_localstatedir}/log/zstor-nginx/error.log
        fi
    fi
fi

%preun
if [ $1 -eq 0 ]; then
%if %use_systemd
    /usr/bin/systemctl --no-reload disable zstor-nginx.service >/dev/null 2>&1 ||:
    /usr/bin/systemctl stop zstor-nginx.service >/dev/null 2>&1 ||:
%else
    /sbin/service zstor-nginx stop > /dev/null 2>&1
    /sbin/chkconfig --del zstor-nginx
    /sbin/chkconfig --del zstor-nginx-debug
%endif
fi

%postun
%if %use_systemd
/usr/bin/systemctl daemon-reload >/dev/null 2>&1 ||:
%endif
if [ $1 -ge 1 ]; then
    /sbin/service zstor-nginx status  >/dev/null 2>&1 || exit 0
    /sbin/service zstor-nginx upgrade >/dev/null 2>&1 || echo \
        "Binary upgrade failed, please check zstor-nginx's error.log"
fi

%changelog
* Tue Oct 17 2017 Konstantin Pavlov <thresh@nginx.com>
- 1.12.2
