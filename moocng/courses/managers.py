import datetime

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from modeltranslation.manager import MultilingualQuerySet

class CourseQuerySet(MultilingualQuerySet):

    def by_status(self, status):
        return self.filter(status=status)

    def public(self):
        # If you change it, you should change the is_public property in Course model
        return self.filter(status__in=['h', 'p'])

    def published(self):
        return self.by_status('p')

    def draft(self):
        return self.by_status('d')

    def hidden(self):
        return self.by_status('h')

    def actives(self):
        # If you change it, you should change the is_active property in Course model
        today = datetime.datetime.today()
        date_filters = (Q(**{'end_date__isnull': True}) |
                        Q(**{'start_date__isnull': True, 'end_date__gte': today}) |
                        Q(**{'start_date__lte': today, 'end_date__gte': today}))
        return self.filter(date_filters).public()


class CourseManager(models.Manager):

    def get_query_set(self):
        return CourseQuerySet(self.model, using=self._db)

    def by_status(self, status):
        return self.get_query_set().by_status(status)

    def public(self):
        return self.get_query_set().public()

    def actives(self):
        return self.get_query_set().actives()

    def published(self):
        return self.get_query_set().published()

    def draft(self):
        return self.get_query_set().draft()

    def hidden(self):
        return self.get_query_set().hidden()

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class UnitQuerySet(MultilingualQuerySet):

    def scorables(self):
        if not settings.COURSES_USING_OLD_TRANSCRIPT:
            return self.filter(~Q(unittype='n') | ~Q(weight=0) | ~Q(status='d'))
        return self.filter(~Q(status='d'))


class UnitManager(models.Manager):

    def get_query_set(self):
        return UnitQuerySet(self.model, using=self._db)

    def scorables(self):
        #return self.get_query_set().scorables()
        if not settings.COURSES_USING_OLD_TRANSCRIPT:
            return self.filter(~Q(unittype='n') | ~Q(weight=0) | ~Q(status='d'))
        return self.filter(~Q(status='d'))

    def get_by_natural_key(self, course_slug, title):
        return self.get(title=title, course__slug=course_slug)


class KnowledgeQuantumManager(models.Manager):

    def get_by_natural_key(self, course_slug, unit_title, title):
        return self.get(title=title, unit__title=unit_title, unit__course__slug=course_slug)

class TranscriptionManager(models.Manager):

    def get_by_natural_key(self, course_slug, unit_title, kq_title, filename_name):
        return self.get(kq__title=kq_title, kq__unit__title=unit_title, kq__unit__course__slug=course_slug, filename=filename_name)

class AttachmentManager(models.Manager):

    def get_by_natural_key(self, course_slug, unit_title, kq_title, attachment_name):
        return self.get(kq__title=kq_title, kq__unit__title=unit_title, kq__unit__course__slug=course_slug, attachment=attachment_name)


class QuestionManager(models.Manager):

    def get_by_natural_key(self, course_slug, unit_title, kq_title):
        return self.get(kq__title=kq_title, kq__unit__title=unit_title, kq__unit__course__slug=course_slug)


class OptionManager(models.Manager):

    def get_by_natural_key(self, course_slug, unit_title, kq_title, x, y):
        return self.get(question__kq__title=kq_title,
                        question__kq__unit__title=unit_title,
                        question__kq__unit__course__slug=course_slug,
                        x=x,
                        y=y)


class AnnouncementQuerySet(QuerySet):

    def portal(self):
        return self.filter(course__isnull=True)


class AnnouncementManager(models.Manager):

    def get_query_set(self):
        return AnnouncementQuerySet(self.model, using=self._db)

    def portal(self):
        return self.get_query_set().portal()
