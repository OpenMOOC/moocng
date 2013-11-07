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

from django.core.management.base import BaseCommand

from moocng.courses.models import KnowledgeQuantum
from moocng.mongodb import get_db


class Command(BaseCommand):

    help = ('Fix the unit ids in the activity\'s documents, some of them have '
            'a null value in that field.')

    def handle(self, *args, **options):
        activity = get_db().get_collection('activity')
        to_fix = activity.find({'$where': 'function() { return this.unit_id == null; }'})
        fixed_counter = 0
        removed_counter = 0
        total = to_fix.count()

        if total > 0:
            for act in to_fix:
                try:
                    kq = KnowledgeQuantum.objects.get(id=int(act['kq_id']))
                    activity.update(
                        {'kq_id': act['kq_id']},
                        {'$set': {'unit_id': kq.unit.id}},
                    )
                    fixed_counter += 1
                except KnowledgeQuantum.DoesNotExist:
                    activity.remove({'kq_id': act['kq_id']})
                    removed_counter += 1

                if ((total / 100) % (fixed_counter + removed_counter)) == 0:
                    percent = int(total / (fixed_counter + removed_counter))
                    print 'Progress: %d%% of %d' % (percent, total)

        print 'Fixed %d activities, removed %d' % (fixed_counter, removed_counter)
