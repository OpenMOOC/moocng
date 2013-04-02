class MediaContentHandlerBase(object):
    def get_iframe_code(self, content_id):
        raise NotImplementedError

    def get_thumbnail_url(self, content_id):
        raise NotImplementedError
