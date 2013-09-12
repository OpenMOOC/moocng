# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from moocng.externalapps.exceptions import InstanceLimitReached
from moocng.externalapps.registry import ExternalAppRegistry
from moocng.externalapps.validators import validate_slug, validate_forbidden_words


registered_externalapps = ExternalAppRegistry()


class ExternalApp(models.Model):
    ERROR = 1
    OK = 2
    IN_PROGRESS = 3

    STATUSES = (
        (ERROR, _('Error')),
        (OK, _('Ok')),
        (IN_PROGRESS, _('In Progress')),
    )

    name = models.CharField(
        verbose_name=_(u'Name'),
        max_length=200,
        null=False,
        blank=False,
    )

    base_url = models.TextField(
        verbose_name=_(u'Base url of the instance'),
        null=False,
        blank=False,
    )

    ip_address = models.IPAddressField(
        verbose_name=_(u'IP address of the instance'),
        null=False,
        blank=False,
    )

    slug = models.SlugField(
        verbose_name=_(u'Slug for the instance'),
        null=False,
        blank=False,
        validators=[validate_slug, validate_forbidden_words]
    )

    status = models.SmallIntegerField(
        verbose_name=_(u' url of the instance'),
        null=False,
        blank=False,
        choices=STATUSES,
        default=IN_PROGRESS,
    )

    class Meta:
        verbose_name = _(u'external app')
        verbose_name_plural = _(u'external apps')

    def __unicode__(self):
        return u'%s:%s' % (self.name, self.ip_address)

    def clean(self):
        external_app = registered_externalapps.get_app(self.name)
        if external_app:
            try:
                external_app.get_instance(self)
            except InstanceLimitReached:
                raise ValidationError(_('There are no instances available'))
        else:
            msg = _('There is no registered class to manage "%s" external app' % self.name)
            raise ValidationError(msg)
