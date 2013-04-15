/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _, moment */

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

MOOC.models = {
    detailUrlToCollection: function (url) {
        "use strict";
        var aux = url.split("/"),
            result = "",
            i;
        for (i = 1; i < (aux.length - 2); i += 1) {
            result += "/" + aux[i];
        }
        return result + "/";
    },
    truncateText: function (text, maxLength) {
        "use strict";
        var idx;

        if (text.length > maxLength) {
            text = text.substr(0, maxLength);
            idx = text.lastIndexOf(' ');
            if (idx > 0) {
                text = text.substring(0, idx);
            } else {
                text = text.substring(0, maxLength - 3);
            }
            text += "...";
        }
        return text;
    }
};

MOOC.models.TastyPieCollection = Backbone.Collection.extend({
    parse: function (resp, xhr) {
        "use strict";
        return resp.objects;
    }
});

MOOC.models.PeerReviewSubmission = Backbone.Model.extend({
    defaults: {
        author: null,
        author_reviews: 0,
        created: null,
        kq: null,
        reviews: 0,
        text: null, // optional
        file: null // optional
    },

    parse: function (resp, xhr) {
        "use strict";
        return _.pick(resp, "_id", "author", "author_reviews", "created", "kq",
            "reviews", "text", "file");
    },

    url: function () {
        "use strict";
        return MOOC.ajax.getAbsoluteUrl("peer_review_submissions/") + this.get("_id") + "/";
    }
});

MOOC.models.PeerReviewSubmissionList = MOOC.models.TastyPieCollection.extend({
    model: MOOC.models.PeerReviewSubmission,
    url: MOOC.ajax.getAbsoluteUrl("peer_review_submissions/")
});

MOOC.models.EvaluationCriterion = Backbone.Model.extend({
    defaults: {
        title: "",
        description: "",
        assignment: null
    },

    parse: function (resp, xhr) {
        "use strict";
        if (resp !== null) {
            return _.pick(resp, "id", "order", "description", "assignment", "title");
        }
        return resp;
    },

    url: function () {
        "use strict";
        return MOOC.ajax.getAbsoluteUrl("evaluation_criterion/") + this.get("id") + "/";
    }
});

MOOC.models.EvaluationCriterionList = MOOC.models.TastyPieCollection.extend({
    model: MOOC.models.EvaluationCriterion,

    comparator: function (criterion) {
        "use strict";
        return criterion.get("order");
    },

    url: function () {
        "use strict";
        return MOOC.ajax.getAbsoluteUrl("evaluation_criterion/");
    }
});

MOOC.models.PeerReviewAssignment = Backbone.Model.extend({
    defaults: {
        description: "",
        minimum_reviewers: null,
        kq: null,

        _criterionList: new MOOC.models.EvaluationCriterionList(),
        _knowledgeQuantumInstance: null,
        _submitted: false
    },

    url: function () {
        "use strict";
        if (this.has("id")) {
            return MOOC.ajax.getAbsoluteUrl("peer_review_assignment/") + this.get("id") + "/";
        }

        return MOOC.ajax.getAbsoluteUrl("peer_review_assignment/");
    }
});

MOOC.models.PeerReviewAssignmentList = MOOC.models.TastyPieCollection.extend({
    model: MOOC.models.PeerReviewAssignment,
    url: MOOC.ajax.getAbsoluteUrl('peer_review_assignment/')
});

MOOC.models.Asset = Backbone.Model.extend({
    defaults: {
        description: "",
        name: "",
        slot_duration: 0,
        max_bookable_slots: 0,
        capacity: 0
    },

    url: function () {
        "use strict";
        if (this.has("id")) {
            return MOOC.ajax.getAbsoluteUrl("asset/") + this.get("id") + "/";
        }

        return MOOC.ajax.getAbsoluteUrl("asset/");
    }
});

MOOC.models.AssetList = MOOC.models.TastyPieCollection.extend({
    model: MOOC.models.Asset,
    url: MOOC.ajax.getAbsoluteUrl('asset/')
});

MOOC.models.AssetAvailability = Backbone.Model.extend({
    defaults: {
        kq: null,
        available_from: null,
        available_to: null,

        knowledgeQuantumInstance: null,
        _assetList: new MOOC.models.AssetList()
    },

    url: function () {
        "use strict";
        if (this.has("id")) {
            return MOOC.ajax.getAbsoluteUrl("asset_availability/") + this.get("id") + "/";
        }

        return MOOC.ajax.getAbsoluteUrl("asset_availability/");
    }
});

