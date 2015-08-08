import gevent.monkey
gevent.monkey.patch_all()

import sys
reload(sys)
sys.setdefaultencoding('gbk')
import os.path

os.environ['DJANGO_SETTINGS_MODULE'] = 'site_config.settings'
PATH = os.path.join(os.path.dirname(__file__))
sys.path.insert(0,os.path.join(PATH, 'site_config'))
sys.path.insert(0,os.path.join(PATH, 'site_packages'))


from site_packages import django 
sys.modules['django'] = django

import sae
from site_config import wsgi
application = sae.create_wsgi_app(wsgi.application)
import pylibmc
sys.modules['memcache'] = pylibmc