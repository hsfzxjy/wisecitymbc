from django.core.files.uploadhandler import FileUploadHandler
from django.core.files.uploadedfile import UploadedFile
import tempfile
from django.core.files.storage import default_storage
from StringIO import StringIO
from time import time

__all__ = ['SAETemporaryFileUploadHandler']

class SAEUploadedFile(UploadedFile):

    DEFAULT_CHUNK_SIZE = 512 * 2 ** 10 

    def __init__(self, dir_name, *args, **kwargs):
        self._temp_files = []
        self.temp = StringIO()
        self.dir_name = dir_name
        self._temp_size = 0

        super(SAEUploadedFile, self).__init__(None, *args, **kwargs)

    def _get_temp_file_name(self):
        return tempfile.mktemp(
            suffix = '.upload',
            dir = '{0}/'.format(self.dir_name)
        )

    def multiple_chunks(self, *args):
        return True

    @property 
    def sections(self):
        print self._temp_files
        return self._temp_files

    def _save_data(self):
        if self._temp_size <= 0:
            return
        temp_file = self._get_temp_file_name()
        self.temp.seek(0)
        default_storage.save(temp_file, self.temp)
        self.temp.close()
        self.temp = StringIO()
        self._temp_size = 0

        self._temp_files.append(temp_file)

    def add_data(self, raw_data):
        self._temp_size += len(raw_data)
        self.temp.write(raw_data)
        if self._temp_size<self.DEFAULT_CHUNK_SIZE:
            return

        self._save_data()

    def read(self):
        return self.chunks()

    def chunks(self, *args, **kwargs):
        for temp_file in self._temp_files:
            yield default_storage.open(temp_file)

class SAETemporaryFileUploadHandler(FileUploadHandler):

    def new_file(self, *args, **kwargs):
        """
        Create the file object to append to as data is coming in.
        """
        super(SAETemporaryFileUploadHandler, self).new_file(*args, **kwargs)
        self.file = SAEUploadedFile(time(), self.file_name, self.content_type, 0, self.charset)

    def receive_data_chunk(self, raw_data, start):
        self.file.add_data(raw_data)

    def file_complete(self, file_size):
        self.file._save_data()
        self.file.size = file_size
        return self.file
