/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _, YT, async, MathJax */

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

MOOC.views = {};

MOOC.views.KQ_TITLE_MAX_LENGTH = 60;

MOOC.views.Unit = Backbone.View.extend({
    events: {
        "click li span.kq": "showKQ",
        "click li span.q": "showQ",
        "click li span.a": "showA",
        "click li span.pr": "showPR",
        "click li span.as": "showAS"
    },

    render: function () {
        "use strict";
        var html = '<div class="accordion-inner kqContainer"><ol>', css_class = null;
        this.model.get("knowledgeQuantumList").each(function (kq) {
            css_class = MOOC.models.activity.hasKQ(kq.get('id')) ? ' label-info' : '';
            html += '<li id="kq' + kq.get("id") + '"><span class="kq label' + css_class + '" title="' + kq.get("title") + '">' + kq.truncateTitle(25) + '</span>';
            if (kq.has("question")) {
                html += ' <span class="q label" title="' + MOOC.trans.classroom.qTooltip + '">' + MOOC.trans.classroom.q + '</span> ';
                html += '/ <span class="a label" title="' + MOOC.trans.classroom.aTooltip + '">' + MOOC.trans.classroom.a + '</span>';
            } else if (kq.has("peer_review_assignment")) {
                html += ' <span class="pr label" title="' + MOOC.trans.classroom.prTooltip + '">' + MOOC.trans.classroom.pr + '</span>';
            } else if (kq.has("asset_availability")) {
                html += ' <span class="as label" title="' + MOOC.trans.classroom.asTooltip + '">' + MOOC.trans.classroom.as + '</span>';
            }
            html += '</li>';
        });
        html += '</ol></div>';
        this.$el.html(html);
        return this;
    },

    showKQ: function (evt) {
        "use strict";
        var kq = $(evt.target).parent().attr("id").split("kq")[1];
        MOOC.router.navigate(this.id + "/kq" + kq, { trigger: true });
    },

    showQ: function (evt) {
        "use strict";
        var kq = $(evt.target).parent().attr("id").split("kq")[1];
        MOOC.router.navigate(this.id + "/kq" + kq + "/q", { trigger: true });
    },

    showA: function (evt) {
        "use strict";
        var kq = $(evt.target).parent().attr("id").split("kq")[1];
        MOOC.router.navigate(this.id + "/kq" + kq + "/a", { trigger: true });
    },

    showPR: function (evt) {
        "use strict";
        var kq = $(evt.target).parent().attr("id").split("kq")[1];
        MOOC.router.navigate(this.id + "/kq" + kq + "/p", { trigger: true });
    },

    showAS: function (evt) {
        "use strict";
        var kq = $(evt.target).parent().attr("id").split("kq")[1];
        MOOC.router.navigate(this.id + "/kq" + kq + "/as", { trigger: true });
    }
});

MOOC.views.unitViews = {};

