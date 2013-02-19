# Copyright 2013 Rooter Analysis S.L.
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

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from moocng.courses.models import (Course, Option)


IMG_FIXED_W = 620
IMG_FIXED_H = 372


def translate_backward_position(max_s, max_t,  s):
    t = (s * (float(max_s) / float(max_t)))
    return int(round(t * 1.15))


def translate_forward_position(max_s, max_t,  s):
    t = (s * (float(max_s) / float(max_t)))
    return int(round(t * (1/1.15)))


class Command(BaseCommand):
    """Migrate options position
    """
    option_list = BaseCommand.option_list + (
        make_option('-c', '--course',
                    action='append',
                    dest='course',
                    default=[],
                    help="Course slug to translate, if not given all courses"
                         "will be translated"),
        make_option('-f', '--forward',
                    action='store_true',
                    dest='forward',
                    default=False,
                    help="Transalate options positions (from old to new)"),
        make_option('-b', '--backward',
                    action='store_true',
                    dest='backward',
                    default=False,
                    help="Transalate options positions (from new to old)")
    )

    def error(self, message):
        self.stderr.write(u"%s\n" % message.encode("ascii", "replace"))

    def message(self, message):
        self.stdout.write(u"%s\n" % message.encode("ascii", "replace"))

    def handle(self, *args, **options):

        self.options = options

        # not one of two options
        if not (self.options.get("backward") ^ self.options.get("forward")):
            raise CommandError("one of -f or -b are required options")

        if options.get("course", None):
            try:
                courses = Course.objects.filter(slug__in=options["course"])
            except Course.DoesNotExist:
                raise CommandError(u"Course %s does not exist" %
                                   options["course"])
        else:
            courses = Course.objects.all()

        for course in courses:
            self.message("Translating position from course %s " % course.slug)

            options = Option.objects.filter(question__kq__unit__course=course)

            for option in options:

                last_frame = option.question.last_frame
                img_height = last_frame.height
                img_width = last_frame.width

                if self.options.get("backward", False):
                    option.x = translate_backward_position(img_width,
                                                           IMG_FIXED_W,
                                                           option.x)
                    option.y = translate_backward_position(img_height,
                                                           IMG_FIXED_H,
                                                           option.y)

                    option.height = translate_backward_position(img_height,
                                                                IMG_FIXED_H,
                                                                option.height)
                    option.width = translate_backward_position(img_width,
                                                               IMG_FIXED_W,
                                                               option.width)

                    option.save()

                elif self.options.get("forward", False):
                    option.x = translate_forward_position(IMG_FIXED_W,
                                                          img_width,
                                                          option.x)
                    option.y = translate_forward_position(IMG_FIXED_H,
                                                          img_height,
                                                          option.y)

                    option.height = translate_forward_position(IMG_FIXED_H,
                                                               img_height,
                                                               option.height)
                    option.width = translate_forward_position(IMG_FIXED_W,
                                                              img_width,
                                                              option.width)

                    option.save()
