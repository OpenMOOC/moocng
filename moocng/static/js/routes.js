/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _, async, gettext */

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

MOOC.io = {
    _loadDataFromUnit: function (unitId, Model) {
        "use strict";
        var dfd = $.Deferred(), list = new Model();

        list.fetch({
            data: { 'unit': unitId },
            success: function () {
                dfd.resolve(list);
            },
            error: function () {
                dfd.reject();
            }
        });

        return dfd.promise();
    },

    loadPeerReviewReviewList: function (unitId) {
        "use strict";
        return MOOC.io._loadDataFromUnit(unitId, MOOC.models.PeerReviewReviewList);
    },

    loadPeerReviewAssignmentList: function (unitId) {
        "use strict";
        return MOOC.io._loadDataFromUnit(unitId, MOOC.models.PeerReviewAssignmentList);
    },

    loadEvaluationCriterionList: function (unitId) {
        "use strict";
        return MOOC.io._loadDataFromUnit(unitId, MOOC.models.EvaluationCriterionList);
    },

    loadPeerReviewSubmissionList: function (unitId) {
        "use strict";
        return MOOC.io._loadDataFromUnit(unitId, MOOC.models.PeerReviewSubmissionList);
    }
};

MOOC.App = Backbone.Router.extend({
    lastUnitView: null,
    unitSteps: function (unit, loadFirstKQ) {
        "use strict";
        var unitObj = MOOC.models.course.get(unit),
            steps = [],
            self = this,
            shouldDelegateEvents = false;

        if (_.isNull(unitObj.get("knowledgeQuantumList"))) {
            steps.push(async.apply(MOOC.router.loadUnitData, unitObj));
        } else {
            shouldDelegateEvents = true;
        }

        if (loadFirstKQ) {
            steps.push(function (callback) {
                var kqObj = unitObj.get("knowledgeQuantumList").first();
                if (_.isUndefined(kqObj)) {
                    MOOC.alerts.show(MOOC.alerts.INFO,
                                     gettext("The module is not ready"),
                                     gettext("This module has no nuggets. Probably the start date hasn't been reached yet."));
                } else {
                    MOOC.router.navigate("unit" + unitObj.get("id") + "/kq" + kqObj.get("id"), { trigger: true });
                    callback();
                }
            });
        } else {
            steps.push(function (callback) {
                self.lastUnitView = MOOC.views.unitViews[unit];
                MOOC.views.unitViews[unit].render();
                if (shouldDelegateEvents && _.has(self.lastUnitView, 'undelegateEventsInSubViews')) {
                    self.lastUnitView.delegateEventsInSubViews();
                }
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

            if (kqObj.has("transcriptionList")) {
                callback();
            } else {
                MOOC.ajax.getTranscriptionsByKQ(kqObj.get("id"), function (data, textStatus, jqXHR) {
                    kqObj.set("transcriptionList", (new MOOC.models.TranscriptionList()).reset(_.map(data.objects, function (transcription) {
                        var data = _.pick(transcription, "id", "filename", "language", "transcription_type");
                        return {
                            id : parseInt(data.id, 10),
                            url: data.filename,
                            language: data.language,
                            type: data.transcription_type
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
        if (!_.isNull(this.lastUnitView)) {
            if (_.has(this.lastUnitView, 'undelegateEventsInSubViews')) {
                this.lastUnitView.undelegateEventsInSubViews();
            }
        }
        async.series(this.unitSteps(unit, MOOC.router.hasHandler("unit1/kq1")));
    },

    kq: function (unit, kq) {
        "use strict";
        unit = parseInt(unit, 10);
        kq = parseInt(kq, 10);
        var toExecute = this.kqSteps(unit, kq, true);
        async.series(toExecute);
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
            cb({ data: 0 });
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
            cb({ data: 0 });
            callback();
        });

        async.series(toExecute);
    },

    kqAS: function (unit, kq) {
        "use strict";
        unit = parseInt(unit, 10);
        kq = parseInt(kq, 10);
        var toExecute = this.kqSteps(unit, kq, false);

        toExecute.push(function (callback) {
            MOOC.views.kqViews[kq].loadAssetsData();
            callback();
        });

        toExecute.push(function (callback) {
            MOOC.views.kqViews[kq].loadAssets();
            callback();
        });

        async.series(toExecute);
    },

    loadUnitData: function (unitObj, callback) {
        "use strict";
        unitObj.set("knowledgeQuantumList", new MOOC.models.KnowledgeQuantumList());
        var unitID = unitObj.get("id"),
            inClassroomView = MOOC.router.hasHandler("unit1/kq1");

        MOOC.ajax.getKQsByUnit(unitID, function (data, textStatus, jqXHR) {
            var unitView,
                hasPeerReviews,
                peerReviewReviewList,
                createView;

            hasPeerReviews = false;

            unitObj.get("knowledgeQuantumList").reset(_.map(data.objects, function (kq) {
                var data = _.pick(kq, "id", "title", "teacher_comments",
                                  "supplementary_material", "question", "order",
                                  "iframe_code", "media_content_type", "media_content_id",
                                  "correct", "completed", "normalized_weight",
                                  "peer_review_assignment", "peer_review_score",
                                  "asset_availability", "thumbnail_url");
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
                $.when(MOOC.io.loadPeerReviewReviewList(unitID),
                       MOOC.io.loadPeerReviewAssignmentList(unitID),
                       MOOC.io.loadEvaluationCriterionList(unitID),
                       MOOC.io.loadPeerReviewSubmissionList(unitID))
                    .then(function (peerReviewReviewList,
                                    peerReviewAssignmentList,
                                    evaluationCriterionList,
                                    peerReviewSubmissionList) {

                        var knowledgeQuantumList = unitObj.get('knowledgeQuantumList');

                        unitObj.set('peerReviewReviewList', peerReviewReviewList);
                        knowledgeQuantumList.setPeerReviewAssignmentList(peerReviewAssignmentList);
                        knowledgeQuantumList.setEvaluationCriterionList(evaluationCriterionList);
                        knowledgeQuantumList.setPeerReviewSubmissionList(peerReviewSubmissionList);
                        createView();
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

    MOOC.models.course.courseId = course_id;

    MOOC.router = new MOOC.App();
    MOOC.router.route("unit:unit", "unit");
    MOOC.host = window.location.protocol + '//' + window.location.host;
    MOOC.players_listener = _.extend({}, Backbone.Events);
    MOOC.players_listener.on('mediaContentFinished', function (view) {
        _.bind(view.loadExercise, view)();
        _.bind(view.loadAssets, view)();
    });

    if (KQRoute) {
        MOOC.router.route("unit:unit/kq:kq", "kq");
        MOOC.router.route("unit:unit/kq:kq/q", "kqQ");
        MOOC.router.route("unit:unit/kq:kq/a", "kqA");
        MOOC.router.route("unit:unit/kq:kq/p", "kqP");
        MOOC.router.route("unit:unit/kq:kq/as", "kqAS");

        MOOC.models.activity = new MOOC.models.ActivityCollection();
        MOOC.models.activity.course_id = course_id;
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
        MOOC.router.on('route:kqAS', function (u, kq) {
            if (last_kq !== null) {
                MOOC.models.activity.addKQ(last_kq);
            }
        });
    }
    if (path.lastIndexOf('/') < path.length - 1) {
        path += '/';
    }

    window.location.hash = window.location.hash.replace(/#!/, '#');
    Backbone.history.start({ root: path });

    if (window.location.hash.length > 1) {
        path = window.location.hash.substring(1); // Remove #
        MOOC.router.navigate(path, { trigger: true });
    } else {
        unit = MOOC.models.course.first();
        MOOC.router.navigate("unit" + unit.get("id"), { trigger: true });
    }
};
