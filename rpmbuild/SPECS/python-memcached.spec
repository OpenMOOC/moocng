%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-memcached
Version:        1.48
Release:        1%{?dist}
Summary:        A Python memcached client library

Group:          Development/Languages
License:        Python
URL:            http://www.tummy.com/Community/software/python-memcached/
Source0:        ftp://ftp.tummy.com/pub/python-memcached/old-releases/python-memcached-%{version}.tar.gz
Source1:        LICENSE
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel, python-setuptools

%description
This software is a 100% Python interface to the memcached memory cache
daemon.  It is the client side software which allows storing values in one
or more, possibly remote, memcached servers.  Search google for memcached
for more information.

%prep
%setup -q -n %{name}-%{version}
cp %{SOURCE1} .

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc ChangeLog README LICENSE
%attr(755,root,root) %{python_sitelib}/memcache.py
%{python_sitelib}/memcache.py[co]
%{python_sitelib}/python_memcached-%{version}-py*.egg-info/

%changelog
* Wed Jul 10 2013 Alejandro Blanco <ablanco@yaco.es> - 1.48-1
- Update to 1.48

* Tue Jul 20 2010 Radek Novacek <rnovacek@redhat.com> - 1.43-5.3
- Added text of the Python License
- Resolves: #615517

* Wed Jan 13 2010 Radek Novacek <rnovacek@redhat.com> - 1.43-5.2
- Fixed source url

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.43-5.1
- Rebuilt for RHEL 6

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.43-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.43-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.43-3
- Rebuild for Python 2.6

* Wed Sep  3 2008 Tom "spot" Callaway <tcallawa@redhat.com> 1.43-2
- add BR: python-setuptools

* Wed Sep  3 2008 Tom "spot" Callaway <tcallawa@redhat.com> 1.43-1
- fix license tag
- update to 1.43

* Tue Aug 14 2007 Sean Reifschneider <jafo@tummy.com> 1.39-1
- Update to 1.39 upstream release.

* Sat Aug 11 2007 Sean Reifschneider <jafo@tummy.com> 1.38-1
- Update to 1.38 upstream release.

* Sun Jun 10 2007 Sean Reifschneider <jafo@tummy.com> 1.36-3
- Changes based on feedback from Ruben Kerkhof:
- Fixing license.
- Removing PKG-INFO from doc.
- Fixing summary.
- Removing setuptools build dependency.
- Changing permissions of memcache module to

* Sat Jun 09 2007 Sean Reifschneider <jafo@tummy.com> 1.36-2
- Adding python-devel build requirement.

* Sat Jun 09 2007 Sean Reifschneider <jafo@tummy.com> 1.36-1
- Initial RPM spec file.
