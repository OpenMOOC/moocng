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

import logging

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator
from django.db import models
from django.db import transaction
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from adminsortable.models import Sortable
from adminsortable.fields import SortableForeignKey
from tinymce.models import HTMLField

from moocng.badges.models import Badge
from moocng.courses.cache import invalidate_template_fragment
from moocng.enrollment import enrollment_methods
from moocng.mongodb import get_db
from moocng.videos.tasks import process_video_task
from moocng.videos.utils import extract_YT_video_id

logger = logging.getLogger(__name__)


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
                                      through='CourseTeacher',
                                      related_name='courses_as_teacher')
    owner = models.ForeignKey(User, verbose_name=_(u'Teacher owner'),
                              related_name='courses_as_owner', blank=False,
                              null=False)
    students = models.ManyToManyField(User, verbose_name=_(u'Students'),
                                      related_name='courses_as_student',
                                      blank=True)
    promotion_video = models.URLField(verbose_name=_(u'Promotion video'),
                                      blank=True)
    threshold = models.DecimalField(
        verbose_name=_(u'Pass threshold'),
        max_digits=4, decimal_places=2,
        blank=True, null=True, help_text="0.00 - 10.00")
    certification_available = models.BooleanField(
        default=False,
        verbose_name=_(u'Certification available'))
    certification_banner = models.ImageField(
        verbose_name=_(u'Certification banner'),
        upload_to='certification_banners', blank=True, null=True)
    completion_badge = models.ForeignKey(
        Badge, blank=True, null=True, verbose_name=_(u'Completion badge'),
        related_name='course', unique=True)
    enrollment_method = models.CharField(
        verbose_name=_(u'Enrollment method'),
        choices=enrollment_methods.get_choices(),
        max_length=200,
        default='free')

    COURSE_STATUSES = (
        ('d', _(u'Draft')),
        ('p', _(u'Published')),
    )

    status = models.CharField(
        verbose_name=_(u'Status'),
        choices=COURSE_STATUSES,
        max_length=10,
        default=COURSE_STATUSES[0][0],
    )

    class Meta(Sortable.Meta):
        verbose_name = _(u'course')
        verbose_name_plural = _(u'courses')
        permissions = (
            ("can_list_allcourses", _("Can list courses of an user")),
            ("can_list_passedcourses", _("Can list passed courses of an user")),
        )

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('course_overview', [self.slug])

    def get_embeded_code_for_promotion_video(self):
        if self.promotion_video:
            return extract_YT_video_id(self.promotion_video)

    @property
    def is_public(self):
        return self.status == 'p'


def course_invalidate_cache(sender, instance, **kwargs):
    invalidate_template_fragment('course_list')
    invalidate_template_fragment('course_overview_main_info', instance.id)
    invalidate_template_fragment('course_overview_secondary_info', instance.id)


signals.post_save.connect(course_invalidate_cache, sender=Course)
signals.post_delete.connect(course_invalidate_cache, sender=Course)


class CourseTeacher(Sortable):

    teacher = models.ForeignKey(User, verbose_name=_(u'Teacher'))
    course = SortableForeignKey(Course, verbose_name=_(u'Course'))

    class Meta(Sortable.Meta):
        verbose_name = _(u'course teacher')
        verbose_name_plural = _(u'course teachers')


def courseteacher_invalidate_cache(sender, instance, **kwargs):
    try:
        invalidate_template_fragment('course_overview_secondary_info',
                                     instance.course.id)
    except Course.DoesNotExist:
        # The course is being deleted, nothing to invalidate
        pass

signals.post_save.connect(courseteacher_invalidate_cache, sender=CourseTeacher)
signals.post_delete.connect(courseteacher_invalidate_cache,
                            sender=CourseTeacher)


