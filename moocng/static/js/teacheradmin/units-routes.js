/*jslint vars: false, browser: true, nomen: true */
/*global MOOC:true, _, jQuery, Backbone */

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

(function ($, Backbone, _) {
    "use strict";

    var errorHandler = function () {
            MOOC.ajax.showAlert("generic");
            MOOC.ajax.hideLoading();
        },
        loadKQs = function (callback) {
            var promises = [];
            MOOC.models.course.each(function (unit) {
                unit.set("knowledgeQuantumList", new MOOC.models.KnowledgeQuantumList());
                promises.push($.ajax(MOOC.ajax.host + "privkq/?format=json&unit=" + unit.get("id"), {
                    success: function (data, textStatus, jqXHR) {
                        unit.get("knowledgeQuantumList").reset(_.map(data.objects, function (kq) {
                            var data = _.pick(kq, "id", "title",
                                "teacher_comments", "supplementary_material",
                                "question", "order", "correct", "completed",
                                "peer_review_assignment", "asset_availability",
                                "iframe_code", "media_content_type", "media_content_id",
                                "normalized_weight", "peer_review_assignment",
                                "thumbnail_url", "weight");
                            data.id = parseInt(data.id, 10);
                            return data;
                        }));
                    }
                }));
            });
            $.when.apply(null, promises).done(callback).fail(errorHandler);
        },
        loadKQDetails = function (kq, callback) {
            var promises = [],
                questionUrl,
                peer_review_assignment,
                asset_availability,
                assetList,
                assetUrl,
                assetId,
                criterionList,
                assignmentUrl,
                assignmentId;

            if (kq.has("question") && !kq.has("questionInstance")) {
                questionUrl = kq.get("question").replace("question", "privquestion");
                promises.push($.ajax(questionUrl, {
                    success: function (data, textStatus, jqXHR) {
                        var question = new MOOC.models.Question({
                            id: parseInt(data.id, 10),
                            lastFrame: data.last_frame,
                            solution_media_content_type: data.solution_media_content_type,
                            solution_media_content_id: data.solution_media_content_id,
                            iframe_code: data.iframe_code,
                            solutionText: data.solution_text,
                            use_last_frame: data.use_last_frame
                        });
                        kq.set("questionInstance", question);
                    }
                }));
            }

            if (kq.has("peer_review_assignment") && !kq.has("peerReviewAssignmentInstance")) {
                peer_review_assignment = new MOOC.models.PeerReviewAssignment();
                criterionList = peer_review_assignment.get("_criterionList");
                assignmentUrl = kq.get("peer_review_assignment").split("/");

                assignmentId = parseInt(assignmentUrl.pop(), 10);
                while (_.isNaN(assignmentId)) {
                    assignmentId = parseInt(assignmentUrl.pop(), 10);
                }

                promises.push($.ajax(kq.get("peer_review_assignment").replace("peer_review_assignment", "privpeer_review_assignment"), {
                    success: function (data, textStatus, jqXHR) {
                        peer_review_assignment.set("id", parseInt(data.id, 10));
                        peer_review_assignment.set("description", data.description);
                        peer_review_assignment.set("minimum_reviewers", data.minimum_reviewers);
                        peer_review_assignment.set("knowledgeQuantum", data.kq);
                        kq.set("peerReviewAssignmentInstance", peer_review_assignment);
                    }
                }));

                promises.push(
                    peer_review_assignment.get("_criterionList").fetch({
                        data: { 'assignment': assignmentId }
                    })
                );
            }

            if (kq.has("asset_availability") && !kq.has("assetAvailabilityInstance")) {
                asset_availability = new MOOC.models.AssetAvailability();
                assetList = asset_availability.get("_assetList");
                assetList = asset_availability.get("_otherAssets");

                promises.push($.ajax(kq.get("asset_availability").replace("asset_availability", "privasset_availability"), {
                    success: function (data, textStatus, jqXHR) {
                        asset_availability.set("id", parseInt(data.id, 10));
                        asset_availability.set("available_from", data.available_from);
                        asset_availability.set("available_to", data.available_to);
                        asset_availability.set("kq", data.kq);
                        asset_availability.set("assets", data.assets);
                        kq.set("assetAvailabilityInstance", asset_availability);
                        asset_availability.set("knowledgeQuantumInstance", kq);
                    }
                }));

                promises.push(
                    asset_availability.get("_assetList").fetch({
                        data: { 'kq': kq.id }
                    }),
                    asset_availability.get("_otherAssets").fetch({
                        data: { 'exclude_kq': kq.id }
                    })
                );
            }


            if (!kq.has("attachmentList")) {
                promises.push($.ajax(MOOC.ajax.host + "attachment/?format=json&kq=" + kq.get("id"), {
                    success: function (data, textStatus, jqXHR) {
                        var attachmentList = new MOOC.models.AttachmentList(
                            _.map(data.objects, function (attachment) {
                                return {
                                    id: parseInt(attachment.id, 10),
                                    url: attachment.attachment
                                };
                            })
                        );
                        kq.set("attachmentList", attachmentList);
                    }
                }));
            }

            $.when.apply(null, promises).done(callback).fail(errorHandler);
        };

    MOOC.ajax = {
        host: "/api/v1/",

        getAbsoluteUrl: function (path) {
            return MOOC.ajax.host + path;
        },

        showLoading: function () {
            $(".loading").removeClass("hide");
        },

        hideLoading: function () {
            $(".loading").addClass("hide");
        },

        showAlert: function (id) {
            var alert = $("#" + id);
            alert.removeClass("hide");
            $("body").animate({ scrollTop: alert.offset().top }, 500);
            setTimeout(function () {
                $("#" + id).addClass("hide");
            }, MOOC.alertTime);
        }
    };

    MOOC.App = Backbone.Router.extend({
        all: function () {
            var callback = function () {
                if (_.isUndefined(MOOC.views.listView)) {
                    MOOC.views.listView = new MOOC.views.List({
                        model: MOOC.models.course,
                        el: $("#units-container")[0]
                    });
                }
                MOOC.views.listView.render();
                MOOC.ajax.hideLoading();
            };

            if (MOOC.models.course.length === 0) {
                MOOC.ajax.showLoading();
                MOOC.models.course.fetch({
                    error: errorHandler,
                    success: function () {
                        loadKQs(callback);
                    }
                });
            } else {
                callback();
            }
        },

        editUnit: function (unit) {
            var callback = function () {
                var unitObj,
                    unitView;

                unit = parseInt(unit, 10);
                unitView = MOOC.views.unitEditorView;
                unitObj = MOOC.models.course.find(function (item) {
                    return unit === item.get("id");
                });

                if (_.isUndefined(unitView)) {
                    unitView = new MOOC.views.UnitEditor({
                        model: unitObj,
                        id: "unitEditor" + unit,
                        el: $("#unit-editor")[0]
                    });
                    MOOC.views.unitEditorView = unitView;
                } else {
                    unitView.model = unitObj;
                }

                unitView.render();
                MOOC.ajax.hideLoading();
            };

            if (MOOC.models.course.length === 0) {
                MOOC.ajax.showLoading();
                MOOC.models.course.fetch({
                    error: errorHandler,
                    success: function () {
                        loadKQs(callback);
                    }
                });
            } else {
                callback();
            }
        },

        editKQ: function (kq) {
            var callback = function () {
                var unitObj,
                    kqObj,
                    kqView,
                    callback;

                kq = parseInt(kq, 10);
                kqView = MOOC.views.kqEditorView;
                unitObj = MOOC.models.course.getByKQ(kq);
                kqObj = unitObj.get("knowledgeQuantumList").find(function (item) {
                    return kq === item.get("id");
                });

                callback = function () {
                    if (_.isUndefined(kqView)) {
                        kqView = new MOOC.views.KQEditor({
                            model: kqObj,
                            id: "kqEditor" + kq,
                            el: $("#kq-editor")[0]
                        });
                        MOOC.views.kqEditorView = kqView;
                    } else {
                        kqView.model = kqObj;
                    }

                    kqView.render();
                    MOOC.ajax.hideLoading();
                };

                if ((kqObj.has("question") && !kqObj.has("questionInstance")) || !kqObj.has("attachmentList")) {
                    loadKQDetails(kqObj, callback);
                } else {
                    callback();
                }
            };

            if (MOOC.models.course.length === 0) {
                MOOC.ajax.showLoading();
                MOOC.models.course.fetch({
                    error: errorHandler,
                    success: function () {
                        loadKQs(callback);
                    }
                });
            } else {
                callback();
            }
        }
    });

    MOOC.init = function (courseID, unitBadgeClasses) {
        var path = window.location.pathname;
        MOOC.host = window.location.protocol + '//' + window.location.host;
        MOOC.unitBadgeClasses = unitBadgeClasses;
        MOOC.alertTime = 4000;
        MOOC.models.course.courseId = courseID;
        MOOC.models.Question.prototype.url = function () {
            return MOOC.ajax.getAbsoluteUrl("privquestion/") + this.get("id") + "/";
        };
        MOOC.models.KnowledgeQuantum.prototype.url = function () {
            return MOOC.ajax.getAbsoluteUrl("privkq/") + this.get("id") + "/";
        };
        MOOC.models.AssetAvailability.prototype.url = function () {
            if (this.has("id")) {
                return MOOC.ajax.getAbsoluteUrl("privasset_availability/") + this.get("id") + "/";
            }
            return MOOC.ajax.getAbsoluteUrl("privasset_availability/");
        };
        MOOC.models.PeerReviewAssignment.prototype.url = function () {
            if (this.has("id")) {
                return MOOC.ajax.getAbsoluteUrl("privpeer_review_assignment/") + this.get("id") + "/";
            }

            return MOOC.ajax.getAbsoluteUrl("privpeer_review_assignment/");
        };
        MOOC.models.EvaluationCriterion.prototype.url = function () {
            if (this.has("id")) {
                return MOOC.ajax.getAbsoluteUrl("privevaluation_criterion/") + this.get("id") + "/";
            }

            return MOOC.ajax.getAbsoluteUrl("privevaluation_criterion/");
        };

        MOOC.router = new MOOC.App();
        MOOC.router.route("", "all");
        MOOC.router.route("unit:unit", "editUnit");
        MOOC.router.route("kq:kq", "editKQ");

        if (path.lastIndexOf('/') < path.length - 1) {
            path += '/';
        }
        Backbone.history.start({ root: path });

        if (window.location.hash.length > 1) {
            path = window.location.hash.substring(1); // Remove #
            MOOC.router.navigate(path, { trigger: true });
        } else {
            MOOC.router.navigate("", { trigger: true });
        }
    };
}(jQuery, Backbone, _));
