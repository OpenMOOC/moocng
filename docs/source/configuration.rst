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


Amazon S3 configuration
-----------------------

moocng use S3 to storage users uploaded files. You need an Amazon AWS account
and create a bucket to store the files.

The bucket must be configured with the next CORS configuration:

.. code-block:: xml

  <?xml version="1.0" encoding="UTF-8"?>
  <CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
      <CORSRule>
          <AllowedOrigin>*</AllowedOrigin>
          <AllowedMethod>PUT</AllowedMethod>
          <MaxAgeSeconds>3000</MaxAgeSeconds>
          <AllowedHeader>Content-Type</AllowedHeader>
          <AllowedHeader>x-amz-acl</AllowedHeader>
          <AllowedHeader>origin</AllowedHeader>
          <AllowedHeader>Accept</AllowedHeader>
          <AllowedHeader>Accept-Charset</AllowedHeader>
          <AllowedHeader>Accept-Encoding</AllowedHeader>
          <AllowedHeader>Accept-Language</AllowedHeader>
          <AllowedHeader>Access-Control-Request-Headers</AllowedHeader>
          <AllowedHeader>Access-Control-Request-Method</AllowedHeader>
          <AllowedHeader>Connection</AllowedHeader>
          <AllowedHeader>Host</AllowedHeader>
          <AllowedHeader>Origin</AllowedHeader>
          <AllowedHeader>Referer</AllowedHeader>
          <AllowedHeader>User-Agent</AllowedHeader>
      </CORSRule>
  </CORSConfiguration>

To improve the security in production environments you can define a more strict
AllowedOrigin setting in your CORS configuration.

And your settings must define your account data, your bucket and the expire
time of upload permissions.

.. code-block:: python

  AWS_ACCESS_KEY_ID = "your-access-key-id"
  AWS_SECRET_ACCESS_KEY = "your-secret-key-id"
  AWS_STORAGE_BUCKET_NAME = "your-bucket-name"
  AWS_S3_UPLOAD_EXPIRE_TIME = (60 * 5) # 5 minutes


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


SAML configuration
------------------

SAML require a cert. You can create your own self-signed certificates. For other purposes buy them:

  * Follow the first five steps of this guide: http://www.akadia.com/services/ssh_test_certificate.html
  * Create a directory called "saml2" at you moong folder
  * Create inside it a certs directory
  * Copy the 'attributemaps' of moocng inside the saml2
  * Copy server.key and server.crt to saml2/certs

.. code-block:: bash

  openssl genrsa -des3 -out server.key 2048
  openssl req -new -key server.key -out server.csr
  cp server.key server.key.org
  openssl rsa -in server.key.org -out server.key
  openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

In moocng, in the settings.py there is a SAML_CONFIG var. You must copy this
var in your local_settings and configure the params based in your environment.

moocng uses djangosaml2, to config it check the doc at `http://pypi.python.org/pypi/djangosaml2 <http://pypi.python.org/pypi/djangosaml2>`_

In order to connect openmooc with an IdP, you will need its metadata. Download
it and save as remote_metadata.xml (check the saml configuration to check that
the path and name match)

Now you need to add the SAML SP metadata to your IdP. First of all you need to
configure in the IdP the metarefresh issue. After that you can go to the idp
and call update entries, You can go to a url like this:
https://idp.example.com/simplesaml/module.php/metarefresh/fetch.php


Asset configuration
-------------------

Slot duration time of assets should always be multiple of the asset slot
granularity.

That slot granularity is set to five minutes by default. To use another value,
simply specify a different value (in minutes) in the ASSET_SLOT_GRANULARITY
property of the settings file.


Enabling required services
--------------------------

There are several services that need to be active in the server so it is
best to configure them to start on the server boot.

.. code-block:: bash

  $ chkconfig --add httpd
  $ chkconfig --add rabbitmq-server
  $ chkconfig --add postgresql
  $ chkconfig --add mongod
  $ chkconfig --add celeryd
  $ chkconfig postgresql on
  $ chkconfig httpd on
  $ chkconfig rabbitmq-server on
  $ chkconfig mongod on
  $ chkconfig celeryd on

Openbadges integration
----------------------

The badges used in the platform can be integrated with Mozilla OpenBadges system (http://openbadges.org/). Every time, a student gets a badge, an assertion (OBI compliant) is created.

You can configure the openbadges service to use, by default the official backpack OpenBadges service:

.. code-block:: python

  BADGES_SERVICE_URL = 'backpack.openbadges.org'

To generate the assertion, we use some functions attached to post_save signals:

.. code-block:: python

  save_identity_for_user()

Copies the actual user data to the assertion for future consistency.

.. code-block:: python

  create_identity_for_user()

As the assertion identity hash contains the email information, if the email changes, the identity should also change.

You must define your issuer info in the settings variables.

.. code-block:: python

  BADGES_SERVICE_URL = "backpack.openbadges.org"
  BADGES_ISSUER_NAME = "OpenMOOC"
  BADGES_ISSUER_URL = "http://openmooc.org"
  BADGES_ISSUER_DESCRIPTION = ""
  BADGES_ISSUER_IMAGE = ""
  BADGES_ISSUER_EMAIL = ""
