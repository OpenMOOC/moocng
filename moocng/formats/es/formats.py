# -*- encoding: utf-8 -*-

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

DATE_INPUT_FORMATS = (
    # '31/12/2009', '31/12/09'
    '%d/%m/%Y', '%d/%m/%y',
    # '2006-10-25', '10/25/2006', '10/25/06'
    '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y',
)

DATETIME_INPUT_FORMATS = (
    '%d/%m/%Y %H:%M:%S',
    '%d/%m/%Y %H:%M',
    '%d/%m/%y %H:%M:%S',
    '%d/%m/%y %H:%M',
    '%d/%m/%y',
    '%d/%m/%Y',
)
