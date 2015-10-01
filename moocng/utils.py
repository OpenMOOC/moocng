# -*- coding: utf-8 -*-
# Copyright 2012-2013 UNED
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
from django.conf import settings
from django.template.loader import get_template
from django.template import Context, RequestContext
import xhtml2pdf.pisa as pisa
try:
    import StringIO
except Exception:
    from io import StringIO
import os

def use_cache(user):
    from moocng.courses.models import CourseTeacher
    return not (user.is_superuser or user.is_staff or
                CourseTeacher.objects.filter(teacher=user.id).exists())

def generate_pdf(request, template_name, context_dict):
    template = get_template(template_name)
    context = RequestContext(request, context_dict)
    html = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), dest=result, link_callback=fetch_resources)
    if not pdf.err:
        return result
    else:
        return None

def fetch_resources(uri, rel):
    path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    return path