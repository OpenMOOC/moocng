# -*- coding: utf-8 -*-
# Copyright 2012-2013 UNED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django import forms
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe


class BootstrapMixin(object):

    error_css_class = 'error'

    def as_bootstrap(self):

        """
        Helper function for outputting HTML. Used by as_table(), as_ul(), as_p().
        """
        top_errors = self.non_field_errors()  # Errors that should be displayed above all fields.
        output, hidden_fields = [], []
        normal_row = u'<div%(html_class_attr)s>%(label)s<div class="controls">%(field)s%(help_text)s</div>%(errors)s</div>'
        boolean_row = u'<div%(html_class_attr)s><div class="controls">%(label_and_field)s%(help_text)s</div>%(errors)s</div>'
        error_row = u'<div class="alert alert-error">%s</div>'
        row_ender = u'</div>'
        help_text_html = u'<span class="help-inline">%s</span>'
        errors_on_separate_row = False

        for name, field in self.fields.items():
            html_class_attr = ''
            bf = self[name]
            is_boolean = isinstance(field, forms.fields.BooleanField)
            bf_errors = self.error_class([conditional_escape(error) for error in bf.errors])  # Escape and cache in local variable.
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
                hidden_fields.append(unicode(bf))
            else:
                # Create a 'class="..."' atribute if the row should have any
                # CSS classes applied.
                css_classes = bf.css_classes(extra_classes='control-group')
                if css_classes:
                    html_class_attr = ' class="%s"' % css_classes

                if errors_on_separate_row and bf_errors:
                    output.append(error_row % force_unicode(bf_errors))

                if bf.label:
                    label = conditional_escape(force_unicode(bf.label))
                    if is_boolean:
                        label = bf.label_tag(unicode(bf) + label,
                                             attrs={'class': 'checkbox'}) or ''
                    else:
                        # Only add the suffix if the label does not end in
                        # punctuation.
                        if self.label_suffix:
                            if label[-1] not in ':?.!':
                                label += self.label_suffix

                        label = bf.label_tag(label,
                                             attrs={'class': 'control-label'}) or ''
                else:
                    label = ''

                if field.help_text:
                    help_text = help_text_html % force_unicode(field.help_text)
                else:
                    help_text = u''

                if bf_errors:
                    errors = u' '.join([error_row % force_unicode(error)
                                        for error in bf_errors])
                else:
                    errors = u''

                if is_boolean:
                    output.append(boolean_row % {
                        'errors': errors,
                        'label_and_field': force_unicode(label),
                        'help_text': help_text,
                        'html_class_attr': html_class_attr
                    })
                else:
                    output.append(normal_row % {
                        'errors': errors,
                        'label': force_unicode(label),
                        'field': unicode(bf),
                        'help_text': help_text,
                        'html_class_attr': html_class_attr
                    })

        if top_errors:
            output.insert(0, error_row % force_unicode(top_errors))

        if hidden_fields:  # Insert any hidden fields in the last row.
            str_hidden = u''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and
                # insert the hidden fields.
                if not last_row.endswith(row_ender):
                    # This can happen in the as_p() case (and possibly others
                    # that users write): if there are only top errors, we may
                    # not be able to conscript the last row for our purposes,
                    # so insert a new, empty row.
                    last_row = (normal_row % {'errors': '', 'label': '',
                                              'field': '', 'help_text': '',
                                              'html_class_attr': html_class_attr})
                    output.append(last_row)
                output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
            else:
                # If there aren't any rows in the output, just append the
                # hidden fields.
                output.append(str_hidden)
        return mark_safe(u'\n'.join(output))


class BootstrapClearableFileInput(forms.widgets.ClearableFileInput):

    template_with_clear = u'<label for="%(clear_checkbox_id)s">%(clear)s %(clear_checkbox_label)s</label>'


class HTML5DateInput(forms.widgets.DateInput):

    input_type = 'date'


class HTML5DateTimeInput(forms.widgets.DateTimeInput):

    input_type = 'datetime'


class BootstrapRadioInput(forms.widgets.RadioInput):

    def render(self, name=None, value=None, attrs=None, choices=()):
        name = name or self.name
        value = value or self.value
        attrs = attrs or self.attrs
        label_for = ''
        if 'id' in self.attrs:
            label_for = '%s for="%s_%s"' % (label_for, self.attrs['id'], self.index)
        label_for = '%s class="radio inline"' % label_for
        choice_label = conditional_escape(force_unicode(self.choice_label))
        return mark_safe(u'<label%s>%s %s</label>' % (label_for, self.tag(), choice_label))


class BootstrapInlineRadioFieldRenderer(forms.widgets.RadioFieldRenderer):

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield BootstrapRadioInput(self.name, self.value, self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx]  # Let the IndexError propogate
        return BootstrapRadioInput(self.name, self.value, self.attrs.copy(), choice, idx)

    def render(self):
        # We don't want the standard render becouse we don't use <ul><li>
        return mark_safe(''.join([u'%s' % force_unicode(w) for w in self]))


class BootstrapInlineRadioSelect(forms.widgets.RadioSelect):

    renderer = BootstrapInlineRadioFieldRenderer
