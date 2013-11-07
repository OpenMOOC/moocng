# -*- coding: utf-8 -*-
# Copyright 2012-2013 Rooter Analysis S.L.
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

import logging

from django.contrib.auth.models import User
from django.conf import settings

from celery import task

from moocng.courses.utils import send_mass_mail_wrapper

logger = logging.getLogger(__name__)


@task
def massmail_send_in_batches(massiveemail, email_send_task):

    """
    Create a task to create the sending mass mail task. This is done this way
    so the form in mass mailing section in the teacher admin can reply as
    fast as possible.

    .. versionadded:: 0.1
    """
    try:
        batch = settings.MASSIVE_EMAIL_BATCH_SIZE
    except AttributeError:
        batch = 30

    students = massiveemail.course.students.all()
    batches = (students.count() / batch) + 1
    for i in range(batches):
        init = batch * i
        end = init + batch
        students_ids = [s.id for s in students[init:end]]
        email_send_task.apply_async(args=[massiveemail.id, students_ids], queue='massmail')


@task
def send_massive_email_task(email_id, students_ids):

    """
    Calls send_mass_mail_wrapper to create a new email task that should be handled
    by celery/rabbitmq.

    .. versionadded:: 0.1
    """
    from moocng.teacheradmin.models import MassiveEmail
    try:
        email = MassiveEmail.objects.get(id=email_id)
    except MassiveEmail.DoesNotExist:
        logger.error('Email with ID %d does not exists' % email_id)
        return

    logger.debug("massive email, students %s email %s" % (students_ids, email.subject))

    recipients = []
    missing = []
    for sid in students_ids:
        try:
            student = User.objects.get(id=sid)
            recipients.append(student.email)
        except User.DoesNotExist:
            missing.append(sid)

    if len(missing) > 0:
        logger.error("These users no longer exists so they won't receive the massive email. Users: %s - Course: %s" % (missing, email.course.slug))

    if len(recipients) > 0:
        send_mass_mail_wrapper(email.subject, email.message, recipients, html_content=True)
