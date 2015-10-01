# -*- coding: utf-8 -*-
# Copyright 2012-2013 UNED
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

import datetime
import logging

from PIL import Image, ImageOps

from django.conf import settings
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
from moocng.courses.cache import invalidate_template_fragment_i18n
from moocng.courses.managers import (CourseManager, UnitManager,
                                     KnowledgeQuantumManager, QuestionManager,
                                     OptionManager, TranscriptionManager,
                                     AttachmentManager, AnnouncementManager)
from moocng.enrollment import enrollment_methods
from moocng.mongodb import get_db
from moocng.videos.tasks import process_video_task
from moocng.media_contents import get_media_content_types_choices, media_content_extract_id

from itertools import groupby

logger = logging.getLogger(__name__)


class Language(models.Model):
    name = models.CharField(verbose_name=_(u'Name'), max_length=200)
    abbr = models.CharField(verbose_name=_(u'Abbr'), max_length=2, null=True)

    def __unicode__(self):
        return self.name


class Course(Sortable):
    THUMBNAIL_WIDTH = 300
    THUMBNAIL_HEIGHT = 200
    BACKGROUND_WIDTH = 1920
    BACKGROUND_HEIGHT = 400

    name = models.CharField(verbose_name=_(u'Name'), max_length=200)
    slug = models.SlugField(verbose_name=_(u'Slug'), unique=True, db_index=True)
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

    ects = models.PositiveSmallIntegerField(verbose_name=_(u'ECTS:'),
                                                              default=8)

    teachers = models.ManyToManyField(User, verbose_name=_(u'Teachers'),
                                      through='CourseTeacher',
                                      related_name='courses_as_teacher')

    owner = models.ForeignKey(User, verbose_name=_(u'Teacher owner'),
                              related_name='courses_as_owner', blank=False,
                              null=False)

    students = models.ManyToManyField(User, verbose_name=_(u'Students'),
                                      through='CourseStudent',
                                      related_name='courses_as_student',
                                      blank=True)

    languages = models.ManyToManyField(Language,
                                       verbose_name=_(u'Language')
                                       )

    estimated_effort = models.CharField(verbose_name=_(u'Estimated effort'),
                                 null = True,
                                 blank=True,
                                 max_length=128)

    hashtag = models.CharField(verbose_name=_(u'Hashtag'),
                                default='Hashtag',
                                max_length=128)

    promotion_media_content_type = models.CharField(verbose_name=_(u'Content type'),
                                                    max_length=20,
                                                    null=True,
                                                    blank=True,
                                                    choices=get_media_content_types_choices())
    promotion_media_content_id = models.CharField(verbose_name=_(u'Content id'),
                                                  null=True,
                                                  blank=True,
                                                  max_length=200)

    forum_slug = models.CharField(verbose_name=_(u'Forum slug'),
                                    null=True,
                                    blank=True,
                                    max_length=350)

    threshold = models.DecimalField(
        verbose_name=_(u'Pass threshold'),
        max_digits=4, decimal_places=2,
        blank=True, null=True, help_text="0.00 - 10.00")
    certification_available = models.BooleanField(
        default=False,
        verbose_name=_(u'Certification available'))
    external_certification_available = models.BooleanField(
        default=False,
        verbose_name=_(u'External certification available'))
    certification_file = models.FileField(verbose_name=_(u'Certification file'),
        upload_to='certifications',
        null=True,
        blank=True)
    completion_badge = models.ForeignKey(
        Badge, blank=True, null=True, verbose_name=_(u'Completion badge'),
        related_name='course')
    enrollment_method = models.CharField(
        verbose_name=_(u'Enrollment method'),
        choices=enrollment_methods.get_choices(),
        max_length=200,
        default='free')

    COURSE_STATUSES = (
        ('d', _(u'Draft')),
        ('p', _(u'Published')),
        ('h', _(u'Hidden')),
        ('o', _(u'Always Open')),
    )

    status = models.CharField(
        verbose_name=_(u'Status'),
        choices=COURSE_STATUSES,
        max_length=10,
        default=COURSE_STATUSES[0][0],
    )
    thumbnail = models.ImageField(
        verbose_name=_(u'Thumbnail'),
        upload_to='course_thumbnails',
        blank=True,
        null=True
    )
    thumbnail_alt = models.CharField(verbose_name=_('thumbnail image alternative text'), max_length=200,
                                                 null=True, blank=True,
                                                 help_text=_('This text is used to describe the thumbnail image. '
                                                     'It is necessary for accessibility ')
                                                 )

    background = models.ImageField(
        verbose_name=_(u'Background'),
        upload_to='course_backgrounds',
        blank=True,
        null=True
    )

    static_page = models.OneToOneField(
        'StaticPage',
        verbose_name=_(u'Static page'),
        blank=True,
        null=True,
    )
    created_from = models.ForeignKey(
        'self',
        related_name='courses_created_of',
        verbose_name=_('Created from'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    is_activity_clonable = models.BooleanField(
        verbose_name=_('Is the activity student of this course clonable?'),
        default=False)
    max_mass_emails_month = models.PositiveSmallIntegerField(
        verbose_name=_('Maximum of massive emails that a course can send per month'),
        default=settings.DEFAULT_MAX_EMAILS_PER_MONTH)


    highlight = models.BooleanField(default=False)

    has_groups = models.BooleanField(verbose_name=_('Has this course groups?'),
                                    default=False)

    group_max_size = models.PositiveSmallIntegerField(verbose_name=_('Maximum number of members allowed for each group'),
        default=settings.DEFAULT_GROUP_MAX_SIZE)

    official_course = models.BooleanField(verbose_name=_('Is this course official?'),
                                          default=False)

    objects = CourseManager()

    class Meta(Sortable.Meta):
        verbose_name = _(u'course')
        verbose_name_plural = _(u'courses')
        permissions = (
            ("can_list_allcourses", _("Can list courses of an user")),
            ("can_list_passedcourses", _("Can list passed courses of an user")),
        )

    def natural_key(self):
        return (self.slug,)

    def get_user_mark(self,user):
        db = get_db()
        activity = db.get_collection("activity")

        mark = activity.find_one({
            "user_id": user.id,
            "course_id": self.id,
            "current" : True
        })

        kq = None
        if mark:
            try:
                kq = KnowledgeQuantum.objects.get(pk=mark["kq_id"])
            except KnowledgeQuantum.DoesNotExist:
                pass
        return kq

    def get_rating(self):
        course_student_set = CourseStudent.objects.filter(course=self)
        rating = 0
        num_students = len(course_student_set)
        if num_students > 0:
            for course_student in course_student_set:
                if course_student.rate is not None:
                    rating += course_student.rate

            rating = rating/num_students
        return rating


    def save(self, *args, **kwargs):
        if self.promotion_media_content_type and self.promotion_media_content_id:
            self.promotion_media_content_id = media_content_extract_id(self.promotion_media_content_type, self.promotion_media_content_id)
        super(Course, self).save(*args, **kwargs)
        if self.thumbnail:
            metadata = {
                'width': self.THUMBNAIL_WIDTH,
                'height': self.THUMBNAIL_HEIGHT,
                'force': True
            }
            image_path = self.thumbnail.path
            self._resize_image(image_path, metadata)

        if self.background:
            metadata = {
                'width': self.BACKGROUND_WIDTH,
                'height': self.BACKGROUND_HEIGHT,
                'force': True
            }
            image_path = self.background.path
            self._resize_image(image_path, metadata)

    def __unicode__(self):
        return self.name

    def can_clone_activity(self):
        return self.created_from and self.is_activity_clonable

    @models.permalink
    def get_absolute_url(self):
        return ('course_overview', [self.slug])

    @property
    def is_public(self):
        # If you change it, you should change the public method in CourseQuerySet class
        return self.status in ['p', 'o', 'h']

    @property
    def is_always_open(self):
        return self.status == 'o'

    @property
    def is_active(self):
        # If you change it, you should change the actives method in CourseQuerySet class
        today = datetime.date.today()
        return (self.is_public and
                (not self.end_date or
                 not self.start_date and self.end_date >= today or
                 self.start_date and self.start_date <= today and self.end_date >= today))

    @property
    def is_deactivated(self):
        today = datetime.date.today()
        return not (self.is_public and
                    (self.status == 'o' or
                    not self.end_date or
                    self.end_date >= today))

    @property
    def is_outdated(self):
        today = datetime.date.today()
        return (self.is_public and
                self.end_date < today and
                self.status != 'o')

    def _resize_image(self, filename, size):
        """
        ripped from:
        https://github.com/humanfromearth/django-stdimage/blob/master/stdimage/fields.py

        Resizes the image to specified width, height and force option

        Arguments::

        filename -- full path of image to resize
        size -- dictionary with
            - width: int
            - height: int
            - force: bool
                if True, image will be cropped to fit the exact size,
                if False, it will have the bigger size that fits the specified
                size, but without cropping, so it could be smaller on width
                or height

        """

        WIDTH, HEIGHT = 0, 1
        img = Image.open(filename)
        if (img.size[WIDTH] > size['width'] or
                img.size[HEIGHT] > size['height']):

            #If the image is big resize it with the cheapest resize algorithm
            factor = 1.61803398875
            while (img.size[0] / factor > 2 * size['width'] and
                    img.size[1] * 2 / factor > 2 * size['height']):
                factor *= 2
            if factor > 1:
                img.thumbnail((int(img.size[0] / factor),
                               int(img.size[1] / factor)), Image.NEAREST)

            if size['force']:
                img = ImageOps.fit(img, (size['width'], size['height']),
                                   Image.ANTIALIAS)
            else:
                img.thumbnail((size['width'], size['height']), Image.ANTIALIAS)
            try:
                img.save(filename, optimize=1, quality=60)
            except IOError:
                img.save(filename)


def course_invalidate_cache(sender, instance, **kwargs):
    invalidate_template_fragment_i18n('course_list')
    invalidate_template_fragment_i18n('course_overview_main_info', instance.id)
    invalidate_template_fragment_i18n('course_overview_secondary_info', instance.id)


def course_stats(sender, instance, created, **kwargs):
    if created:
        stats_course = get_db().get_collection('stats_course')
        stats_course.insert({
            'course_id': instance.id,
            'started': 0,
            'completed': 0,
            'passed': 0,
        }, data=True)


signals.post_save.connect(course_invalidate_cache, sender=Course)
signals.post_save.connect(course_stats, sender=Course)
signals.post_delete.connect(course_invalidate_cache, sender=Course)


class StaticPage(models.Model):

    title = models.CharField(
        verbose_name=_(u'Title'),
        max_length=100,
        blank=True,
        null=True
    )

    body = HTMLField(
        verbose_name=_(u'Body'),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _(u'Static page')
        verbose_name_plural = _(u'Static pages')

    def __unicode__(self):
        return self.title


class CourseTeacher(Sortable):

    teacher = models.ForeignKey(User, verbose_name=_(u'Teacher'))
    course = SortableForeignKey(Course, verbose_name=_(u'Course'))

    class Meta(Sortable.Meta):
        verbose_name = _(u'course teacher')
        verbose_name_plural = _(u'course teachers')


def courseteacher_invalidate_cache(sender, instance, **kwargs):
    try:
        invalidate_template_fragment_i18n('course_overview_secondary_info',
                                          instance.course.id)
    except Course.DoesNotExist:
        # The course is being deleted, nothing to invalidate
        pass

signals.post_save.connect(courseteacher_invalidate_cache, sender=CourseTeacher)
signals.post_delete.connect(courseteacher_invalidate_cache,
                            sender=CourseTeacher)


class CourseStudent(models.Model):

    student = models.ForeignKey(User, verbose_name=_(u'Student'))
    course = models.ForeignKey(Course, verbose_name=_(u'Course'))

    COURSE_STATUSES = (
        ('f', _(u'First time in this course')),
        ('n', _(u'No cloned')),
        ('c', _(u'Cloned')),
    )
    old_course_status = models.CharField(verbose_name=_(u'Old course status'),
                                         choices=COURSE_STATUSES,
                                         default='f',
                                         max_length=1)
    progress = models.IntegerField(verbose_name=_(u'Progress'),
                                        default=0)
    rate = models.PositiveSmallIntegerField(verbose_name=_(u'Rate'),
                                            null=True)
    timestamp = models.BigIntegerField(verbose_name=_(u'Enrollment timestamp'),
                                    null=True)
    pos_lat = models.FloatField(verbose_name=_(u'Latitude'),
                                default=0.0)
    pos_lon = models.FloatField(verbose_name=_(u'Longitude'),
                                default=0.0)

    class Meta:
        verbose_name = _(u'course student')
        verbose_name_plural = _(u'course students')

    def can_clone_activity(self):
        return self.course.can_clone_activity() and self.old_course_status == 'n'


class Announcement(models.Model):

    title = models.CharField(verbose_name=_(u'Title'), max_length=200)
    slug = models.SlugField(verbose_name=_(u'Slug'))
    content = HTMLField(verbose_name=_(u'Content'))
    course = models.ForeignKey(Course, verbose_name=_(u'Course'),
                               null=True, blank=True)
    datetime = models.DateTimeField(verbose_name=_(u'Datetime'),
                                    auto_now_add=True, editable=False)
    objects = AnnouncementManager()

    class Meta:
        verbose_name = _(u'announcement')
        verbose_name_plural = _(u'announcements')
        ordering = ('-datetime',)

    def __unicode__(self):
        return self.title

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "title__icontains",)

    @models.permalink
    def get_absolute_url(self):
        if self.course:
            return ('announcement_detail', [self.course.slug, self.id, self.slug])
        return ('portal_announcement_detail', [self.id, self.slug])


def announcement_invalidate_cache(sender, instance, **kwargs):
    try:
        if instance.course:  # else: globals announcements
            invalidate_template_fragment_i18n('course_overview_secondary_info',
                                              instance.course.id)
    except Course.DoesNotExist:
        logger.error('Saving/removing announcement. Can\'t invalidate course '
                     'sidebar html, not valid reference to course object, '
                     'it is probably being deleted...')


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
        ('h', _(u'Hidden')),
        ('p', _(u'Published')),
        ('l', _(u'Listable')),
    )

    status = models.CharField(
        verbose_name=_(u'Status'),
        choices=UNIT_STATUSES,
        max_length=10,
        default=UNIT_STATUSES[0][0],
    )

    objects = UnitManager()

    class Meta(Sortable.Meta):
        verbose_name = _(u'unit')
        verbose_name_plural = _(u'units')
        unique_together = ('title', 'course')

    def __unicode__(self):
        return u'%s - %s (%s)' % (self.course, self.title, self.unittype)

    def get_unit_type_name(self):
        for t in self.UNIT_TYPES:
            if t[0] == self.unittype:
                return t[1]

    def natural_key(self):
        return self.course.natural_key() + (self.title, )

    def is_scorable(self):
        if not settings.COURSES_USING_OLD_TRANSCRIPT:
            return self.unittype != 'n'
        else:
            return True


def unit_invalidate_cache(sender, instance, **kwargs):
    try:
        invalidate_template_fragment_i18n('course_overview_secondary_info',
                                          instance.course.id)
    except Course.DoesNotExist:
        # The course is being deleted, nothing to invalidate
        pass


def unit_stats(sender, instance, created, **kwargs):
    stats_unit = get_db().get_collection('stats_unit')
    if created:
        stats_unit.insert({
            'course_id': instance.course.id,
            'unit_id': instance.id,
            'started': 0,
            'completed': 0,
            'passed': 0,
        }, safe=True)
    else:
        stats_unit.update(
            {'unit_id': instance.id},
            {'$set': {'course_id': instance.course.id}},
            safe=True
        )

signals.post_save.connect(unit_invalidate_cache, sender=Unit)
signals.post_save.connect(unit_stats, sender=Unit)
signals.post_delete.connect(unit_invalidate_cache, sender=Unit)


class KnowledgeQuantum(Sortable):

    title = models.CharField(verbose_name=_(u'Title'), max_length=200)
    unit = SortableForeignKey(Unit, verbose_name=_(u'Unit'))
    weight = models.SmallIntegerField(verbose_name=_(u'Weight'), null=False,
                                      default=0,
                                      help_text='0-100%',
                                      validators=[MaxValueValidator(100)])
    media_content_type = models.CharField(verbose_name=_(u'Content type'),
                                          max_length=20,
                                          null=True,
                                          blank=False,
                                          choices=get_media_content_types_choices())
    media_content_id = models.CharField(verbose_name=_(u'Content id'),
                                        null=True,
                                        blank=False,
                                        max_length=200)
    teacher_comments = HTMLField(verbose_name=_(u'Instructor\'s comments'),
                                 blank=True, null=False)
    supplementary_material = HTMLField(
        verbose_name=_(u'Supplementary material'),
        blank=True, null=False)

    objects = KnowledgeQuantumManager()

    class Meta(Sortable.Meta):
        verbose_name = _(u'nugget')
        verbose_name_plural = _(u'nuggets')
        unique_together = ('title', 'unit')

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

    def kq_type(self):
        from moocng.peerreview.models import PeerReviewAssignment
        if self.question_set.count() > 0:
            return "Question"
        else:
            try:
                if self.peerreviewassignment is not None:
                    return "PeerReviewAssignment"
            except PeerReviewAssignment.DoesNotExist:
                pass
        return "Video"

    def kq_visited_by(self, user):
        db = get_db()

        activity = db.get_collection("activity")
        # Verify if user has watch the video from kq
        user_activity_exists = activity.find({
            "user_id": user.id,
            "kq_id": self.id,
        })

        return user_activity_exists.count() > 0

    def set_as_current(self,user):
        db = get_db()
        activity = db.get_collection("activity")

        activity.update({
                "user_id": user.id,
                "course_id": self.unit.course.id,
                "current" : True
            },
            {
                "$unset": { "current": "" },
            }
        )

        activity.update({
            "user_id": user.id,
            "kq_id": self.id
            },
            {
                "$set": { "current": True },
            }
        )

    def natural_key(self):
        return self.unit.natural_key() + (self.title, )

    def save(self, *args, **kwargs):
        if self.media_content_type and self.media_content_id:
            self.media_content_id = media_content_extract_id(self.media_content_type, self.media_content_id)
        return super(KnowledgeQuantum, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s - %s' % (self.unit, self.title)


def handle_kq_post_save(sender, instance, created, **kwargs):
    if transaction.is_dirty():
        transaction.commit()
    question_list = instance.question_set.all()
    if len(question_list) > 0:
        process_video_task.delay(question_list[0].id)


def kq_stats(sender, instance, created, **kwargs):
    stats_kq = get_db().get_collection('stats_kq')
    if created:
        stats_kq.insert({
            'course_id': instance.unit.course.id,
            'unit_id': instance.unit.id,
            'kq_id': instance.id,
            'viewed': 0,
            'submitted': 0,
            'reviews': 0,
            'reviewers': 0,
            'passed': 0,
        }, safe=True)
        # It doesn't matter if it has all the fields because the teacheradmin
        # view only returns the proper fields depending on the kq type
    else:
        stats_kq.update(
            {'kq_id': instance.id},
            {'$set': {
                'course_id': instance.unit.course.id,
                'unit_id': instance.unit.id,
            }},
            safe=True
        )


signals.post_save.connect(handle_kq_post_save, sender=KnowledgeQuantum)
signals.post_save.connect(kq_stats, sender=KnowledgeQuantum)

def get_transcription_types_choices():
    choices = []
    for handler_dict in settings.TRANSCRIPTION_TYPES:
        choices.append((handler_dict['id'], handler_dict.get('name', handler_dict['id'])))
    return choices

class Transcription(models.Model):
    kq = models.ForeignKey(KnowledgeQuantum,
                           verbose_name=_(u'Nugget'))

    filename = models.FileField(verbose_name=_(u'VTT file'),
                                upload_to='transcriptions')
    transcription_type = models.CharField(verbose_name=_(u'Transcription type'),
                                          max_length=20,
                                          null=True,
                                          blank=False,
                                          choices=get_transcription_types_choices())
    language = models.ForeignKey(Language,
                                   verbose_name=_(u'Language'))

    objects = TranscriptionManager()

    class Meta:
        verbose_name = _(u'transcription')
        verbose_name_plural = _(u'transcriptions')

    def __unicode__(self):
        return self.filename.name

    def natural_key(self):
        return self.kq.natural_key() + (self.filename.name,)

class Attachment(models.Model):

    kq = models.ForeignKey(KnowledgeQuantum,
                           verbose_name=_(u'Nugget'))
    attachment = models.FileField(verbose_name=_(u'Attachment'),
                                  upload_to='attachments',
                                  max_length=200)

    objects = AttachmentManager()

    class Meta:
        verbose_name = _(u'attachment')
        verbose_name_plural = _(u'attachments')

    def __unicode__(self):
        return self.attachment.name

    def natural_key(self):
        return self.kq.natural_key() + (self.attachment.name,)


class Question(models.Model):

    kq = models.ForeignKey(KnowledgeQuantum, unique=True,
                           verbose_name=_(u'Nugget'))
    solution_media_content_type = models.CharField(verbose_name=_(u'Content type'),
                                                   max_length=20,
                                                   null=True,
                                                   blank=False,
                                                   choices=get_media_content_types_choices())
    solution_media_content_id = models.CharField(verbose_name=_(u'Content id'),
                                                 null=True,
                                                 blank=False,
                                                 max_length=200)
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

    objects = QuestionManager()

    class Meta:
        verbose_name = _(u'question')
        verbose_name_plural = _(u'questions')

    def natural_key(self):
        # Knowledge quantum only have a question. Kq should be a one to one relation
        return self.kq.natural_key()

    def save(self, *args, **kwargs):
        if self.solution_media_content_type and self.solution_media_content_id:
            self.solution_media_content_id = media_content_extract_id(self.solution_media_content_type, self.solution_media_content_id)
        return super(Question, self).save(*args, **kwargs)

    def __unicode__(self):
        return ugettext(u'{0} - Question {1}').format(self.kq, self.id)

    def is_correct(self, answer):
        result = 0.0
        if answer['replyList'] is not None:
            replies = dict([(int(r['option']), r['value'])
                            for r in answer['replyList']])
        else:
            replies = {}

        options_dict = {}
        results_dict = {}
        for k, g in groupby(self.option_set.all(), lambda x: x.name):
            opt_list = list(g)
            if k in options_dict:
                options_dict[k] = options_dict[k] + opt_list
            else:
                options_dict[k] = opt_list
            results_dict[k] = 0.0

        for key, value in options_dict.iteritems():
            correct_q = True
            for option in value:
                reply = replies.get(option.id, None)
                if reply is None:
                    return False
                correct_q = correct_q and option.is_correct(reply)

            result_q = 10.0/len(options_dict) if correct_q else 0.0
            results_dict[key] = result_q
            result += result_q

        return result

    def is_completed(self, user, visited=None):
        db = get_db()

        if visited is None:
            visited = self.kq.kq_visited_by(user)
            if not visited:
                return False

        # Verify if user has answered the question
        answers = db.get_collection("answers")
        answer_exists = answers.find_one({
            "user_id": user.id,
            "question_id": self.id,
        })

        return not (answer_exists is None)


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
    order = models.PositiveSmallIntegerField(verbose_name=_(u'Order'),
                                            null=True)
    name = models.CharField(verbose_name=_(u'Group name'), max_length=100,
        blank=True, null=False)
    objects = OptionManager()

    class Meta:
        verbose_name = _(u'option')
        verbose_name_plural = _(u'options')
        unique_together = ('question', 'x', 'y')

    def __unicode__(self):
        return ugettext(u'{0}.{1} ({2}: {3}) at {4} x {5}').format(self.id, self.optiontype, self.name, self.text, self.x, self.y)

    def natural_key(self):
        return self.question.natural_key() + (self.x, self.y)

    def is_correct(self, reply):
        if self.optiontype == 'l' or self.optiontype == 'q':
            return True
        elif self.optiontype == 't':
            if not hasattr(reply, 'lower'):
                logger.error('Error at option %s - Value %s - Solution %s' % (str(self.id), str(reply), self.solution))
                return True
            else:
                return reply.lower() == self.solution.lower()
        else:
            return bool(reply) == (self.solution.lower() == u'true')
