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

from django import template

register = template.Library()

@register.inclusion_tag('courses/usercourses.html', takes_context=True)
def usercourses(context):
    user = context['user']
    courses = user.courses_as_student.all()
    return {'courses': courses}


@register.inclusion_tag('courses/clone_activity.html', takes_context=False)
def clone_activity(course, user):
    course_student_relation = user.coursestudent_set.get(course=course)
    return {'course': course,
            'course_student_relation': course_student_relation}