class Announcement(models.Model):

    title = models.CharField(verbose_name=_(u'Title'), max_length=200)
    slug = models.SlugField(verbose_name=_(u'Slug'))
    content = HTMLField(verbose_name=_(u'Content'))
    course = models.ForeignKey(Course, verbose_name=_(u'Course'))
    datetime = models.DateTimeField(verbose_name=_(u'Datetime'),
                                    auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _(u'announcement')
        verbose_name_plural = _(u'announcements')

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('announcement_detail', [self.course.slug, self.id, self.slug])


def announcement_invalidate_cache(sender, instance, **kwargs):
    invalidate_template_fragment('course_overview_secondary_info', instance.course.id)


signals.post_save.connect(announcement_invalidate_cache, sender=Announcement)
signals.post_delete.connect(announcement_invalidate_cache, sender=Announcement)


class Unit(Sortable):
    title = models.CharField(verbose_name=_(u'Title'), max_length=200)
    course = SortableForeignKey(Course, verbose_name=_(u'Course'))

    UNIT_TYPES = (
        ('n', _(u'Normal')),
        ('h', _(u'Homework')),
        ('e', _(u'Exam')),
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
    weight = models.SmallIntegerField(verbose_name=_(u'Weight'), null=False,
                                      default=0,
                                      help_text='0-100%',
                                      validators=[MaxValueValidator(100)])

    UNIT_STATUSES = (
        ('d', _(u'Draft')),
        ('l', _(u'Listable')),
        ('p', _(u'Published')),
    )

    status = models.CharField(
        verbose_name=_(u'Status'),
        choices=UNIT_STATUSES,
        max_length=10,
        default=UNIT_STATUSES[0][0],
    )

    class Meta(Sortable.Meta):
        verbose_name = _(u'unit')
        verbose_name_plural = _(u'units')

    def __unicode__(self):
        return u'%s - %s (%s)' % (self.course, self.title, self.unittype)

    def get_unit_type_name(self):
        for t in self.UNIT_TYPES:
            if t[0] == self.unittype:
                return t[1]


def unit_invalidate_cache(sender, instance, **kwargs):
    try:
        invalidate_template_fragment('course_overview_secondary_info',
                                     instance.course.id)
    except Course.DoesNotExist:
        # The course is being deleted, nothing to invalidate
        pass


signals.post_save.connect(unit_invalidate_cache, sender=Unit)
signals.post_delete.connect(unit_invalidate_cache, sender=Unit)


class KnowledgeQuantum(Sortable):

    title = models.CharField(verbose_name=_(u'Title'), max_length=200)
    unit = SortableForeignKey(Unit, verbose_name=_(u'Unit'))
    weight = models.SmallIntegerField(verbose_name=_(u'Weight'), null=False,
                                      default=0,
                                      help_text='0-100%',
                                      validators=[MaxValueValidator(100)])
    video = models.URLField(verbose_name=_(u'Video'))
    teacher_comments = HTMLField(verbose_name=_(u'Teacher comments'),
                                 blank=True, null=False)
    supplementary_material = HTMLField(
        verbose_name=_(u'Supplementary material'),
        blank=True, null=False)

    def is_completed(self, user):
        if not self.kq_visited_by(user):
            return False

        questions = self.question_set.filter()
        if len(questions):
            return questions[0].is_completed(user, visited=True)

        try:
            return self.peerreviewassignment.is_completed(user, visited=True)
        except ObjectDoesNotExist:
            pass

        return True

    def kq_visited_by(self, user):
        db = get_db()

        activity = db.get_collection("activity")
        # Verify if user has watch the video from kq
        user_activity_exists = activity.find({
            "user": user.id,
            "courses.%s.kqs" % (self.unit.course.id): unicode(self.id)
        })

        return user_activity_exists.count() > 0

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
    solution_video = models.URLField(
        verbose_name=_(u'Solution video'),
        help_text=_(u'If this belongs to a homework or an exam, then the '
                    u'stundents won\'t see this video until the deadline is '
                    u'reached.'),
        blank=True, null=False)
    solution_text = HTMLField(
        verbose_name=_(u'Solution text'),
        help_text=_(u'If the solution video is specified then this text will '
                    u'be ignored.'),
        blank=True, null=False)
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
        return ugettext(u'{0} - Question {1}').format(self.kq, self.id)

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

    def is_completed(self, user, visited=None):
        db = get_db()

        if visited is None:
            visited = self.kq.kq_visited_by(user)
            if not visited:
                return False

        # Verify if user has answered the question
        answers = db.get_collection("answers")
        answers_exists = answers.find_one({
            "user": user.id,
            "questions.%s" % (self.id): {
                "$exists": True
            }
        })

        if not answers_exists:
            return False

        return True


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
    feedback = models.CharField(
        verbose_name=_(u'Solution feedback for the student'), max_length=200,
        blank=True, null=False)

    class Meta:
        verbose_name = _(u'option')
        verbose_name_plural = _(u'options')

    def __unicode__(self):
        return ugettext(u'{0} at {1} x {2}').format(self.optiontype, self.x, self.y)

    def is_correct(self, reply):
        if self.optiontype == 'l':
            return True
        elif self.optiontype == 't':
            if not hasattr(reply, 'lower'):
                logger.error('Error at option %s - Value %s - Solution %s' % (str(self.id), str(reply), self.solution))
                return True
            else:
                return reply.lower() == self.solution.lower()
        else:
            return bool(reply) == (self.solution.lower() == u'true')
