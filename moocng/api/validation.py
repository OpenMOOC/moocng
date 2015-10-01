# -*- coding: utf-8 -*-
# Copyright 2012-2013 UNED
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

from cgi import escape
from datetime import datetime
import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from tastypie.validation import Validation


from moocng.courses.models import Question, Option
from moocng.mongodb import get_db

logger = logging.getLogger(__name__)


def answer_validate_date(bundle, request=None):
    question_id = bundle.data.get("question_id", None)
    if question_id is None:
        raise ValidationError("question_id is required")

    question = Question.objects.get(id=question_id)
    unit = question.kq.unit

    if (unit.unittype != 'n' and unit.course.status != 'o' and unit.deadline and
            datetime.now(unit.deadline.tzinfo) > unit.deadline):
        raise ValidationError("Unit's deadline is exceed")
    return {}


class AnswerValidation(Validation):

    def _gen_message(self, username, reply, should_be):
        return 'Reply from user %s for option %s is should be %s but is %s' % (
            username, reply['option'], should_be,
            escape(unicode(type(reply['value']))))

    def is_valid(self, bundle, request=None):
        errors = {}
        errors.update(self.validate_date(bundle, request))
        errors.update(self.validate_replyList(bundle, request))
        return errors

    def validate_date(self, bundle, request=None):
        return answer_validate_date(bundle, request)

    def validate_replyList(self, bundle, request=None):
        questionID = bundle.data.get("question_id", None)
        replyList = bundle.data.get("replyList", None)

        if (replyList is None or not isinstance(replyList, list) or
                len(replyList) == 0):
            msg = "replyList is empty or isn't a list"
            logger.error(msg)
            raise ValidationError(msg)

        if (questionID is not None) and (len(bundle.data['replyList']) > 0):
            try:
                question = Question.objects.get(id=questionID)
                for reply in bundle.data['replyList']:
                    option = question.option_set.get(id=reply['option'])
                    msg = None

                    if (option.optiontype == 't') and (not isinstance(reply['value'], basestring)):
                        msg = self._gen_message(request.user.username, reply, 'text')
                    elif (option.optiontype in ['c', 'r']) and (not isinstance(reply['value'], bool)):
                        msg = self._gen_message(request.user.username, reply, 'boolean')

                    if msg is not None:
                        logger.error(msg)
                        raise ValidationError(msg)
            except Question.DoesNotExist:
                msg = 'Question %s does not exist' % questionID
                logger.error(msg)
                raise ValidationError(msg)
            except Option.DoesNotExist:
                msg = 'Option %s does not exist' % reply['option']
                logger.error(msg)
                raise ValidationError(msg)

        return {}


class PeerReviewSubmissionsResourceValidation(Validation):

    def is_valid(self, bundle, request):
        if not bundle.data or not ("kq" in bundle.data):
            return {'__all__': 'Expected kq id'}

        errors = {}

        db = get_db()
        collection = db.get_collection("peer_review_submissions")

        exists = collection.find({
            "kq": bundle.data["kq"],
            "author": unicode(request.user.id)
        })

        if exists.count() > 0:
            msg = "Already exists a submission for kq=%s and user=%s" % (
                bundle.data["kq"],
                request.user.id)
            logger.error(msg)
            errors["kq"] = [msg]
            errors["author"] = [msg]

        text = bundle.data.get("text", "")
        max_text_leng = getattr(settings, "PEER_REVIEW_TEXT_MAX_SIZE", 5000)

        if len(text) > max_text_leng:
            errors["text"] = "Text is longer than %s chars" % max_text_leng

        return errors
