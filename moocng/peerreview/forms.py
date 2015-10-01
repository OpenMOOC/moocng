# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

EVALUTION_CRITERIA_CHOICES = [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
]


class ReviewSubmissionForm(forms.Form):
    comments = forms.CharField(widget=forms.widgets.Textarea(attrs={'class': 'input-block-level', 'rows': 7, 'placeholder': _(u'Type here your comments about this review')}), required=False)


class EvalutionCriteriaResponseForm(forms.Form):
    evaluation_criterion_id = forms.IntegerField(widget=forms.widgets.HiddenInput)
    value = forms.ChoiceField(choices=EVALUTION_CRITERIA_CHOICES, widget=forms.widgets.RadioSelect)
