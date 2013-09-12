# -*- coding: utf-8 -*-
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


slug_re = re.compile(r'^[a-zA-Z0-9_]+$')
validate_slug = RegexValidator(slug_re, _("Enter a valid 'slug' consisting of letters, numbers or underscores."))

def validate_forbidden_words(value):
    forbidden_words = settings.MOOCNG_EXTERNALAPPS_FORBIDDEN_WORDS

    for forbidden_word in forbidden_words:
        if forbidden_word in value:
            raise ValidationError(u'%s contains a forbidden word' % value)
