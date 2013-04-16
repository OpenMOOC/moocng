import re

from django.template.loader import get_template
from django.template import Context

from moocng.videos.download import process_video

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

    def get_thumbnail_url(self, content_id, **kwargs):
        return "//img.youtube.com/vi/%s/1.jpg" % unicode(content_id)

    def get_last_frame(self, content_id, tmpdir):
        return process_video(tmpdir, "http://youtu.be/%s" % content_id)

    def extract_id(self, url):
        patterns = [
            'youtube\.com/watch[#\?].*?v=([^"\& ]+)',
            'youtube\.com/embed/([^"\&\? ]+)',
            'youtube\.com/v/([^"\&\? ]+)',
            'youtube\.com/\?v=([^"\& ]+)',
            'youtu\.be/([^"\&\? ]+)',
            'gdata\.youtube\.com/feeds/api/videos/([^"\&\? ]+)',
            '^([^"\&\? ]+)$',
        ]
        for pattern in patterns:
            result = re.search(pattern, url, re.IGNORECASE)
            if result:
                return result.group(1)
        return ''
