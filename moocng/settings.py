# Copyright 2012 Rooter Analysis S.L.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Django settings for moocng project.

import os
BASEDIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'moocng',                # Or path to database file if using sqlite3.
        'USER': 'moocng',                # Not used with sqlite3.
        'PASSWORD': 'moocng',            # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

MONGODB_URI = 'mongodb://localhost:27017/moocng'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

gettext = lambda s: s

LANGUAGES = (
    ('en', gettext('English')),
    ('es', gettext('Spanish')),
)

# the default value is 'django_language' but changing this
# to 'language' makes it easier to integrate with the IdP
LANGUAGE_COOKIE_NAME = 'language'

LOCALE_PATHS = (
    os.path.join(BASEDIR, 'locale'),
    )

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASEDIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASEDIR, 'collected_static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASEDIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'r$=%l$j4(#5a%$rd*g+q5o7!m3z&amp;b@z1+n*d!n2im-hf0n%730'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'moocng.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'moocng.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASEDIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'adminsortable',
    'djcelery',
    'gravatar',
    'tinymce',
    'tastypie',
    'compressor',
    'moocng.courses',
    'moocng.portal',
    'moocng.videos',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
#    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'moocng.context_processors.site',
    'moocng.context_processors.theme',
    'moocng.context_processors.idp_urls',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'djangosaml2.backends.Saml2Backend',
    )

FIXTURE_DIRS = (
    os.path.join(BASEDIR, 'fixtures', 'django.contrib.flatpages'),
)

TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'theme_advanced_toolbar_location': 'top',
    'theme_advanced_buttons1': 'bold,italic,underline,strikethrough,separator,undo,redo,separator,cleanup,separator,bullist,numlist',
    'theme_advanced_buttons2' : '',
    'theme_advanced_buttons3' : '',
    }


GOOGLE_ANALYTICS_CODE = ''

MOOCNG_THEME = {
#    'logo': u'',
#    'subtitle': u'',
#    'top_banner': u'',
#    'right_banner1': u'',
#    'right_banner2': u'',
#    'bootstrap_css': u'',
#    'moocng_css': u'',
    }

FFMPEG = '/usr/bin/ffmpeg'

# Celery settings
import djcelery
djcelery.setup_loader()

BROKER_URL = 'amqp://moocng:moocngpassword@localhost:5672/moocng'

REGISTRY_URL = 'https://localhost/simplesaml/module.php/userregistration/newUser.php'
PROFILE_URL = 'https://localhost/simplesaml/module.php/userregistration/reviewUser.php'
ASKBOT_URL_TEMPLATE = 'https://questions.example.com/%s/questions/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
LOGIN_URL = '/saml2/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/saml2/logout/'
LOGOUT_REDIRECT_URL = '/'

SAML_CREATE_UNKNOWN_USER = True
SAML_ATTRIBUTE_MAPPING = {
    'mail': ('username', 'email', ),
    'cn': ('first_name', ),
    'sn': ('last_name', ),
    }

import saml2

SAML_CONFIG = {
    # full path to the xmlsec1 binary programm
    'xmlsec_binary': '/usr/bin/xmlsec1',

    # your entity id, usually your subdomain plus the url to the metadata view
    'entityid': 'https://moocng.example.com/saml2/metadata/',

    # directory with attribute mapping
    'attribute_map_dir': os.path.join(BASEDIR, 'attributemaps'),

    # this block states what services we provide
    'service': {
        # we are just a lonely SP
        'sp' : {
            'name': 'PEER SP',
            'endpoints': {
                # url and binding to the assetion consumer service view
                # do not change the binding or service name
                'assertion_consumer_service': [
                    ('https://moocng.example.com/saml2/acs/', saml2.BINDING_HTTP_POST),
                    ],
                # url and binding to the single logout service view
                # do not change the binding or service name
                'single_logout_service': [
                    ('https://moocng.example.com/saml2/ls/', saml2.BINDING_HTTP_REDIRECT),
                    ],
                },

            # in this section the list of IdPs we talk to are defined
            'idp': {
                # we do not need a WAYF service since there is
                # only an IdP defined here. This IdP should be
                # present in our metadata

                # the keys of this dictionary are entity ids
                'https://idp.example.com/simplesaml/saml2/idp/metadata.php': {
                    'single_sign_on_service': {
                        saml2.BINDING_HTTP_REDIRECT: 'https://idp.example.com/simplesaml/saml2/idp/SSOService.php',
                        },
                    'single_logout_service': {
                        saml2.BINDING_HTTP_REDIRECT: 'https://idp.example.com/simplesaml/saml2/idp/SingleLogoutService.php',
                        },
                    },
                },
            },
        },

    # where the remote metadata is stored
    'metadata': {
        'local': [os.path.join(BASEDIR, 'remote_metadata.xml')],
        },

    # set to 1 to output debugging information
    'debug': 1,

    # certificate
    'key_file': os.path.join(BASEDIR, 'mycert.key'),  # private part
    'cert_file': os.path.join(BASEDIR, 'mycert.pem'),  # public part

    # own metadata settings
    'contact_person': [
        {'given_name': 'Sysadmin',
         'sur_name': '',
         'company': 'Example CO',
         'email_address': 'sysadmin@example.com',
         'contact_type': 'technical'},
        {'given_name': 'Boss',
         'sur_name': '',
         'company': 'Example CO',
         'email_address': 'admin@example.com',
         'contact_type': 'administrative'},
        ],
    # you can set multilanguage information here
    'organization': {
        'name': [('Example CO', 'es'), ('Example CO', 'en')],
        'display_name': [('Example', 'es'), ('Example', 'en')],
        'url': [('http://www.example.com', 'es'), ('http://www.example.com', 'en')],
        },
    }

try:
    from local_settings import *
except ImportError:
    pass
