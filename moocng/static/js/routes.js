/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _ */

if (typeof MOOC === 'undefined') {
    window.MOOC = {};
}

MOOC.App = Backbone.Router.extend({
    routes: {
        "unit:unit": "unit",
        "unit:unit/kq:kq": "kq"
    },

    unit: function (unit) {
        "use strict";
        unit = parseInt(unit, 10);
        $("#unit" + unit).collapse("show");
    },

    kq: function (unit, kq) {
        "use strict";
        // TODO
    }
});

MOOC.init = function () {
    "use strict";
    MOOC.models.init();

    var path = window.location.pathname,
        unit;

    MOOC.router = new MOOC.App();
    if (path.lastIndexOf('/') < path.length - 1) {
        path += '/';
    }
    Backbone.history.start({ root: path });

    unit = MOOC.models.course.find(function (unit) {
        return unit.get("order") === 0;
    });
    MOOC.router.navigate("unit" + unit.get("id"), { trigger: true });
};