class SendNoticeModelMixin(object):

    @classmethod
    def generate_title(klass, *args, **kwargs):
        return ''

    @classmethod
    def generate_content(klass, *args, **kwargs):
        return ''

    @classmethod
    def generate_url(klass, *args, **kwargs):
        return ''

    @classmethod
    def generate_user(klass, *args, **kwargs):
        return []