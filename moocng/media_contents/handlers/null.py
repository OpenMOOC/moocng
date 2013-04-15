from .base import MediaContentHandlerBase


class NullMediaContentHandler(MediaContentHandlerBase):
    def get_iframe_code(self, content_id, **kwargs):
        return ""

    def get_iframe_template(self, content_id, **kwargs):
        return ""

    def get_thumbnail_url(self, content_id):
        return ""

    def get_javascript_code(self, **kwargs):
        return ""

    def get_last_frame(self, content_id, tmpdir):
        return None

    def extract_id(self, url):
        return ""