MOOC.views.KnowledgeQuantum = Backbone.View.extend({
    render: function () {
        "use strict";
        var player,
            html,
            unit,
            order,
            kq,
            kqObj,
            comments,
            supplementary;

        html = '<iframe id="ytplayer" width="620px" height="372px" ';
        html += 'src="//www.youtube.com/embed/' + this.model.get("videoID");
        html += '?rel=0&origin=' + MOOC.host;
        html += '" frameborder="0" allowfullscreen></iframe>';
        $("#kq-video").removeClass("question").html(html);

        $("#kq-q-buttons").addClass("hide");
        $("#kq-next-container").addClass("offset4");

        if (this.model.has("question")) {
            this.loadQuestionData();
        } else if (this.model.has("peer_review_assignment")) {
            this.loadPeerReviewData();
        }
        this.repeatedlyCheckIfPlayer();

        $("#kq-title").html(this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH));

        unit = MOOC.models.course.getByKQ(this.model.get("id"));
        this.setEventForNavigation("#kq-previous", unit, this.model, false);
        this.setEventForNavigation("#kq-next", unit, this.model, true);

        this.$el.parent().children().removeClass("active");
        this.$el.addClass("active");

        comments = this.model.get("teacher_comments") || '';
        $("#comments").html(comments);

        supplementary = this.model.get("supplementary_material") || '';
        supplementary += "<ul id='attachments'></ul>";
        $("#supplementary").html(supplementary);

        this.setupListernerFor(this.model, "attachmentList", _.bind(function () {
            this.model.get("attachmentList").each(function (attachment) {
                var view = new MOOC.views.Attachment({
                    model: attachment,
                    el: $("#supplementary").find("ul#attachments")[0]
                });
                view.render();
            });
        }, this));

        if (_.isObject(window.MathJax)) {
            _.each($('.mathjax'), function (item) {
                MathJax.Hub.Queue(["Typeset", MathJax.Hub, item]);
            });
        }

        return this;
    },

    setEventForNavigation: function (selector, unit, kq, next) {
        "use strict";
        var path = window.location.hash,
            order = kq.get("order"),
            getUrlForOtherKQ,
            target,
            url;

        getUrlForOtherKQ = function (position, next) {
            var aux = unit.get("knowledgeQuantumList").getAdjacent(position, next),
                url;
            if (_.isUndefined(aux)) {
                $(selector).addClass("disabled");
            } else {
                url = "unit" + unit.get("id") + "/kq" + aux.get("id");
                if (!next && aux.has("question")) {
                    url += "/a";
                } else if (!next && aux.has("peer_review_assignment")) {
                    url += "/p";
                }
                return url;
            }
        };

        $(selector).unbind("click");

        if (/#[\w\/]+\/q/.test(path)) { // Viewing question
            target = next ? "answer" : "same";
        } else if (/#[\w\/]+\/a/.test(path)) { // Viewing answer
            target = next ? "next" : "exercise";
        } else if (/#[\w\/]+\/p/.test(path)) { // Viewing peer review
            target = next ? "next" : "same";
        } else { // Viewing kq
            target = next ? "exercise" : "prev";
        }
        if (target === "exercise" && !kq.has("question") && !kq.has("peer_review_assignment")) {
            target = "next";
        }

        switch (target) {
        case "exercise":
            url = "unit" + unit.get("id") + "/kq" + kq.get("id");
            if (kq.has("question")) {
                url += "/q";
            } else { // peer review
                url += "/p";
            }
            break;
        case "answer":
            url = "unit" + unit.get("id") + "/kq" + kq.get("id") + "/a";
            break;
        case "next":
            url = getUrlForOtherKQ(order, true);
            break;
        case "prev":
            url = getUrlForOtherKQ(order, false);
            break;
        case "same":
            url = "unit" + unit.get("id") + "/kq" + kq.get("id");
            break;
        }

        if (_.isUndefined(url)) {
            $(selector).addClass("disabled");
        } else {
            $(selector).removeClass("disabled");
            $(selector).click(function (evt) {
                MOOC.router.navigate(url, { trigger: true });
            });
        }
    },

    player: null,

    // The callback is only used in the router, not in the views
    repeatedlyCheckIfPlayer: function (callback) {
        "use strict";
        if (MOOC.YTready) {
            this.player = YT.get("ytplayer");
            // A new player instance for a new video
            if (!_.isUndefined(this.player) && !_.isNull(this.player)) {
                this.player.destroy();
            }
            this.player = new YT.Player("ytplayer", {
                events: {
                    onStateChange: _.bind(this.loadExercise, this)
                }
            });
            if (!_.isUndefined(callback)) { callback(); }
        } else {
            _.delay(_.bind(this.repeatedlyCheckIfPlayer, this), 200, callback);
        }
    },

    setupListernerFor: function (model, property, callback) {
        "use strict";
        if (model.has(property)) {
            callback();
        } else {
            model.on("change", function (evt) {
                if (this.has(property)) {
                    this.off("change");
                    callback();
                }
            }, model);
        }
    },

    loadQuestionData: function () {
        "use strict";
        var kqObj = this.model;
        if (!kqObj.has("questionInstance")) {
            // Load Question Data
            MOOC.ajax.getResource(kqObj.get("question"), function (data, textStatus, jqXHR) {
                var question = new MOOC.models.Question({
                        id: data.id,
                        lastFrame: data.last_frame,
                        solutionVideo: data.solutionID,
                        use_last_frame: data.use_last_frame
                    });
                if (data.solution_text !== "") {
                    question.set("solutionText", data.solution_text);
                }
                kqObj.set("questionInstance", question);
                // Load Options for Question
                MOOC.ajax.getOptionsByQuestion(question.get("id"), function (data, textStatus, jqXHR) {
                    var options = _.map(data.objects, function (opt) {
                        return new MOOC.models.Option(_.pick(opt, "id", "optiontype", "x", "y", "width", "height", "solution", "text", "feedback"));
                    });
                    question.set("optionList", new MOOC.models.OptionList(options));
                });
                // Load Answer for Question
                MOOC.ajax.getAnswerByQuestion(question.get("id"), function (data, textStatus, jqXHR) {
                    var obj, replies, answer;
                    if (data.objects.length === 1) {
                        obj = data.objects[0];
                        replies = _.map(obj.replyList, function (reply) {
                            return new MOOC.models.Reply(_.pick(reply, "option", "value"));
                        });
                        answer = new MOOC.models.Answer({
                            id: question.get('id'),
                            date: obj.date,
                            replyList: new MOOC.models.ReplyList(replies)
                        });
                    } else {
                        answer = new MOOC.models.Answer({
                            date: null,
                            replyList: new MOOC.models.ReplyList([])
                        });
                    }
                    question.set("answer", answer);
                });
            });
        }
    },

    loadPeerReviewData: function () {
        "use strict";
        var kqObj = this.model;
        if (!kqObj.has("peerReviewAssignmentInstance")) {
            MOOC.ajax.getResource(kqObj.get("peer_review_assignment"), function (data, textStatus, jqXHR) {
                var ajaxCounter = 0,
                    peerReviewObj = new MOOC.models.PeerReviewAssignment({
                        id: data.id,
                        description: data.description,
                        minimum_reviewers: data.minimum_reviewers
                    }),
                    callback;

                callback = function () {
                    if (ajaxCounter === 2) {
                        // Don't set the peerReviewAssignmentInstance until the
                        // evaluation criteria is loaded and the submitted flag
                        // set
                        kqObj.set("peerReviewAssignmentInstance", peerReviewObj);
                    }
                };

                peerReviewObj.set("_knowledgeQuantumInstance", kqObj);
                MOOC.ajax.getPRSubmission(kqObj.get("id"), function (data, textStatus, jqXHR) {
                    if (data.objects.length > 0) {
                        peerReviewObj.set("_submitted", true);
                    }
                    ajaxCounter += 1;
                    callback();
                });
                // Load Evalutation Criteria
                peerReviewObj.get("_criterionList").fetch({
                    data: { 'assignment': peerReviewObj.get("id") },
                    success: function (collection, resp, options) {
                        ajaxCounter += 1;
                        callback();
                    }
                });
            });
        }
    },

    loadAssetsData: function () {
        "use strict";
        var kqObj,
            assetList;

        kqObj = this.model;

        if (!kqObj.has("assetAvailabilityInstance")) {
            if (!kqObj.has("_assetList")) {
                assetList = new MOOC.models.AssetList();
                assetList.fetch({
                    data: { 'kq': kqObj.get("id") },
                    success: function (collection, resp, options) {
                        kqObj.set("_assetList", assetList);
                    }
                });
            }
            MOOC.ajax.getResource(kqObj.get("asset_availability"), function (data, textStatus, jqXHR) {
                var assetAvailabilityObj;

                assetAvailabilityObj = new MOOC.models.AssetAvailability({
                    id: data.id,
                    kq: data.kq,
                    available_from: data.available_from,
                    available_to: data.available_to
                });

                kqObj.set('assetAvailabilityInstance', assetAvailabilityObj);
            });
        }
    },

    loadExercise: function (evt) {
        "use strict";
        if (evt.data === YT.PlayerState.ENDED) {
            var model = this.model,
                toExecute = [];

            // Mark kq as "viewed"
            MOOC.models.activity.addKQ(String(model.get("id")), function () {
                var unit = MOOC.models.course.getByKQ(model),
                    view = MOOC.views.unitViews[unit.get("id")];

                view.render();
            });

            // We can't assume the question exists
            if (model.has("question")) {
                if (!this.model.has("questionInstance")) {
                    toExecute.push(async.apply(this.setupListernerFor, this.model, "questionInstance"));
                }

                toExecute.push(_.bind(function (callback) {
                    var question = this.model.get("questionInstance");
                    this.setupListernerFor(question, "optionList", callback);
                }, this));

                toExecute.push(_.bind(function (callback) {
                    var question = this.model.get("questionInstance");
                    this.setupListernerFor(question, "answer", callback);
                }, this));

                toExecute.push(_.bind(function (callback) {
                    var question = this.model.get("questionInstance"),
                        view = MOOC.views.questionViews[question.get("id")],
                        data = {
                            kq: this.model.get("id")
                        },
                        path = window.location.hash.substring(1),
                        unit = MOOC.models.course.getByKQ(this.model);

                    $("#kq-title").html(this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH));
                    if (!(/[\w\/]+\/q/.test(path))) {
                        path = path + "/q";
                        MOOC.router.navigate(path, { trigger: false });
                    }
                    this.setEventForNavigation("#kq-previous", unit, this.model, false);
                    this.setEventForNavigation("#kq-next", unit, this.model, true);

                    if (this.player && !_.isNull(this.player.getIframe())) {
                        this.player.destroy();
                    }
                    $("#kq-video").empty();
                    this.player = null;

                    if (_.isUndefined(view)) {
                        view = new MOOC.views.Question({
                            model: question,
                            el: $("#kq-video")[0]
                        });
                        MOOC.views.questionViews[question.get("id")] = view;
                    }
                    view.render();

                    callback();
                }, this));
            } else if (model.has("peer_review_assignment")) {
                toExecute = [];

                if (!this.model.has("peerReviewAssignmentInstance")) {
                    toExecute.push(async.apply(this.setupListernerFor, this.model, "peerReviewAssignmentInstance"));
                }

                toExecute.push(_.bind(function (callback) {
                    var peerReviewObj = this.model.get("peerReviewAssignmentInstance"),
                        view = MOOC.views.peerReviewAssignmentViews[peerReviewObj.get("id")],
                        path = window.location.hash.substring(1),
                        unit = MOOC.models.course.getByKQ(this.model);

                    $("#kq-title").html(this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH));
                    if (!(/[\w\/]+\/p/.test(path))) {
                        path = path + "/p";
                        MOOC.router.navigate(path, { trigger: false });
                    }

                    this.setEventForNavigation("#kq-previous", unit, this.model, false);
                    this.setEventForNavigation("#kq-next", unit, this.model, true);

                    if (this.player && !_.isNull(this.player.getIframe())) {
                        this.player.destroy();
                    }
                    $("#kq-video").empty();
                    this.player = null;

                    if (_.isUndefined(view)) {
                        view = new MOOC.views.PeerReviewAssignment({
                            model: peerReviewObj,
                            el: $("#kq-video")[0]
                        });
                        MOOC.views.peerReviewAssignmentViews[peerReviewObj.get("id")] = view;
                    }
                    view.render();

                    callback();
                }, this));

            }

            async.series(toExecute);
        }

        return this;
    },

    loadAssets: function () {
        "use strict";
        var toExecute = [];

        if (!this.model.has("assetAvailabilityInstance")) {
            toExecute.push(async.apply(this.setupListernerFor, this.model, "assetAvailabilityInstance"));
        }

        if (!this.model.has("_assetList")) {
            toExecute.push(async.apply(this.setupListernerFor, this.model, "_assetList"));
        }

        toExecute.push(_.bind(function (callback) {
            var unit = MOOC.models.course.getByKQ(this.model),
                assetAvailability = this.model.get("assetAvailabilityInstance"),
                html;

            html = "<div class='solution-wrapper white'>";
            html += "<h2>" + MOOC.trans.classroom.asDates + "</h2><ul>";
            html += "<li>" + MOOC.trans.classroom.asDatesFrom + assetAvailability.get("available_from") + "</li>";
            html += "<li>" + MOOC.trans.classroom.asDatesTo + assetAvailability.get("available_to") + "</li></ul>";

            html += "<h2>" + MOOC.trans.classroom.asAssetList + "</h2><ul>";
            this.model.get("_assetList").each(function (asset) {
                html += "<li>" + asset.get('name') + "</li>";
            });
            html += "</ul>";


            $("#kq-video").html(html);
            $("#kq-q-showkq").addClass("hide");
            $("#kq-q-submit").addClass("hide");
            $("#kq-title").html(this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH));

            this.setEventForNavigation("#kq-previous", unit, this.model, false);
            this.setEventForNavigation("#kq-next", unit, this.model, true);

            callback();
        }, this));

        async.series(toExecute);

        return this;
    },

    loadSolution: function () {
        "use strict";
        var toExecute = [];

        if (!this.model.has("questionInstance")) {
            toExecute.push(async.apply(this.setupListernerFor, this.model, "questionInstance"));
        }

        toExecute.push(_.bind(function (callback) {
            var unit = MOOC.models.course.getByKQ(this.model),
                questionInstance = this.model.get("questionInstance"),
                html = "";

            if (questionInstance.has("solutionText")) {
                html = "<div class='solution-wrapper white mathjax'>" + questionInstance.get("solutionText") + "</div>";
            } else if (questionInstance.has("solutionVideo")) {
                html = '<iframe id="ytplayer" width="620px" height="372px" ';
                html += 'src="//www.youtube.com/embed/' + this.model.get("questionInstance").get("solutionVideo");
                html += '?rel=0&origin=' + MOOC.host + '" frameborder="0" allowfullscreen></iframe>';
            } else {
                MOOC.alerts.show(MOOC.alerts.INFO, MOOC.trans.api.solutionNotReadyTitle, MOOC.trans.api.solutionNotReady);
            }

            $("#kq-video").removeClass("question").html(html);
            $("#kq-q-buttons").addClass("hide");
            $("#kq-next-container").addClass("offset4");
            $("#kq-title").html(this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH));

            this.setEventForNavigation("#kq-previous", unit, this.model, false);
            this.setEventForNavigation("#kq-next", unit, this.model, true);

            callback();
        }, this));

        if (_.isObject(window.MathJax)) {
            toExecute.push(function (callback) {
                _.each($('.mathjax'), function (item) {
                    MathJax.Hub.Queue(["Typeset", MathJax.Hub, item]);
                });
            });
        }

        async.series(toExecute);

        return this;
    }
});

