/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _, gettext */

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

if (_.isUndefined(window.MOOC)) {
    window.MOOC = {};
}

MOOC.ajax = {};

MOOC.ajax.showLoading = function () {
    "use strict";
    $(".loading").removeClass("hide");
};

MOOC.ajax.hideLoading = function () {
    "use strict";
    $(".loading").addClass("hide");
};

MOOC.ajax.host = "/api/v1/";

MOOC.ajax.getAbsoluteUrl = function (path) {
    "use strict";
    return MOOC.ajax.host + path;
};

MOOC.ajax.genericError = function (jqXHR, textStatus, errorThrown) {
    "use strict";
    var message,
        responseText;
    responseText = JSON.parse(jqXHR.responseText);
    if (_.isString(responseText.error_message) && responseText.error_message.length > 0) {
        message = responseText.error_message;
    } else if (!_.isNull(textStatus)) {
        message = gettext("Error") + ": " + textStatus;
    } else {
        message = gettext("Unknown error with ajax petition");
    }
    if (jqXHR.status >= 500) {
        message = errorThrown;
    }
    MOOC.alerts.show(MOOC.alerts.ERROR, gettext("Error"), message);
};

MOOC.ajax.getResource = function (uri, callback) {
    "use strict";
    $.ajax(uri + "?format=json", {
        success: callback,
        error: MOOC.ajax.genericError
    });
};

MOOC.ajax.getKQsByUnit = function (unit, callback) {
    "use strict";
    $.ajax(MOOC.ajax.host + "kq/?format=json&unit=" + unit, {
        success: callback,
        error: MOOC.ajax.genericError
    });
};

MOOC.ajax.getAttachmentsByKQ = function (kq, callback) {
    "use strict";
    $.ajax(MOOC.ajax.host + "attachment/?format=json&kq=" + kq, {
        success: callback,
        error: MOOC.ajax.genericError
    });
};

MOOC.ajax.getOptionsByQuestion = function (question, callback) {
    "use strict";
    $.ajax(MOOC.ajax.host + "option/?format=json&question=" + question, {
        success: callback,
        error: MOOC.ajax.genericError
    });
};

MOOC.ajax.getAnswerByQuestion = function (question, callback) {
    "use strict";
    $.ajax(MOOC.ajax.host + "answer/?format=json&question_id=" + question, {
        success: callback,
        error: MOOC.ajax.genericError
    });
};

MOOC.ajax.sendAnswer = function (answer, callback) {
    "use strict";
    var url = MOOC.ajax.host + "answer/",
        method = "post",
        data = answer.toJSON();
    if (!answer.isNew()) {
        url += answer.get('question_id') + "/";
        method = "put";
    }
    $.ajax(url, {
        type: method,
        data: JSON.stringify(data),
        contentType: "application/json",
        success: callback,
        error: MOOC.ajax.genericError
    });
};

MOOC.ajax.sendPRSubmission = function (submission, callback) {
    "use strict";
    var url = MOOC.ajax.host + "peer_review_submissions/";
    $.ajax(url, {
        type: "POST",
        data: JSON.stringify(submission),
        contentType: "application/json",
        success: callback,
        error: MOOC.ajax.genericError
    });
};

MOOC.ajax.getPRSubmission = function (kq, callback) {
    "use strict";
    var url = MOOC.ajax.host + "peer_review_submissions/?kq=" + kq;
    $.ajax(url, {
        success: callback,
        error: MOOC.ajax.genericError
    });
};

MOOC.alerts = {};

MOOC.alerts.ERROR = "error";
MOOC.alerts.SUCCESS = "success";
MOOC.alerts.INFO = "info";

MOOC.alerts.show = function (type, title, message) {
    "use strict";
    var alert = $(".alert.alert-" + type);
    alert.find("h4").text(title);
    alert.find("p").text(message);
    alert.removeClass("hide");
    $("body").animate({ scrollTop: alert.offset().top }, 500);
    _.delay(function () {
        MOOC.alerts.hide();
    }, 10000);
};

MOOC.alerts.hide = function () {
    "use strict";
    $(".alert").addClass("hide");
};
