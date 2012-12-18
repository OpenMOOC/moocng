# Copyright 2012 Rooter Analysis S.L.
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

from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from adminsortable.models import Sortable
from adminsortable.fields import SortableForeignKey
from tinymce.models import HTMLField

from moocng.courses.fields import PercentField
from moocng.videos.tasks import process_video_task
from moocng.videos.utils import extract_YT_video_id


class Course(Sortable):

    name = models.CharField(verbose_name=_(u'Name'), max_length=200)
    slug = models.SlugField(verbose_name=_(u'Slug'))
    description = HTMLField(verbose_name=_(u'Description'))
    requirements = HTMLField(verbose_name=_(u'Requirements'),
                             blank=True, null=False)
    learning_goals = HTMLField(verbose_name=_(u'Learning goals'),
                               blank=True, null=False)
    intended_audience = HTMLField(verbose_name=_(u'Intended audience'),
                                  blank=True, null=True)
    estimated_effort = HTMLField(verbose_name=_(u'Estimated effort'),
                                 blank=True, null=True)
    learning_goals = HTMLField(verbose_name=_(u'Learning goals'),
                               blank=True, null=False)
    start_date = models.DateField(verbose_name=_(u'Start date'),
                                  blank=True, null=True)
    end_date = models.DateField(verbose_name=_(u'End date'),
                                blank=True, null=True)
    teachers = models.ManyToManyField(User, verbose_name=_(u'Teachers'),
                                      related_name='courses_as_teacher')
    owner = models.ForeignKey(User, verbose_name=_(u'Teacher owner'),
                              related_name='courses_as_owner', blank=False,
                              null=False)
    students = models.ManyToManyField(User, verbose_name=_(u'Students'),
                                      related_name='courses_as_student',
                                      blank=True)
    promotion_video = models.URLField(verbose_name=_(u'Promotion video'),
                                      blank=True)

    class Meta(Sortable.Meta):
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


def handle_course_m2m_changed(sender, instance, action, **kwargs):
    if action.startswith('post') and not instance.teachers.filter(id=instance.owner.id).exists():
        instance.teachers.add(instance.owner)


signals.m2m_changed.connect(handle_course_m2m_changed, sender=Course.teachers.through)


class Announcement(models.Model):

    title = models.CharField(verbose_name=_(u'Title'), max_length=200)
    slug = models.SlugField(verbose_name=_(u'Slug'), unique=True)
    content = HTMLField(verbose_name=_(u'Content'))
    course = models.ForeignKey(Course, verbose_name=_(u'Course'))
    datetime = models.DateTimeField(
        verbose_name=_(u'Datetime'),
        help_text=_(u"Use format:  DD/MM/AAAA 00:00"))

    class Meta:
        verbose_name = _(u'announcement')
        verbose_name_plural = _(u'announcements')

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('announcement_detail', [self.course.slug, self.slug])


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
    start = models.DateTimeField(verbose_name=_(u'Start'),
                                 null=True, blank=True,
                                 help_text=_(u'Until this date is reached, no '
                                             u'contents of this module will '
                                             u'be shown to the students.'))
    deadline = models.DateTimeField(verbose_name=_(u'Deadline'),
                                    null=True, blank=True,
                                    help_text=_(u'Until this date is reached, '
                                                u'the students will be able '
                                                u'to modify their answers, '
                                                u"but won't see the solution"))
    weight = PercentField(verbose_name=_(u'Weight'), null=False, default=0,
                          help_text='0-100%')

    class Meta(Sortable.Meta):
        verbose_name = _(u'unit')
        verbose_name_plural = _(u'units')

    def __unicode__(self):
        return u'%s - %s (%s)' % (self.course, self.title, self.unittype)


