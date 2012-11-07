/*jslint vars: false, browser: true, nomen: true */
/*global _, jQuery, MOOC */

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

jQuery(document).ready(function () {
    "use strict";

    (function ($) {
        $("#invite-teacher").typeahead({
            source: function (query, process) {
                $.getJSON("/api/v1/user/",
                    {
                        format: "json",
                        first_name__istartswith: query,
                        last_name__istartswith: query
                    },
                    function (data, textStatus, jqXHR) {
                        process(_.map(data.objects, function (user) {
                            return user.first_name + " " + user.last_name + " (" + user.id + ")";
                        }));
                    });
            },
            minLength: 1
        });

        var re = /\S+@\S+\.\S+/; // Very simple email validation
        $("#invite-teacher").next().click(function (evt) {
            evt.preventDefault();
            evt.stopPropagation();
            var data = $("#invite-teacher").val(),
                csrf,
                idxA,
                idxB;

            $("#invite-teacher").val("");
            if (!re.test(data)) {
                // Extract id from name
                idxA = data.lastIndexOf('(');
                idxB = data.lastIndexOf(')');
                if (idxA > 0 && idxB > 0) {
                    data = data.substring(idxA + 1, idxB);
                } else {
                    data = ""; // Invalid
                }
            }
            csrf = $("#invite-teacher").parent().parent().parent().find("input[name=csrfmiddlewaretoken]").val();

            $.ajax(MOOC.basePath + "invite", {
                data: {
                    data: data,
                    csrfmiddlewaretoken: csrf
                },
                dataType: "json",
                type: "POST",
                success: function (data, textStatus, jqXHR) {
                    var html = "<tr><td class='hide'>" + data.id + "</td>" +
                            "<td></td><td>" + data.name + "</td><td>";
                    if (data.pending) {
                        html += "<span class='label label-warning'>Pending</span>";
                    }
                    html += "</td><td class='align-right'><i class='icon-remove pointer'></i></td></r>";
                    $("table > tbody").append(html);
                    $(".alert-success").show();
                    setTimeout(function () {
                        $(".alert-success").hide();
                    }, 3500);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    $(".alert-error").show();
                    setTimeout(function () {
                        $(".alert-error").hide();
                    }, 3500);
                }
            });
        });
    }(jQuery));
});