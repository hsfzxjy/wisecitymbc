# encoding=utf8
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from accounts.models import User, UserProfile

from notices.models import NoticeDispatcher
from notices.mixins import SendNoticeModelMixin

from bs4 import BeautifulSoup

__all__ = ['Status', 'Comment']

class Status(models.Model, SendNoticeModelMixin):

    ADMIN_STATUS_TYPE_CHOICES = (
        ('govern', u'政府'),
        ('media', u'媒体'),
    )
    
    STATUS_TYPE_MAP = {
        User.ADMIN: ADMIN_STATUS_TYPE_CHOICES,
        User.PLAYER: UserProfile.INDUSTRY_CHOICES
    }

    title        = models.CharField(max_length = 255, verbose_name = u'标题')
    body_text    = models.TextField(verbose_name=u'正文')
    summary      = models.TextField(default = '', blank = True,verbose_name=u'摘要')
    author       = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = 'statuses', verbose_name='作者')
    created_time = models.DateTimeField(auto_now_add = True, verbose_name=u'发布时间')
    view_times   = models.PositiveIntegerField(blank = True, default = 0)
    attachments  = models.ManyToManyField('file_storage.File',verbose_name='附件')

    category     = models.CharField(
        verbose_name = u'分类',
        choices    = User.CATEGORY_CHOICES,
        max_length = 20,
        blank      = True
    )
    status_type  = models.CharField(
        verbose_name = u'类型',
        choices    = ADMIN_STATUS_TYPE_CHOICES+UserProfile.INDUSTRY_CHOICES, 
        max_length = 20, 
        default    = UserProfile.EMPTY,
        blank      = True
    )

    @property
    def url(self):
        return reverse('status-detail', args = [self.id])

    def __unicode__(self):
        return u"《%s》" % self.title

    def incr_view_times(self):
        self.view_times += 1
        self.save()
        
    def save(self, *args, **kwargs):
        self.category = self.author.category 

        if self.author.category == User.PLAYER:
            self.status_type = self.author.profile.industry

        soup = BeautifulSoup(self.body_text, "html.parser")
        self.body_text = unicode(soup)
        self.summary = soup.get_text()[:400]+'...'

        super(Status, self).save(*args, **kwargs)

    def shorten(self):
        if len(self.body_text)<10:
            return self.body_text
        else:
            return u'%s...' % self.body_text[:10]
        
    class Meta:
        default_permissions = ()
        ordering = ('-id', '-view_times')
        verbose_name = verbose_name_plural = u'文章'
        
class Comment(models.Model, SendNoticeModelMixin):

    ACTION_MAP = {
        'delete': u'删除',
        'post': u'发布',
    }

    author           = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = 'comments', verbose_name='评论者')
    body_text        = models.TextField(verbose_name='内容')
    created_time     = models.DateTimeField(auto_now_add = True, verbose_name='时间')
    status           = models.ForeignKey(Status, related_name = 'comments', verbose_name='所属文章')
    
    @classmethod
    def generate_content(klass, related_object, *args, **kwargs):
        return related_object.shorten()

    @classmethod
    def generate_title(klass, action, related_object, *args, **kwargs):
        if action == 'post':
            template = u'%(author)s 在你的文章 《%(name)s》 中发表了评论'
        else:
            template = u'作者 %(action)s 了你在文章 《%(name)s》 中的评论'

        return template % {
            'action': klass.ACTION_MAP[action],
            'author': related_object.author.nickname,
            'name': related_object.status.title,
        }

    @classmethod
    def generate_url(klass, related_object, *args, **kwargs):
        return related_object.status.url

    @classmethod
    def generate_user(klass, related_object, action, *args, **kwargs):
        if action == 'post':
            user = related_object.status.author
        else:
            user = related_object.author

        return user

    def __unicode__(self):
        return self.shorten()
        
    def save(self, *args, **kwargs):
        super(Comment, self).save(*args, **kwargs)

        CommentNotice.send(action = 'post', related_object = self)

    def delete(self):
        CommentNotice.send(action = 'delete', related_object = self)
        super(Comment, self).delete()
        
    def shorten(self):
        if len(self.body_text)<100:
            return self.body_text
        else:
            return u'%s...' % self.body_text[:100]
            
    shorten.short_description = '摘要'

    class Meta:
        verbose_name = verbose_name_plural = '评论'
        default_permissions = ()
        ordering = ('-id',)

CommentNotice = NoticeDispatcher(Comment)
