import csv
from HTMLParser import HTMLParser
from optparse import make_option
import StringIO
from zipfile import ZipFile, ZipInfo


from django.core.management.base import BaseCommand, CommandError

from moocng.courses.models import Course


class Command(BaseCommand):

    help = ("create a zip bundle with csv files with students (firt_name, "
            "last_name, email)")

    option_list = BaseCommand.option_list + (
        make_option('-c', '--course',
                    action='append',
                    dest='courses',
                    default=[],
                    help='Only list this courses (can repeat this param)'),
        make_option('-f', '--filename',
                    action='store',
                    dest='filename',
                    default="",
                    help="Filename.zip to save the csv files"),
    )

    def error(self, message):
        self.stderr.write("%s\n" % message.encode("ascii", "replace"))

    def message(self, message):
        self.stdout.write("%s\n" % message.encode("ascii", "replace"))

    def handle(self, *args, **options):

        if not options["filename"]:
            raise CommandError("-f filename.zip is required")

        if options["courses"]:
            courses = options["courses"]
            courses = Course.objects.filter(slug__in=options["courses"])
        else:
            courses = Course.objects.all()

        if not courses:
            raise CommandError("Courses not found")

        if options["filename"].endswith(".zip"):
            self.filename = options["filename"]
        else:
            self.filename = "%s.zip" % options["filename"]

        h = HTMLParser()

        zip = ZipFile(self.filename, mode="w")

        for course in courses:
            self.message("Adding course file %s.csv" % course.slug)

            course_file = StringIO.StringIO()

            course_csv = csv.writer(course_file, quoting=csv.QUOTE_ALL)
            headers = ["first_name", "last_name", "email"]

            course_csv.writerow(headers)

            for student in course.students.all():
                row = []
                for field in headers:
                    fieldvalue = getattr(student, field)
                    row.append(h.unescape(fieldvalue.encode("ascii", "ignore")))
                course_csv.writerow(row)

            course_fileinfo = ZipInfo("%s.csv" % course.slug)

            course_file.seek(0)

            zip.writestr(course_fileinfo, course_file.read())

            course_file.close()

        zip.close()

        self.message("Created %s file" % self.filename)
