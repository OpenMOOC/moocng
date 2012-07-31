from django.core.management.base import BaseCommand

from moocng.videos import download
from moocng.courses.models import Question


class Command(BaseCommand):
    help = 'Download a YouTube video and extracts the last frame'

    def handle(self, *args, **options):
        question_id = args[0]
        question = Question.objects.get(id=question_id)
        download.process_video(question)
