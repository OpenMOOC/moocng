# -*- coding: utf-8 -*-

import urlparse


def extract_YT_video_id(url):
    parsed_url = urlparse.urlparse(url)
    video_id = urlparse.parse_qs(parsed_url.query)
    video_id = video_id['v'][0]
    return video_id
