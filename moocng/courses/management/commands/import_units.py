from optparse import make_option
import tarfile
import os

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db.models import signals
from django.utils import simplejson

from moocng.courses.models import (Course, KnowledgeQuantum,
                                   Question, Option)

from moocng.courses.models import handle_kq_post_save, handle_question_post_save


IMG_FIXED_W = 620
IMG_FIXED_H = 372


def translate_position(max_s, max_t,  s):
    t = (s * (float(max_s) / float(max_t)))
    return int(round(t * 1.15))


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
        self.stderr.write(u"%s\n" % message.encode("ascii", "replace"))

    def message(self, message):
        self.stdout.write(u"%s\n" % message.encode("ascii", "replace"))

    def create_object_with_files(self, manager, o_dict, fkey,
                                 filefields):
        fields = o_dict["fields"].copy()
        ffields = []
        for field in filefields:
            ffields.append((field, fields[field]))
            del fields[field]
        del fields[fkey]
        obj = manager.create(**fields)

        for field in filefields:
            filename = o_dict["fields"][field]
            fileintar = self.tar.extractfile(filename)
            modelfile = File(fileintar)
            getattr(obj, field).save(filename, modelfile)
        obj.save()
        return obj

    def add_question(self, q_dict, kq):
        del q_dict["fields"]["use_last_frame"]
        return self.create_object_with_files(kq.question_set, q_dict,
                                             "kq", ["last_frame"])

    def add_option(self, o_dict, question):
        del o_dict["fields"]["question"]
        if "text" in o_dict["fields"]:
            del o_dict["fields"]["text"]
        option = question.option_set.create(**o_dict["fields"])
        img_height = option.question.last_frame.height
        img_width = option.question.last_frame.width

        option.x = translate_position(img_width, IMG_FIXED_W, option.x)
        option.y = translate_position(img_height, IMG_FIXED_H, option.y)

        option.height = translate_position(img_height, IMG_FIXED_H, option.height)
        option.width = translate_position(img_width, IMG_FIXED_W, option.width)

        option.save()
        return option

    def add_attachment(self, a_dict, kq):
        return self.create_object_with_files(kq.attachment_set,
                                             a_dict, "kq", ["attachment"])

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

        signals.post_save.disconnect(receiver=handle_question_post_save,
                                     sender=Question)
        signals.post_save.disconnect(receiver=handle_kq_post_save,
                                     sender=KnowledgeQuantum)

        self.tar = tarfile.open(filename, "r:gz")

        course_file = self.tar.extractfile("course.json")
        course_json = course_file.read()
        course_file.close()

        course_dict = simplejson.loads(course_json)

        self.message(u"Course slug in the bundle is %s" %
                     course_dict["fields"]["slug"])

        for unit_dict in course_dict["units"]:
            unit = course.unit_set.create(**unit_dict["fields"])
            self.message(u"Added unit %s" % unit)
            for kq_dict in unit_dict["knowledgequantums"]:
                del kq_dict["fields"]["unit"]
                kq = unit.knowledgequantum_set.create(**kq_dict["fields"])
                self.message(u"\tAdded unit %s" % kq)

                for attachment_dict in kq_dict["attachments"]:
                    attachment = self.add_attachment(attachment_dict, kq)
                    self.message(u"\t\tAdding attachment %s" % attachment)

                for question_dict in kq_dict["questions"]:
                    question = self.add_question(question_dict, kq)
                    self.message(u"\t\tAdding question %s" % question)

                    for option_dict in question_dict["options"]:
                        option = self.add_option(option_dict, question)
                        self.message(u"\t\t\tAdding option %s" % option)

        self.tar.close()

        self.message(u"\n %s Units readed from %s " %
                     (len(course_dict["units"]), filename))