MOOC.views.kqViews = {};

MOOC.views.AssetAvailability = Backbone.View.extend({
    render: function () {
        "use strict";
        var kqPath = window.location.hash.substring(1, window.location.hash.length - 2), // Remove trailing /q
            answer = this.model.get('answer'),
            html;

        if (this.model.get("use_last_frame")) {
            html = '<img src="' + this.model.get("lastFrame") + '" ' +
                'alt="' + this.model.get("title") +
                '" style="width: 620px; height: 372px;" />';
        } else {
            html = "<div class='white' style='width: 620px; height: 372px;'></div>";
        }
        this.$el.html(html);
        this.$el.addClass("question");

        $("#kq-q-buttons").removeClass("hide");
        if (this.model.isActive()) {
            $("#kq-q-submit").attr("disabled", false);
        } else {
            $("#kq-q-submit").attr("disabled", "disabled");
        }
        $("#kq-q-showkq").off('click').on('click', function () {
            MOOC.router.navigate(kqPath, { trigger: true });
        });
        $("#kq-q-submit").off('click').on('click', _.bind(function () {
            this.submitAnswer();
        }, this));
        $("#kq-next-container").removeClass("offset4");

        this.model.get("optionList").each(function (opt) {
            var view = MOOC.views.optionViews[opt.get("id")], reply = null;
            if (_.isUndefined(view)) {
                reply = answer.getReply(opt.get('id'));
                view = new MOOC.views.Option({
                    model: opt,
                    reply: reply,
                    el: $("#kq-video")[0]
                });
                MOOC.views.optionViews[opt.get("id")] = view;
            }
            view.render();
        });

        return this;
    }
});