MOOC.models.Reservation = Backbone.Model.extend({
    defaults: {
        asset: null,
        user: null,
        kq: null,
        slot_id: 0,
        reservation_begins: null,
        reservation_ends: null,

        _knowledgeQuantumInstance: null,
        _assetInstance: null,
        _userInstance: null
    },

    url: function () {
        "use strict";
        if (this.has("id")) {
            return MOOC.ajax.getAbsoluteUrl("reservation/") + this.get("id") + "/";
        }

        return MOOC.ajax.getAbsoluteUrl("reservation/");
    }
});

MOOC.models.Activity = Backbone.Model.extend({
    defaults: {
        kqs: []
    },

    url: function () {
        "use strict";
        return MOOC.ajax.getAbsoluteUrl('activity/') + this.get('id') + '/';
    },

    addKQ: function (kq, callback) {
        "use strict";
        if (!_.include(this.get('kqs'), kq)) {
            this.set('kqs', _.union(this.get('kqs'), [kq]));
            if (_.isUndefined(callback)) {
                this.save();
            } else {
                this.save("kqs", this.get("kqs"), { success: callback });
            }
        }
    },

    hasKQ: function (kq) {
        "use strict";
        return _.include(this.get('kqs'), String(kq));
    }
});

MOOC.models.Option = Backbone.Model.extend({
    defaults: {
        optiontype: 't',
        x: 0,
        y: 0,
        width: 100,
        height: 12,
        solution: null,
        text: "",
        feedback: null
    },

    /**
     * Returns:
     *  true if correct
     *  false if incorrect
     *  undefined if can't be corrected yet, because the deadline hasn't been
     *               reached, there is no solution data
     */
    isCorrect: function (reply) {
        "use strict";
        var solution = this.get('solution'),
            optiontype = this.get('optiontype'),
            result;

        if (_.isUndefined(solution) || _.isNull(solution)) {
            return;
        }

        if (optiontype === 'l') {
            result = true;
        } else if (optiontype === 't') {
            if (_.isString(reply.get("value"))) {
                result = solution.toLowerCase() === reply.get('value').toLowerCase();
            } else {
                // This shouldn't happen
                result = false;
            }
        } else {
            if (solution.toLowerCase() === "true") {
                result = reply.get('value') === true;
            } else {
                result = reply.get('value') === false;
            }
        }

        return result;
    }
});

MOOC.models.OptionList  = MOOC.models.TastyPieCollection.extend({
    model: MOOC.models.Option
});

MOOC.models.Question = Backbone.Model.extend({
    defaults: {
        lastFrame: null, // of the KnowledgeQuantum's video
        solutionVideo: null,
        solutionText: null,
        optionList: null,
        answer: null,
        use_last_frame: true
    },

    url: function () {
        "use strict";
        return MOOC.ajax.getAbsoluteUrl("question/") + this.get("id") + "/";
    },

    parse: function (resp, xhr) {
        "use strict";
        return {
            id: parseInt(resp.id, 10),
            lastFrame: resp.last_frame,
            solutionVideo: resp.solutionID,
            use_last_frame: resp.use_last_frame
        };
    },

    sync: function (method, model, options) {
        "use strict";
        var model2send = model.clone(),
            question,
            kqObj,
            i;
        MOOC.models.course.each(function (unit) {
            if (unit.has("knowledgeQuantumList")) {
                unit.get("knowledgeQuantumList").each(function (kq) {
                    if (kq.has("questionInstance")) {
                        question = kq.get("questionInstance");
                        if (question.cid === model.cid) {
                            kqObj = kq;
                        }
                    } else if (kq.has("question")) {
                        question = kq.get("question");
                        question = question.split("question/")[1].split("/")[0];
                        question = parseInt(question, 10);
                        if (question === model.get("id")) {
                            kqObj = kq;
                        }
                    }
                });
            }
        });
        model2send.set("kq", kqObj.url());
        if (method === "create") {
            model2send.url = MOOC.models.detailUrlToCollection(model.url());
        }
        model2send.unset("lastFrame");
        if (model.has("solutionVideo") && model.get("solutionVideo") !== "") {
            model2send.set("solutionID", model.get("solutionVideo"));
        } else {
            model2send.set("solutionID", "");
        }
        model2send.unset("solutionVideo");
        if (model.has("solutionText") && model.get("solutionText") !== "") {
            model2send.set("solution_text", model.get("solutionText"));
        } else {
            model2send.set("solution_text", "");
        }
        model2send.unset("solutionText");
        model2send.unset("optionList");
        model2send.unset("answer");
        Backbone.sync(method, model2send, options);
    },

    /**
     * Returns:
     *  true if correct
     *  false if incorrect
     *  undefined if can't be corrected yet, because the deadline hasn't been
     *               reached, there is no solution data
     */
    isCorrect: function () {
        "use strict";
        var answer = this.get("answer"),
            unknown = false,
            correct = false;

        if (_.isUndefined(answer) || _.isNull(answer)) { return; }

        unknown = this.get('optionList').any(function (opt) {
            return _.isUndefined(opt.isCorrect(answer.getReply(opt.get('id'))));
        });
        if (unknown) { return; }

        return this.get('optionList').all(function (opt) {
            return opt.isCorrect(answer.getReply(opt.get('id')));
        });
    },

    isActive: function () {
        "use strict";
        var id = this.id,
            unit;

        unit = MOOC.models.course.find(function (u) {
            var knowledgeQuantumList = u.get("knowledgeQuantumList");
            if (_.isNull(knowledgeQuantumList)) { return false; }
            return knowledgeQuantumList.any(function (kq) {
                var url = kq.get("question");
                if (_.isNull(url)) { return false; }
                url = url.split('/');
                url = url[url.length - 2];
                return url === id;
            });
        });

        if (!_.isUndefined(unit) && unit.get("type") !== 'n' && this.has("solution")) {
            return false;
        }
        return true;
    }
});

