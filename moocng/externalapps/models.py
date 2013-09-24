# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from moocng.courses.models import Course
from moocng.externalapps.exceptions import InstanceLimitReached
from moocng.externalapps.managers import ExternalAppManager
from moocng.externalapps.registry import ExternalAppRegistry
from moocng.externalapps.tasks import process_instance_creation
from moocng.externalapps.validators import validate_slug, validate_forbidden_words


EXTERNAL_APPS_QUEUE = 'externalapps'


externalapps = ExternalAppRegistry()

def get_instance_types():
    return [(key, key) for key in settings.MOOCNG_EXTERNALAPPS.keys()]


class ExternalApp(models.Model):

    CREATED = 1
    NOT_CREATED = 2
    IN_PROGRESS = 3
    ERROR = 4

    ME = 1
    ALL = 2

    STATUSES = (
        (CREATED, _('Created')),
        (NOT_CREATED, _('Not Created')),
        (IN_PROGRESS, _('In Progress')),
        (ERROR, _('Error')),
    )

    VISIBILITIES = (
        (ME, _('Just me')),
        (ALL, _('Everybody')),
    )

    course = models.ForeignKey(
        Course,
        verbose_name=_('Course'),
        related_name='external_apps',
        blank=False,
        null=True)

    app_name = models.CharField(
        verbose_name=_('Visible app name'),
        max_length=200,
        null=False,
        blank=False,
    )

    base_url = models.TextField(
        verbose_name=_('Base url of the instance'),
        null=False,
        blank=False,
    )

    ip_address = models.IPAddressField(
        verbose_name=_('IP address of the instance'),
        null=False,
        blank=False,
    )

    slug = models.SlugField(
        verbose_name=_('Slug for the instance'),
        null=False,
        blank=False,
        validators=[validate_slug, validate_forbidden_words]
    )

    status = models.SmallIntegerField(
        verbose_name=_('Creation status of the instance'),
        null=False,
        blank=False,
        choices=STATUSES,
        default=NOT_CREATED,
    )

    instance_type = models.CharField(
        verbose_name=_('Type of instance'),
        null=False,
        blank=False,
        max_length=50,
        choices=get_instance_types(),
        default='askbot'
    )

    execute_task_on_save = models.NullBooleanField(
        verbose_name=_('Execute task on save'),
        blank=True,
        null=True
    )

    visibility = models.SmallIntegerField(
        verbose_name=_('Visibility of the instance'),
        null=False,
        blank=False,
        choices=VISIBILITIES,
        default=ME,
    )

    objects = ExternalAppManager()

    class Meta:
        unique_together = ('ip_address', 'slug')
        verbose_name = _('external app')
        verbose_name_plural = _('external apps')

    def __unicode__(self):
        return u'%s:%s' % (self.instance_type, self.ip_address)

    def url(self):
        if not self.instance_ready():
            return _('url not available')
        return u'%s/%s' % (self.base_url, self.slug)
    url.short_description = _('Url')
    url.admin_order_field = 'ip_address'

    def url_link(self):
        if not self.instance_ready():
            url = _('url not available')
        else:
            url = '<a href="%s" target="_blank">%s</a>' % (self.url(), self.url())
        return url
    url_link.allow_tags = True
    url_link.short_description = _('Url')
    url_link.admin_order_field = 'ip_address'

    def instance_ready(self):
        return self.status == self.CREATED

    def clean(self):
        external_app = externalapps.get_app_by_name(self.instance_type)
        if external_app:
            if not self.id:
                try:
                    instance_assigned = external_app.get_instance(self)
                    self.ip_address = instance_assigned[0]
                    self.base_url = instance_assigned[1]
                    self.status = self.IN_PROGRESS
                    self.instance_type = external_app._meta.instance_type
                except InstanceLimitReached:
                    raise ValidationError(_('There are no instances available'))
        else:
            msg = _('There is no registered class to manage "%s" external app' % self.app_name)
            raise ValidationError(msg)

    def in_progress(self):
        return self.status == ExternalApp.IN_PROGRESS


def on_process_instance_creation(sender, instance, created, **kwargs):
    if created:
        if instance and instance.execute_task_on_save:
            process_instance_creation.apply_async(
                args=[instance.id],
                queue=EXTERNAL_APPS_QUEUE
            )
signals.post_save.connect(on_process_instance_creation, sender=ExternalApp)
