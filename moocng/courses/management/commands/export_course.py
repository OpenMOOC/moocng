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

from optparse import make_option
from datetime import datetime
import tarfile
import StringIO

from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson

from moocng.courses.models import Course


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-c', '--course',
                    action='store',
                    dest='course',
                    default="",
                    help='Course slug to export'),
        make_option('-f', '--filename',
                    action='store',
                    dest='filename',
                    default="",
                    help="Filename to save the course (without file extension)"),
    )

    def error(self, message):
        self.stderr.write("%s\n" % message.encode("ascii", "replace"))

    def message(self, message):
        self.stdout.write("%s\n" % message.encode("ascii", "replace"))

    def save_file(self, filefield):
        self.message("Saving file %s" % filefield.name)
        self.tar.add(filefield.file.name, filefield.name)

    def properties_dict(self, obj):
        data = serializers.serialize("json", [obj], use_natural_keys=True)
        _dict = simplejson.loads(data)[0]
        return _dict

    def option_dict(self, option):
        return self.properties_dict(option)

    def question_dict(self, question):
        _dict = self.properties_dict(question)

        options = []
        for option in question.option_set.all():
            options.append(self.option_dict(option))
        _dict["options"] = options

        return _dict

    def kq_dict(self, kq):
        _dict = self.properties_dict(kq)

        questions = []
        for question in kq.question_set.all():
            questions.append(self.question_dict(question))
            self.save_file(question.last_frame)

        _dict["questions"] = questions

        attachments = []
        for attachment in kq.attachment_set.all():
            attachments.append(self.properties_dict(attachment))
            self.save_file(attachment.attachment)

        _dict["attachments"] = attachments

        return _dict

    def unit_dict(self, unit):
        _dict = self.properties_dict(unit)
        kqs = []
        for kq in unit.knowledgequantum_set.all():
            kqs.append(self.kq_dict(kq))

        _dict["knowledgequantums"] = kqs

        return _dict

    def course_dict(self, course):
        _dict = self.properties_dict(course)
        units = []

        for unit in course.unit_set.all():
            units.append(self.unit_dict(unit))

        _dict["units"] = units

        return _dict

    def handle(self, *args, **options):
        if not options["course"]:
            raise CommandError("--course / -c param is required")

        try:
            course = Course.objects.get(slug=options["course"])
        except Course.DoesNotExist:
            raise CommandError(u"Course %s does not exist" % options["course"])

        filename = options.get("filename", "")

        if not filename:
            today = datetime.today()
            timestamp = today.strftime("%Y%m%d-%H%M%S")
            filename = "%s-%s" % (course.slug, timestamp)

        self.filename = filename

        self.tar = tarfile.open("%s.tgz" % filename, "w:gz")

        course_dict = self.course_dict(course)

        coursefile = StringIO.StringIO()
        coursefile.write(simplejson.dumps(course_dict))
        coursefile.seek(0)

        self.message("Saving course metadata file course.json")
        tarinfo = tarfile.TarInfo(name="course.json")
        tarinfo.size = len(coursefile.buf)
        self.tar.addfile(tarinfo=tarinfo, fileobj=coursefile)

        self.tar.close()

        self.message("\n\nCourse saved in %s.tar.gz" % filename)
