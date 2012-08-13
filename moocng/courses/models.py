from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from adminsortable.models import Sortable
from adminsortable.fields import SortableForeignKey
from tinymce.models import HTMLField

from moocng.courses.utils import extract_YT_video_id
from moocng.videos.tasks import process_video_task


class Course(models.Model):

    name = models.CharField(verbose_name=_(u'Name'), max_length=200)
    slug = models.SlugField(verbose_name=_(u'Slug'))
    description = HTMLField(verbose_name=_(u'Description'))
    requirements = HTMLField(verbose_name=_(u'Requirements'),
                             blank=True, null=False)
    learning_goals = HTMLField(verbose_name=_(u'Learning goals'),
                               blank=True, null=False)
    teachers = models.ManyToManyField(User, verbose_name=_(u'Teachers'),
                                      related_name='courses_as_teacher')
    students = models.ManyToManyField(User, verbose_name=_(u'Students'),
                                      related_name='courses_as_student',
                                      blank=True)
    promotion_video = models.URLField(verbose_name=_(u'Promotion video'),
                                      blank=True)

    class Meta:
        verbose_name = _(u'course')
        verbose_name_plural = _(u'courses')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('course_overview', [self.slug])

    def get_embeded_code_for_promotion_video(self):
        if self.promotion_video:
            return extract_YT_video_id(self.promotion_video)


class Announcement(models.Model):

    title = models.CharField(verbose_name=_(u'Title'), max_length=200)
    slug = models.SlugField(verbose_name=_(u'Slug'))
    content = HTMLField(verbose_name=_(u'Content'))
    course = models.ForeignKey(Course, verbose_name=_(u'Course'))
    datetime = models.DateTimeField(verbose_name=_(u'Datetime'))

    class Meta:
        verbose_name = _(u'announcement')
        verbose_name_plural = _(u'announcements')

    def __unicode__(self):
        return self.title


class Unit(Sortable):
    title = models.CharField(verbose_name=_(u'Title'), max_length=200)
    course = SortableForeignKey(Course, verbose_name=_(u'Course'))

    UNIT_TYPES = (
        ('n', u'Normal'),
        ('h', u'Homeworks'),
        ('e', u'Exam'),
    )
    unittype = models.CharField(verbose_name=_(u'Type'), choices=UNIT_TYPES,
                                max_length=1, default=UNIT_TYPES[0][0])
    deadline = models.DateTimeField(verbose_name=_(u'Deadline'),
                                    null=True, blank=True)

    class Meta(Sortable.Meta):
        verbose_name = _(u'unit')
        verbose_name_plural = _(u'units')

    def __unicode__(self):
        return u'%s - %s (%s)' % (self.course, self.title, self.unittype)


class KnowledgeQuantum(Sortable):

    title = models.CharField(verbose_name=_(u'Title'), max_length=200)
    unit = SortableForeignKey(Unit, verbose_name=_(u'Unit'))
    video = models.URLField(verbose_name=_(u'Video'))

    class Meta(Sortable.Meta):
        verbose_name = _(u'knowledge quantum')
        verbose_name_plural = _(u'knowledge quantums')

    def __unicode__(self):
        return u'%s - %s' % (self.unit, self.title)


def handle_kq_post_save(sender, instance, created, **kwargs):
    question_list = instance.question_set.all()
    if len(question_list) > 0:
        process_video_task.delay(question_list[0])


signals.post_save.connect(handle_kq_post_save, sender=KnowledgeQuantum)


class Question(models.Model):

    kq = models.ForeignKey(KnowledgeQuantum, unique=True,
                           verbose_name=_(u'Knowledge Quantum'))
    solution = models.URLField(verbose_name=_(u'Solution video'))
    last_frame = models.ImageField(
        verbose_name=_(u'Last frame of the question video'),
        upload_to='questions', blank=True, editable=False)

    class Meta:
        verbose_name = _(u'question')
        verbose_name_plural = _(u'questions')

    def __unicode__(self):
        return u'%s - Question' % self.kq


def handle_question_post_save(sender, instance, created, **kwargs):
    if created:
        process_video_task.delay(instance)


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

    class Meta:
        verbose_name = _(u'option')
        verbose_name_plural = _(u'options')

    def __unicode__(self):
        return u'%s at %s x %s' % (self.optiontype, self.x, self.y)
