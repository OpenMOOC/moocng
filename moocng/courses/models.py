import urlparse

from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from moocng.videos.download import process_video


class Course(models.Model):

    name = models.CharField(verbose_name=_(u'Name'), max_length=200)
    slug = models.SlugField(verbose_name=_(u'Slug'))
    description = models.TextField(verbose_name=_(u'Description'))
    requirements = models.TextField(verbose_name=_(u'Requirements'),
                                    blank=True, null=False)
    learning_goals = models.TextField(verbose_name=_(u'Learning goals'),
                                      blank=True, null=False)
    teachers = models.ManyToManyField(User, verbose_name=_(u'Teachers'),
                                      related_name='course_teachers')
    students = models.ManyToManyField(User, verbose_name=_(u'Students'),
                                      related_name='course_students',
                                      blank=True)
    promotion_video = models.URLField(verbose_name=_(u'Promotion video'),
                                      blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('course_overview', [self.slug])

    def get_embeded_code_for_promotion_video(self):
        if self.promotion_video:
            parts = urlparse.urlparse(self.promotion_video)
            if parts.query:
                params = urlparse.parse_qs(parts.query)
                if params and 'v' in params:
                    return params['v'][0]


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

    UNIT_TYPES = (
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


def handle_kq_post_save(sender, instance, created, **kwargs):
    # TODO Use Celery to process the video asynchronously
    try:
        question = Question.objects.get(kq=instance)
        process_video(question)
    except Question.DoesNotExist:
        pass


signals.post_save.connect(handle_kq_post_save, sender=KnowledgeQuantum)


class Question(models.Model):

    kq = models.ForeignKey(KnowledgeQuantum,
                           verbose_name=_(u'Knowledge Quantum'))
    solution = models.URLField(verbose_name=_(u'Solution video'))
    last_frame = models.ImageField(verbose_name=_(u'Question Last Frame'),
                                   upload_to='questions', blank=True,
                                   editable=False)


def handle_question_post_save(sender, instance, created, **kwargs):
    # TODO Use Celery to process the video asynchronously
    if created:
        process_video(instance)


signals.post_save.connect(handle_question_post_save, sender=Question)


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
