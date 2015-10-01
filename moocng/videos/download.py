# Copyright 2012 UNED
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

# -*- coding: utf-8 -*-

from os import path
import datetime
import logging
import re
import subprocess
import urllib2

from django.conf import settings

from youtube import YouTube

from moocng.videos.utils import extract_YT_video_id


logger = logging.getLogger(__name__)

durationRegExp = re.compile(r'Duration: (\d+:\d+:\d+\.\d+)')
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
    if getattr(settings, "FFMPEG_DEBUG", False):
        print out
        print err
        logger.debug(out)
        logger.debug(err)
    return err


def download(url, tempdir):
    yt = YouTube()
    yt.url = url
    video = None

    if len(yt.videos) == 0:
        raise NotFound(url)

    if len(yt.filter('webm')) > 0:
        video = yt.filter('webm')[-1]  # Best resolution
    elif len(yt.filter('mp4')) > 0:
        video = yt.filter('mp4')[-1]  # Best resolution
    else:
        video = yt.videos[-1]  # Best resolution

    video.download(tempdir)

    return video.filename


def duration(filename):
    command = [settings.FFMPEG, "-i", filename]
    output = execute_command(command)
    matches = durationRegExp.search(output)
    return matches.group(1)


def last_frame(filename, time):
    command = [settings.FFMPEG, "-i", filename, "-y", "-ss", time,
               "-vframes", "1", "-vcodec", "png", "%s.png" % filename]
    execute_command(command)
    return "%s.png" % filename


def process_video(tempdir, url):
    """Download the youtube video associated with the KQ of this question
    and extract the last frame of such video."""

    video_id = extract_YT_video_id(url)
    if video_id == u'':
        raise NotFound(url)
    url2download = "http://www.youtube.com/watch?v=%s" % video_id

    logger.info('Downloading video %s' % url2download)

    try:
        filename = download(url2download, tempdir)
        filename = path.join(tempdir, filename)
    except urllib2.HTTPError as e:
        logger.error('Error downloading video %s: %s' % (url2download, e))
        return None
    except:
        raise

    try:
        time = duration(filename)
        logger.info('The downloaded video %s has a duration of %s'
                    % (filename, time))
    except:
        raise

    try:
        # Get the time position of the last second of the video
        dt = datetime.datetime.strptime(time, "%H:%M:%S.%f")
        dt = dt - second
        fototime = dt.strftime("%H:%M:%S.%f")
        logger.info('Getting the last frame at %s' % fototime)
        frame = last_frame(filename, fototime)
    except:
        raise

    return frame
