/*jslint vars: false, browser: true, nomen: true */
/*global _, jQuery, MOOC */

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

jQuery(document).ready(function () {
    "use strict";

    (function ($) {
        var getCookie,
            csrftoken,
            removeTeacher,
            re;

        getCookie = function (name) {
            var cookieValue = null,
                cookies,
                i,
                cookie;

            if (document.cookie && document.cookie !== '') {
                cookies = document.cookie.split(';');
                for (i = 0; i < cookies.length; i += 1) {
                    cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        };

        csrftoken = getCookie("csrftoken");

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
            minLength: 3
        });

        removeTeacher = function (evt) {
            var id, table, row = $(evt.target).parent().parent();

            table = row.parents('table').attr('id');

            if (table === 'teachers') {
                id = parseInt(row.children().eq(0).text(), 10);
            } else if (table === 'invitations') {
                id = row.children().eq(1).text();
            }

            $.ajax(MOOC.basePath + "delete/" + id + "/", {
                headers: {
                    "X-CSRFToken": csrftoken
                },
                type: "DELETE",
                success: function (data, textStatus, jqXHR) {
                    row.remove();
                    $("#removed.alert-success").show();
                    setTimeout(function () {
                        $(".alert-success").hide();
                    }, MOOC.alertTime);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    $("#generic.alert-error").show();
                    setTimeout(function () {
                        $(".alert-error").hide();
                    }, MOOC.alertTime);
                }
            });
        };

        $("table .icon-remove").click(removeTeacher);

        re = /\S+@\S+\.\S+/; // Very simple email validation
        $("#invite-teacher").next().click(function (evt) {
            evt.preventDefault();
            evt.stopPropagation();
            var data = $("#invite-teacher").val(),
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

            $.ajax(MOOC.basePath + "invite/", {
                data: {
                    data: data
                },
                headers: {
                    "X-CSRFToken": csrftoken
                },
                dataType: "json",
                type: "POST",
                success: function (data, textStatus, jqXHR) {
                    var html;
                    if (data.pending === false) {
                        html = "<tr>" +
                            "<td class='hide'>" + data.id + "</td>" +
                            "<td class='cell-drag-handle'><span class='icon-th'></span></td>" +
                            "<td>" + data.gravatar + "</td>" +
                            "<td>" + data.name + "</td>" +
                            "<td class='ownership'></td>" +
                            "<td class='align-right'><span class='icon-remove pointer'></span></td>" +
                            "</tr>";
                        $("table#teachers > tbody").append(html);
                        $("table#teachers .icon-remove").off("click").click(removeTeacher);
                    } else {
                        html = "<tr>" +
                            "<td>" + data.gravatar + "</td>" +
                            "<td>" + data.name + "</td>" +
                            "<td class='align-right'><span class='icon-remove pointer'></span></td>" +
                            "</tr>";
                        $("table#invitations > tbody").append(html);
                        $("table#invitations .icon-remove").off("click").click(removeTeacher);
                    }

                    $("#added.alert-success").show();
                    setTimeout(function () {
                        $(".alert-success").hide();
                    }, MOOC.alertTime);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    $("#" + jqXHR.status).show();
                    setTimeout(function () {
                        $(".alert-error").hide();
                    }, MOOC.alertTime);
                }
            });
        });

        $(".make-owner").click(function (evt) {
            var data = $(evt.target).parent().parent().children()[0],
                originalOwner = $("table span.label.owner").parent().parent();
            data = $(data).text();
            $.ajax(MOOC.basePath + "transfer/", {
                data: {
                    data: data
                },
                headers: {
                    "X-CSRFToken": csrftoken
                },
                dataType: "json",
                type: "POST",
                success: function (data, textStatus, jqXHR) {
                    var td = $(evt.target).parent();
                    $("table td.ownership").html("");
                    td.html("<span class='label label-info owner'>" + MOOC.owner +
                            "</span>");
                    td.parent().find("td:last-child").html("");
                    originalOwner.find("td:last-child").html("<span class='icon-remove pointer'></span>");
                    originalOwner.find(".icon-remove").click(removeTeacher);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    $("#generic").show();
                    setTimeout(function () {
                        $(".alert-error").hide();
                    }, MOOC.alertTime);
                }
            });
        });

        $("table#teachers tbody").sortable({
            handle: '.cell-drag-handle',
            opacity: 0.7
        }).on('sortstop', function (evt, ui) {
            var new_order = $(this).children("tr").map(function (index, element) {
                return $(element).children("td").eq(0).text();
            }).get();
            $.ajax(MOOC.basePath + "reorder/", {
                data: JSON.stringify(new_order),
                headers: {
                    "X-CSRFToken": csrftoken
                },
                contentType: "application/json",
                dataType: "json",
                type: "POST",
                success: function (data, textStatus, jqXHR) {
                    $("#reordered.alert-success").show();
                    setTimeout(function () {
                        $(".alert-success").hide();
                    }, MOOC.alertTime);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    $("#generic").show();
                    setTimeout(function () {
                        $(".alert-error").hide();
                    }, MOOC.alertTime);
                }
            });
        });
    }(jQuery));
});
