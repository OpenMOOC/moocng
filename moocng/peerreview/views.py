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

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext


from moocng.courses.models import Course
from moocng.peerreview.utils import course_get_peer_review_assignments


@login_required
def course_reviews(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    assignments = course_get_peer_review_assignments(course)

    return render_to_response('peerreview/reviews.html', {
            'course': course,
            'assignments': assignments,
            }, context_instance=RequestContext(request))
