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


def media_contents_javascripts(**kwargs):
    html = '<script>var COUNT_MEDIA_CONTENT_HANDLERS = %d;</script>' % len(settings.MEDIA_CONTENT_TYPES)
    for handler_name in settings.MEDIA_CONTENT_TYPES.keys():
        handler = handlers.get_handler(handler_name)
        html += handler.get_javascript_code(**kwargs)
    return html


def get_media_content_types_choices():
    choices = []
    for key, value in settings.MEDIA_CONTENT_TYPES.iteritems():
        if type(value) == dict:
            choices.append((key, value.get('name', key)))
        else:
            choices.append((key, key))
    return choices
