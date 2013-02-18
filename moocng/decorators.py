# Copyright 2013 Rooter Analysis S.L.
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
from functools import wraps

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.utils.decorators import available_attrs


def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """Saner version of django.contrib.auth.decorators.user_passes_test.

    The problem with Django's version of this function is that if the user
    does not pass the test it get redirected to the LOGIN_URL, even if
    he is already logged in. In this later case, he should get a
    Forbidden (403) error instead.
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)

            # This is different from the Django version
            # if the user is already logged in, we return a 403 error response
            if request.user.is_authenticated():
                raise PermissionDenied

            path = request.build_absolute_uri()
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse.urlparse(login_url or
                                                           settings.LOGIN_URL)[:2]
            current_scheme, current_netloc = urlparse.urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            return redirect_to_login(path, login_url, redirect_field_name)
        return _wrapped_view
    return decorator
