from django import forms

EVALUTION_CRITERIA_CHOICES = [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
]


class ReviewSubmissionForm(forms.Form):
    comments = forms.CharField(widget=forms.widgets.Textarea)


class EvalutionCriteriaResponseForm(forms.Form):
    evaluation_criterion_id = forms.IntegerField(widget=forms.widgets.HiddenInput)
    value = forms.ChoiceField(choices=EVALUTION_CRITERIA_CHOICES, widget=forms.widgets.RadioSelect)
