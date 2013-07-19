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
# Remove MathJax if mathjax = 1. Intended for testing purposes.
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
# TODO celeryd is fixed to /var/www
mkdir -p %{buildroot}%{_sysconfdir}/init.d/
cp celeryd %{buildroot}%{_sysconfdir}/init.d/celeryd
mkdir -p %{buildroot}%{_sysconfdir}/%{platform}/%{component}/
ln -s %{component}/settings/local.py.example %{buildroot}%{_sysconfdir}/%{platform}/%{component}/local.py
mkdir -p %{buildroot}%{_localstatedir}/www/%{name}/{media,static}


%pre
if [ -z "$(/usr/bin/getent group %{name})" ]; then
    /usr/sbin/groupadd -r %{name}
    /usr/bin/gpasswd -a apache %{name}
fi


%postun
/usr/bin/gpasswd -d apache %{name}


#%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc CHANGES COPYING README manuals/
%attr(640,root,%{name}) %config(noreplace) %{_sysconfdir}/%{platform}/%{component}/*

%{python_sitelib}/%{component}/
%{python_sitelib}/%{component}*.egg-info
%{_sysconfdir}/init.d/celeryd


%changelog
* Thu Jul 19 2013 Oscar Carballal Prego <ocarballal@yaco.es> - 0.1.0-2
- Fixed paths, local.py file. Changed location of the config files. Added mathjax variable to
  avoid excessive compulation times when testing.

* Wed Jul 10 2013 Alejandro Blanco <ablanco@yaco.es> - 0.1.0-1
- Initial package
