Configuration
=============

In this section we will guide you through the options you need to configure
to setup your moocng instance.

Most of the settings go to a file called `local_settings.py` which is located
inside the moocng package. It is very important that you **never modify** the
`settings.py` file directly since it will be overriden when moocng is update
with a new version.

If you have followed the installation instructions, the local_settings.py file
should be located at `/var/www/moocng/lib/python2.7/site-packages/moocng-X.Y.Z-py2.7.egg/moocng/local_settings.py`

.. note::
  Bear in mind that the exact path may be different in your case, specially
  the Python and moocng version numbers. The path
  fragment :file:`moocng-X.Y.Z-py2.7` is ficticious and will be something like
  |full_release_name| in real life.


Database connection
-------------------

The first you should configure is the database connection settings. Actually
you probably have done that if you have followed the installation instructions
since this is required to create the database schema.

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


Rabbitmq connection
-------------------

Similar to the database connection settings, you need to configure
the message broker connection settings:

.. code-block:: python

 BROKER_URL = 'amqp://moocng:moocngpassword@localhost:5672/moocng'

Where the syntax of that url is `amqp://user:password@host:port/virtual_host`

FFmpeg location
---------------

It's required to configure the FFmpeg path in the moocng settings.
The default value is:

.. code-block:: python

  FFMPEG = '/usr/bin/ffmpeg'


Static root
-----------

In this step you will collect all necessary static resources needed by
moocng and put them in a single directory so you can serve them directly
through your web server increasing the efficiency of the whole system.

The STATIC_ROOT option is the absolute path where the static files will
be copied. It is recommended to be placed outside the moocng package.
The user who runs the Apache process will need read access to this directory.

.. code-block:: python

  STATIC_ROOT = '/var/www/moocng/static'

Once you have configured this option you should run the `collectstatic`
Django command to copy the static files to that destination:

.. code-block:: bash

  $ source /var/www/moocng/bin/activate
  $ django-admin.py collectstatic --settings=moocng.settings

 You have requested to collect static files at the destination
 location as specified in your settings file.

 This will overwrite existing files.
 Are you sure you want to do this?

 Type 'yes' to continue, or 'no' to cancel: yes

Media root
----------

In a similar fashion as the Static root, the media root is an
absolute path where the files uploaded by the moocng users will
be stored. It is also recommended to put this directory outside
the moocng package:

.. code-block:: python

  MEDIA_ROOT = '/var/www/moocng/media'

You should create this directory since you are going to change its
permissions when configuring the web server:

.. code-block:: bash

  $ mkdir /var/www/moocng/media


Secret key
----------

The secret key is a random string that Django uses in several places
like the CSRF attack protection. It is considered a security problem
if you don't change this value and leave it as the moocng default.

You can generate a random value with the following command:

.. code-block:: bash

  $ tr -c -d '0123456789abcdefghijklmnopqrstuvwxyz' </dev/urandom | dd bs=32 count=1 2>/dev/null;echo

And then set it in the SECRET_KEY option:

.. code-block:: python

  SECRET_KEY = 'qt6p480yug2t36on4ugpynp31tyveq39'


Google Analytics support
------------------------

This setting is optional and allows you to integrate your moocng with Google
Analytics so you can track who, when and how uses your site.

Just set the Google Analytics Code in this setting:

.. code-block:: python

  GOOGLE_ANALYTICS_CODE = 'XX-XXXX'


Theme
-----

TODO


Registry and profile URLs
-------------------------

moocng does not handle any user registration or user profile information.
It needs an external service for this. There are two options in the settings
to configure these urls:

.. code-block:: python

  REGISTRY_URL = 'https://idp.example.com/simplesaml/module.php/userregistration/newUser.php'
  PROFILE_URL = 'https://idp.example.com/simplesaml/module.php/userregistration/reviewUser.php'


Askbot URLs
-----------

moocng uses a instance of Askbot for each course so it needs these URLs to
display a link in the UI. The relevant setting is `ASKBOT_URL_TEMPLATE`:

.. code-block:: python

  ASKBOT_URL_TEMPLATE = 'https://questions.example.com/%s/questions/'

Where the fragment `%s` will be replaced by the name of the course.


Web server configuration
------------------------

The recommended way to serve a moocng site is with a real web server that
supports the WSGI (Web Server Gateway Interface) protocol. This is no
surprise since the same applies to Django.

If you use the Apache web server all you need to do is write the
following configuration into your specific virtual host section:

.. code-block:: none

  NameVirtualHost *:80

  <VirtualHost *:80>
    ServerName moocng.example.com
    DocumentRoot /var/www/moocng/static/

    SetEnv VIRTUALENV /var/www/moocng

    WSGIScriptAlias / /var/www/moocng/lib/python2.7/site-packages/moocng-X.Y.Z-py2.7.egg/moocng/wsgi.py
    Alias /static/ /var/www/moocng/static/
    Alias /media/ /var/www/moocng/media/
  </VirtualHost>

.. note::
  Bear in mind that the exact path may be different in your case, specially
  the Python and moocng version numbers. The path
  fragment :file:`moocng-X.Y.Z-py2.7` is ficticious and will be something like
  |full_release_name| in real life.

Finally, you need to make sure that the user that the Apache run as has write
access to the media directory and read access to the static directory of your
moocng site.

.. code-block:: bash

  # Fedora example:
  $ chown apache:apache /var/www/moocng/media
  $ chown apache:apache /var/www/moocng/static

  # Debian/Ubuntu example:
  $ chown www-data:www-data /var/www/moocng/media
  $ chown www-data:www-data /var/www/moocng/static


Default site
------------

TODO


Enabling required services
--------------------------

There are several services that need to be active in the server so it is
best to configure them to start on the server boot.

.. code-block:: bash

  $ chkconfig --add httpd
  $ chkconfig --add rabbitmq-server
  $ chkconfig --add postgresql
  $ chkconfig --add mongodb
  $ chkconfig --add celeryd
  $ chkconfig postgresql on
  $ chkconfig httpd on
  $ chkconfig rabbitmq-server on
  $ chkconfig mongodb on
  $ chkconfig celeryd on
