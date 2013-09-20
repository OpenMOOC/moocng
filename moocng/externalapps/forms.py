# -*- coding: utf-8 -*-
from django import forms
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from moocng.externalapps.models import ExternalApp
from moocng.forms import BootstrapMixin


class ExternalAppForm(forms.ModelForm, BootstrapMixin):

    error_messages = {
        'status_in_progress': _("The external application creation task is being processed. Save is not allowed in that status."),
        'status_tampering': _("Oops! It might seem you have tried tampering the object status..."),
    }

    status = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = ExternalApp
        fields = ('instance_type', 'app_name', 'slug', 'status', 'visibility',)

    def clean(self):
        status = self.cleaned_data.get('status')
        if status and self.instance.id:
            status = int(self.cleaned_data.get('status'))
            slug = self.cleaned_data.get('slug')
            instance_type = self.cleaned_data.get('instance_type')
            if slug and instance_type:
                try:
                    externalapp = ExternalApp.objects.get(slug=slug, instance_type=instance_type)
                except ExternalApp.DoesNotExist:
                    pass
                else:
                    if status == externalapp.status:
                        if status == ExternalApp.IN_PROGRESS:
                            raise ValidationError(self.error_messages['status_in_progress'])
                    else:
                        raise ValidationError(self.error_messages['status_tampering'])
        return self.cleaned_data
