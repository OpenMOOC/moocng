# -*- coding: utf-8 -*-
import logging

from celery import (task, Task,)

from moocng.externalapps.exceptions import InstanceCreationError


logger = logging.getLogger(__name__)


class BaseExternalAppTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        from moocng.externalapps.models import ExternalApp
        logger.error('Task with id %r raised exception: %r. Traceback: %r' % (task_id, exc, einfo))
        externalapp_id = args[0]
        self.update_external_app_state(externalapp_id, ExternalApp.ERROR)
        super(BaseExternalAppTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        from moocng.externalapps.models import ExternalApp
        externalapp_id = args[0]
        self.update_external_app_state(externalapp_id, ExternalApp.CREATED)
        super(BaseExternalAppTask, self).on_success(retval, task_id, args, kwargs)

    def update_external_app_state(self, externalapp_id, status):
        from moocng.externalapps.models import ExternalApp, on_process_instance_creation
        from django.db.models import signals
        externalapp = ExternalApp.objects.get(pk=externalapp_id)
        externalapp.status = status

        signals.post_save.disconnect(receiver=on_process_instance_creation, sender=ExternalApp)
        externalapp.save()
        signals.post_save.connect(on_process_instance_creation, sender=ExternalApp)


@task(base=BaseExternalAppTask)
def process_instance_creation(externalapp_id):
    from fabric.api import execute
    from django.conf import settings
    from moocng.externalapps.fabfile import create_instance
    from moocng.externalapps.models import ExternalApp

    externalapp = ExternalApp.objects.get(pk=externalapp_id)
    fabric_user = settings.FABRIC_TASK_USER
    host = '%s@%s' % (fabric_user, externalapp.ip_address)

    result = execute(create_instance, externalapp_id, hosts=[host])
    created = result.get(host, False)
    if not created:
        raise InstanceCreationError
