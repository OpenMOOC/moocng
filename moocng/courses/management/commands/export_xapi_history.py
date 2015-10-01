# -*- coding: utf-8 -*-

import requests
import sys
import json
import re
import time
import calendar
from optparse import make_option

import pyprind

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from moocng.users.models import User
from moocng.courses.models import Course, CourseStudent
from moocng.x_api.utils import learnerAccessAPage, learnerEnrollsInMooc
from moocng import mongodb

class Command(BaseCommand):
	option_list = BaseCommand.option_list + (
		make_option('-b', '--datebefore',
					action='store',
					dest='datebefore',
					default='',
					help='Max date to export. Format "DD/MM/YYYY hh:mm"'),
		make_option('-a', '--dateafter',
					action='store',
					dest='dateafter',
					default='',
					help='Min date to export. Format "DD/MM/YYYY hh:mm"'),
		make_option('-e', '--enrollments',
					action='store_true',
					dest='enrollments',
					default='',
					help='Export only enrollments'),

		make_option('-c', '--accesses',
					action='store_true',
					dest='accesses',
					default='',
					help='Export only accesses'),
	)

	def error(self, message):
		self.stderr.write("%s\n" % message.encode("ascii", "replace"))

	def message(self, message):
		self.stdout.write("%s\n" % message.encode("ascii", "replace"))

	def handle(self, *args, **options):
		if options['datebefore']:
			max_timestamp = calendar.timegm(time.strptime(options['datebefore'], '%d/%m/%Y %H:%M'))
		else:
			max_timestamp = calendar.timegm(time.gmtime())

		if options['dateafter']:
			min_timestamp = calendar.timegm(time.strptime(options['dateafter'], '%d/%m/%Y %H:%M'))
		else:
			min_timestamp = 0

		if options['enrollments'] or not options['accesses']:
			# Get enrollments
			enrollments = CourseStudent.objects.exclude(timestamp__lte=min_timestamp).filter(timestamp__lte=max_timestamp)
			self.message("%d enrollments between %d and %d" % (enrollments.count(), min_timestamp, max_timestamp))

			#Send each enrollment entry as xAPI statement
			bar = pyprind.ProgBar(enrollments.count())
			for enrollment in enrollments:
				try:
					geolocation = {
						'lat': enrollment.pos_lat,
						'lon': enrollment.pos_lon
					}
					timestamp = time.gmtime(enrollment.timestamp)
					learnerEnrollsInMooc(enrollment.student, enrollment.course, geolocation, timestamp)
				except:
					self.error('ERROR sending an statement for user %s in enrollment with timestamp %s' % (enrollment.student, time.strftime("%d/%m/%Y %H:%M:%S", timestamp)))
					continue

				bar.update()

			self.message('Enrollments succesfully exported')

		if options['accesses'] or not options['enrollments']:
			# Get history
			history_col = mongodb.get_db().get_collection('history')
			histories = history_col.find({'$and': [
        									{'timestamp': {'$lte': max_timestamp * 1000} },
        									{'timestamp': {'$gte': min_timestamp * 1000} }
        								]})
			self.message("%d histories until %d" % (histories.count(), max_timestamp))

			# Send each history entry as xAPI Statement
			bar = pyprind.ProgBar(histories.count())
			for history in histories:
				course = None
				try:
					user_id = str(int(history['user_id']))
					user = User.objects.get(pk=user_id)
					if 'course_id' in history:
						course_id = str(int(history['course_id']))
						course = Course.objects.get(pk=course_id)

					page = {}
					page['url'] = history['url']
					if course:
						page['name'] = course.name
						page['description'] = course.name
					else:
						page['name'] = ''
						page['description'] = ''
					
					geolocation = {
						'lat': history['lat'],
						'lon': history['lon']
					}
					timestamp = time.gmtime(history['timestamp']/1000)
					learnerAccessAPage(user, page, geolocation, timestamp)
				except:
					self.error('ERROR sending a statement for user %s in history with timestamp %s' % (history['user_id'], time.strftime("%d/%m/%Y %H:%M:%S", timestamp)))
					continue

				bar.update()

			self.message('History succesfully exported')
