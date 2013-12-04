# -*- coding: utf-8 -*-
# Copyright 2013 Pablo Martín
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
from functools import update_wrapper

from django.db import transaction
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.admin.options import csrf_protect_m
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator

from moocng.decorators import user_passes_test


class MassiveGlobalAdmin(admin.ModelAdmin):

    global_massive_form = None
    subfix_url = 'send/'
    global_massive_title = ''
    global_massive_message = ''

    def get_urls(self):
        urlpatterns = super(MassiveGlobalAdmin, self).get_urls()
        from django.conf.urls import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name
        urlpatterns = patterns('',
            url(r'^%s$' % self.subfix_url,
                wrap(self.send_global_massive_view),
                name='%s_%s_send' % info),
        ) + urlpatterns
        return urlpatterns

    def is_send_global_massive_url(self, request):
        return request.get_full_path().endswith('/%s' % self.subfix_url)

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if self.is_send_global_massive_url(request):
            defaults.update({
                'form': self.global_massive_form,
            })
        defaults.update(kwargs)
        return super(MassiveGlobalAdmin, self).get_form(request, obj, **defaults)

    @csrf_protect_m
    @transaction.commit_on_success
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def send_global_massive_view(self, request, form_url='', extra_context=None):
        return self.add_view(request, form_url=form_url, extra_context=extra_context)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        is_send_global_massive_url = self.is_send_global_massive_url(request)
        extra_context = {'is_send_global_massive_url': is_send_global_massive_url}
        if is_send_global_massive_url:
            context['title'] = self.global_massive_title
        extra_context.update(context)
        return super(MassiveGlobalAdmin, self).render_change_form(request, extra_context, add=add,
                                                                  change=change,
                                                                  form_url=form_url,
                                                                  obj=obj)

    def response_add(self, request, obj, post_url_continue='../%s/'):
        is_send_global_massive_url = self.is_send_global_massive_url(request)
        if is_send_global_massive_url:
            self.message_user(request, self.global_massive_message)
            return HttpResponseRedirect(reverse('admin:index'))
        return super(MassiveGlobalAdmin, self).response_add(request, obj, post_url_continue=post_url_continue)
