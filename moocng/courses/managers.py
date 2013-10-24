from django.db import models


class CourseManager(models.Manager):

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class UnitManager(models.Manager):

    def get_by_natural_key(self, course_slug, title):
        return self.get(title=title, course__slug=course_slug)


class KnowledgeQuantumManager(models.Manager):

    def get_by_natural_key(self, course_slug, unit_title, title):
        return self.get(title=title, unit__title=unit_title, unit__course__slug=course_slug)


class AttachmentManager(models.Manager):

    def get_by_natural_key(self, attachment_name):
        return self.get(attachment=attachment_name)


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
