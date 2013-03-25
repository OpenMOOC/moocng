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


from datetime import datetime

from django.db import IntegrityError

from moocng.mongodb import get_db
from moocng.peerreview import cache
from moocng.peerreview.models import PeerReviewAssignment


def course_get_peer_review_assignments(course):
    return PeerReviewAssignment.objects.from_course(course)


def course_get_visible_peer_review_assignments(user, course):
    return PeerReviewAssignment.objects.visible_from_course(user, course)


def course_has_peer_review_assignments(course):
    result = cache.get_course_has_peer_review_assignments_from_cache(course)
    if result is None:
        assignments = course_get_peer_review_assignments(course)
        result = assignments.count() > 0
        cache.set_course_has_peer_review_assignments_in_cache(course, result)

    return result


def get_peer_review_review_score(review):
    if len(review["criteria"]) == 0:
        return 0
    return (float(sum(c[1] for c in review["criteria"])) /
            len(review["criteria"]))


def kq_get_peer_review_score(kq, author, pra=None):
    """ppr_collection is peer_review_reviews mongo collection

        Return a tuple with (score, scorable)
        * If this kq isn't peer_review type:
            return (None, false)
        * If there is no submission:
            return (0, True)
        * If I haven't reviewed enough submissions of other students:
            return (0, True)
        * If nobody reviewed my submission:
            return (None, False)
        * If there are some reviews from other students to my submission but
          less than the minimum the teacher wants:
            return (Average, False)
        * If I got enough reviews of my submission and I have reviewed enough
          reviews of other students' submissions:
            rerturn (Average, True)
    """

    if not pra:
        try:
            pra = kq.peerreviewassignment
        except PeerReviewAssignment.DoesNotExist:
            return (None, False)

    db = get_db()

    prs_collection = db.get_collection("peer_review_submissions")

    submission = prs_collection.find_one({
        "kq": kq.id,
        "author": author.id
    })

    if not submission:
        return (0, True)

    if (submission.get("author_reviews", 0) < pra.minimum_reviewers):
        return (0, True)

    if (submission["reviews"] == 0):
        return (None, False)

    ppr_collection = db.get_collection("peer_review_reviews")

    reviews = ppr_collection.find({
        "kq": kq.id,
        "author": author.id
    })

    reviews_count = reviews.count()

    sum_average = 0
    for review in reviews:
        sum_average += float(get_peer_review_review_score(review))

    average = sum_average / reviews_count

    if (submission["reviews"] > 0 and
            submission.get("author_reviews", 0) < pra.minimum_reviewers):
        return (average, False)

    else:
        return (average, True)


def save_review(kq, reviewer, user_reviewed, criteria, comment):

    parsed_criteria = [[int(a), int(b)] for (a, b) in criteria]

    db = get_db()
    submissions = db.get_collection("peer_review_submissions")
    reviews = db.get_collection("peer_review_reviews")

    submission = submissions.find_one({
        "author": user_reviewed.id,
        "kq": kq.id
    })

    peer_review_review = {
        "submission_id": submission.get("_id"),
        "author": user_reviewed.id,
        "comment": comment,
        "created": datetime.utcnow(),
        "reviewer": reviewer.id,
        "criteria": parsed_criteria,
        "kq": kq.id,
        "unit": kq.unit.id,
        "course": kq.unit.course.id
    }

    review_exists = (reviews.find({
        "submission_id": submission.get("_id"),
        "reviewer": reviewer.id,
    }).count() > 0)

    if review_exists:
        raise IntegrityError("Already exist one review for this submission and"
                             " reviewer")

    reviews.insert(peer_review_review)

    submissions.update({
        "author": user_reviewed.id,
        "kq": kq.id,
    }, {
        "$inc": {
            "reviews": 1,
        },
        "$unset": {
            "assigned_to": 1,
            "assigned_when": 1,
        },
        "$push": {
            "reviewers": reviewer.id,
        }
    })

    submissions.update({
        "author": reviewer.id,
        "kq": kq.id,
    }, {
        "$inc": {
            "author_reviews": 1,
        }
    })

    return peer_review_review
