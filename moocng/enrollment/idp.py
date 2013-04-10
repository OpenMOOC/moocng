# Copyright 2013 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging

import requests
import requests.exceptions

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import simplejson

logger = logging.getLogger(__name__)


def get_api_key():
    try:
        return settings.COURSE_ENROLLMENT_API_KEY
    except AttributeError:
        raise ImproperlyConfigured('The COURSE_ENROLLMENT_API_KEY setting is missing')


def get_destination_url(student):
    try:
        template_url = settings.COURSE_ENROLLMENT_URL
    except AttributeError:
        raise ImproperlyConfigured('The COURSE_ENROLLMENT_URL setting is missing')

    return template_url % {'user_email': student.email}


def get_enrollment_attribute():
    try:
        return settings.COURSE_ENROLLMENT_ATTRIBUTE
    except AttributeError:
        return 'schacUserStatus'  # default value


def get_headers(key):
    return {
        'Content-type': 'application/json',
        'Authentication': 'APIKEY %s' % key
    }


def enroll_course_at_idp(student, course):
    key = get_api_key()
    url = get_destination_url(student)
    enrollment_attribute = get_enrollment_attribute()

    verify = not settings.DEBUG

    # get existing user resource
    try:
        response = requests.get(url, headers=get_headers(key), verify=verify)
    except requests.exceptions.SSLError:
        logger.error('SSLError with the IdP enroll requests')
        return False

    if response.ok:
        payload = response.json
        existing_courses = payload.get(enrollment_attribute, [])
        course_id = unicode(course.id)
        if course_id not in existing_courses:
            existing_courses.append(course_id)
            payload[enrollment_attribute] = existing_courses
            logger.debug('Enrolling the student %s in the course %s' %
                         (student.email, course_id))

            # Update the student with the new course
            try:
                response = requests.put(url,
                                        data=simplejson.dumps(payload),
                                        headers=get_headers(key),
                                        verify=verify)
            except requests.exceptions.SSLError:
                logger.error('SSLError with the IdP enroll requests')
                return False

            if response.ok:
                logger.debug('The student %s has been succesfully enrolled in course %s' %
                             (student.email, course_id))
                return response.json.get('success', False)
            else:
                logger.info('The IdP has not enrolled the student %s in the course %s' %
                            (student.email, course_id))
                return False

        else:
            logger.debug('The student %s is already enrolled in the course %s' %
                         (student.email, course_id))
            return True

    else:
        logger.info('The user %s does not exists in the IdP' % student.email)
        return False
