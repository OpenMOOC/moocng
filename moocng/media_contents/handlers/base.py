class MediaContentHandlerBase(object):
    def get_iframe_template(self, content_id, **kwargs):
        raise NotImplementedError

    def get_iframe_code(self, content_id, **kwargs):
        raise NotImplementedError

    def get_javascript_code(self, **kwargs):
        raise NotImplementedError

    def get_thumbnail_url(self, content_id, **kwargs):
        raise NotImplementedError

    def get_last_frame(self, content_id, tmpdir, **kwargs):
        raise NotImplementedError

    def extract_id(self, url, **kwargs):
        raise NotImplementedError
