/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _ */

if (typeof MOOC === 'undefined') {
    window.MOOC = {};
}

MOOC.App = Backbone.Router.extend({
    routes: {
        "unit:unit": "unit"
    },

    unit: function (unit) {
        "use strict";
        unit = parseInt(unit, 10);
        var unitObj = MOOC.models.course.get(unit),
            unitView = MOOC.views.unitViews[unit];

        if (typeof unitView === "undefined") {
            MOOC.router.loadUnitData(unit, function () {});
        } else {
            unitView.render();
        }
    },

    loadUnitData: function (unit, callback) {
        "use strict";
        var unitObj = MOOC.models.course.get(unit);
        unitObj.set("knowledgeQuantumList", new MOOC.models.KnowledgeQuantumList());

        MOOC.ajax.getKQsByUnit(unit, function (data, textStatus, jqXHR) {
            var unitView;

            unitObj.get("knowledgeQuantumList").reset(_.map(data.objects, function (kq) {
                var data = _.pick(kq, "id", "title", "videoID", "question", "order");
                data.id = parseInt(data.id, 10);
                return data;
            }));

            unitView = MOOC.views.unitViews[unit];
            if (typeof unitView === "undefined") {
                unitView = new MOOC.views.Unit({
                    model: unitObj,
                    id: "unit" + unit,
                    el: $("#unit" + unit)[0]
                });
                MOOC.views.unitViews[unit] = unitView;
            }
            unitView.render();

            callback();
        });
    }
});

MOOC.init = function () {
    "use strict";
    var path = window.location.pathname,
        unit;

    MOOC.router = new MOOC.App();
    if (path.lastIndexOf('/') < path.length - 1) {
        path += '/';
    }
    Backbone.history.start({ root: path });

    if (window.location.hash.length > 1) {
        path = window.location.hash.substring(1); // Remove #
        MOOC.router.navigate(path, { trigger: true });
    } else {
        unit = MOOC.models.course.first();
        MOOC.router.navigate("unit" + unit.get("id"), { trigger: true });
    }
};