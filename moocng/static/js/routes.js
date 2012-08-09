/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _, async */

if (typeof MOOC === 'undefined') {
    window.MOOC = {};
}

MOOC.App = Backbone.Router.extend({
    unit: function (unit) {
        "use strict";
        unit = parseInt(unit, 10);
        var unitObj = MOOC.models.course.get(unit),
            toExecute = [];

        if (unitObj.get("knowledgeQuantumList") === null) {
            toExecute.push(async.apply(MOOC.router.loadUnitData, unit));
        }

        if (MOOC.router.hasHandler("unit1/kq1")) {
            toExecute.push(function (callback) {
                var kqObj = unitObj.get("knowledgeQuantumList").first();
                MOOC.router.navigate("unit" + unitObj.get("id") + "/kq" + kqObj.get("id"), { trigger: true });
                callback();
            });
        } else {
            toExecute.push(function (callback) {
                MOOC.views.unitViews[unit].render();
                callback();
            });
        }

        async.series(toExecute);
    },

    kq: function (unit, kq) {
        "use strict";
        unit = parseInt(unit, 10);
        kq = parseInt(kq, 10);
        var unitObj = MOOC.models.course.get(unit),
            kqView = MOOC.views.kqViews[kq],
            toExecute = [];

        if (unitObj.get("knowledgeQuantumList") === null) {
            toExecute.push(async.apply(MOOC.router.loadUnitData, unit));
        }

        toExecute.push(function (callback) {
            MOOC.views.unitViews[unit].render();
            callback();
        });

        toExecute.push(function (callback) {
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

            callback();
        });

        async.series(toExecute);
    },

    kqQ: function (unit, kq) {
        "use strict";
        this.kq(unit, kq);
        kq = parseInt(kq, 10);
        var view = MOOC.views.kqViews[kq];
        view.loadQuestion();
    },

    kqA: function (unit, kq) {
        "use strict";
        this.kq(unit, kq);
        kq = parseInt(kq, 10);
        var view = MOOC.views.kqViews[kq];
    },

    loadUnitData: function (unit, callback) {
        "use strict";
        var unitObj = MOOC.models.course.get(unit);
        unitObj.set("knowledgeQuantumList", new MOOC.models.KnowledgeQuantumList());

        MOOC.ajax.getKQsByUnit(unit, function (data, textStatus, jqXHR) {
            var unitView;

            unitObj.get("knowledgeQuantumList").reset(_.map(data.objects, function (kq) {
                var data = _.pick(kq, "id", "title", "videoID", "question", "order", "correct", "completed");
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

            callback();
        });
    },

    hasHandler: function (fragment) {
        "use strict";
        return _.any(Backbone.history.handlers, function (handler) {
            return handler.route.test(fragment);
        });
    }
});

MOOC.init = function (KQRoute) {
    "use strict";
    var path = window.location.pathname,
        unit;

    MOOC.router = new MOOC.App();
    MOOC.router.route("unit:unit", "unit");
    if (KQRoute) {
        MOOC.router.route("unit:unit/kq:kq", "kq");
        MOOC.router.route("unit:unit/kq:kq/q", "kqQ");
        MOOC.router.route("unit:unit/kq:kq/a", "kqA");
    }
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