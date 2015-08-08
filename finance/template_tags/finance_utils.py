from django import template
from django.template.loader import render_to_string, TemplateDoesNotExist
from django.utils.importlib import import_module

from notices.models import Notice

register = template.Library()

@register.simple_tag(takes_context = True)
def finance_models(context):
    