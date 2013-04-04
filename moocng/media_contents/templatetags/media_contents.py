from django import template

from moocng.media_contents import media_content_get_iframe_code, media_content_get_js_code, media_contents_javascripts

register = template.Library()


@register.simple_tag(name='media_content_js_code')
def media_content_js_code_tag(content_type, **kwargs):
    return media_content_get_js_code(content_type, **kwargs)


@register.simple_tag(name='media_content_iframe_code')
def media_content_iframe_code_tag(content_type, content_id, **kwargs):
    return media_content_get_iframe_code(content_type, content_id, **kwargs)


@register.simple_tag(name='media_contents_javascripts')
def media_contents_javascripts_tag(**kwargs):
    return media_contents_javascripts(**kwargs)
