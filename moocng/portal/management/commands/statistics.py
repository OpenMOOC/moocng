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
from optparse import make_option

from django.db.models import Q
from django.core.management.base import BaseCommand

from moocng.courses.models import Course
from moocng.mongodb import get_db
from moocng.portal.stats import calculate_all_stats


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--courses',
            dest='courses',
            default='',
            help='List of courses\' id or slug to calculate stats of. Comma separated'
        ),
        make_option(
            '--include-finished-courses',
            action='store_true',
            dest='finished_courses',
            default=False,
            help='Include in the statistics calculations those courses that are already finished.'
        ),
        make_option(
            '--all',
            action='store_true',
            dest='all_courses',
            default=False,
            help='Calculate statistics for all courses, this overrides any other option.'
        )
    )

    def handle(self, *args, **options):
        all_courses_objs = Course.objects.only('id').all()
        all_courses_ids = [c.id for c in all_courses_objs]

        if options['all_courses']:
            courses = all_courses_objs
        elif not options['courses']:
            # FIXME this crashes, there are problems with the dates
            courses = Course.objects.only('id').filter(status='p').filter(
                # exclude courses that haven't started
                Q(start_date__is_null=True) |
                Q(start_date__is_null=False, start_date__lte=datetime.now)
            )
            if not options['finished_courses']:
                # exclude finished courses
                courses = courses.filter(
                    Q(end_date__is_null=True) |
                    Q(end_date__is_null=False, end_date__gte=datetime.now)
                )
        else:
            user_courses = options['courses'].split(',')
            courses = []
            for id_or_slug in user_courses:
                try:
                    if id_or_slug.isdigit():
                        c = Course.objects.only('id').get(id=id_or_slug)
                    else:
                        c = Course.objects.only('id').get(slug=id_or_slug)
                    courses.append(c)
                except Course.DoesNotExist:
                    print '"%s" does not exist' % id_or_slug
                    pass

        courses = [c.id for c in courses]
        blacklist = [cid for cid in all_courses_ids if cid not in courses]

        # Drop existing stats for selected courses
        db = get_db()
        stats_course = db.get_collection('stats_course')
        stats_unit = db.get_collection('stats_unit')
        stats_kq = db.get_collection('stats_kq')
        for cid in courses:
            stats_course.remove({'course_id': cid}, safe=True)
            stats_unit.remove({'course_id': cid}, safe=True)
            stats_kq.remove({'course_id': cid}, safe=True)

        # Callback to show some progress information
        def callback(step='', counter=0, total=0):
            if counter % int(total / 100) == 0:
                if step == 'calculating':
                    print 'Processed %d of %d users' % (counter, total)
                elif step == 'storing':
                    print 'Saved %d of %d statistics entries' % (counter, total)

        calculate_all_stats(callback=callback, course_blacklist=blacklist)
