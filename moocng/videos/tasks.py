from celery import task

from moocng.videos.download import process_video

@task
def process_video_task(question):
    process_video(question)
