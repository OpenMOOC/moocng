# -*- coding: utf-8 -*-

from os import path
import datetime
import re
import shutil
import subprocess
import tempfile
import urlparse

from django.core.files import File
from django.conf import settings

from youtube import YouTube


durationRegExp = re.compile(r'Duration: (\d+:\d+:\d+)')
second = datetime.timedelta(seconds=1)


class NotFound(Exception):

    def __init__(self, value):
        self.value = "YouTube video not found: %s" % repr(value)

    def __str__(self):
        return self.value


def execute_command(proc):
    # ffmpeg uses stderr for comunicating
    p = subprocess.Popen(proc, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return err


def download(url):
    yt = YouTube()
    yt.url = url

    if len(yt.videos) == 0:
        raise NotFound(url)

    if len(yt.filter('webm')) > 0:
        video = yt.filter('webm')[-1]  # Best resolution
    elif len(yt.filter('mp4')) > 0:
        video = yt.filter('mp4')[-1]  # Best resolution
    else:
        video = yt.videos[-1]  # Best resolution

    try:
        tempdir = tempfile.mkdtemp()
        video.download(tempdir)
    except:
        # Remove temp files only if something goes awry
        shutil.rmtree(tempdir)
        raise

    return tempdir, video.filename


def duration(filename):
    command = [settings.FFMPEG, "-i", filename]
    output = execute_command(command)
    matches = durationRegExp.search(output)
    return matches.group(1)


def last_frame(filename, time):
    command = [settings.FFMPEG, "-i", filename, "-y", "-sameq", "-ss", time,
               "-vframes", "1", "-vcodec", "png", "%s.png" % filename]
    execute_command(command)
    return "%s.png" % filename


def process_video(question):
    try:
        url = question.kq.video
        parsed_url = urlparse.urlparse(url)
        video_id = urlparse.parse_qs(parsed_url.query)
        video_id = video_id['v'][0]
        tempdir, filename = download(url)
        filename = path.join(tempdir, filename)
        time = duration(filename)

        # Get the time position of the last second of the video
        time = time.split(':')
        dt = datetime.datetime(2012, 01, 01, int(time[0]), int(time[1]),
                               int(time[2]))
        dt = dt - second
        time = "%s.900" % dt.strftime("%H:%M:%S")

        frame = last_frame(filename, time)

        question.last_frame.save("%s.png" % video_id, File(open(frame)))
    except:
        raise
    finally:
        try:
            shutil.rmtree(tempdir)  # Remove temporal directory and contents
        except NameError:
            # No temporal files were created, so there is nothing to delete
            pass
