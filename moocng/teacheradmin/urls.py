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

from django.conf.urls import patterns, url

from .views import (
    TeacherAdminStats, TeacherAdminStatsUnits, TeacherAdminStatsKqs,
    TeacherAdminUnits, TeacherAdminUnitsForceVideoProcess,
    TeacherAdminUnitsAttachment, TeacherAdminUnitsQuestion,
    TeacherAdminUnitsOption, TeacherAdminTeachers, TeacherAdminTeachersDelete,
    TeacherAdminTeachersInvite, TeacherAdminTeachersTransfer,
    TeacherAdminTeachersReorder, TeacherAdminInfo, TeacherAdminCategories,
    TeacherAdminAssets, TeacherAdminAssetsEdit, TeacherAdminAnnouncements,
    TeacherAdminAnnouncementsView, TeacherAdminAnnouncementsAddOrEdit,
    TeacherAdminAnnouncementsDelete, TeacherAdminEmails,
)

urlpatterns = patterns(
    'moocng.teacheradmin.views',

    url(r'^$', TeacherAdminInfo.as_view(), name='teacheradmin_index'),
    url(r'^stats/$', TeacherAdminStats.as_view(), name='teacheradmin_stats'),
    url(r'^stats/units/$', TeacherAdminStatsUnits.as_view(),
        name='teacheradmin_stats_units'),
    url(r'^stats/kqs/$', TeacherAdminStatsKqs.as_view(),
        name='teacheradmin_stats_kqs'),

    url(r'^units/$', TeacherAdminUnits.as_view(), name='teacheradmin_units'),
    url(r'^units/forcevideoprocess/$', TeacherAdminUnitsForceVideoProcess.as_view(),
        name='teacheradmin_units_forcevideoprocess'),
    url(r'^units/attachment/$', TeacherAdminUnitsAttachment.as_view(),
        name='teacheradmin_units_attachment'),
    url(r'^units/question/(?P<kq_id>\d+)/$', TeacherAdminUnitsQuestion.as_view(),
        name='teacheradmin_units_question'),
    url(r'^units/question/(?P<kq_id>\d+)/(?P<option_id>\d+)/$',
        TeacherAdminUnitsOption.as_view(), name='teacheradmin_units_option'),

    url(r'^teachers/$', TeacherAdminTeachers.as_view(), name='teacheradmin_teachers'),
    url(r'^teachers/delete/(?P<email_or_id>[^/]+)/$', TeacherAdminTeachersDelete.as_view(),
        name='teacheradmin_teachers_delete'),
    url(r'^teachers/invite/$', TeacherAdminTeachersInvite.as_view(),
        name='teacheradmin_teachers_invite'),
    url(r'^teachers/reorder/$', TeacherAdminTeachersReorder.as_view(),
        name='teacheradmin_teachers_reorder'),
    url(r'^teachers/transfer/$', TeacherAdminTeachersTransfer.as_view(),
        name='teacheradmin_teachers_transfer'),

    url(r'^info/$', TeacherAdminInfo.as_view(), name='teacheradmin_info'),

    url(r'^categories/$', TeacherAdminCategories.as_view(),
        name='teacheradmin_categories'),

    url(r'^announcements/$', TeacherAdminAnnouncements.as_view(),
        name='teacheradmin_announcements'),

    url(r'^announcements/add/',
        TeacherAdminAnnouncementsAddOrEdit.as_view(),
        name='teacheradmin_announcements_add'),

    url(r'^announcements/(?P<announ_id>\d+)/(?P<announ_slug>[^/]+)/edit/$',
        TeacherAdminAnnouncementsAddOrEdit.as_view(),
        name='teacheradmin_announcements_edit'),

    url(r'^announcements/(?P<announ_id>\d+)/(?P<announ_slug>[^/]+)/$',
        TeacherAdminAnnouncementsView.as_view(),
        name='teacheradmin_announcements_view'),

    url(r'^announcements/(?P<announ_id>\d+)/(?P<announ_slug>[^/]+)/delete/$',
        TeacherAdminAnnouncementsDelete.as_view(),
        name='teacheradmin_announcements_delete'),

    url(r'^emails/$', TeacherAdminEmails.as_view(), name='teacheradmin_emails'),

    url(r'^assets/$', TeacherAdminAssets.as_view(),
        name='teacheradmin_assets'),

    url(r'^assets/(?P<asset_id>\d+)/edit/$',
        TeacherAdminAssetsEdit.as_view(),
        name='teacheradmin_assets_edit'),

)
