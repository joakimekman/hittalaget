from django import forms
from django.core.exceptions import ValidationError
from django.http import Http404
from .models import PmMessage, AdMessage


class MessageForm(forms.ModelForm):
    class Meta:
        fields = ['content']


class PmMessageForm(MessageForm):
    class Meta(MessageForm.Meta):
        model = PmMessage


class AdMessageForm(MessageForm):
    class Meta(MessageForm.Meta):
        model = AdMessage



