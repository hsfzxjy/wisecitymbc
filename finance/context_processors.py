from .models import get_finance_class
from .constants import finance_categories

def finance_processor(request):
    return {
        'finance_models': {
            model_name: get_finance_class(model_name)
            for model_name in finance_categories
        }
    }