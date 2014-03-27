/*jslint vars: false, browser: true */
/*global django*/

// Copyright 2012 UNED
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

django.jQuery(document).ready(function () {
    "use strict";
    django.jQuery("#id_unittype").change(function (evt) {
        var select = django.jQuery(evt.target),
            option = select.find("option:selected").val();

        if (option === 'n') {
            django.jQuery(".grp-row.start").hide();
            django.jQuery(".grp-row.deadline").hide();
        } else {
            django.jQuery(".grp-row.start").show();
            django.jQuery(".grp-row.deadline").show();
        }
    });
    django.jQuery("#id_unittype").trigger("change");
});
