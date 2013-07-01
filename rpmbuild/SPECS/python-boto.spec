%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
Summary:        A simple lightweight interface to Amazon Web Services
Name:           python-boto
Version:        2.5.2
Release:        3%{?dist}
License:        MIT
Group:          Development/Languages
URL:            https://github.com/boto/boto
Source:         http://pypi.python.org/packages/source/b/boto/boto-%{version}.tar.gz
BuildRequires:  python-devel >= 2.5, python-setuptools-devel
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# https://bugzilla.redhat.com/show_bug.cgi?id=838076
# Fixed with upstream commit 6870daf
Patch1:         python-boto-2.5.2-emptydata.patch
# https://github.com/boto/boto/issues/881
# Fixed with upstream commit a23c379
Patch2:         python-boto-2.5.2-statechg.patch

%description
Boto is a Python package that provides interfaces to Amazon Web Services.
It supports S3 (Simple Storage Service), SQS (Simple Queue Service) via
the REST API's provided by those services and EC2 (Elastic Compute Cloud)
via the Query API. The goal of boto is to provide a very simple, easy to
use, lightweight wrapper around the Amazon services.

%prep
%setup -q -n boto-%{version}
%patch1 -p1
%patch2 -p1

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_bindir}/asadmin
%{_bindir}/bundle_image
%{_bindir}/cfadmin
%{_bindir}/cq
%{_bindir}/cwutil
%{_bindir}/elbadmin
%{_bindir}/fetch_file
%{_bindir}/instance_events
%{_bindir}/kill_instance
%{_bindir}/launch_instance
%{_bindir}/list_instances
%{_bindir}/lss3
%{_bindir}/pyami_sendmail
%{_bindir}/route53
%{_bindir}/s3multiput
%{_bindir}/s3put
%{_bindir}/sdbadmin
%{_bindir}/taskadmin
%{python_sitelib}/*

%changelog
* Tue Jan  8 2013 Garrett Holmstrom <gholms@fedoraproject.org> - 2.5.2-3
- Fixed parsing of current/previous instance state data (boto #881)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul  6 2012 Garrett Holmstrom <gholms@fedoraproject.org> - 2.5.2-1
- Updated to 2.5.2
- Fixed failure when metadata is empty (#838076)

* Thu Jun 14 2012 Garrett Holmstrom <gholms@fedoraproject.org> - 2.5.1-1
- Updated to 2.5.1 (last-minute upstream bugfix)

* Wed Jun 13 2012 Garrett Holmstrom <gholms@fedoraproject.org> - 2.5.0-1
- Updated to 2.5.0 (#828912)

* Wed Mar 21 2012 Robert Scheck <robert@fedoraproject.org> 2.3.0-1
- Upgrade to 2.3.0 (#786301 #c10)

* Tue Mar 13 2012 Robert Scheck <robert@fedoraproject.org> 2.2.2-1
- Upgrade to 2.2.2 (#786301, thanks to Bobby Powers)

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Aug 15 2011 Robert Scheck <robert@fedoraproject.org> 2.0-1
- Upgrade to 2.0 (#723088)

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9b-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Jan 02 2011 Robert Scheck <robert@fedoraproject.org> 1.9b-6
- Added a patch for python 2.4 support (#656446, #661233)

* Thu Dec 02 2010 Lubomir Rintel <lubo.rintel@gooddata.com> 1.9b-5
- Apply a patch for python 2.7 support (#659248)

* Thu Nov 18 2010 Robert Scheck <robert@fedoraproject.org> 1.9b-4
- Added patch to fix parameter of build_list_params() (#647005)

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 1.9b-3
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Tue Feb 09 2010 Robert Scheck <robert@fedoraproject.org> 1.9b-2
- Backported upstream patch for image registration (#561216)

* Sat Jan 09 2010 Robert Scheck <robert@fedoraproject.org> 1.9b-1
- Upgrade to 1.9b

* Fri Jul 24 2009 Robert Scheck <robert@fedoraproject.org> 1.8d-1
- Upgrade to 1.8d (#513560)

* Wed Jun 03 2009 Luke Macken <lmacken@redhat.com> 1.7a-2
- Add python-setuptools-devel to our build requirements, for egg-info

* Thu Apr 16 2009 Robert Scheck <robert@fedoraproject.org> 1.7a-1
- Upgrade to 1.7a

* Mon Feb 23 2009 Robert Scheck <robert@fedoraproject.org> 1.5c-2
- Rebuild against rpm 4.6

* Sun Dec 07 2008 Robert Scheck <robert@fedoraproject.org> 1.5c-1
- Upgrade to 1.5c

* Fri Dec 05 2008 Jeremy Katz <katzj@redhat.com> 1.2a-2
- Rebuild for python 2.6

* Wed May 07 2008 Robert Scheck <robert@fedoraproject.org> 1.2a-1
- Upgrade to 1.2a

* Sat Feb 09 2008 Robert Scheck <robert@fedoraproject.org> 1.0a-1
- Upgrade to 1.0a

* Sat Dec 08 2007 Robert Scheck <robert@fedoraproject.org> 0.9d-1
- Upgrade to 0.9d

* Thu Aug 30 2007 Robert Scheck <robert@fedoraproject.org> 0.9b-1
- Upgrade to 0.9b
- Initial spec file for Fedora and Red Hat Enterprise Linux
