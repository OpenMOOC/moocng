%define platform openmooc
%define component moocng
%define version 0.0dev
%define release 1

Name: %{platform}-%{component}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
Summary: Engine for MOOC applications (OpenMOOC core)

License: Apache Software License
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Rooter <info@rooter.es>
URL: https://github.com/OpenMOOC/moocng

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
Requires: Django-south = 0.7.5
Requires: python-django-admin-sortable = 1.4.9
Requires: python-django-compressor = 1.2
Requires: python-django-grappelli = 2.4.5
Requires: python-django-mathjax = 0.0.2
Requires: python-djangosaml2 = 0.10.0
Requires: python-django-tinymce = 1.5.1b4

# nginx EPEL
Requires: nginx = 1.0.15
# gunicorn EPEL
Requires: python-gunicorn = 0.14.6
# ffmpeg
Requires: ffmpeg = 20120806
# postgresql BASE
Requires: postgresql-server = 8.4.13
# mongodb 10GEN
Requires: mongo-10gen-server = 2.4.4
# rabbitmq EPEL
Requires: rabbitmq-server = 2.6.1
# memcached BASE
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
rm -rf rpmbuild
# TODO build docs instead of removing them
rm -rf docs
rm -f celeryd
rm -f .gitignore
%{__python} setup.py build


%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}


%files
%defattr(-,root,root,-)
%doc CHANGES COPYING README
%{python_sitelib}/%{component}/
%{python_sitelib}/%{component}*.egg-info
