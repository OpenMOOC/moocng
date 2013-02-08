# Copyright 2012 Rooter Analysis S.L.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.core.management.base import BaseCommand, CommandError
from django.contrib.flatpages.models import FlatPage

from moocng.courses.cache import invalidate_flatpage


class Command(BaseCommand):
    args = '<flatpage_id flatpage_id ...>'
    help = 'Invalidate the cached items related to the specified flatpage'

    def handle(self, *args, **kwargs):

        if args:
            for flatpage_id in args:
                try:
                    flatpage = FlatPage.objects.get(id=int(flatpage_id))
                except FlatPage.DoesNotExist:
                    raise CommandError('FlatPage %s does not exist' % flatpage_id)

                self._invalidate_flatpage_cache(flatpage)

        else:
            for flatpage in FlatPage.objects.all():
                self._invalidate_flatpage_cache(flatpage)


    def _invalidate_flatpage_cache(self, flatpage):
        self.stdout.write('Invalidating cache for %s\n' % flatpage)
        invalidate_flatpage(flatpage)