/* An answer is a student submission to a question */
MOOC.models.Answer = Backbone.Model.extend({
    defaults: {
        date: null,
        replyList: null
    },

    /* Return a reply which option is opt_id or null otherwise */
    getReply: function (opt_id) {
        "use strict";
        var replies = this.get('replyList'),
            result = null;
        if (replies) {
            result = replies.find(function (reply) {
                return reply.get('option') === opt_id;
            });
        }
        return result;
    }
});

/* A reply is a student value for an option */
MOOC.models.Reply = Backbone.Model.extend({
    defaults: {
        option: null,
        value: null
    }
});

MOOC.models.ReplyList = MOOC.models.TastyPieCollection.extend({
    model: MOOC.models.Reply
});

MOOC.models.Attachment = Backbone.Model.extend({
    defaults: {
        id: -1,
        url: null
    }
});

MOOC.models.AttachmentList = MOOC.models.TastyPieCollection.extend({
    model: MOOC.models.Attachment
});

MOOC.models.PeerReviewReview  = Backbone.Model.extend({
    idAttribute: '_id',
    defaults: {
        kq: null,
        created: null,
        criteria: [],
        comment: null,
        score: 0
    },

    parse: function (resp, xhr) {
        "use strict";
        if (!_.isUndefined(resp.created)) {
            resp.created = moment(resp.created, "YYYY-MM-DDTHH:mm:ss.SSSZ");
        }
        return resp;
    }
});

MOOC.models.PeerReviewReviewList  = MOOC.models.TastyPieCollection.extend({
    model: MOOC.models.PeerReviewReview,

    url: MOOC.ajax.getAbsoluteUrl('peer_review_reviews/')
});


MOOC.models.KnowledgeQuantum = Backbone.Model.extend({
    defaults: {
        order: -1,
        title: null,
        videoID: null,
        teacher_comments: null,
        supplementary_material: null,
        question: null, // Optional
        completed: false,
        correct: null,
        weight: 0,
        normalized_weight: 0,
        peer_review_assignment: null, // Optional
        asset_availability: null,
        peer_review_score: null,

        attachmentList: null,
        questionInstance: null,
        assetAvailabilityInstance: null,
        peerReviewAssignmentInstance: null,
        _peerReviewSubmissionInstance: null,
        _assetList: null
    },

    url: function () {
        "use strict";
        return MOOC.ajax.getAbsoluteUrl("kq/") + this.get("id") + "/";
    },

    parse: function (resp, xhr) {
        "use strict";
        resp.id = parseInt(resp.id, 10);
        delete resp.resource_uri;
        delete resp.unit;
        delete resp.video;
        return resp;
    },

    sync: function (method, model, options) {
        "use strict";
        var model2send = model.clone(),
            unit = MOOC.models.course.getByKQcid(model.cid);
        model2send.set("unit", MOOC.ajax.host + "unit/" + unit.get("id") + "/");
        model2send.unset("normalized_weight");
        model2send.unset("completed");
        model2send.unset("correct");
        model2send.unset("questionInstance");
        model2send.unset("attachmentList");
        model2send.unset("peerReviewAssignmentInstance");
        if (model.get("order") < 0) {
            model2send.unset("order");
        }
        if (method === "create") {
            model2send.url = MOOC.models.detailUrlToCollection(model.url());
        }
        Backbone.sync(method, model2send, options);
    },

    truncateTitle: function (maxLength) {
        "use strict";
        return MOOC.models.truncateText(this.get('title'), maxLength);
    }
});

