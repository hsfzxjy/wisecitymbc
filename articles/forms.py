#encoding=utf8
from django.utils.safestring import mark_safe
from django import forms 
from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join
from .models import Status

class ReadOnlyStatusWidget(forms.Widget):

    def render(self, name, value, attrs):
        final_attrs = self.build_attrs(attrs)
        html = mark_safe(value)

        return format_html(u"<div class='col-xs-12' {0}>{1}</div>", flatatt(final_attrs), html)

class ReadOnlyStatusField(forms.Field):

    widget = ReadOnlyStatusWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        super(ReadOnlyStatusField, self).__init__(*args, **kwargs)

    def bound_data(self, data, initial):
        return initial

    def _has_changed(self, initial, data):
        return False

class StatusChangeForm(forms.ModelForm):

    body_text = ReadOnlyStatusField(label = '正文')

    class Meta:
        model = Status
        fields = '__all__'

    def clean_body_text(self):
        return self.initial['body_text']