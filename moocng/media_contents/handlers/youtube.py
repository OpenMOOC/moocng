from django.template.loader import get_template
from django.template import Context
from .base import MediaContentHandlerBase


class YoutubeMediaContentHandler(MediaContentHandlerBase):
    def get_iframe_template(self, content_id, **kwargs):
        template = get_template("media_contents/handlers/youtube_template.html")
        context = Context({
            'content_id': content_id,
        })
        return template.render(context)

    def get_iframe_code(self, content_id, **kwargs):
        template = get_template("media_contents/handlers/youtube.html")
        context = Context({
            'content_id': content_id,
            'origin': kwargs.get('host', ''),
            'height': kwargs.get('height', '349px'),
            'width': kwargs.get('width', '620px'),
            'allowfullscreen': kwargs.get('allowfullscreen', ''),
            'controls': kwargs.get('controls', ''),
        })
        return template.render(context)

    def get_javascript_code(self, **kwargs):
        template = get_template("media_contents/handlers/youtube_js.html")
        context = Context(kwargs)
        return template.render(context)

    def get_thumbnail_url(self, content_id):
        return "//img.youtube.com/vi/%s/1.jpg" % unicode(content_id)