MOOC.models.KnowledgeQuantumList  = MOOC.models.TastyPieCollection.extend({
    model: MOOC.models.KnowledgeQuantum,

    comparator: function (kq) {
        "use strict";
        return kq.get("order");
    },

    getAdjacent: function (position, next) {
        "use strict";
        var kqs = this.toArray(),
            aux,
            result,
            i;

        for (i = 0; i < kqs.length && _.isUndefined(result); i += 1) {
            aux = kqs[i];
            if (aux.get("order") === position) {
                if (next && i < kqs.length - 1) {
                    result = kqs[i + 1];
                } else if (!next && i > 0) {
                    result = kqs[i - 1];
                }
            }
        }

        return result;
    },

    setPeerReviewAssignmentList: function (peerReviewAssignmentList) {
        "use strict";
        peerReviewAssignmentList.each(function (pra) {
            this.each(function (kq) {
                if (pra.get('kq') === kq.url()) {
                    kq.set('peerReviewAssignmentInstance', pra);
                }
            });
        }, this);
    },

    setEvaluationCriterionList: function (evaluationCriterionList) {
        "use strict";
        evaluationCriterionList.each(function (ec) {
            this.each(function (kq) {
                var pra = kq.get('peerReviewAssignmentInstance'),
                    criterionList;
                if (pra !== null) {
                    if (ec.get('assignment') === pra.url()) {
                        criterionList = pra.get('_criterionList');
                        criterionList.add(ec);
                    }
                }
            });
        }, this);
    },

    setPeerReviewSubmissionList: function (peerReviewSubmissionList) {
        "use strict";
        peerReviewSubmissionList.each(function (prs) {
            this.each(function (kq) {
                if (prs.get('kq') === kq.get("id")) {
                    kq.set("_peerReviewSubmissionInstance", prs);
                }
            });
        }, this);
    }
});

MOOC.models.Unit = Backbone.Model.extend({
    defaults: {
        order: -1,
        title: "",
        type: 'n',
        status: 'd',
        weight: 0,
        start: null,
        deadline: null,

        knowledgeQuantumList: null,
        peerReviewReviewList: null
    },

    statuses: {
        p: "published",
        l: "listable",
        d: "draft"
    },

    url: function () {
        "use strict";
        return MOOC.ajax.getAbsoluteUrl("unit/") + this.get("id") + "/";
    },

    parse: function (resp, xhr) {
        "use strict";
        var result = {},
            start = new Date(),
            deadline = new Date();

        if (!_.isNull(resp)) {
            if (resp.start) {
                start = new Date(resp.start);
            }
            if (resp.deadline) {
                deadline = new Date(resp.deadline);
            }

            result = {
                id: parseInt(resp.id, 10),
                order: resp.order,
                title: resp.title,
                type: resp.unittype,
                status: resp.status,
                weight: parseInt(resp.weight, 10),
                start: start,
                deadline: deadline
            };
        }
        return result;
    },

    sync: function (method, model, options) {
        "use strict";
        var model2send = model.clone();
        if (model.get("type") === 'n') {
            model2send.set("start", null);
            model2send.set("deadline", null);
        }
        model2send.set("unittype", model.get("type"));
        model2send.unset("type");
        model2send.unset("knowledgeQuantumList");
        if (model.get("order") < 0) {
            model2send.unset("order");
        }
        if (method === "create") {
            model2send.url = MOOC.ajax.getAbsoluteUrl("unit/");
            model2send.set("course", MOOC.ajax.host + "course/" +
                MOOC.models.course.courseId + "/");
        }
        Backbone.sync(method, model2send, options);
    },

    calculateProgress: function (conditions) {
        "use strict";
        var kqs = this.get("knowledgeQuantumList").length,
            progress = this.get("knowledgeQuantumList").where(conditions),
            result = 0;

        _.each(progress, function (kq) {
            result += kq.get("normalized_weight");
        });

        if (!_.isNumber(result) || _.isNaN(result)) {
            result = 0;
        }
        return result;
    },

    getPeerReviewReviewsForKq: function (kq) {
        "use strict";
        return this.get('peerReviewReviewList').where({kq: kq.id});
    }
});

MOOC.models.UnitList = MOOC.models.TastyPieCollection.extend({
    model: MOOC.models.Unit,
    courseId: -1,

    url: function () {
        "use strict";
        return MOOC.ajax.getAbsoluteUrl("unit/") + "?course=" + this.courseId;
    },

    getByKQ: function (kqID) {
        "use strict";
        return this.find(function (unit) {
            var kq = unit.get("knowledgeQuantumList");
            if (_.isNull(kq)) {
                return false;
            }
            kq = kq.get(kqID);
            return !_.isUndefined(kq);
        });
    },

    getByKQcid: function (cid) {
        "use strict";
        return this.find(function (unit) {
            var kqList = unit.get("knowledgeQuantumList");
            if (_.isNull(kqList)) {
                return false;
            }
            kqList = kqList.find(function (kq) {
                return kq.cid === cid;
            });
            return !_.isUndefined(kqList);
        });
    }
});

MOOC.models.course = new MOOC.models.UnitList();
