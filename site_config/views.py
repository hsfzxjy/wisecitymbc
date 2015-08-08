import common

@common.render_to('index.html')
def index(request):
	return {}

@common.render_to('css_test.html')
def css_test(*args):
    return {}