class KnowledgeQuantum(Sortable):

    title = models.CharField(verbose_name=_(u'Title'), max_length=200)
    unit = SortableForeignKey(Unit, verbose_name=_(u'Unit'))
    weight = PercentField(verbose_name=_(u'Weight'), null=False, default=0,
                          help_text='0-100%')
    video = models.URLField(verbose_name=_(u'Video'))
    teacher_comments = HTMLField(verbose_name=_(u'Teacher comments'),
                                 blank=True, null=False)
    supplementary_material = HTMLField(
        verbose_name=_(u'Supplementary material'),
        blank=True, null=False)

    class Meta(Sortable.Meta):
        verbose_name = _(u'nugget')
        verbose_name_plural = _(u'nuggets')

    def __unicode__(self):
        return u'%s - %s' % (self.unit, self.title)


def handle_kq_post_save(sender, instance, created, **kwargs):
    if transaction.is_dirty():
        transaction.commit()
    question_list = instance.question_set.all()
    if len(question_list) > 0:
        process_video_task.delay(question_list[0].id)


signals.post_save.connect(handle_kq_post_save, sender=KnowledgeQuantum)


class Attachment(models.Model):

    kq = models.ForeignKey(KnowledgeQuantum,
                           verbose_name=_(u'Nugget'))
    attachment = models.FileField(verbose_name=_(u'Attachment'),
                                  upload_to='attachments')


class Question(models.Model):

    kq = models.ForeignKey(KnowledgeQuantum, unique=True,
                           verbose_name=_(u'Nugget'))
    solution = models.URLField(verbose_name=_(u'Solution video'),
                               help_text=_(u'If this belongs to a homework or '
                                           u'an exam, then the stundents '
                                           u"won't see this video until the "
                                           u'deadline is reached.'))
    last_frame = models.ImageField(
        verbose_name=_(u"Last frame of the nugget's video"),
        upload_to='questions', blank=True)

    use_last_frame = models.BooleanField(
        verbose_name=_(u'Use the last frame of the video'),
        help_text=_(u'Chooses if the nugget\'s video last frame is used, or a '
                    u'white canvas instead.'),
        default=True, blank=False, null=False)

    class Meta:
        verbose_name = _(u'question')
        verbose_name_plural = _(u'questions')

    def __unicode__(self):
        return u'%s - Question %d' % (self.kq, self.id)

    def is_correct(self, answer):
        correct = True
        replies = dict([(int(r['option']),
                         r['value']) for r in answer['replyList']])

        for option in self.option_set.all():
            reply = replies.get(option.id, None)
            if reply is None:
                return False

            correct = correct and option.is_correct(reply)

        return correct


def handle_question_post_save(sender, instance, created, **kwargs):
    if created:
        process_video_task.delay(instance.id)


signals.post_save.connect(handle_question_post_save, sender=Question)


class Option(models.Model):

    question = models.ForeignKey(Question, verbose_name=_(u'Question'))
    x = models.PositiveSmallIntegerField(default=0)
    y = models.PositiveSmallIntegerField(default=0)
    width = models.PositiveSmallIntegerField(default=100)
    height = models.PositiveSmallIntegerField(default=12)

    OPTION_TYPES = (
        ('t', u'Input box'),
        ('c', u'Check box'),
        ('r', u'Radio button'),
        ('l', u'Label'),
    )
    optiontype = models.CharField(verbose_name=_(u'Type'), max_length=1,
                                  choices=OPTION_TYPES,
                                  default=OPTION_TYPES[0][0])
    solution = models.CharField(verbose_name=_(u'Solution'), max_length=200)
    text = models.CharField(verbose_name=_(u'Label text'), max_length=500,
                            blank=True, null=True)

    class Meta:
        verbose_name = _(u'option')
        verbose_name_plural = _(u'options')

    def __unicode__(self):
        return u'%s at %s x %s' % (self.optiontype, self.x, self.y)

    def is_correct(self, reply):
        if self.optiontype == 'l':
            return True
        elif self.optiontype == 't':
            return reply == self.solution
        else:
            return bool(reply) == (self.solution.lower() == u'true')
