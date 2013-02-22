# Copyright 2012 Rooter Analysis S.L.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import urlparse


def extract_YT_video_id(url):
    if url is None:
        return u'None'
    parsed_url = urlparse.urlparse(url)
    if parsed_url.path != u'/watch':
        # short YT url
        video_id = parsed_url.path[1:]
    else:
        # long YT url
        video_id = urlparse.parse_qs(parsed_url.query)
        try:
            video_id = video_id['v'][0]
        except KeyError:
            return u''
    return video_id