MOOC.views.Question = Backbone.View.extend({
    render: function () {
        "use strict";
        var kqPath = window.location.hash.substring(1, window.location.hash.length - 2), // Remove trailing /q
            answer = this.model.get('answer'),
            html;

        if (this.model.get("use_last_frame")) {
            html = '<img src="' + this.model.get("lastFrame") + '" ' +
                'alt="' + this.model.get("title") +
                '" style="width: 620px; height: 372px;" />';
        } else {
            html = "<div class='white' style='width: 620px; height: 372px;'></div>";
        }
        this.$el.html(html);
        this.$el.addClass("question");

        $("#kq-q-buttons").removeClass("hide");
        if (this.model.isActive()) {
            $("#kq-q-submit").attr("disabled", false);
        } else {
            $("#kq-q-submit").attr("disabled", "disabled");
        }
        $("#kq-q-showkq").off('click').on('click', function () {
            MOOC.router.navigate(kqPath, { trigger: true });
        });
        $("#kq-q-submit").off('click').on('click', _.bind(function () {
            this.submitAnswer();
        }, this));
        $("#kq-next-container").removeClass("offset4");

        this.model.get("optionList").each(function (opt) {
            var view = MOOC.views.optionViews[opt.get("id")], reply = null;
            if (_.isUndefined(view)) {
                reply = answer.getReply(opt.get('id'));
                view = new MOOC.views.Option({
                    model: opt,
                    reply: reply,
                    el: $("#kq-video")[0]
                });
                MOOC.views.optionViews[opt.get("id")] = view;
            }
            view.render();
        });

        return this;
    },

    submitAnswer: function () {
        "use strict";
        var self = this,
            answer = this.model.get('answer'),
            replies,
            fetch_solutions;

        replies = this.model.get("optionList").map(function (opt) {
            var view = MOOC.views.optionViews[opt.get("id")],
                input = view.$el.find("input#option" + opt.get("id")),
                type = input.attr("type"),
                value;

            if (type === "text") {
                value = input.val();
            } else {
                value = !_.isUndefined(input.attr("checked"));
            }

            return new MOOC.models.Reply({
                option: view.model.get("id"),
                value: value
            });
        });
        if (replies.length > 0) {
            answer.set('replyList', new MOOC.models.ReplyList(replies));
            answer.set('date', new Date());

            fetch_solutions = self.model.get("optionList").any(function (option) {
                return _.isNull(option.get("solution"));
            });

            MOOC.ajax.sendAnswer(answer, this.model.get('id'), function (data, textStatus, jqXHR) {
                if (jqXHR.status === 201 || jqXHR.status === 204) {
                    answer.set('id', self.model.get('id'));
                    self.model.set('answer', answer);

                    self.loadSolution(fetch_solutions);
                }
            });
        }
    },

    loadSolution: function (fetch_solutions) {
        "use strict";
        // Set the solution for each option.
        // As there is an answer already, the options will have the solution included
        var self = this, answer = this.model.get('answer'),
            load_reply = function (oid, solution, feedback) {
                var view = MOOC.views.optionViews[oid],
                    reply = answer.getReply(oid),
                    model = self.model.get('optionList').get(oid);
                view.setReply(reply);
                model.set('solution', solution);
                model.set("feedback", feedback);
                view.render();
            },
            show_result_msg = function () {
                var correct = self.model.isCorrect();
                if (_.isUndefined(correct)) {
                    MOOC.alerts.show(MOOC.alerts.INFO,
                                     MOOC.trans.classroom.answersSent,
                                     MOOC.trans.classroom.answersUnknown);
                } else if (correct) {
                    MOOC.alerts.show(MOOC.alerts.SUCCESS,
                                     MOOC.trans.classroom.answersSent,
                                     MOOC.trans.classroom.answersCorrect);
                } else {
                    MOOC.alerts.show(MOOC.alerts.ERROR,
                                     MOOC.trans.classroom.answersSent,
                                     MOOC.trans.classroom.answersIncorrect);
                }
            };


        if (fetch_solutions) {
            MOOC.ajax.getOptionsByQuestion(this.model.get("id"), function (data, textStatus, jqXHR) {
                _.each(data.objects, function (opt) {
                    load_reply(opt.id, opt.solution, opt.feedback);
                });
                show_result_msg();
            });
        } else {
            this.model.get('optionList').each(function (opt_obj) {
                load_reply(opt_obj.get('id'), opt_obj.get('solution'), opt_obj.get("feedback"));
                show_result_msg();
            });
        }
    }
});

