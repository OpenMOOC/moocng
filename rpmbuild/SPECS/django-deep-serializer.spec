%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           django-deep-serializer
Version:        0.1.0
Release:        1%{?dist}
Summary:        Serialize/Deserialize an object and its relations through class definitions

Group:          Development/Languages
License:        LGPL 3
URL:            https://github.com/goinnn/%{name}
Source0:        https://pypi.python.org/packages/source/d/%{name}/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-devel, python-setuptools


%description
With django-deep-serializer you can serialize/deserialize
an object and its relations through class definitions

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc README.rst CHANGES.rst COPYING.LGPLv3
%{python_sitelib}/deep_serializer
%{python_sitelib}/django_deep_serializer-%{version}-py*.egg-info/

%changelog

* Wed Nov 06 2013 Pablo Martin <pmartin@yaco.es> - 0.1.0-1
- Initial package
