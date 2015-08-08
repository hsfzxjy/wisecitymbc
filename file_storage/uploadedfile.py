import os
from io import BytesIO

from django.conf import settings
from django.core.files.base import File
from django.utils.encoding import force_str
from django.core.files.uploadedfile import UploadedFile

from django.core.files.utils import FileProxyMixin
import tempfile
import os

class NamedTemporaryFile(FileProxyMixin):
    """
    Temporary file object constructor that works in Windows and supports
    reopening of the temporary file in windows.
    """
    def __init__(self, mode='w+b', bufsize=-1, suffix='', prefix='',
            dir=None):
        name = tempfile.mktemp(suffix=suffix, prefix=prefix,
                                      dir=dir)
        self.name = name
        print '124124125125:', name
        self.file = open(name, mode, bufsize)
        self.close_called = False

    # Because close can be called during shutdown
    # we need to cache os.unlink and access it
    # as self.unlink only
    unlink = os.unlink

    def close(self):
        if not self.close_called:
            self.close_called = True
            try:
                self.file.close()
            except (OSError, IOError):
                pass
            try:
                self.unlink(self.name)
            except (OSError):
                pass

    def __del__(self):
        self.close()


class TemporaryUploadedFile(UploadedFile):
    """
    A file uploaded to a temporary location (i.e. stream-to-disk).
    """
    def __init__(self, name, content_type, size, charset):
        if settings.FILE_UPLOAD_TEMP_DIR:
            file = NamedTemporaryFile(suffix='.upload',
                dir=settings.FILE_UPLOAD_TEMP_DIR)
        else:
            file = NamedTemporaryFile(suffix='.upload')
        print file
        super(TemporaryUploadedFile, self).__init__(file, name, content_type, size, charset)

    def temporary_file_path(self):
        """
        Returns the full path of this file.
        """
        return self.file.name

    def close(self):
        try:
            return self.file.close()
        except OSError as e:
            if e.errno != 2:
                # Means the file was moved or deleted before the tempfile
                # could unlink it.  Still sets self.file.close_called and
                # calls self.file.file.close() before the exception
                raise
