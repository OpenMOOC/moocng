%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define platform openmooc
%define component moocng
%define version 0.1.0
%define release 1

Name: %{platform}-%{component}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
Source1: %{name}-moocng.py
Source2: %{name}-wsgi.py
Source3: %{name}-common.py
Source4: %{name}-celeryd
Source5: %{name}-saml_settings.py
Summary: Engine for MOOC applications (OpenMOOC core)

License: Apache Software License 2.0
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Rooter Analysis <info@rooter.es>
URL: https://github.com/OpenMOOC/moocng

BuildRequires: python-devel
BuildRequires: python-setuptools
BuildRequires: python-sphinx
BuildRequires: make
BuildRequires: postgresql-devel
BuildRequires: libjpeg-turbo-devel
BuildRequires: libpng-devel

Requires: openmooc-tastypie = 0.9.11

Requires: pymongo = 2.4.2
Requires: python-boto = 2.8.0
Requires: python-celery = 3.0.20
Requires: python-imaging = 1.1.6
Requires: python-memcached = 1.48
Requires: python-psycopg2 = 2.4.2
Requires: python-requests = 1.2.0
Requires: python-gunicorn = 0.14.6

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
Requires: openmooc-ffmpeg = 20120806
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


# Create a subpackage for the Mathjax static files, they take a loooong while to
# generate. Follow this guide if you feel lost: http://www.rpm.org/max-rpm/s1-rpm-subpack-spec-file-changes.html
# This will generate an openmooc-moocng-mathjax package
%package mathjax
Summary: Mathjax symbols for OpenMOOC Engine (moocng)
Requires: %{name} = %{version}-%{release}
%description mathjax
Static files needed in OpenMOOC Engine (moocng) for using Mathjax.
# end mathjax


%prep
%setup -q -n %{name}-%{version}


%build
# Build the moocng documentation
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
# Add custom celeryd to init
mkdir -p %{buildroot}%{_sysconfdir}/init.d/
cp %{SOURCE4} %{buildroot}%{_sysconfdir}/init.d/celeryd
# Create local configuration file
mkdir -p %{buildroot}%{_sysconfdir}/%{platform}/%{component}/moocngsettings/
mkdir -p %{buildroot}%{_sysconfdir}/%{platform}/%{component}/moocngsaml2/
cp -R %{component}/settings/* %{buildroot}%{_sysconfdir}/%{platform}/%{component}/moocngsettings/
# Copy a modified version of common.py and saml_settings
cp %{SOURCE3} %{buildroot}%{_sysconfdir}/%{platform}/%{component}/moocngsettings/
cp %{SOURCE5} %{buildroot}%{_sysconfdir}/%{platform}/%{component}/moocngsettings/
# Create the manage file and the WSGI file
mkdir -p %{buildroot}%{_bindir}/
mkdir -p %{buildroot}%{_libexecdir}/
cp %{SOURCE1} %{buildroot}%{_bindir}/moocngadmin
cp %{SOURCE2} %{buildroot}%{_libexecdir}/openmooc-moocng
# Create media and static dirs
mkdir -p %{buildroot}%{_localstatedir}/lib/%{platform}/%{component}/{media,static}


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
/usr/bin/gpasswd -d nginx %{name}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc CHANGES COPYING README manuals/
%attr(644,root,%{name}) %config(noreplace) %{_sysconfdir}/%{platform}/%{component}/moocngsettings/*

%{_sysconfdir}/init.d/celeryd
%attr(755,root, %{name}) %{_bindir}/moocngadmin
%attr(755,root, %{name}) %{_libexecdir}/openmooc-moocng

%{python_sitelib}/%{component}/api/
%{python_sitelib}/%{component}/assets/
%{python_sitelib}/%{component}/attributemaps/
%{python_sitelib}/%{component}/auth_handlers/
%{python_sitelib}/%{component}/badges/
%{python_sitelib}/%{component}/categories/
%{python_sitelib}/%{component}/contact/
%{python_sitelib}/%{component}/courses/
%{python_sitelib}/%{component}/enrollment/
%{python_sitelib}/%{component}/fixtures/
%{python_sitelib}/%{component}/formats/
%{python_sitelib}/%{component}/locale/
%{python_sitelib}/%{component}/media/
%{python_sitelib}/%{component}/media_contents/
%{python_sitelib}/%{component}/peerreview/
%{python_sitelib}/%{component}/portal/
%{python_sitelib}/%{component}/settings/
%{python_sitelib}/%{component}/teacheradmin/
%{python_sitelib}/%{component}/templates/
%{python_sitelib}/%{component}/videos/
%{python_sitelib}/%{component}/context_processors.py*
%{python_sitelib}/%{component}/decorators.py*
%{python_sitelib}/%{component}/forms.py*
%{python_sitelib}/%{component}/mongodb.py*
%{python_sitelib}/%{component}/urls.py*
%{python_sitelib}/%{component}/wsgi.py*

# We do this so we don't duplicate the validation of mathjax files
%{python_sitelib}/%{component}/static/crossdomain.xml
%{python_sitelib}/%{component}/static/favicon.ico
%{python_sitelib}/%{component}/static/humans.txt
%{python_sitelib}/%{component}/static/robots.txt
%{python_sitelib}/%{component}/static/css/
%{python_sitelib}/%{component}/static/img/
%{python_sitelib}/%{component}/static/js/teacheradmin/
%{python_sitelib}/%{component}/static/js/*.js
%{python_sitelib}/%{component}/static/js/libs/*.js
#%{python_sitelib}/%{component}/static/js/ajax.js
#%{python_sitelib}/%{component}/static/js/classroom-views.js
#%{python_sitelib}/%{component}/static/js/csrf-ajax.js
#%{python_sitelib}/%{component}/static/js/models.js
#%{python_sitelib}/%{component}/static/js/progress-view.js
#%{python_sitelib}/%{component}/static/js/question-editor.js
#%{python_sitelib}/%{component}/static/js/routes.js
#%{python_sitelib}/%{component}/static/js/unit-admin.js
#%{python_sitelib}/%{component}/static/js/libs/*.js
%{python_sitelib}/%{component}*.egg-info


%files mathjax
%defattr(-,root,root,-)
%{python_sitelib}/%{component}/static/js/libs/mathjax/

%changelog
* Mon Jul 29 2013 Oscar Carballal Prego <ocarballal@yaco.es> - 0.1.0-1
- Fixed paths, local.py file. Changed location of the config files. Added mathjax
  variable to avoid excessive compulation times when testing. Added mathjax subpackage

* Wed Jul 10 2013 Alejandro Blanco <ablanco@yaco.es> - 0.1.0-1
- Initial package
