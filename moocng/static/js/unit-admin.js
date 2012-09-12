/*jslint vars: false, browser: true */
/*global django*/

// Copyright 2012 Rooter Analysis S.L.
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
    django.jQuery(".field-unittype").change(function (evt) {
        var select = django.jQuery(evt.target),
            option = select.find("option:selected").val();

        if (option === 'n') {
            django.jQuery(".field-start").hide();
            django.jQuery(".field-deadline").hide();
        } else {
            django.jQuery(".field-start").show();
            django.jQuery(".field-deadline").show();
        }
    });
    django.jQuery(".field-unittype").trigger("change");
});
