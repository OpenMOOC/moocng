/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _ */

if (typeof MOOC === 'undefined') {
    window.MOOC = {};
}

MOOC.ajax = {};

MOOC.ajax.host = "/api/v1/";

// TODO errors?

MOOC.ajax.getResource = function (uri, callback) {
    "use strict";
    $.ajax(uri + "?format=json", {
        success: callback
    });
};

MOOC.ajax.getKQsByUnit = function (unit, callback) {
    "use strict";
    $.ajax(MOOC.ajax.host + "kq/?format=json&unit=" + unit, {
        success: callback
    });
};

MOOC.ajax.getOptionsByQuestion = function (question, callback) {
    "use strict";
    $.ajax(MOOC.ajax.host + "option/?format=json&question=" + question, {
        success: callback
    });
};
