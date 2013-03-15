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

FFMPEG_DEBUG = DEBUG

ADMINS = (
    ('Admin', 'admin@eopenmooc.org'),
)

MANAGERS = ADMINS

EMAIL_SUBJECT_PREFIX = '[OpenMOOC] | '

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

# Tastypie resource limit per page, 0 means unlimited
API_LIMIT_PER_PAGE = 0

#SMTP server
EMAIL_HOST = 'idp.openmooc.org'
SERVER_EMAIL = 'idp.openmooc.org'
DEFAULT_FROM_EMAIL = 'info@openmooc.org'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

EMAIL_SUBJECT_PREFIX = '[OpenMOOC] | '

# Amazon credentials
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_STORAGE_BUCKET_NAME = ""
AWS_S3_UPLOAD_EXPIRE_TIME = (60 * 5) # 5 minutes

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

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

# Use custom formats
FORMAT_MODULE_PATH = 'moocng.formats'

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
    'moocng.contact',
    'moocng.badges',  # this must be defined before moocng.courses
    'moocng.courses',
    'moocng.portal',
    'moocng.videos',
    'moocng.teacheradmin',
    'moocng.enrollment',
    'moocng.api',
    'moocng.categories',
    'moocng.peerreview',
    'djangosaml2',
    'south',
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
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'moocng.videos.download': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'moocng.videos.tasks': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'moocng.courses.admin': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
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
    'moocng.context_processors.extra_settings',
    'moocng.context_processors.idp_urls',
    'moocng.context_processors.google_analytics',
    'moocng.context_processors.certificate_url',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'moocng.courses.backends.Saml2BackendExtension',
)

FIXTURE_DIRS = (
    os.path.join(BASEDIR, 'fixtures', 'django.contrib.flatpages'),
    os.path.join(BASEDIR, 'fixtures', 'django.contrib.auth'),
)

TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'theme_advanced_toolbar_location': 'top',
    'theme_advanced_buttons1': 'bold,italic,underline,strikethrough,separator,link,unlink,separator,undo,redo,copy,paste,separator,cleanup,separator,bullist,numlist',
    'theme_advanced_buttons2' : '',
    'theme_advanced_buttons3' : '',
    }


GOOGLE_ANALYTICS_CODE = ''

GRAVATAR_URL_PREFIX = '//www.gravatar.com/'

MOOCNG_THEME = {
#    'logo': u'',
#    'subtitle': u'',
#    'top_banner': u'',
#    'right_banner1': u'',
#    'right_banner2': u'',
#    'bootstrap_css': u'',
#    'moocng_css': u'',
#    'cert_banner': u'',
    }


ENABLED_COMUNICATIONS = (
    'feedback',
    'incidence',
    'rights',
    'unsubscribe',
    'others'
)


#SHOW_TOS = True

FFMPEG = '/usr/bin/ffmpeg'

# Let authenticated users create their own courses
ALLOW_PUBLIC_COURSE_CREATION = False

# Make this unique, and don't share it with anybody else than payment system
# Override this in local settings
USER_API_KEY = '123456789'

# A list with the slugs of the courses that use the old qualification system
# where the normal units counted
COURSES_USING_OLD_TRANSCRIPT = []

# Enrollment methods
ENROLLMENT_METHODS = (
    'moocng.enrollment.methods.FreeEnrollment',
    )


# Celery settings
import djcelery
djcelery.setup_loader()

BROKER_URL = 'amqp://moocng:moocngpassword@localhost:5672/moocng'

REGISTRY_URL = 'https://idp.openmooc.org/simplesaml/module.php/userregistration/newUser.php'
PROFILE_URL = 'https://idp.openmooc.org/simplesaml/module.php/userregistration/reviewUser.php'
CHANGEPW_URL = 'https://idp.openmooc.org/simplesaml/module.php/userregistration/changePassword.php'
ASKBOT_URL_TEMPLATE = 'https://questions.example.com/%s/'

CERTIFICATE_URL = 'http://example.com/idcourse/%(courseid)s/email/%(email)s'  # Example, to be overwritten in local settings

MASSIVE_EMAIL_BATCH_SIZE = 30

PEER_REVIEW_TEXT_MAX_SIZE = 5000  # in chars
PEER_REVIEW_FILE_MAX_SIZE = 5  # in MB
PEER_REVIEW_ASSIGNATION_EXPIRE = 24  # in hours

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
    'eduPersonAffiliation': ('groups', ),
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
            'name': 'Moocng SP',
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
