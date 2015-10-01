# -*- coding: utf-8 -*-

import requests
import sys
import json
import re
import time
from optparse import make_option

import pyprind

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from moocng.users.models import User
from moocng.courses.models import Course, CourseStudent, KnowledgeQuantum
from moocng.x_api.utils import learnerAccessAPage, learnerEnrollsInMooc
from moocng import mongodb

class Command(BaseCommand):
	option_list = BaseCommand.option_list + (
		make_option('-k', '--kqset',
					action='store',
					dest='kq_toset',
					default='',
					help='KQ to set as completed'),
		make_option('-c', '--kqcond',
					action='store',
					dest='kq_tocheck',
					default='',
					help='KQ to check'),
	)
	activity_col = mongodb.get_db().get_collection('activity')
	act_created = 0

	def error(self, message):
		self.stderr.write("%s\n" % message.encode("ascii", "replace"))

	def message(self, message):
		self.stdout.write("%s\n" % message.encode("ascii", "replace"))

	def createActivity(self, user, kq):
		statement = {
			'user_id': user.id,
			'timestamp': int(round(time.time() * 1000)),
			'course_id': kq.unit.course.id,
			'unit_id': kq.unit.id,
			'kq_id': kq.id
		}
		self.activity_col.insert(statement)
		self.act_created += 1

	def handle(self, *args, **options):
		try:
			kq_toset = KnowledgeQuantum.objects.get(pk=options['kq_toset'])
			course = kq_toset.unit.course
			students = course.students.all()
			self.message('The course %s has %d students' % (course.name, students.count()))
			bar = pyprind.ProgBar(students.count())
			if 'kq_tocheck' in options and options['kq_tocheck']:
				kq_id_tocheck = int(options['kq_tocheck'])
				for student in students:
					if self.activity_col.find({'user_id': student.id, 'kq_id': kq_id_tocheck}).count():
						if not self.activity_col.find({'user_id': student.id, 'kq_id': kq_toset.id}).count():
							self.createActivity(student, kq_toset)
					bar.update()
			else:
				for student in students:
					if not self.activity_col.find({'user_id': student.id, 'kq_id': kq_toset.id}).count():
						self.createActivity(student, kq_toset)
					bar.update()
			self.message('%d students affected' % (self.act_created))
		except KeyError:
			self.error('You must specify a KQ to set as completed')
