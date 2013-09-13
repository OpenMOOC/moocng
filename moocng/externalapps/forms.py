# -*- coding: utf-8 -*-
from django import forms
from moocng.externalapps.models import ExternalApp


class ExternalAppForm(forms.ModelForm):

    class Meta:
        model = ExternalApp
        include = ('base_url',)
