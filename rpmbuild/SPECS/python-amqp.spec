%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define component amqp

Name:           python-%{component}
Version:        1.0.13
Release:        1%{?dist}
Summary:        This is a fork of amqplib, used by kombu when librabbitmq is not available.

Group:          Development/Languages
License:        Python
URL:            http://pypi.python.org/pypi/%{component}/
Source0:        https://github.com/celery/py-%{component}/archive/v%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-devel, python-setuptools

%description
This is a fork of amqplib which was originally written by Barry Pederson. It is
maintained by the Celery project, and used by kombu as a pure python
alternative when librabbitmq is not available.

This library should be API compatible with librabbitmq.

%prep
%setup -q -n py-%{component}-%{version}

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc Changelog README.rst LICENSE AUTHORS
%attr(755,root,root) %{python_sitelib}/memcache.py
%{python_sitelib}/python_memcached-%{version}-py*.egg-info/

%changelog

* Thu Oct 03 2013 Alejandro Blanco <ablanco@yaco.es> - 1.0.13-1
- Initial package
