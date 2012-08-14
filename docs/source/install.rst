Installation
============

After these steps you should have a moocng instance up and running but
please note that many configuration defaults may not be good for your
installation. It is recommended to read the :doc:`configuration` chapter
right after this one.


Prerequisites
-------------

The minimum version of Python needed to run moocng is 2.7.

In the process of installing moocng, both in the standard installation and
the development installation, it is necessary that some libraries already
exist on your system. It is also needed the baseic compiler chaintool and
the development version of those libraries since the installation process
compiles a couple of Python modules.

.. code-block:: bash

  # CentOS/Fedora example:
  $ yum install python-devel postgresql-devel libjpeg-turbo-devel libpng-devel
  $ yum groupinstall "Development Tools"

  # Debian/Ubuntu example:
  $ apt-get install build-essential python-dev libpq-dev libjpeg-turbo8-dev libpng12-dev


Creating a virtualenv
---------------------

When installing a python application from the source you may put it in your
system python site-packages directory running the standard
*python setup.py install* dance but that is not recommended since it will
pollute your system Python and make upgrades unnecessarily difficult. If
the python application have some dependencies, as the moocng application has,
things will become worse since you may have conflicts between the
dependencies versions needed by the application and the versions installed
on your system and needed by other applications.

.. note::
  You should always install software using your Linux distribution packages.
  Python applications are not a exception to this rule. This documentation
  assumes that there is no moocng package yet in your Linux distribution or
  it is very out of date.

For all these reasons it is highly recommended to install the moocng
application (any as a general rule, any Python application) in its own
isolated environment. To do so there are a number of tools available. We
will use *virtualenv* since it is a very popular one.

So first we will install virtualenv:

.. code-block:: bash

  # Fedora example:
  $ yum install python-virtualenv

  # Debian/Ubuntu example:
  $ apt-get install python-virtualenv

In CentOS/RedHat 6 there is no virtualenv package available but we can
install it with the easy_install command, available in the setuptools
package:

.. code-block:: bash

  # CentOS example:
  $ yum install python-setuptools
  $ easy_install virtualenv

Check your distribution documentation if you do not use neither Fedora nor
Ubuntu nor CentOS.

Now a new command called *virtualenv* is available on your system and we
will use it to create a new virtual environment where we will install moocng.

.. code-block:: bash

  $ virtualenv /var/www/moocng --no-site-packages

The *--no-site-packages* option tells virtualenv to not depend on any system
package. For example, even if you already have Django installed on your
system it will install another copy inside this virtualenv. This improves
the reliability by making sure you have the same versions of the
dependencies that the developers have tested.

.. note::
  We are using the system python and not a custom compiled one, which would
  improve the system isolation, because we are going to deploy the
  application with Apache and mod_wsgi and they depend on the system python.

Installing moocng and its dependencies
--------------------------------------

In this step the moocng software and all its depenencies will get installed
into the virtualenv that was just created in the previous step.

We first need to activate the virtualenv:

.. code-block:: bash

  $ source /var/www/moocng/bin/activate

This will change the *PATH* and some other environment variables so this
will take precedence over your regular system python.

Now we can install the moocng software:

.. code-block:: bash

  $ easy_install moocng

After a while you will have a bunch of new packages inside
*/var/www/moocng/lib/python2.7/site-packages/*

FFmpeg
~~~~~~

FFmpeg is an extra dependence of moocng, and we'll install it through system
package system. FFmpeg is used to extract the last frame from YouTube's videos.

The FFmpeg version to install must have *webm* and *mp4* support. We recommend
0.11.X version, but it should work with a 0.7.X version or newer. 0.6.X are no
longer mantained by FFmpeg team and its use is discouraged.

.. code-block:: bash

  # Fedora example (requires an extra repository):
  $ rpm -Uvh http://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-stable.noarch.rpm http://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-stable.noarch.rpm
  $ yum install ffmpeg

  # Debian/Ubuntu example:
  $ apt-get install ffmpeg

In CentOS/Redhat 6 there are no easy packages for FFmpeg so in this platform it
is recommended to use a statically compiled ffmpeg binary. You can find an
example of it at http://dl.dropbox.com/u/24633983/ffmpeg/index.html


Creating the database
---------------------

The moocng application uses two types of storage:

- A non relational database to store user interactions. Right now only MongoDB
  is supported.
- A relational database to store courses and users.

Being a Django project, the moocng application support several different types
of SQL databases such as Postgresql, Mysql, Sqlite, Oracle, etc.

In this documentation we will cover the installation with a Postgresql
database because it is the RDMS we recommend. Check the
`Django documentation`_ to learn how to configure other database backends.

.. _`Django documentation`: http://docs.djangoproject.com/

The first step is to install database server. It is recommended to use the
packages for your Linux distribution:

.. code-block:: bash

  # Fedora example:
  $ yum install postgresql postgresql-server postgresql-libs

  # Debian/Ubuntu example:
  $ apt-get install postgresql postgresql-client

Check your distribution documentation if you do not use neither Fedora nor
Ubuntu.

Now a database user and the database itself must be created. The easiest way
to do this is to login as the postgres system user and creating the user
with that account:

.. code-block:: bash

  $ su - postgres
  $ createuser moocng --no-createrole --no-createdb --no-superuser -P
  Enter password for new role: *****
  Enter it again: *****
  $ createdb -E UTF8 --owner=moocng moocng

With the previous commands we have created a database called *moocng* and a
user, which owns the database, called also *moocng*. When creating the user
the createuser command ask for a password. You should remember this password
in a later stage of the installation/configuration process.

Now we need to configure Postgresql to accept database connections from the
*moocng* user into the *moocng* database. To do so, we need to add the
following directive in the pg_hba.conf file:

.. code-block:: bash

  # TYPE   DATABASE    USER       CIDR-ADDRESS        METHOD
  local    moocng      moocng                         md5

And restart the Postgresql server to reload its configuration:

.. code-block:: bash

  $ service postgresql restart

.. note::
  The location of the pg_hba.conf file depends on your Linux distribution. On
  Fedora it is located at /var/lib/pgsql/data/pg_hba.conf but in Ubuntu it is
  located at /etc/postgresql/8.1/main/pg_hba.conf being 8.1 the version of
  Postgresql you have installed.

To check that everything is correct you should try to connect to the *moocng*
database using the *moocng* user and the password you assigned to it:

.. code-block:: bash

  $ psql -U moocng -W moocng
  Password for user moocng:
  psql (9.0.4)
  Type "help" for help.

  moocng=#

.. note::
  We have deliberately keep this postgresql installation super simple since
  we want to focus in the moocng software. If you are serious about puting
  this into production you may consider checking other Postgresql
  configuration settings to improve its performance and security.

TODO: MongoDB installation

Creating the database schema
----------------------------

Now we have to create the database tables needed by moocng but before we need
to configure it to tell the database parameters needed to connect to the
database. This will be described with more deails in the :doc:`configuration`
chapter.

Add the following information into the
*/var/www/moocng/lib/python2.7/site-packages/moocng-X.Y.Z-py2.7.egg/moocng/local_settings.py* file:

