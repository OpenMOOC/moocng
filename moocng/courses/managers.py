import datetime

from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet


class CourseQuerySet(QuerySet):

    def actives(self):
        now = datetime.datetime.now()
        date_filters = (models.Q(**{'end_date__isnull': True}) |
                        models.Q(**{'end_date__gte': now}),
                        models.Q(**{'start_date__isnull': True}) |
                        models.Q(**{'start_date__lte': now}))
        return self.filter(status='p').filter(*date_filters)


class CourseManager(models.Manager):

    def get_query_set(self):
        return CourseQuerySet(self.model, using=self._db)

    def actives(self):
        return self.get_query_set().actives()

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class UnitQuerySet(QuerySet):

    def scorables(self):
        if not settings.COURSES_USING_OLD_TRANSCRIPT:
            return self.exclude(unittype='n')
        return self.all()


class UnitManager(models.Manager):

    def get_query_set(self):
        return UnitQuerySet(self.model, using=self._db)

    def scorables(self):
        return self.get_query_set().scorables()

    def get_by_natural_key(self, course_slug, title):
        return self.get(title=title, course__slug=course_slug)


class KnowledgeQuantumManager(models.Manager):

    def get_by_natural_key(self, course_slug, unit_title, title):
        return self.get(title=title, unit__title=unit_title, unit__course__slug=course_slug)


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
