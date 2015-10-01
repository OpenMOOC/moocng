# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.messages import success
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from moocng.courses.security import (get_course_if_user_can_view_or_404,
                                    get_course_if_user_can_view_and_permission)
from moocng.enrollment.idp import enroll_course_at_idp
from moocng.x_api import utils as x_api
from moocng import mongodb
from bson.objectid import ObjectId
import pymongo
import time

def free_enrollment(request, course_slug):
    course, permission = get_course_if_user_can_view_and_permission(course_slug, request)
    if permission:
        if request.method == 'POST':
            if course.has_groups:
                groupNames = {
                    'es': 'Grupo',
                    'en': 'Group',
                    'fr': 'Groupe',
                    'pt': 'Grupo',
                    'de': 'Gruppe',
                    'it': 'Gruppo'
                }

                if request.user.get_profile().language and request.user.get_profile().language in groupNames:
                    language = request.user.get_profile().language
                else:
                    language = request.LANGUAGE_CODE

                print 'Language = %s' % (language)

                groupCollection = mongodb.get_db().get_collection('groups')
                groups = groupCollection.find({ 'id_course': course.id, 'lang': language }).sort("size",pymongo.ASCENDING)
                if groups:
                    new_member = {"id_user": request.user.id, "username": request.user.username,
                                  "first_name":request.user.first_name, "last_name":request.user.last_name,
                                  "email": request.user.email, "karma": request.user.get_profile().karma, "country": request.user.get_profile().country,
                                  "language": language}
                    if groups.count() > 0:
                        group = groups[0]

                        if(len(group["members"]) <= course.group_max_size):
                            group["members"].append(new_member)
                            if "size" in group:
                                group["size"] += 1
                            else:
                                group["size"] = len(group["members"])

                            groupCollection.update({'_id': ObjectId(group["_id"])}, {"$set": {"members": group["members"], "size": group["size"]}})

                        else:
                            group = {"id_course": course.id, "name": groupNames[language] + str(groups.count()+1), "hashtag": course.hashtag+groupNames[language] + str(groups.count()+1) ,"lang": language, "size": 1, "members": []}
                            group["members"].append(new_member)
                            groupCollection.insert(group)
                    else:
                        group = {"id_course": course.id, "name": groupNames[language] + str(groups.count()+1), "hashtag": course.hashtag+groupNames[language] + str(groups.count()+1), "lang": language, "size": 1, "members": []}
                        group["members"].append(new_member)
                        groupCollection.insert(group)

            user = request.user
            lat = request.POST["latitude"]
            lon = request.POST["longitude"]
            geolocation = {
                'lat': lat,
                'lon': lon
            }
            old_course_status = 'f'
            if course.created_from:
                if course.created_from.students.filter(pk=user.pk):
                    old_course_status = 'n'
            course.students.through.objects.create(student=user,
                                                   course=course,
                                                   old_course_status=old_course_status,
                                                   timestamp=int(round(time.time())),
                                                   pos_lat=lat,
                                                   pos_lon=lon)
            if getattr(settings, 'FREE_ENROLLMENT_CONSISTENT', False):
                enroll_course_at_idp(request.user, course)

            # Send xAPI event
            x_api.learnerEnrollsInMooc(user, course, geolocation)

            success(request,
                    _(u'Congratulations, you have successfully enroll in the course %(course)s')
                    % {'course': unicode(course)})

    return HttpResponseRedirect(reverse('course_dashboard',
                                       args=(course.slug, )))


def free_unenrollment(request, course_slug):
    course, permission = get_course_if_user_can_view_and_permission(course_slug, request)
    if request.method == 'POST':
        if course.has_groups:
            groupCollection = mongodb.get_db().get_collection('groups')
            group = groupCollection.find_one( { 'id_course': course.id, 'members.id_user':request.user.id } )
            if(group):
                for m in group["members"]:
                    if(m["id_user"] == request.user.id):
                        group["members"].remove(m)
                        if "size" in group:
                            group["size"] -= 1
                        else:
                            group["size"] = len(group["members"])

                groupCollection.update({'_id': ObjectId(group["_id"])}, {"$set": {"members": group["members"], "size": group["size"]}})

        user = request.user
        lat = request.POST["latitude"]
        lon = request.POST["longitude"]
        geolocation = {
            'lat': lat,
            'lon': lon
        }
        course.students.through.objects.get(student=user,
                                            course=course).delete()

        x_api.learnerUnenrollsInMooc(user, course, geolocation)

        success(request,
                _(u'You have successfully unenroll in the course %(course)s')
                % {'course': unicode(course)})



    return HttpResponseRedirect(reverse('course_overview',
                                        args=(course.slug, )))
