%define platform openmooc
%define component moocng
%define version 0.0dev
%define release 1

Summary: Engine for MOOC applications (OpenMOOC core)
Name: %{platform}-%{component}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz

License: Apache Software License
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Rooter <info@rooter.es>
URL: https://github.com/OpenMOOC/moocng

#         'zipimportx==0.3.2', # Required for some operations during install
# TODO
#         'boto==2.8.0', EPEL
Requires: python-boto = 2.8.0
#         'celery==3.0.20', EPEL FIXME bad version in epel
Requires: python-celery = 2.2.8
#         'Django==1.4.5', EPEL
Requires: Django14 = 1.4.5
#         'django-admin-sortable==1.4.9',
# TODO
#         'django-celery==3.0.17', EPEL FIXME bad version in epel
Requires: django-celery = 3.0.17
#         'django-tinymce==1.5.1b2', EPEL
Requires: python-django-tinymce = 1.5.1b4
#         'django-tastypie==0.9.11-openmooc', TODO version
Requires: openmooc-tastypie
#         'South==0.7.6', EPEL
Requires: Django-south = 0.7.5
#         'psycopg2==2.4.2', BASE FIXME bad version in base
Requires: python-psycopg2 = 2.0.14
#         'pymongo==2.4.2', EPEL FIXME bad version in epel
Requires: pymongo = 2.1.1
#         'djangosaml2==0.9.2',
# TODO
#         'PIL>=1.1.7', BASE
Requires: python-imaging = 1.1.6
#         'django_compressor==1.1.2', EPEL
Requires: python-django-compressor = 1.2
#         'python-memcached==1.48', base
Requires: python-memcached = 1.43
#         'django-grappelli==2.4.4',
# TODO
#         'django-mathjax==0.0.1',
# TODO
#         'requests==1.2.0', EPEL FIXME bad version in epel
Requires: python-requests = 1.1.0
# nginx EPEL
Requires: nginx = 1.0.15
# gunicorn EPEL
Requires: python-gunicorn = 0.14.6
# ffmpeg
# TODO
# postgresql BASE
Requires: postgresql-server = 8.4.13
# mongodb 10GEN
Requires: mongo-10gen-server = 2.4.4
# rabbitmq EPEL
Requires: rabbitmq-server = 2.6.1
# memcached BASE
Requires: memcached = 1.4.4

%description
Askbot customizations for OpenMOOC
==================================

 * OpenMOOC theme
 * Specific Settings
 * SAML2 integration


%prep
%setup -n %{name}-%{version}

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
