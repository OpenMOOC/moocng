# -*- coding: utf-8 -*-
# Copyright 2012-2013 Rooter Analysis S.L.
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

from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.admin.options import csrf_protect_m
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from moocng.teacheradmin.forms import MassiveGlobalEmailAdminForm
from moocng.teacheradmin.models import Invitation, MassiveEmail


class InvitationAdmin(admin.ModelAdmin):

    """
    Invitation model administration for Moocng.

    .. versionadded:: 0.1
    """
    raw_id_fields = ('host',)
    autocomplete_lookup_fields = {'fk': ['host'], }

    list_display = ('course', 'email', 'datetime')
    list_filter = ('course', )


class MassiveEmailAdmin(admin.ModelAdmin):

    """
    MassiveEmail model administration.

    .. versionadded:: 0.1
    """

    list_display = ('subject', 'datetime', 'course')
    list_filter = ('course', )
    send_email_form = MassiveGlobalEmailAdminForm

    def get_urls(self):
        urlpatterns = super(MassiveEmailAdmin, self).get_urls()
        from django.conf.urls import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name
        urlpatterns = patterns('',
            url(r'^send/$',
                wrap(self.send_global_massive_email),
                name='%s_%s_send' % info),
        ) + urlpatterns
        return urlpatterns

    def is_send_email_url(self, request):
        return request.get_full_path().endswith('/send/')

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if self.is_send_email_url(request):
            defaults.update({
                'form': self.send_email_form,
            })
        defaults.update(kwargs)
        return super(MassiveEmailAdmin, self).get_form(request, obj, **defaults)

    @csrf_protect_m
    @transaction.commit_on_success
    def send_global_massive_email(self, request, form_url='', extra_context=None):
        return self.add_view(request, form_url=form_url, extra_context=extra_context)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        is_send_email_url = self.is_send_email_url(request)
        extra_context = {'is_send_email_url': is_send_email_url}
        if is_send_email_url:
            context['title'] = _('Send email massive')
        extra_context.update(context)
        return super(MassiveEmailAdmin, self).render_change_form(request, extra_context, add=add,
                                                                 change=change,
                                                                 form_url=form_url,
                                                                 obj=obj)

    def response_add(self, request, obj, post_url_continue='../%s/'):
        is_send_email_url = self.is_send_email_url(request)
        if is_send_email_url:
            self.message_user(request, _("The emails will be sent soon"))
            return HttpResponseRedirect(reverse('admin:index'))
        return super(MassiveEmailAdmin, self).response_add(request, obj, post_url_continue=post_url_continue)


admin.site.register(Invitation, InvitationAdmin)
admin.site.register(MassiveEmail, MassiveEmailAdmin)
