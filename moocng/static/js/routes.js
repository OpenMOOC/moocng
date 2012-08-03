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
        var unitObj = MOOC.models.course.get(unit),
            navigateToFirstKQ;

        navigateToFirstKQ = function () {
            var kqObj = unitObj.get("knowledgeQuantumList").first();
            MOOC.router.navigate("unit" + unitObj.get("id") + "/kq" + kqObj.get("id"), { trigger: true });
        };

        if (unitObj.get("knowledgeQuantumList") === null) {
            MOOC.router.loadUnitData(unit, function () {
                navigateToFirstKQ();
            });
        } else {
            navigateToFirstKQ();
        }
    },

    kq: function (unit, kq) {
        "use strict";
        unit = parseInt(unit, 10);
        kq = parseInt(kq, 10);
        var unitObj = MOOC.models.course.get(unit),
            kqView = MOOC.views.kqViews[kq],
            renderKQ;

        renderKQ = function () {
            var kqObj = unitObj.get("knowledgeQuantumList").get(kq);

            if (typeof kqView === "undefined") {
                kqView = new MOOC.views.KnowledgeQuantum({
                    model: kqObj,
                    id: "kq" + kq,
                    el: MOOC.views.unitViews[unit].$("#kq" + kq)[0]
                });
                MOOC.views.kqViews[kq] = kqView;
            }
            kqView.render();
        };

        if (unitObj.get("knowledgeQuantumList") === null) {
            MOOC.router.loadUnitData(unit, function () {
                $("#unit" + unit).collapse("show");
                renderKQ();
            });
        } else {
            $("#unit" + unit).collapse("show");
            renderKQ();
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
    MOOC.models.init();

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