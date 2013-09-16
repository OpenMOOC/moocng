# -*- coding: utf-8 -*-
from django import forms

from moocng.externalapps.models import ExternalApp
from moocng.forms import BootstrapMixin


class ExternalAppForm(forms.ModelForm, BootstrapMixin):

    class Meta:
        model = ExternalApp
        fields = ('instance_type', 'app_name', 'slug',)
