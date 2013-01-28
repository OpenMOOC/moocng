from optparse import make_option
import tarfile
import os

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

    def handle(self, *args, **options):
        if not options["course"]:
            raise CommandError("--course / -c course_slug is required")

        if not options["filename"]:
            raise CommandError("--file / -f filename is required")

        try:
            course = Course.objects.get(slug=options["course"])
        except Course.DoesNotExist:
            raise CommandError(u"Course %s does not exist" % options["course"])

        filename = options.get("filename", "")

        if not os.path.exists(filename):
            raise CommandError(u"File %s does not exist" % filename)

        self.message(course.slug)

        self.tar = tarfile.open(filename, "r:gz")

        course_file = self.tar.extractfile("course.json")
        course_json = course_file.read()
        course_file.close()

        course_dict = simplejson.loads(course_json)

        self.message("Course slug in the bundle is %s" %
                     course_dict["fields"]["slug"])

        self.tar.close()

        self.message("\n %s Units readed from %s " %
                     (len(course_dict["units"]), filename))
