%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%define version 3.0
%define release 1

Summary:  A System for Allowing the Control of Process State on UNIX
Name: supervisor
Version: %{version}
Release: %{release}

License: ZPLv2.1 and BSD and MIT
Group: System Environment/Base
URL: http://supervisord.org/
Source0: http://pypi.python.org/packages/source/s/%{name}/%{name}-%{version}.tar.gz
Source1: supervisord.init
Source2: supervisord.conf
Source3: supervisor.logrotate
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch
BuildRequires: python-devel
BuildRequires: python-setuptools

Requires: python-meld3 >= 0.6.5
Requires: python-setuptools
Requires(preun): /sbin/service, /sbin/chkconfig
Requires(postun): /sbin/service, /sbin/chkconfig


%description
The supervisor is a client/server system that allows its users to control a
number of processes on UNIX-like operating systems.

%prep
%setup -q -n %{name}-%{version}

%build
CFLAGS="%{optflags}" %{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install --skip-build --root %{buildroot}
mkdir -p %{buildroot}/%{_sysconfdir}
mkdir -p %{buildroot}/%{_sysconfdir}/supervisord.d
mkdir -p %{buildroot}/%{_sysconfdir}/logrotate.d/
mkdir -p %{buildroot}/%{_initrddir}
mkdir -p %{buildroot}/%{_localstatedir}/log/%{name}
chmod 770 %{buildroot}/%{_localstatedir}/log/%{name}
install -p -m 755 %{SOURCE1} %{buildroot}/%{_initrddir}/supervisord
install -p -m 644 %{SOURCE2} %{buildroot}/%{_sysconfdir}/supervisord.conf
install -p -m 644 %{SOURCE3} %{buildroot}/%{_sysconfdir}/logrotate.d/supervisor
sed -i s'/^#!.*//' $( find %{buildroot}/%{python_sitelib}/supervisor/ -type f)

rm -rf %{buildroot}/%{python_sitelib}/supervisor/meld3/
rm -f %{buildroot}%{_prefix}/doc/*.txt

%clean
rm -rf %{buildroot}

%post
/sbin/chkconfig --add %{name}d || :

%preun
if [ $1 = 0 ]; then
    /sbin/service supervisord stop > /dev/null 2>&1 || :
    /sbin/chkconfig --del %{name}d || :
fi

%files
%defattr(-,root,root,-)
%doc README.rst LICENSES.txt TODO.txt CHANGES.txt COPYRIGHT.txt PLUGINS.rst
%dir %{_localstatedir}/log/%{name}
%{_initrddir}/supervisord
%{python_sitelib}/*
%{_bindir}/supervisor*
%{_bindir}/echo_supervisord_conf
%{_bindir}/pidproxy

%config(noreplace) %{_sysconfdir}/supervisord.conf
%dir %{_sysconfdir}/supervisord.d
%config(noreplace) %{_sysconfdir}/logrotate.d/supervisor

%changelog
* Mon Aug 12 2013 Oscar Carballal Prego <ocarballal@yaco.es> - 3.0-1
- Updated to version 3.0 final

* Mon Aug 01 2011 Nils Philippsen <nils@redhat.com> - 3.0-0.5.a10
- require python-setuptools (#725191)

* Tue Apr 05 2011 Nils Philippsen <nils@redhat.com> - 3.0-0.4.a10
- version 3.0a10
- fix source URL
- don't use macros for system executables (except python)

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0-0.3.a8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 3.0-0.2.a8
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Tue Apr 13 2010 Nils Philippsen <nils@redhat.com> - 3.0-0.1.a8
- add BR: python-setuptools

* Mon Apr 12 2010 Nils Philippsen <nils@redhat.com>
- bundle updated config file

* Sat Apr 10 2010 Nils Philippsen <nils@redhat.com>
- version 3.0a8
- update URLs
- versionize python-meld3 dependency

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 2.1-6
- Rebuild for Python 2.6

* Sat Sep  6 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 2.1-5
- fix license tag

* Mon Jan 07 2008 Toshio Kuratomi <toshio@fedoraproject.org>  2.1-4
- Include egginfo files when python generates them.

* Sun Apr 22 2007 Mike McGrath <mmcgrath@redhat.com> 2.1-3
- Added BuildRequires of python-devel

* Fri Apr 20 2007 Mike McGrath <mmcgrath@redhat.com> 2.1-2
- Added patch suggested in #153225

* Fri Apr 20 2007 Mike McGrath <mmcgrath@redhat.com> 2.1-1
- Initial packaging

