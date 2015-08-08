#encoding=utf8
from django.db import models
from file_storage.models import File

class SharedFileManager(models.Manager):

    def multi_create(self, uploader, files):
        files = File.objects.filter(pk__in = files)
        self.bulk_create(
            SharedFile(uploader = uploader, file = file) for file in files
        )

class SharedFile(models.Model):

    uploader = models.ForeignKey('accounts.User', verbose_name='上传者')
    file = models.ForeignKey('file_storage.File', verbose_name='文件名')

    objects = SharedFileManager()

    class Meta:
        permissions = (
            ('manage_file', '允许管理文件'),
        )
        verbose_name=verbose_name_plural='文件'

    def __unicode__(self):
        return self.file.file_name