.. code-block:: python

 DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.postgresql_psycopg2',
         'NAME': 'moocng',
         'USER': 'moocng',
         'PASSWORD': 'secret',
         'HOST': '',
         'PORT': '',
     }
 }

Fill this dictionary with the appropiate values for your database
installation, as performed in the previous step.

.. note::
  The location of the *local_settings.py* file depends on the moocng version
  that you have. The path fragment :file:`moocng-X.Y.Z-py2.7` is ficticious and
  will be something like |full_release_name| in real life.

Then, activate the virtualenv:

.. code-block:: bash

  $ source /var/www/moocng/bin/activate

And run the Django syncdb command to create the database schema:

.. code-block:: bash

  $ django-admin.py syncdb --settings=moocng.settings --migrate

.. note::
  The syncdb Django command will ask you if you want to create an admin
  user. You should answer yes to that question and write this admin's
  username and password down. You will need them later. This administrator's
  name should be `admin` because there are fixtures that depends on this
  name. You can create more administrators in the future with other names.


Installing the message broker
-----------------------------

moocng uses a message queu to process the videos. You can use several
different message broker for handling the message queue but RabbitMQ is
the recommended option because it is easy to setup and has very good
performance.

So, first we need to install the RabbitMQ packages for your operating
system:

.. code-block:: bash

  # Fedora example:
  $ yum install rabbitmq-server

  # Debian/Ubuntu example:
  $ apt-get install rabbitmq-server

  # CentOS/RedHat example:
  $ cd /root
  $ wget http://ftp.cica.es/epel/6/x86_64/epel-release-6-7.noarch.rpm
  $ rpm -Uvh epel-release-6-7.noarch.rpm
  $ yum install erlang
  $ yum install rabbitmq-server

A RabbitMQ user and a virtual host need to be created. Then the user
needs to have permissions to access to that virtual host:

.. code-block:: bash

  $ service rabbitmq-server start
  $ rabbitmqctl add_user moocng moocngpassword
  $ rabbitmqctl add_vhost moocng
  $ rabbitmqctl set_permissions -p moocng moocng ".*" ".*" ".*"

Collecting static files
-----------------------

TODO: this should go to the configuration chapter as it depends on
a settings option

In this step you will collect all necessary static resources needed by
moocng and put them in a single directory so you can serve them directly
through your web server increasing the efficiency of the whole system.

The nice thing is that you don't have to do this manually. There is a
Django command just for that:

.. code-block:: bash

  $ django-admin.py collectstatic --settings=moocng.settings

 You have requested to collect static files at the destination
 location as specified in your settings file.

 This will overwrite existing files.
 Are you sure you want to do this?

 Type 'yes' to continue, or 'no' to cancel: yes


Installing the web server
-------------------------

The packages needed for installing Apache and wsgi support are:

.. code-block:: bash

  # Fedora example:
  $ yum install httpd mod_wsgi

  # Debian/Ubuntu example:
  $ apt-get install apache2 libapache2-mod-wsgi

.. note::
  If you use someting different from Apache, please check the documentation
  of your web server about how to integrate it with a WSGI application.


Development Installation
------------------------

The development installation is very similar to the standard installation. The
only difference is that instead of installing moocng with easy_install you
clone the git repository and then install it manually.

So, first you clone the repository:

.. code-block:: bash

  $ cd /var/www/moocng
  $ git clone git://github.com/OpenMOOC/moocng.git

Then you activate the virtualenv if you have not already done so:

.. code-block:: bash

  $ source /var/www/moocng/bin/activate

Finally, you install the moocng package in development mode:

.. code-block:: bash

  $ cd /var/www/moocng/moocng
  $ python setup.py develop
