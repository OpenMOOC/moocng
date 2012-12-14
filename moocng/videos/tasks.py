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

import logging
import tempfile
import shutil

from celery import task

from moocng.videos.download import process_video, NotFound
from moocng.videos.utils import extract_YT_video_id

from django.core.files import File

logger = logging.getLogger(__name__)


def do_process_video_task(question):
    url = question.kq.video

    try:
        tempdir = tempfile.mkdtemp()
        frame = process_video(tempdir, url)

        if frame is not None:
            video_id = extract_YT_video_id(url)
            if video_id == u'':
                raise NotFound(url)
            question.last_frame.save("%s.png" % video_id, File(open(frame)))
    except IOError:
        logger.error('Video %s could not be downloaded or processed. Probably the codec is not supported, please try again with a newer YouTube video.' % url)
    except NotFound:
        logger.error('Video %s not found' % url)
    finally:
        shutil.rmtree(tempdir)

@task
def process_video_task(question):
    return do_process_video_task(question)
