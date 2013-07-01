%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%endif

Name:           python-celery
Version:        2.2.8
Release:        1%{?dist}
Summary:        Distributed Task Queue

Group:          Development/Languages
License:        BSD
URL:            http://celeryproject.org
Source0:        http://pypi.python.org/packages/source/c/celery/celery-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  python-setuptools
Requires:       python-anyjson
Requires:       python-dateutil
Requires:       python-kombu
Requires:       pyparsing
%if ! (0%{?fedora} > 13 || 0%{?rhel} > 6)
Requires:       python-importlib
%endif
%if ! (0%{?fedora} > 13 || 0%{?rhel} > 5)
Requires:       python-multiprocessing
Requires:       python-uuid
%endif

%description
An open source asynchronous task queue/job queue based on
distributed message passing. It is focused on real-time
operation, but supports scheduling as well.

The execution units, called tasks, are executed concurrently
on one or more worker nodes using multiprocessing, Eventlet
or gevent. Tasks can execute asynchronously (in the background)
or synchronously (wait until ready).

Celery is used in production systems to process millions of
tasks a day.

Celery is written in Python, but the protocol can be implemented
in any language. It can also operate with other languages using
webhooks.

The recommended message broker is RabbitMQ, but limited support
for Redis, Beanstalk, MongoDB, CouchDB and databases
(using SQLAlchemy or the Django ORM) is also available.

%prep
%setup -q -n celery-%{version}
for script in celery/bin/camqadm.py celery/bin/celerybeat.py celery/bin/celeryd.py; do
  %{__sed} -i.orig -e 1d ${script}
  touch -r ${script}.orig ${script}
  %{__rm} ${script}.orig
  chmod a-x ${script} 
done
rm -f docs/.static/.keep

%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc AUTHORS LICENSE README THANKS TODO docs examples
%{python_sitelib}/*
%{_bindir}/*


%changelog
* Mon Nov 28 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 2.2.8-1
- Security FIX CELERYSA-0001

* Fri Jul 15 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 2.2.7-3
- Fix rpmlint errors
- Fix dependencies

* Sat Jun 25 2011 Andrew Colin Kissa <andrew@topdog.za.net> 2.2.7-2
- Update for RHEL6

* Tue Jun 21 2011 Andrew Colin Kissa <andrew@topdog.za.net> 2.2.7-1
- Initial package