MOOC.views.questionViews = {};

MOOC.views.Option = Backbone.View.extend({
    MIN_TEXT_HEIGHT: 14,

    types: {
        l: "textarea",
        t: "text",
        c: "checkbox",
        r: "radio"
    },

    initialize: function () {
        "use strict";
        this.reply = this.options.reply;
    },

    setReply: function (reply) {
        "use strict";
        this.reply = reply;
    },

    render: function () {
        "use strict";
        var image = this.$el.find("img"),
            optiontype = this.model.get('optiontype'),
            solution = this.model.get('solution'),
            width = "auto;",
            height = "auto;",
            tag = "input",
            content = "",
            attributes = {
                type: this.types[optiontype],
                id: 'option' + this.model.get('id')
            },
            // The scale is required because the question editor is smaller
            // than the classroom question
            scale = 1.1481481, // 620/540 or 372/324
            left = Math.floor(this.model.get('x') * scale),
            top = Math.floor(this.model.get('y') * scale),
            feedbackBtn,
            correct;

        if (optiontype === 't') {
            width = Math.floor(this.model.get('width') * scale) + 'px;';
            height = Math.floor(this.model.get('height') * scale);
            if (height < this.MIN_TEXT_HEIGHT) {
                height = this.MIN_TEXT_HEIGHT;
            }
            height = height + 'px;';
        }

        attributes.style = [
            'top: ' + top + 'px;',
            'left: ' + left + 'px;'
        ];
        if (optiontype === 'l') {
            attributes.cols = this.model.get("width");
            attributes.rows = this.model.get("height");
            attributes.disabled = "disabled";
            attributes["class"] = "text";
            tag = attributes.type;
            delete attributes.type;
            content = this.model.get("text");
            attributes.style.push('resize: none;');
            attributes.style.push('cursor: default;');
        } else {
            attributes.style.push('width: ' + width + 'px;');
            attributes.style.push('height: ' + height + 'px;');
        }
        attributes.style = attributes.style.join(' ');
        if (optiontype === 'r') {
            attributes.name = 'radio';
        }

        this.$el.find("#" + attributes.id).remove();
        this.$el.find("#" + attributes.id + "-fb").remove();

        if (this.reply && this.reply.get('option') === this.model.get('id') && optiontype !== 'l') {
            correct = false;
            if (optiontype === 't') {
                attributes.value = this.reply.get('value');
                if (!(_.isUndefined(solution) || _.isNull(solution))) {
                    correct = this.model.isCorrect(this.reply);
                    attributes['class'] = correct ? 'correct' : 'incorrect';
                }
            } else {
                if (this.reply.get('value')) {
                    attributes.checked = 'checked';
                }
                if (!(_.isUndefined(solution) || _.isNull(solution))) {
                    correct = this.model.isCorrect(this.reply);
                    attributes['class'] = correct ? 'correct' : 'incorrect';
                }
            }

            if (!correct && this.model.has("feedback") && this.model.get("feedback") !== "") {
                feedbackBtn = $("<button class='btn btn-warning' id='" + attributes.id + "-fb'><i class='icon-info-sign'></i></button>");
                feedbackBtn.css("top", (top - 4) + "px");
                feedbackBtn.css("left", (left - 32) + "px");
                feedbackBtn.popover({
                    trigger: "click",
                    placement: "top",
                    content: this.model.get("feedback")
                });
                this.$el.append(feedbackBtn);
            }
        }

        this.$el.append(this.make(tag, attributes, content));

        return this;
    }
});

