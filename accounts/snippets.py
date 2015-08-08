from .models import User, UserProfile

_first_arg = lambda x: x[0]
_or_reg    = lambda _list: '|'.join(map(_first_arg, _list))

REG_USER_ID = r'(?P<user_id>\d+|me)'
REG_CATEGORY = r'(?P<category>{0})'.format(_or_reg(User.CATEGORY_CHOICES))
REG_INDUSTRY = r'(?P<industry>{0})'.format(_or_reg(UserProfile.INDUSTRY_CHOICES))