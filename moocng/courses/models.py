from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Course(models.Model):

    name = models.CharField(verbose_name=_(u'Name'), max_length=200)
    slug = models.SlugField(verbose_name=_(u'Slug'))
    teachers = models.ManyToManyField(User, verbose_name=_(u'Teachers'),
                                      related_name='course_teachers')
    students = models.ManyToManyField(User, verbose_name=_(u'Students'),
                                      related_name='course_students')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('course_overview', (str(self.id), ))


class Announcement(models.Model):

    title = models.CharField(verbose_name=_(u'Title'), max_length=200)
    slug = models.SlugField(verbose_name=_(u'Slug'))
    content = models.TextField(verbose_name=_(u'Content'))
    course = models.ForeignKey(Course, verbose_name=_(u'Course'))
    datetime = models.DateTimeField(verbose_name=_(u'Datetime'))

    def __unicode__(self):
        return self.title


class Unit(models.Model):

    title = models.CharField(verbose_name=_(u'Title'), max_length=200)
    course = models.ForeignKey(Course, verbose_name=_(u'Course'))

    UNIT_TYPES=(
        ('n', u'Normal'),
        ('h', u'Homeworks'),
        ('e', u'Exam'),
        )
    unittype = models.CharField(verbose_name=_(u'Type'), choices=UNIT_TYPES,
                                max_length=1)
    deadline = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.unittype)


class KnowledgeQuantum(models.Model):

    title = models.CharField(verbose_name=_(u'Title'), max_length=200)
    unit = models.ForeignKey(Unit, verbose_name=_(u'Unit'))
    video = models.URLField(verbose_name=_(u'Video'))

    def __unicode__(self):
        return self.title


class Question(models.Model):

    kq = models.ForeignKey(KnowledgeQuantum,
                           verbose_name=_(u'Knowledge Quantum'))
    solution = models.URLField(verbose_name=_(u'Solution video'))


class Option(models.Model):

    question = models.ForeignKey(Question, verbose_name=_(u'Question'))
    x = models.PositiveSmallIntegerField(default=0)
    y = models.PositiveSmallIntegerField(default=0)

    OPTION_TYPES = (
        ('i', u'Input box'),
        ('c', u'Check box'),
        ('r', u'Radio button'),
        )
    optiontype = models.CharField(verbose_name=_(u'Type'), max_length=1,
                                  choices=OPTION_TYPES,
                                  default=OPTION_TYPES[0][0])

    def __unicode__(self):
        return u'%s at %s x %s' % (self.optiontype, self.x, self.y)
