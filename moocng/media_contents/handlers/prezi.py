from django.template.loader import get_template
from django.template import Context
from .base import MediaContentHandlerBase


class PreziMediaContentHandler(MediaContentHandlerBase):
    def get_iframe_template(self, content_id, **kwargs):
        template = get_template("media_contents/handlers/prezi_template.html")
        context = Context({
            'content_id': content_id,
            'origin': kwargs.pop('host', ''),
        })
        return template.render(context)

    def get_iframe_code(self, content_id, **kwargs):
        template = get_template("media_contents/handlers/prezi.html")
        context = Context({
            'content_id': content_id,
            'origin': kwargs.get('host', ''),
            'height': kwargs.get('height', '349px'),
            'width': kwargs.get('width', '620px'),
            'extra_params': kwargs.get('extra_params', ''),
            'extra_attribs': kwargs.get('extra_attribs', ''),
        })
        return template.render(context)

    def get_javascript_code(self, **kwargs):
        template = get_template("media_contents/handlers/prezi_js.html")
        context = Context(kwargs)
        return template.render(context)

    def get_thumbnail_url(self, content_id):
        return ""
