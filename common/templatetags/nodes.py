from django import template 
from deepcopy import deepcopy

class PagerNode(template.Node):
    def __init__(self, id):
        self.id = id

    def render(self, context):
        t = template.loader.get_template('pager.html')
        context = deepcopy(context)
        context['id'] = self.id
        return t.render(template.Context(context), autoescape = context.autoescape)