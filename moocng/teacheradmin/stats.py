from bson import Code

from moocng.courses.models import KnowledgeQuantum
from moocng.mongodb import get_db


def course_completed_started(course):
    activity = get_db().get_collection('activity')

    total_kqs = KnowledgeQuantum.objects.filter(unit__course=course).count()
    kqs_by_user = activity.group(
        condition={"course_id": course.id},
        key={"user_id": 1},
        initial={
            "kqs": 0
        },
        reduce=Code("""function (curr, result) {
            result.kqs += 1
        }""")
    )

    def is_completed(e):
        return e.get("kqs", 0) == total_kqs

    completed = len(filter(is_completed, kqs_by_user))
    started = len(kqs_by_user)

    return (completed, started)


def unit_completed_started(unit):
    activity = get_db().get_collection('activity')

    total_kqs = unit.knowledgequantum_set.count()
    kqs_by_user = activity.group(
        condition={"unit_id": unit.id},
        key={"user_id": 1},
        initial={
            "kqs": 0
        },
        reduce=Code("""function (curr, result) {
            result.kqs += 1
        }""")
    )

    def is_completed(e):
        return e.get("kqs", 0) == total_kqs

    completed = len(filter(is_completed, kqs_by_user))
    started = len(kqs_by_user)

    return (completed, started)


def kq_viewed(kq):
    activity = get_db().get_collection('activity')

    return activity.find({"kq_id": kq.id}).count()


def question_answered(question):
    answers = get_db().get_collection('answers')

    return answers.find({"question_id": question.id}).count()
