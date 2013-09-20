# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from fabric.api import (task, run, sudo,)

from moocng.externalapps.models import ExternalApp


logger = logging.getLogger(__name__)


def exists_instance(instance_name):
    res = run("ls %s" % settings.FABRIC_ASKBOT_INSTANCES_PATH)
    return instance_name in res


@task(warn_only=True)
def create_instance(externalapp_id):
    status = False
    externalapp = ExternalApp.objects.get(pk=externalapp_id)
    instance_name = externalapp.slug
    exists = exists_instance(instance_name)
    if exists:
        status = False

    instance_type = externalapp.instance_type
    result = run("openmooc-askbot-instancetool -c %s %s_%s" % (instance_name, instance_type, instance_name))
    if result.succeeded:
        sudo("service supervisord restart")
        sudo("service nginx restart")
        status = True

    return status
