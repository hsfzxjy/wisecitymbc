from django.db import connection
import logging

logger = logging.getLogger('default')

class SQLMiddleware(object):

    def process_response(self, request, response):
        url = request.META.get('PATH_INFO', '')
        for query in connection.queries:
            logger.warning('[%(url)s] [%(time)ss]\n[%(sql)s]\n' % {
                'url': url,
                'sql': query['sql'],
                'time': query['time']
            })
        return response            