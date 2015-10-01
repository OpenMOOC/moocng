# Copyright 2013 UNED
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
from django.utils.translation import ugettext as _

from tastypie.exceptions import BadRequest

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
            return None
        * If there is no submission:
            return 0
        * If I haven't reviewed enough submissions of other students:
            return 0
        * If nobody reviewed my submission:
            return None
        * If I got enough reviews of my submission and I have reviewed enough
          reviews of other students' submissions:
            rerturn Average
    """

    if not pra:
        try:
            pra = kq.peerreviewassignment
        except PeerReviewAssignment.DoesNotExist:
            return None

    db = get_db()

    prs_collection = db.get_collection("peer_review_submissions")

    submission = prs_collection.find_one({
        "kq": kq.id,
        "author": author.id
    })

    if (not submission or
       submission.get("author_reviews", 0) < pra.minimum_reviewers):
        return 0
    elif submission["reviews"] == 0:
        return None

    ppr_collection = db.get_collection("peer_review_reviews")
    reviews = ppr_collection.find({
        "kq": kq.id,
        "author": author.id
    })
    reviews_count = reviews.count()
    sum_average = 0
    for review in reviews:
        sum_average += float(get_peer_review_review_score(review))

    if(reviews_count > 0):
        return (sum_average / reviews_count) * 2  # * 2 due peer_review range is 1-5
    else:
        return 10


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


def insert_p2p_if_does_not_exists_or_raise(p2p_submission, submissions=None):
    if submissions is None:
        db = get_db()
        submissions = db.get_collection("peer_review_submissions")
    if submissions.find({'kq': p2p_submission['kq'], 'author': p2p_submission['author']}).count() > 0:
        raise BadRequest(_('You have already sent a submission. Please reload the page'))
    return submissions.insert(p2p_submission)
