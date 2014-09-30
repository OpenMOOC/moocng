import json

from django.conf import settings

from . import handlers


def media_content_get_iframe_code(handler, content_id, **kwargs):
    handler = handlers.get_handler(handler)
    return handler.get_iframe_code(content_id, **kwargs)


def media_content_get_thumbnail_url(handler, content_id, **kwargs):
    handler = handlers.get_handler(handler)
    return handler.get_thumbnail_url(content_id, **kwargs)


def media_content_get_iframe_template(handler, content_id, **kwargs):
    handler = handlers.get_handler(handler)
    return handler.get_iframe_template(content_id, **kwargs)


def media_content_get_js_code(handler, **kwargs):
    handler = handlers.get_handler(handler)
    return handler.get_javascript_code(**kwargs)


def media_content_get_last_frame(handler, content_id, tmpdir, **kwargs):
    handler = handlers.get_handler(handler)
    return handler.get_last_frame(content_id, tmpdir, **kwargs)


def media_content_extract_id(handler, url, **kwargs):
    handler = handlers.get_handler(handler)
    return handler.extract_id(url, **kwargs)


def media_contents_javascripts(**kwargs):
    course = kwargs.get('course', None)
    handlers_ids = []

    if course:
        if course.promotion_media_content_type:
            handlers_ids.append(course.promotion_media_content_type)

        for unit in course.unit_set.all():
            for kq in unit.knowledgequantum_set.all():
                handlers_ids.append(kq.media_content_type)
                for question in kq.question_set.all():
                    handlers_ids.append(question.solution_media_content_type)
        handlers_ids = list(set(handlers_ids))

    html = "<script>MEDIA_CONTENT_TYPES = %s;</script>" % json.dumps(dict([(item['id'], item) for item in settings.MEDIA_CONTENT_TYPES]))
    for handler_id in handlers_ids:
        handler = handlers.get_handler(handler_id)
        html += handler.get_javascript_code(**kwargs)
    return html


def get_media_content_types_choices():
    choices = []
    for handler_dict in settings.MEDIA_CONTENT_TYPES:
        choices.append((handler_dict['id'], handler_dict.get('name', handler_dict['id'])))
    return choices


def get_media_type(mediaid):
    if not mediaid:
        return None
    for media in settings.MEDIA_CONTENT_TYPES:
        if media["id"] == mediaid:
            return media["type"]
