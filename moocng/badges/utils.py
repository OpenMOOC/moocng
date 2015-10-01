# -*- coding: utf-8 -*-
from moocng.badges.models import BadgeByCourse as Badge
from moocng.courses.models import Course
from moocng.mongodb import get_db

def get_user_badges_group_by_course(user):
    badgeCollection = get_db().get_collection('badge')
    badges = badgeCollection.find({"id_user": user.id})
    courses = {}
    for badge in badges:
        try:
            badge_def =Badge.objects.get(id=badge['id_badge'])
            badge['course'] = badge_def.course
            course_id = str(badge_def.course.id)
            if not courses.has_key(course_id):
                courses[course_id] = badge_def.course
                courses[course_id].badges = []
            badge['definition'] = badge_def
            courses[course_id].badges.append(badge)
        except:
            pass

    return courses
