import os
import django
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
STATIC_DOC_ROOT = '/media'
# Django settings for cc project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': SITE_ROOT + '/sq3.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'django_db',                      # Or path to database file if using sqlite3.
        'USER': 'django_login',                      # Not used with sqlite3.
        'PASSWORD': 'CalClassified3$BsQl',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = SITE_ROOT + '/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = SITE_ROOT + '/static_files/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    SITE_ROOT + '/static/',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '^tt79jl83l5jyasco(nkg+&7%fz#6gf+g&y7urk9g(!95nj1bi'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

import middleware

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'middleware.SubdomainsMiddleware', # this is for subdomain
)


ROOT_URLCONF = 'cc.urls'

TEMPLATE_DIRS = (
    SITE_ROOT + "/templates/",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django_facebook.context_processors.facebook',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.core.context_processors.media',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_facebook',
    'ccapp',
    'multiuploader',
    'sorl.thumbnail',
    'django.contrib.admin',
    'django_evolution',
    'haystack',
    'templated_email',
    'django_resized',
    'widget_tweaks'
    # 'django.contrib.admindocs',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'user_sessions',
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

MULTI_FILE_DELETE_URL = 'multi_delete'
MULTI_IMAGE_URL = 'images'
MULTI_IMAGES_FOLDER = 'images'

AUTHENTICATION_BACKENDS = (
    'django_facebook.auth_backends.FacebookBackend',
    #'django.contrib.auth.backends.ModelBackend',
    'ccapp.models.CaseInsensitiveModelBackend'
)

SERIALIZATION_MODULES = {
    'json': 'wadofstuff.django.serializers.json'
}

AUTH_PROFILE_MODULE = 'django_facebook.FacebookProfile'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'INFO',
        },
    }
}

DJANGORESIZED_DEFAULT_SIZE = [800, 600]

FACEBOOK_APP_ID = '171685159547122'
FACEBOOK_APP_SECRET = '1b87bf57984631d3830f64edd60ebfcf'
FACEBOOK_LOGIN_DEFAULT_REDIRECT = '/accounts/profile/'
FACEBOOK_STORE_FRIENDS = True
FACEBOOK_STORE_GROUPS = True

TEMPLATED_EMAIL_TEMPLATE_DIR = SITE_ROOT + '/templates/email/'
TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django'

# HANDLES SENDING EMAILS FROM DJANGO
# supposedly you have to at least log into the HOST_USER at least once normally
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'buynearme'
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST_USER = 'noreply@buynear.me'#'buynearme@gmail.com'

EMAIL_HOST_PASSWORD = 'CalClassified'
EMAIL_PORT = 587

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#from django.core.mail import send_mail      
#send_mail('Test', 'meow', 'noreply@buynear.me', ['seung.j@live.com']) 

"""#haystack 2.0.0
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}
"""

#haystack 1.27
HAYSTACK_SITECONF = 'ccapp.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(os.path.dirname(__file__), 'whoosh_index')

