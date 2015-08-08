from django.conf import settings

ACCESS_KEY = settings.QINIU.get('ACCESS_KEY','')
SECRET_KEY = settings.QINIU.get('SECRET_KEY', '')
domain_name = settings.QINIU.get('domain_name', '')

from qiniu import Auth, BucketManager
from urllib import quote

auth = Auth(ACCESS_KEY, SECRET_KEY)
bucket = BucketManager(auth)

def encode_url(key):
    return '{0}{1}'.format(domain_name, quote(key.encode('utf8')))

__all__ = ['auth', 'bucket', 'encode_url']