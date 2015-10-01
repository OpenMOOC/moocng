# -*- coding: utf-8 -*-

# Copyright 2012 UNED
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

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseGone
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import Site, RequestSite

from moocng.badges.models import Badge, Award, Revocation, build_absolute_url, BadgeByCourse
import json
from moocng.mongodb import get_db
from bson.objectid import ObjectId
import hashlib

@login_required
def my_badges(request):
    try:
        award_list = Award.objects.filter(user=request.user)
        return render_to_response('badges/my_badges.html', {
            'award_list': award_list,
            'user': request.user,
            'openbadges_service_url': settings.BADGES_SERVICE_URL,
        }, context_instance=RequestContext(request))
    except Award.DoesNotExist:
        return HttpResponse(status=404)


def badge(request, badge_slug):
    badge = get_object_or_404(Badge, slug=badge_slug)
    return HttpResponse(json.dumps(badge.to_dict()))


def revocation_list(request):
    revocations = [r.to_dict() for r in Revocation.objects.all()]

    return HttpResponse(json.dumps(revocations))


def issuer(request):
    issuer = {
        'name': settings.BADGES_ISSUER_NAME,
        'image': settings.BADGES_ISSUER_IMAGE,
        'url': settings.BADGES_ISSUER_URL,
        'email': settings.BADGES_ISSUER_EMAIL,
        'revocationList': build_absolute_url(reverse('revocation_list'))
    }
    return HttpResponse(json.dumps(issuer))


def assertion(request, assertion_uuid):
    assertion = get_object_or_404(Award, uuid=assertion_uuid)
    if assertion.revoked:
        return HttpResponseGone(json.dumps({'revoked': True}))

    return HttpResponse(json.dumps(assertion.to_dict()))

def badge_assertion(request, assertion_uuid):
    try:
        site = Site.objects.get_current()
    except ImproperlyConfigured:
        site = RequestSite(request)

    try:
        badge = get_db().get_collection('badge').find({"_id": ObjectId(assertion_uuid)})[0]
        user = get_object_or_404(User, pk=badge['id_user'])
        hashed_email = hashlib.sha256(user.email + settings.BADGES_HASH_SALT).hexdigest()
        if hasattr(badge, 'date'):
            date = badge['date']
        else:
            badge_def = BadgeByCourse.objects.get(pk=badge['id_badge'])
            date = badge_def.course.end_date.isoformat()

        assertion = {
            "uid": str(badge['_id']),
            "badge": "https://%s/badges/badge/%s.json" % (site, badge['id_badge']),
            "recipient": {
                "identity": "sha256$%s" % ( hashed_email ),
                "type": "email",
                "hashed": True,
                "salt": settings.BADGES_HASH_SALT
            },
            "verify": {
                "type": "hosted",
                "url": "https://%s/badges/assertion/%s.json" % (site, str(badge['_id']))
            },
            "issuedOn": date
        }
    except:
        assertion = {
            'error': 'error'
        }

    return HttpResponse(json.dumps(assertion), mimetype='application/json')

def badge_badge(request, id):
    badge = get_object_or_404(BadgeByCourse, pk=id)
    return HttpResponse(json.dumps(badge.to_dict()), mimetype='application/json')

def badge_image(request, id=None, assertion_uuid=None):
    try:
        if id:
            badge = get_object_or_404(BadgeByCourse, pk=id)
            badge_assert = badge
        else:
            badge_assert = get_db().get_collection('badge').find({"_id": ObjectId(assertion_uuid)})[0]
            badge = get_object_or_404(BadgeByCourse, pk=badge_assert['id_badge'])

        try:
            site = Site.objects.get_current()
        except ImproperlyConfigured:
            site = RequestSite(request)

        if badge.image:
            image = badge.image.read()
            content_type = "image/png"
            # Bake image
        else:
            if assertion_uuid:
                assertion = badge_assertion(request, assertion_uuid).content
                badge_assert['id'] = badge_assert['_id']
            else:
                assertion = None

            if not hasattr(settings, 'BADGES_DEFAULT_IMAGE_MIMETYPE'):
                image = render_to_string('badge_image.html', {
                    'site': site,
                    'badge': badge_assert,
                    'assertion': assertion
                })
                content_type = 'image/svg+xml'
            else:
                image_path = '%s/img/%s' % (settings.STATIC_ROOT, settings.BADGES_DEFAULT_IMAGE_FILE)
                handle=open(image_path,'r+')
                image = handle.read()
                content_type = settings.BADGES_DEFAULT_IMAGE_MIMETYPE
                # Bake image

            return HttpResponse(image, content_type=content_type)
    except:
        return HttpResponse(status=404)
