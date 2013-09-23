# -*- coding: utf-8 -*-
from django import forms
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from moocng.externalapps.models import ExternalApp
from moocng.forms import BootstrapMixin


class ExternalAppForm(forms.ModelForm, BootstrapMixin):

    error_messages = {
        'slug_edit': _("Once the slug has been set, you must contact an administrator to change it"),
        'status_in_progress': _("The external application creation task is being processed. Save is not allowed in that status."),
        'status_tampering': _("Oops! It might seem you have tried tampering the object status..."),
    }

    status = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = ExternalApp
        fields = ('instance_type', 'app_name', 'slug', 'status', 'visibility',)

    def clean(self):
        cleaned_data = super(ExternalAppForm, self).clean()
        slug = cleaned_data.get("slug")
        status = int(self.cleaned_data.get('status'))

        if self.instance.id:
            externalapp = ExternalApp.objects.get(pk=self.instance.id)
            if slug and externalapp.slug != slug:
                raise ValidationError(self.error_messages['slug_edit'])

            if status == externalapp.status:
                if status == ExternalApp.IN_PROGRESS:
                    raise ValidationError(self.error_messages['status_in_progress'])
            else:
                raise ValidationError(self.error_messages['status_tampering'])

        return self.cleaned_data
