# -*- coding: utf-8 -*-
import time
import logging
import tempfile

from celery import (task, Task,)


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


def do_process_instance_creation(externalapp_id):
    from moocng.externalapps.models import ExternalApp
    externalapp = ExternalApp.objects.get(pk=externalapp_id)

    #sample code. Need to be changed to execute remote commands.
    # Code run here need to raise Exceptions to reache on_failure method
    time.sleep(2)
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write('k4k1t4!')
    f.write(str(externalapp.id))
    f.close()
    time.sleep(2)

    return externalapp_id


@task(base=BaseExternalAppTask)
def process_instance_creation(externalapp_id):
    return do_process_instance_creation(externalapp_id)
