from django.core.urlresolvers import reverse
from sae.taskqueue import add_task
from urllib import urlencode
from common.rest.tools import render_to_json
from random import randint

def trigger(queue_name, url_name, payload = {}, *args, **kwargs):

    if not isinstance(payload, (str, unicode)) and isinstance(payload, dict):
        payload = urlencode(payload)

    add_task(
        'chat'+str(randint(0,9)),
        reverse(url_name),
        payload,
        *args, 
        **kwargs
    )