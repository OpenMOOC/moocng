# -*- coding: utf-8 -*-

import time
import hashlib
import requests
import sys
import json
import re

from optparse import make_option

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from moocng import mongodb
from moocng.badges.models import Badge
from moocng.courses.models import Course
from moocng.courses.utils import get_groups_by_course



class Command(BaseCommand):

    help = ("Creates forum topics for each group in a course that has no forum topic yet.")

    option_list = BaseCommand.option_list + (
        make_option('-c', '--courses',
                    action='store',
                    dest='course_pk',
                    default="",
                    help='Course pk'),
    )

    def error(self, message):
        self.stderr.write("%s\n" % message.encode("ascii", "replace"))

    def message(self, message):
        self.stdout.write("%s\n" % message.encode("ascii", "replace"))

    def handle(self, *args, **options):

        if not options["course_pk"]:
            raise CommandError("-c course_pk is required")

        groups = list(get_groups_by_course(options["course_pk"]))
        print "Groups: " + str(len(groups))
        for group in groups:
            if "forum_slug" in group and group["forum_slug"] is not None:
                print "\nGroup " + str(group["name"]) + " already has forum topic"
            else:
                print "\nGroup " + str(group["name"]) + " has NO forum topic"

                course = Course.objects.filter(id=int(options["course_pk"]))[:1].get()
                split_result = re.split(r'([0-9]+)', course.forum_slug)
                cid = split_result[1]

                content = _(u"This is the topic for ") + group["name"] + _(u" where you can comment and help other team members")
                data = {
                    "uid": 1,
                    "title": group["name"],
                    "content": content,
                    "cid": cid
                }
                timestamp = int(round(time.time() * 1000))
                authhash = hashlib.md5(settings.FORUM_API_SECRET + str(timestamp)).hexdigest()
                headers = {
                    "Content-Type": "application/json",
                    "auth-hash": authhash,
                    "auth-timestamp": timestamp
                }
                
                if settings.FEATURE_FORUM:
                    try:
                        r = requests.post(settings.FORUM_URL + "/api2/topics", data=json.dumps(data), headers=headers)
                        if r.status_code == requests.codes.ok:
                            group["forum_slug"] = r.json()["slug"]
                            mongodb.get_db().get_collection('groups').update({"_id": group["_id"]}, {"$set": {"forum_slug": group["forum_slug"]}})
                            print "  --> Topic for Group '" + group["name"] + "' created succesfully."
                        else:
                            print "  --> Could no create a topic for Group '" + group["name"] + "'. Server returns error code " + r.status_code + "."
                            print r.text

                    except:
                        print "  !!! Error creating course forum topic"
                        print "      Unexpected error:", sys.exc_info()


