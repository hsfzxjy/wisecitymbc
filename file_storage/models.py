#encoding=utf8
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage

import os

class ListField(models.TextField):

    SEPERATOR = '\n\b'
    __metaclass__ = models.SubfieldBase

    def get_prep_value(self, value):
        if not isinstance(value, basestring):
            return self.SEPERATOR.join(value or [])

        return value

    def to_python(self, value):
        if not isinstance(value, basestring):
            return value

        return value.split(self.SEPERATOR)

class File(models.Model):
    
    created_time = models.DateTimeField(auto_now_add = True, db_index=True)
    name = models.CharField(max_length=255, null = True, blank = True)
    sections = ListField(null = True, blank = True)
    content_type = models.CharField(max_length=255,default='', null = True, blank = True)
    upload_type = models.CharField(max_length = 30, choices = (
            ('qiniu', 'QINIU'),
            ('normal', 'normal'),
        ),
    blank=True, default = 'qiniu')

    @property 
    def file_name(self):
        from os import path
        return path.basename(self.name)

    @property
    def url(self):
        if self.upload_type == 'qiniu':
            from qiniu_utils import encode_url
            return encode_url(self.name)
        else:
            return reverse('file.download', args = [self.id])

    def delete(self, *args, **kwargs):
        if self.upload_type == 'normal':
            for file in self.sections:
                default_storage.delete(file)
        elif self.upload_type == 'qiniu':
            from qiniu_utils import bucket

            bucket.delete('hfmun', self.name)

        super(File, self).delete(*args, **kwargs)
    
    def __unicode__(self):
        return self.file_name
    
    class Meta:
        ordering = ['-created_time']
        default_permissions = ()
        verbose_name=verbose_name_plural='文件'