MOOC.views.optionViews = {};

MOOC.views.Attachment = Backbone.View.extend({
    render: function () {
        "use strict";
        var html = "<li><a href='" + this.model.get("url") + "' target='_blank'>",
            parts = this.model.get("url").split('/');
        html += parts[parts.length - 1];
        html += "</a></li>";
        this.$el.append(html);
        return this;
    }
});

MOOC.views.PeerReviewAssignment = Backbone.View.extend({
    events: {
        "click button#pr-view-criteria": "viewCriteria"
    },

    initialize: function () {
        "use strict";
        _.bindAll(this, "render", "getTemplate", "getCriteriaModal",
            "viewCriteria", "submit", "confirmedSubmit", "supportFileAPI",
            "uploadFile");
    },

    template: undefined,
    modal: undefined,
    confirmModal: undefined,

    getTemplate: function () {
        "use strict";
        if (_.isUndefined(this.template)) {
            this.template = $("#peer-review-tpl").text();
            if (this.template === "") {
                // HACK for IE8
                this.template = $("#peer-review-tpl").html();
            }
        }
        return this.template;
    },

    getCriteriaModal: function () {
        "use strict";
        if (_.isUndefined(this.modal)) {
            this.modal = $("#evaluation-criteria");
            this.modal.modal({ show: false });
        }
        return this.modal;
    },

    getConfirmModal: function () {
        "use strict";
        if (_.isUndefined(this.confirmModal)) {
            this.confirmModal = $("#confirm-peer-review");
            this.confirmModal.modal({
                show: false,
                backdrop: "static",
                keyboard: false
            });
        }
        return this.confirmModal;
    },

    render: function (justSent) {
        "use strict";
        var kqPath,
            html,
            unit;

        if (this.model.get("_submitted")) {
            // Message telling the student he has already sent the exercise
            $("#kq-q-buttons").addClass("hide");
            $("#kq-next-container").addClass("offset4");

            html = ["<div class='alert alert-block"];
            if (justSent) {
                html.push(" alert-success'>");
                html.push("<h4>" + MOOC.trans.classroom.prSent + "</h4>");
                html.push("<p>" + MOOC.trans.classroom.prJust.replace("#(minimum_reviewers)s", this.model.get("minimum_reviewers")) + "</p>");
                html.push("</div>");
                html.push("<p><strong><a href='" + MOOC.peerReview.urls.prReview + "#kq" + this.model.get("_knowledgeQuantumInstance").get("id") + "'>" + MOOC.trans.classroom.prReview + "</a></strong></p>");
            } else {
                unit = MOOC.models.course.getByKQ(this.model.get("_knowledgeQuantumInstance"));
                html.push(" alert-info'>");
                html.push("<h4>" + MOOC.trans.classroom.prSent + "</h4>");
                html.push("<p>" + MOOC.trans.classroom.prAlready + "</p>");
                html.push("</div>");
                html.push("<p><strong><a href='" + MOOC.peerReview.urls.prReview + "#kq" + this.model.get("_knowledgeQuantumInstance").get("id") + "'>" + MOOC.trans.classroom.prReview + "</a></strong></p>");
                html.push("<p><a href='" + MOOC.peerReview.urls.prProgress + "#unit" + unit.get("id") + "'>" + MOOC.trans.classroom.prProgress + "</a></p>");
            }

            this.$el.removeClass("question").html(html.join(""));
        } else {
            // Show the peer review submission form
            kqPath = window.location.hash.substring(1, window.location.hash.length - 2); // Remove trailing /p

            this.$el.removeClass("question").html(this.getTemplate());
            this.$el.find("#pr-description").html(this.model.get("description"));
            this.$el.find("#pr-submission").off("input propertychange").on("input propertychange", function () {
                var $input = $(this),
                    maxLength = $input.attr('maxlength');
                if ($input.val().length > maxLength) {
                    $input.val($input.val().substring(0, maxLength));
                }
            });

            $("#kq-q-buttons").removeClass("hide");
            $("#kq-q-submit").attr("disabled", false);
            $("#kq-q-showkq").off('click').on('click', function () {
                MOOC.router.navigate(kqPath, { trigger: true });
            });
            $("#kq-q-submit").off('click').on('click', this.submit);
            $("#kq-next-container").removeClass("offset4");
        }

        if (_.isObject(window.MathJax)) {
            _.each(this.$el.find('.mathjax'), function (item) {
                MathJax.Hub.Queue(["Typeset", MathJax.Hub, item]);
            });
        }

        return this;
    },

    viewCriteria: function (evt) {
        "use strict";
        evt.preventDefault();
        evt.stopPropagation();
        var criteria = this.model.get("_criterionList"),
            body = "",
            $modal;
        if (criteria.length === 0) { return; }
        $modal = this.getCriteriaModal();
        criteria.each(function (criterion) {
            body += "<h4>" + criterion.get("title") + "</h4><p>" + criterion.get("description") + "</p>";
        });
        $modal.find(".modal-body").html(body);
        if (_.isObject(window.MathJax)) {
            _.each($modal.find('.mathjax'), function (item) {
                MathJax.Hub.Queue(["Typeset", MathJax.Hub, item]);
            });
        }
        $modal.modal('show');
    },

    submit: function (evt) {
        "use strict";
        evt.preventDefault();
        evt.stopPropagation();
        var modal = this.getConfirmModal();
        modal.find("#pr-confirm").off("click").on("click", _.bind(function () {
            this.confirmedSubmit();
            modal.modal("hide");
        }, this));
        modal.modal("show");
    },

    confirmedSubmit: function () {
        "use strict";
        MOOC.ajax.showLoading();

        var file = this.$el.find("form input[type=file]")[0],
            text = $.trim(this.$el.find("#pr-submission").val()),
            form = $(this.$el.find("form")[0]),
            callback;

        if (!this.supportFileAPI(file)) {
            form.append($('<input type="hidden" name="kq_id" value="' + this.model.get("_knowledgeQuantumInstance").get("id") + '" />'));
            form.submit();
        }

        if (text === "" && file.files.length === 0) {
            MOOC.alerts.show(MOOC.alerts.ERROR, MOOC.trans.classroom.prRequired, MOOC.trans.classroom.prRequiredMsg);
            MOOC.ajax.hideLoading();
            return;
        }

        callback = _.bind(function (file) {
            var kq = this.model.get("_knowledgeQuantumInstance").get("id"),
                unitObj = MOOC.models.course.getByKQ(kq),
                submission = {
                    kq: kq,
                    unit: unitObj.get("id"),
                    course: unitObj.courseId
                };

            if (text !== "") {
                submission.text = text;
            }
            if (!_.isUndefined(file)) {
                submission.file = file;
            }

            MOOC.ajax.hideLoading();
            MOOC.ajax.sendPRSubmission(submission, _.bind(function () {
                this.model.set("_submitted", true);
                this.render(true);
            }, this));
        }, this);

        if ($(file).val().length > 0) {
            this.uploadFile(file, callback);
        } else {
            callback();
        }
    },

    supportFileAPI: function (fileInput) {
        "use strict";
        var support = true;

        if (fileInput.files === undefined) {
            support = false;
        }

        return support;
    },

    uploadFile: function (fileInput, callback) {
        "use strict";
        var that = this,
            file = null;

        if (fileInput.files.length > 0) {
            file = fileInput.files[0];
            if (file.size / (1024 * 1024) <= MOOC.peerReview.settings.file_max_size) {
                that.executeOnSignedUrl(file, function (signedURL) {
                    that.uploadToS3(file, signedURL, callback);
                });
            } else {
                MOOC.ajax.hideLoading();
                MOOC.alerts.show(MOOC.alerts.ERROR,
                                 MOOC.trans.peerreview.prFileMaxSize,
                                 MOOC.trans.peerreview.prFileMaxSizeMsg);
            }
        }
    },

    uploadToS3: function (file, url, callback) {
        "use strict";
        var that = this;

        $.ajax({
            url: url,
            type: "PUT",
            data: file,
            processData: false,
            crossDomain: true,
            xhr: function () {
                var myXhr = $.ajaxSettings.xhr();
                if (myXhr.upload) {
                    myXhr.upload.addEventListener('progress', function (event) {
                        if (event.lengthComputable) {
                            var percentLoaded = Math.round((event.loaded / event.total) * 100);
                            that.setProgress(percentLoaded, percentLoaded === 100 ? 'Finalizing.' : 'Uploading.');
                        }
                    }, false);
                }
                return myXhr;
            },
            headers: { 'Content-Type': file.type, 'x-amz-acl': 'public-read' },
            success: function (data) {
                that.setProgress(100, 'Upload completed.');
                $.ajax({
                    url: '/s3_download_url/?name=' + file.name + '&kq=' + that.model.get("_knowledgeQuantumInstance").get("id"),
                    success: function (data) {
                        callback(decodeURIComponent(data));
                    }
                });
            },
            error: function () {
                MOOC.ajax.hideLoading();
                that.setProgress(0, 'Upload error.');
            }
        });
    },

    executeOnSignedUrl: function (file, callback) {
        "use strict";
        var that = this;

        $.ajax({
            url: '/s3_upload_url/?name=' + file.name + '&type=' + file.type + '&kq=' + that.model.get("_knowledgeQuantumInstance").get("id"),
            crossDomain: true,
            success: function (data) {
                callback(decodeURIComponent(data));
            }
        });
    },

    setProgress: function (percent, statusLabel) {
        "use strict";
        // TODO: Update the progress bar
    }
});

MOOC.views.peerReviewAssignmentViews = {};
