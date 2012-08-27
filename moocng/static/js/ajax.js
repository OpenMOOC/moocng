/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _ */

if (_.isUndefined(window.MOOC)) {
    window.MOOC = {};
}

MOOC.ajax = {};

MOOC.ajax.host = "/api/v1/";

MOOC.ajax.getAbsoluteUrl = function (path) {
    "use strict";
    return MOOC.ajax.host + path;
};

MOOC.ajax.genericError = function (jqXHR, textStatus, errorThrown) {
    "use strict";
    var message;
    if (!_.isNull(textStatus)) {
        message = MOOC.trans.ajax.error + ": " + textStatus;
    } else {
        message = MOOC.trans.ajax.unknownError;
    }
    if (!_.isNull(errorThrown)) {
        message += " - " + errorThrown;
    }
    MOOC.alerts.show(MOOC.alerts.ERROR, "AJAX " + MOOC.trans.ajax.error, message);
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

MOOC.ajax.getOptionsByQuestion = function (question, callback) {
    "use strict";
    $.ajax(MOOC.ajax.host + "option/?format=json&question=" + question, {
        success: callback,
        error: MOOC.ajax.genericError
    });
};

MOOC.ajax.getAnswerByQuestion = function (question, callback) {
    "use strict";
    $.ajax(MOOC.ajax.host + "answer/?format=json&question=" + question, {
        success: callback,
        error: MOOC.ajax.genericError
    });
};

MOOC.ajax.sendAnswer = function (answer, question_id, callback) {
    "use strict";
    var url = MOOC.ajax.host + "answer/", method = "post", data = answer.toJSON();
    if (answer.get('id')) {
        url += answer.get('id') + "/";
        method = "put";
    }
    data.question = MOOC.ajax.getAbsoluteUrl('question/' + question_id + '/');
    $.ajax(url, {
        type: method,
        data: JSON.stringify(data),
        contentType: "application/json",
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
    _.delay(function () {
        MOOC.alerts.hide();
    }, 5000);
};

MOOC.alerts.hide = function () {
    "use strict";
    $(".alert").addClass("hide");
};
