# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _

class PostForm(forms.Form):
    postText = forms.CharField(required=True, max_length="500", label="", widget=forms.Textarea(attrs={'placeholder': _('Write a message...')}))

