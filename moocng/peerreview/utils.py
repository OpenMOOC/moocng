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

from moocng.peerreview import cache
from moocng.peerreview.models import PeerReviewAssignment


def course_get_peer_review_assignments(course):
    return PeerReviewAssignment.objects.from_course(course)


def course_has_peer_review_assignments(course):
    result = cache.get_course_has_peer_review_assignments_from_cache(course)
    if result is None:
        assignments = course_get_peer_review_assignments(course)
        result = assignments.count() > 0
        cache.set_course_has_peer_review_assignments_in_cache(course, result)

    return result


def kq_get_peer_review_score(kq, author, ppr):
    """ppr is peer_review_reviews mongo collection"""

    reviews = ppr.find({
        "kq": unicode(kq.id),
        "author": unicode(2)
    })

    if reviews.count() == 0:
        return None

    # TODO tests minimum_reviews

    average = 0
    for review in reviews:
        average += (float(sum([c[1] for c in review["criteria"]]) /
                    len(review["criteria"])))

    return (average / reviews.count())
