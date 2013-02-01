# Copyright 2013 Rooter Analysis S.L.
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

from celery import task

from moocng.teacheradmin.models import MassiveEmail
from moocng.teacheradmin.utils import send_mass_mail_wrapper

logger = logging.getLogger(__name__)


@task
def send_massive_email_task(email_id, students_ids):
    try:
        email = MassiveEmail.objects.get(id=email_id)
    except MassiveEmail.DoesNotExist:
        logger.error('Email with ID %d does not exists' % email_id)
        return

    print "massive email, students %s email %s" % (students_ids, email.subject)

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
