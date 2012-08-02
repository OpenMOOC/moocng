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
            var kqObj = unitObj.get("knowledgeQuantumList").find(function (kq) {
                return kq.get("order") === 0;
            });
            MOOC.router.navigate("unit" + unitObj.get("id") + "/kq" + kqObj.get("id"), { trigger: true });
        };

        if (unitObj.get("knowledgeQuantumList") === null) {
            unitObj.set("knowledgeQuantumList", new MOOC.models.KnowledgeQuantumList());

            MOOC.ajax.getKQsByUnit(unit, function (data, textStatus, jqXHR) {
                var unitView;

                unitObj.get("knowledgeQuantumList").reset(_.map(data.objects, function (kq) {
                    var data = _.pick(kq, "id", "title", "videoID");
                    // TODO order
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

                navigateToFirstKQ();
                $("#unit" + unit).collapse("show");
            });
        } else {
            navigateToFirstKQ();
            $("#unit" + unit).collapse("show");
        }
    },

    kq: function (unit, kq) {
        "use strict";
        unit = parseInt(unit, 10);
        kq = parseInt(kq, 10);
        // TODO what if unit is not loaded?
        var unitObj = MOOC.models.course.get(unit),
            kqObj = unitObj.get("knowledgeQuantumList").get(kq),
            kqView = MOOC.views.kqViews[kq];

        if (typeof kqView === "undefined") {
            kqView = new MOOC.views.KnowledgeQuantum({
                model: kqObj,
                id: "kq" + kq,
                el: MOOC.views.unitViews[unit].$("#kq" + kq)[0]
            });
            MOOC.views.kqViews[kq] = kqView;
        }
        kqView.render();
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