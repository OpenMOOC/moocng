/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _, async */

// Copyright 2012 Rooter Analysis S.L.
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

MOOC.App = Backbone.Router.extend({
    unitSteps: function (unit, inClassroomView) {
        "use strict";
        var unitObj = MOOC.models.course.get(unit),
            steps = [];

        if (_.isNull(unitObj.get("knowledgeQuantumList"))) {
            steps.push(async.apply(MOOC.router.loadUnitData, unitObj, inClassroomView));
        }

        if (inClassroomView) {
            steps.push(function (callback) {
                var kqObj = unitObj.get("knowledgeQuantumList").first();
                if (_.isUndefined(kqObj)) {
                    MOOC.alerts.show(MOOC.alerts.INFO, MOOC.trans.api.unitNotReadyTitle, MOOC.trans.api.unitNotReady);
                } else {
                    MOOC.router.navigate("unit" + unitObj.get("id") + "/kq" + kqObj.get("id"), { trigger: true });
                    callback();
                }
            });
        } else {
            steps.push(function (callback) {
                MOOC.views.unitViews[unit].render();
                $("#unit-selector").find("div.collapse").removeClass("in");
                $("#unit" + unit + "-container").addClass("in");

                // HACK for IE 9, see http://stackoverflow.com/questions/5584500/ordered-list-showing-all-zeros-in-ie9
                var rv = -1;
                if (navigator.appName === 'Microsoft Internet Explorer') {
                    if ((new RegExp("MSIE ([0-9]{1,}[.0-9]{0,})")).exec(navigator.userAgent) !== null) {
                        rv = parseFloat(RegExp.$1);
                    }
                }
                if (rv > 8.0) {
                    setTimeout(function () {
                        $("ol").css("counter-reset", "item");
                    }, 1);
                }
                // END HACK

                callback();
            });
        }

        return steps;
    },

    kqSteps: function (unit, kq, render) {
        "use strict";
        var steps = this.unitSteps(unit, false);

        steps.push(function (callback) {
            var unitObj = MOOC.models.course.get(unit),
                kqObj = unitObj.get("knowledgeQuantumList").get(kq);

            if (kqObj.has("attachmentList")) {
                callback();
            } else {
                MOOC.ajax.getAttachmentsByKQ(kqObj.get("id"), function (data, textStatus, jqXHR) {
                    kqObj.set("attachmentList", (new MOOC.models.AttachmentList()).reset(_.map(data.objects, function (attachment) {
                        var data = _.pick(attachment, "id", "attachment");
                        return {
                            id : parseInt(data.id, 10),
                            url: data.attachment
                        };
                    })));

                    callback();
                });
            }
        });

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

            callback();
        });

        if (render) {
            steps.push(function (callback) {
                MOOC.views.kqViews[kq].render();
                callback();
            });
        }

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
        async.series(this.kqSteps(unit, kq, true));
    },

    kqQ: function (unit, kq) {
        "use strict";
        unit = parseInt(unit, 10);
        kq = parseInt(kq, 10);
        var toExecute = this.kqSteps(unit, kq, false);

        toExecute.push(function (callback) {
            MOOC.views.kqViews[kq].loadQuestionData();
            callback();
        });

        toExecute.push(function (callback) {
            var view = MOOC.views.kqViews[kq],
                cb = _.bind(view.loadExercise, view);
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
        var toExecute = this.kqSteps(unit, kq, false);

        toExecute.push(function (callback) {
            MOOC.views.kqViews[kq].loadQuestionData();
            callback();
        });

        toExecute.push(function (callback) {
            MOOC.views.kqViews[kq].loadSolution();
            callback();
        });

        async.series(toExecute);
    },

    kqP: function (unit, kq) {
        "use strict";
        unit = parseInt(unit, 10);
        kq = parseInt(kq, 10);
        var toExecute = this.kqSteps(unit, kq, false);

        toExecute.push(function (callback) {
            MOOC.views.kqViews[kq].loadPeerReviewData();
            callback();
        });

        toExecute.push(function (callback) {
            var view = MOOC.views.kqViews[kq],
                cb = _.bind(view.loadExercise, view);
            cb = async.apply(cb, { data: 0 });
            // data: 0 because YT.PlayerState.ENDED = 0s
            _.bind(view.repeatedlyCheckIfPlayer, view)(cb);
            callback();
        });

        async.series(toExecute);
    },

    loadUnitData: function (unitObj, inClassroomView, callback) {
        "use strict";
        unitObj.set("knowledgeQuantumList", new MOOC.models.KnowledgeQuantumList());
        var unitID = unitObj.get("id");

        MOOC.ajax.getKQsByUnit(unitID, function (data, textStatus, jqXHR) {
            var unitView, hasPeerReviews, peerReviewReviewList, createView;

            hasPeerReviews = false;

            unitObj.get("knowledgeQuantumList").reset(_.map(data.objects, function (kq) {
                var data = _.pick(kq, "id", "title", "videoID", "teacher_comments",
                                  "supplementary_material", "question", "order",
                                  "correct", "completed", "normalized_weight",
                                  "peer_review_assignment");
                data.id = parseInt(data.id, 10);
                if (data.peer_review_assignment !== null) {
                    hasPeerReviews = true;
                }
                return data;
            }));

            createView = function () {
                unitView = MOOC.views.unitViews[unitID];
                if (_.isUndefined(unitView)) {
                    unitView = new MOOC.views.Unit({
                        model: unitObj,
                        id: "unit" + unitID,
                        el: $("#unit" + unitID + "-container")[0]
                    });
                    MOOC.views.unitViews[unitID] = unitView;
                }

                callback();
            };

            if (!inClassroomView && hasPeerReviews) {
                // Only in progress view
                peerReviewReviewList = new MOOC.models.PeerReviewReviewList();
                unitObj.set('peerReviewReviewList', peerReviewReviewList);
                peerReviewReviewList.fetch({
                    data: { 'unit': unitID },
                    success: function () {
                        var peerReviewAssignmentList = new MOOC.models.PeerReviewAssignmentList();
                        peerReviewAssignmentList.fetch({
                            data: { 'unit': unitID },
                            success: function () {
                                var knowledgeQuantumList = unitObj.get('knowledgeQuantumList');
                                knowledgeQuantumList.setPeerReviewAssignments(peerReviewAssignmentList);
                                createView();
                            }
                        });
                    }
                });
            } else {
                createView();
            }

        });
    },

    hasHandler: function (fragment) {
        "use strict";
        return _.any(Backbone.history.handlers, function (handler) {
            return handler.route.test(fragment);
        });
    }
});

MOOC.init = function (course_id, KQRoute) {
    "use strict";
    var path = window.location.pathname,
        unit,
        last_kq = null;

    MOOC.router = new MOOC.App();
    MOOC.router.route("unit:unit", "unit");
    MOOC.host = window.location.protocol + '//' + window.location.host;
    if (KQRoute) {
        MOOC.router.route("unit:unit/kq:kq", "kq");
        MOOC.router.route("unit:unit/kq:kq/q", "kqQ");
        MOOC.router.route("unit:unit/kq:kq/a", "kqA");
        MOOC.router.route("unit:unit/kq:kq/p", "kqP");

        MOOC.models.activity = new MOOC.models.Activity({id: course_id});
        MOOC.models.activity.fetch();

        MOOC.router.on('route:kq', function (u, kq) {
            if (last_kq !== null) {
                MOOC.models.activity.addKQ(last_kq);
            }
            last_kq = kq;
        });
        MOOC.router.on('route:kqQ', function (u, kq) {
            if (last_kq !== null) {
                MOOC.models.activity.addKQ(last_kq);
            }
        });
        MOOC.router.on('route:kqA', function (u, kq) {
            if (last_kq !== null) {
                MOOC.models.activity.addKQ(last_kq);
            }
        });
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
