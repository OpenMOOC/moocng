/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _, async */

if (_.isUndefined(window.MOOC)) {
    window.MOOC = {};
}

MOOC.App = Backbone.Router.extend({
    unitSteps: function (unit, loadKQ) {
        "use strict";
        var unitObj = MOOC.models.course.get(unit),
            steps = [];

        if (_.isNull(unitObj.get("knowledgeQuantumList"))) {
            steps.push(async.apply(MOOC.router.loadUnitData, unitObj));
        }
        if (loadKQ) {
            steps.push(function (callback) {
                var kqObj = unitObj.get("knowledgeQuantumList").first();
                MOOC.router.navigate("unit" + unitObj.get("id") + "/kq" + kqObj.get("id"), { trigger: true });
                callback();
            });
        } else {
            steps.push(function (callback) {
                MOOC.views.unitViews[unit].render();
                callback();
            });
        }

        return steps;
    },

    kqSteps: function (unit, kq) {
        "use strict";
        var steps = this.unitSteps(unit, false);

        steps.push(function (callback) {
            var unitObj = MOOC.models.course.get(unit),
                kqObj = unitObj.get("knowledgeQuantumList").get(kq),
                kqView = MOOC.views.kqViews[kq];

            if (_.isUndefined(kqView)) {
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

        return steps;
    },

    unit: function (unit) {
        "use strict";
        unit = parseInt(unit, 10);
        async.series(this.unitSteps(unit, MOOC.router.hasHandler("unit1/kq1")));
    },

    kq: function (unit, kq) {
        "use strict";
        unit = parseInt(unit, 10);
        kq = parseInt(kq, 10);
        async.series(this.kqSteps(unit, kq));
    },

    kqQ: function (unit, kq) {
        "use strict";
        unit = parseInt(unit, 10);
        kq = parseInt(kq, 10);
        var toExecute = this.kqSteps(unit, kq);

        toExecute.push(function (callback) {
            var view = MOOC.views.kqViews[kq],
                cb = _.bind(view.loadQuestion, view);
            cb = async.apply(cb, { data: 0 });
            // data: 0 because YT.PlayerState.ENDED = 0s
            _.bind(view.repeatedlyCheckIfPlayer, view)(cb);
            callback();
        });
        async.series(toExecute);
    },

    kqA: function (unit, kq) {
        "use strict";
        unit = parseInt(unit, 10);
        kq = parseInt(kq, 10);
        var toExecute = this.kqSteps(unit, kq);

        toExecute.push(function (callback) {
            MOOC.views.kqViews[kq].loadSolution();
            callback();
        });
        async.series(toExecute);
    },

    loadUnitData: function (unitObj, callback) {
        "use strict";
        unitObj.set("knowledgeQuantumList", new MOOC.models.KnowledgeQuantumList());
        var unitID = unitObj.get("id");

        MOOC.ajax.getKQsByUnit(unitID, function (data, textStatus, jqXHR) {
            var unitView;

            unitObj.get("knowledgeQuantumList").reset(_.map(data.objects, function (kq) {
                var data = _.pick(kq, "id", "title", "videoID", "teacher_comments",
                                  "supplementary_material", "question", "order",
                                  "correct", "completed");
                data.id = parseInt(data.id, 10);
                return data;
            }));

            unitView = MOOC.views.unitViews[unitID];
            if (_.isUndefined(unitView)) {
                unitView = new MOOC.views.Unit({
                    model: unitObj,
                    id: "unit" + unitID,
                    el: $("#unit" + unitID)[0]
                });
                MOOC.views.unitViews[unitID] = unitView;
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
