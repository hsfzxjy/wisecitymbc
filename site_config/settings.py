from os import environ

debug = not environ.get("APP_NAME", "")

try:
    if debug:
        raise ImportError

    import sae.const 

    MYSQL_DB = sae.const.MYSQL_DB
    MYSQL_USER = sae.const.MYSQL_USER
    MYSQL_PASS = sae.const.MYSQL_PASS
    MYSQL_HOST_M = sae.const.MYSQL_HOST
    MYSQL_HOST_S = sae.const.MYSQL_HOST_S
    MYSQL_PORT = sae.const.MYSQL_PORT
except ImportError:
    MYSQL_DB = ''  # If not on SAE, complete this options.
    MYSQL_USER = ''  # If not on SAE, complete this options.
    MYSQL_PASS = ''  # If not on SAE, complete this options.
    MYSQL_HOST_M = ''  # If not on SAE, complete this options.
    MYSQL_HOST_S = ''  # If not on SAE, complete this options.
    MYSQL_PORT = ''  # If not on SAE, complete this options.

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': MYSQL_DB,
        'USER': MYSQL_USER,
        'PASSWORD': MYSQL_PASS,
        'HOST': MYSQL_HOST_M,
        'PORT': MYSQL_PORT,
    }
}

ALLOWED_HOSTS = ['*']

TIME_ZONE = 'Asia/Shanghai'

LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATIC_URL = '/static/' 
STATICFILES_DIRS = (
    'static/',
)

SECRET_KEY = 'k!i4u4q!d65qfj@z6wqvwm5h8km50btsc$%1%ol&3%))0&#ol='

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'site_config.context_processors.debug',
    'finance.context_processors.finance_processor',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'common.middlewares.SQLMiddleware'
)

ROOT_URLCONF = 'site_config.urls'

WSGI_APPLICATION = 'site_config.wsgi.application'

TEMPLATE_DIRS = (
    'templates/',
)

INSTALLED_APPS = (
    'django_admin_bootstrapped',
    'site_packages.bootstrap3',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'notices',
    'articles',
    'finance',
    'file_storage',
    'files',
    'api',
    'task_queues',
)
AUTH_USER_MODEL = 'accounts.User'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
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
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'default': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '', # Complete this option.
    }
}

PATH_DATETIME_FORMAT = '%Y_%m_%d_%H_%M_%S'

REST_FRAMEWORK = {

    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'limit',
    'MAX_PAGINATE_BY': 250,
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_PERMISSION_CLASSES': [],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend','rest_framework.filters.OrderingFilter'),
    'DATETIME_FORMAT': '%m-%d %H:%M:%S',
    'EXCEPTION_HANDLER': 'common.exceptions.handle_403_exception'
}

DAB_FIELD_RENDERER = 'django_admin_bootstrapped.renderers.BootstrapFieldRenderer'

# Options for Qiniu Storage, complete it.

QINIU = {
    'ACCESS_KEY': '',
    'SECRET_KEY': '',
    'domain_name': '',
    'bucket_name': '',
}