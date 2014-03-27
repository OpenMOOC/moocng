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

import logging
import tempfile
import shutil

from celery import task

from moocng.videos.download import NotFound
from moocng.media_contents import media_content_get_last_frame

from django.core.files import File

logger = logging.getLogger(__name__)


def do_process_video_task(question_id):
    from moocng.courses.models import Question
    question = Question.objects.get(id=question_id)
    content_type = question.kq.media_content_type
    content_id = question.kq.media_content_id

    try:
        tmpdir = tempfile.mkdtemp()
        frame = media_content_get_last_frame(content_type, content_id, tmpdir)

        if frame is not None:
            if not content_id:
                raise NotFound(content_id)
            question.last_frame.save("%s.png" % content_id, File(open(frame)))
    except IOError:
        logger.error('Video %s could not be downloaded or processed. Probably the codec is not supported, please try again with a newer YouTube video.' % content_id)
    except NotFound:
        logger.error('Video %s not found' % content_id)
    finally:
        shutil.rmtree(tmpdir)


@task
def process_video_task(question_id):
    return do_process_video_task(question_id)
