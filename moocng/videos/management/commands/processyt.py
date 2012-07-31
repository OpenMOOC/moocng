from django.core.management.base import BaseCommand

from moocng.videos import download
from moocng.courses.models import Question


class Command(BaseCommand):
    help = 'Download a YouTube video and extracts the last frame'

    def handle(self, *args, **options):
        video_id = args[0]
        question_id = args[1]
        question = Question.objects.get(id=question_id)
        download.process_video(video_id, question)
