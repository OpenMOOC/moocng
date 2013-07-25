%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define mathjax 0
%define platform openmooc
%define component moocng
%define version 0.1.0
%define release 2

Name: %{platform}-%{component}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
Summary: Engine for MOOC applications (OpenMOOC core)

License: Apache Software License 2.0
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Rooter <info@rooter.es>
URL: https://github.com/OpenMOOC/moocng

BuildRequires: python-devel
BuildRequires: python-setuptools
BuildRequires: python-sphinx
BuildRequires: make

Requires: openmooc-tastypie = 0.9.11

Requires: pymongo = 2.4.2
Requires: python-boto = 2.8.0
Requires: python-celery = 3.0.20
Requires: python-imaging = 1.1.6
Requires: python-memcached = 1.48
Requires: python-psycopg2 = 2.4.2
Requires: python-requests = 1.2.0

Requires: Django14 = 1.4.5
Requires: django-celery = 3.0.17
Requires: django-mathjax = 0.0.2
Requires: Django-south = 0.7.5
Requires: python-django-admin-sortable = 1.4.9
Requires: python-django-compressor = 1.2
Requires: python-django-grappelli = 2.4.5
Requires: python-djangosaml2 = 0.10.0
Requires: python-django-tinymce = 1.5.1b4

Requires: nginx = 1.0.15
Requires: python-gunicorn = 0.14.6
Requires: ffmpeg = 20120806
Requires: postgresql-server = 8.4.13
Requires: mongo-10gen-server = 2.4.5
Requires: rabbitmq-server = 2.6.1
Requires: memcached = 1.4.4


%description
OpenMOOC is an open source platform (Apache license 2.0) that implements a
fully open MOOC solution.

MoocNG is the engine that powers the OpenMOOC solution, is the central
component where the courses take place.

It's a Django and Backbone.js application.


%prep
%setup -q -n %{name}-%{version}


%build
# Remove MathJax if mathjax = 1. Intended for testing purposes (avoid excessive
# compilation times)
%if %{mathjax}
    rm -rf moocng/static/js/libs/mathjax/
%endif

# docs
cd docs
make html
mv build/html ../manuals
cd ..

# clean
rm -rf rpmbuild
rm -rf docs
rm -f .gitignore

# program
%{__python} setup.py build


%install
%{__python} setup.py install -O2 --skip-build --root %{buildroot}
# Add celeryd custom init
mkdir -p %{buildroot}%{_sysconfdir}/init.d/
cp celeryd %{buildroot}%{_sysconfdir}/init.d/celeryd
# Create local configuration file
mkdir -p %{buildroot}%{_sysconfdir}/%{platform}/%{component}/
cp -R %{component}/settings/* %{buildroot}%{_sysconfdir}/%{platform}/%{component}/
mv %{component}/settings/local.py.example %{buildroot}%{_sysconfdir}/%{platform}/%{component}/local.py
# Create the manage file and the WSGI file
mkdir -p %{buildroot}/%{bindir}/
mkdir -p %{buildroot}/%{_libexecdir}/
cp $RPM_SOURCE_DIR/moocng.py %{buildroot}/%{bindir}/moocng.py
cp $RPM_SOURCE_DIR/wsgi.py %{buildroot}/%{_libexecdir}/moocng_wsgi.py
# Create media and static dirs
mkdir -p %{buildroot}%{_localstatedir}/www/%{name}/{media,static}


%pre
# If the group openmooc-moocng doesn't exist, create it.
if ! /usr/bin/getent group %{name} > /dev/null 2>&1; then
    /usr/sbin/groupadd -r %{name}
fi

# If the nginx user is not on the group, add it.
if ! /usr/bin/groups nginx | /bin/grep %{name} > /dev/null 2>&1; then
    /usr/bin/gpasswd -a nginx %{name}
fi


%postun
/usr/bin/gpasswd -d apache %{name}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc CHANGES COPYING README manuals/
%attr(644,root,%{name}) %config(noreplace) %{_sysconfdir}/%{platform}/%{component}/*

%{python_sitelib}/%{component}/
%{python_sitelib}/%{component}*.egg-info
%{_sysconfdir}/init.d/celeryd
%{_sysconfdir}/openmooc/moocng/local.py
%{_sysconfdir}/openmooc/moocng/common.py
%{_sysconfdir}/openmooc/moocng/__init__.py
%{_sysconfdir}/openmooc/moocng/devel.py
%{_sysconfdir}/openmooc/moocng/saml_settings.py
/%{bindir}/moocng.py
/%{_libexecdir}/moocng_wsgi.py

%changelog
* Mon Jul 22 2013 Oscar Carballal Prego <ocarballal@yaco.es> - 0.1.0-2
- Fixed paths, local.py file. Changed location of the config files. Added mathjax variable to
  avoid excessive compulation times when testing.

* Wed Jul 10 2013 Alejandro Blanco <ablanco@yaco.es> - 0.1.0-1
- Initial package
