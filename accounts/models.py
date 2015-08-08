#encoding=utf8

from django.core import validators
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import models
from django.core.urlresolvers import reverse

class UserManager(BaseUserManager):

    def _create_user(self, username, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        user = self.model(username=username,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        return self._create_user(username, password, False, False,
                                 **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        return self._create_user(username, password, True, True,
                                 **extra_fields)

class UserProfile(models.Model):

    ESTATE = 'estate'
    IT     = 'it'
    DEVICE = 'device'
    CAR    = 'car'
    BANK   = 'bank'
    MEDIA  = 'media'
    EMPTY  = 'empty'

    INDUSTRY_CHOICES = (
        (ESTATE, u'房地产'),
        (IT, u'IT'),
        (DEVICE, u'电器'),
        (CAR, u'汽车'),
        (BANK, u'银行'),
        (MEDIA, u'媒体'),
        (EMPTY, u'其他'),
    )

    user = models.OneToOneField('accounts.User', related_name="_profile")
    description = models.TextField(u'简介', blank = True)
    contact = models.CharField(u'联系方式', max_length=30, blank=True)
    location = models.CharField(u'位置', max_length=255,blank=True)
    remark = models.TextField(u'备注',blank=True)
    industry = models.CharField(u'行业', max_length=20, choices=INDUSTRY_CHOICES, default = EMPTY)

    class Meta:
        verbose_name=verbose_name_plural=u'附加信息（可选）'

    display_fields = ['description', 'contact', 'location', 'remark']

    def data(self):
        meta = self._meta
        return [
            (meta.get_field_by_name(name)[0].verbose_name, getattr(self, name),)
            for name in self.display_fields
        ]

class User(AbstractBaseUser, PermissionsMixin):

    ADMIN = 'admin'
    PLAYER = 'player'

    CATEGORY_CHOICES = (
        (ADMIN, ADMIN),
        (PLAYER, PLAYER),
    )    

    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$', _('Enter a valid username.'), 'invalid')
        ])

    nickname = models.CharField('昵称',
        max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer.'),
        )
    is_staff = models.BooleanField(_('staff status'), default=True,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleteing accounts.'))
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default=ADMIN)
    
    USERNAME_FIELD = 'username'
    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering=('-id',)

    def __unicode__(self):
        return self.nickname

    def get_full_name(self):
        return self.nickname

    def get_short_name(self):
        return self.nickname

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.category = self.ADMIN
            super(User, self).save(*args, **kwargs)
        else:
            self.category = self.PLAYER
            super(User, self).save(*args, **kwargs)
            if not self.profile:
                self.profile = UserProfile.objects.create(user = self)

    @property
    def profile(self):
        try:
            return self._profile
        except:
            return None

    @profile.setter
    def profile(self, _profile):
        self._profile = _profile
    

    @property 
    def admin_url(self):
        if self.is_superuser:
            return '/accounts/admin/'
        else:
            return '/admin/'

    @property 
    def unique_id(self):
        return 'user{0}'.format(self.id)

    @property 
    def a_tag(self):
        return u'<a href="{0}" target="_blank" class="user-name">{1}</a>'.format(
            self.url,
            self.nickname
        )

    @property 
    def url(self):
        return reverse('user-info', args = [self.id])
