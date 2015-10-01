/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _, YT, async, MathJax */

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
if (_.isUndefined(MOOC.views)) {
    MOOC.views = {};
}

MOOC.views.KQ_TITLE_MAX_LENGTH = 60;

MOOC.views.Unit = Backbone.View.extend({
    events: {
        "click li span.kq": "showKQ",
        "click li span.q": "showQ",
        "click li span.a": "showA",
        "click li span.pr": "showPR",
        "click li span.as": "showAS",
		"click #kq-q-showq": "showPR",
    },

    initialize: function() {
        var self = this;
        $('#course-share').off('click').on('click', self.shareKQ);
        $('.social_share_btn').off('click').on('click', function(e){
          sendHistoryEntry(MOOC.models.course.courseId, {delay: 0, url: e.delegateTarget.href});
        });
    },

	/* RENDER INDEX */
    render: function () {
        "use strict";
        var html = '<div class="accordion-inner kqContainer"><ol>', css_class = null;
		var that = this;
        this.model.get("knowledgeQuantumList").each(function (kq) {
            css_class = MOOC.models.activity.hasKQ(kq.get('id')) ? ' done' : '';
			css_class += kq.get('id') == that.model.get("id") ? ' current': '';
            html += '<li id="kq' + kq.get("id") + '" class="' + css_class + '"><span class="kq label" title="' + kq.get("title") + '">' + kq.truncateTitle(25) + '</span>';
            if (kq.has("question")) {
                html += ' <span class="q label" title="' + MOOC.trans.classroom.qTooltip + '">' + MOOC.trans.classroom.q + '</span> ';
                html += ' <span class="a label" title="' + MOOC.trans.classroom.aTooltip + '">' + MOOC.trans.classroom.a + '</span>';
            } else if (kq.has("peer_review_assignment")) {
                html += ' <span class="pr label" title="' + MOOC.trans.classroom.prTooltip + '">' + MOOC.trans.classroom.pr + '</span>';
            } else if (kq.has("asset_availability")) {
                html += ' <span class="as label" title="' + MOOC.trans.classroom.asTooltip + '">' + MOOC.trans.classroom.as + '</span>';
            }
            var content_type = kq.get("media_content_type");
            if (content_type == "youtube" || content_type == "vimeo"){
				html += ' <span class="video label" title="' + MOOC.trans.classroom.videoTooltip + '">' + MOOC.trans.classroom.video + '</span>';
            } else if (content_type == "ytaccesible") {
                html += ' <span class="video label" title="' + MOOC.trans.classroom.videoTooltip + '">' + MOOC.trans.classroom.video + '</span>';
            } else if (content_type == "prezi" || content_type == "scribd") {
				html += ' <span class="presentation label" title="' + MOOC.trans.classroom.presentationTooltip + '">' + MOOC.trans.classroom.presentation + '</span>';
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
    },

    shareKQ: function (evt) {
        "use strict";
        evt.preventDefault();
        var hashtag = $('#hashtag').html();
        var url = window.location.href;
        if(hashtag && url){
            console.log(hashtag);
            console.log(url);
            var $microblog = $('#microblog-share');
            var $textarea = $microblog.find('.editor textarea');
            $textarea.val(' ' + hashtag + ' ' + url);
            $textarea[0].setSelectionRange(0,0);
            $microblog.addClass('open');
            $textarea.focus();
        }
    }
});

MOOC.views.unitViews = {};

MOOC.views.lastPlayerView = null;

MOOC.views.KnowledgeQuantum = Backbone.View.extend({
    render: function () {
        "use strict";
        var callback;

        callback = _.bind(function () {
            var html,
                unit,
                iframe_template;

            iframe_template = _.template(this.model.get('iframe_code'));
            html = iframe_template({
                height: 'auto',
                width: '100%',
                allowfullscreen: true,
                controls: true,
                origin: MOOC.host
            });
            $("#kq-video").empty().removeClass('question').html(html).find("iframe");

            _.each(MOOC.views.players, function (Player) {
                if (Player.test("#kq-video")) {
                    MOOC.views.lastPlayerView = new Player({
                        kq: this.model.get("id"),
                        transcripts: this.model.get("transcriptionList")
                    });
                }
            }, this);

            //$("#kq-q-buttons").addClass("hide");
			$("#kq-q-showq").addClass("hide");
			$("#kq-q-showkq").addClass("hide");
			$("#kq-q-submit").addClass("hide");
			$("#kq-q-showa").addClass("hide");

            $("#kq-next-container").addClass("offset4");

            if (this.model.has("question")) {
                this.loadQuestionData();
            } else if (this.model.has("peer_review_assignment")) {
                this.loadPeerReviewData();
            } else if (this.model.has("asset_availability")) {
                this.loadAssetsData();
            }

            $("#kq-title").html(this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH));

            var meta_fb_name = $("meta[property*='site_name']");
            if (meta_fb_name.length > 0){
                meta_fb_name.attr('content', MOOC.vars.course_name + ' - ' + this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH));
            }else{
                $('head').append('<meta property="og:site_name" content="' + MOOC.vars.course_name + ' - ' + this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH) + '"/>');
            }
            $("#share_fb").attr('href', 'https://www.facebook.com/sharer/sharer.php?u=' + location.href.replace('#','%23'));
            $("#share_tw").attr('href', 'https://twitter.com/home?status=' + location.href.replace('#','%23'));
            $("#share_gplus").attr('href', 'https://plus.google.com/share?url=' + location.href.replace('#','%23'));

            unit = MOOC.models.course.getByKQ(this.model.get("id"));
            this.setEventForNavigation("#kq-previous", unit, this.model, false);
            this.setEventForNavigation("#kq-next", unit, this.model, true);

            this.$el.parent().children().removeClass("active");
            this.$el.addClass("active");

            var self = this;
            if(!this.model.get('marked')){
                $("#bookmark_btn img").attr('src','/static/img/ECO_icon_marcador_0.svg');
            }else{
                $("#bookmark_btn img").attr('src','/static/img/ECO_icon_marcador_1.svg');
            }
            $("#bookmark_btn").off('click').on('click', function () {
                $.ajax({
                    url: '/course/setmark/'+self.model.get("id")+'/',
                    type: 'GET'
                }).done(function(data){
                    $("#bookmark_btn img").attr('src','/static/img/ECO_icon_marcador_1.svg');
                });
            });

            this.renderExtraTabs();

            if (_.isObject(window.MathJax)) {
                _.each($('.mathjax'), function (item) {
                    MathJax.Hub.Queue(["Typeset", MathJax.Hub, item]);
                });
            }

            // Update progress
            $.ajax({
                url: '/users/'+ MOOC.vars.user_id +'/courses',
                type: 'GET'
            }).done(function(data){
                var userprogress = _.find(data, function(item){
                    return parseInt(item.id) == MOOC.router.lastUnitView.model.collection.courseId;
                });
                var $progressbar = $('.course-toolbar .progress-bar');
                var progress = userprogress.progressPercentage + '%';
                $progressbar.find('p').eq(0).html(progress);
                $progressbar.find('.progress span').eq(0).css('width', progress);
            });

            // Call activity if media type has no end event
            var media_type = this.model.get('media_content_type');
            if(media_type != 'youtube' && media_type != 'ytaccesible' && media_type != 'vimeo'){
                //MOOC.players_listener.trigger('mediaContentFinished', MOOC.views.kqViews[this.model.get('id')]);
            }
        }, this);

        if (MOOC.views.lastPlayerView) {
            MOOC.views.lastPlayerView.destroyPlayer(callback);
            MOOC.views.lastPlayerView = null;
        } else {
            callback();
        }

        // Update height to show the full sidemenu
        var menu_height = $('.unit-menu ol').outerHeight() + $('.unit-menu .heading').outerHeight();
        $('.nugget-view').css('min-height', menu_height+'px');

        //Emit render finish event
        $(window).trigger('renderfinished');

        if (sendHistoryEntry){
            sendHistoryEntry(MOOC.models.course.courseId);
        }

        return this;
    },

    renderExtraTabs: function () {
        "use strict";
        var comments,
            supplementary,
            attachments;

        comments = this.model.get("teacher_comments") || '';
        if(comments){
            $("#comments").html(comments).parent().removeClass('hide');
        }else{
            $("#comments").parent().addClass('hide');
        }

        supplementary = this.model.get("supplementary_material") || '';
        if(supplementary){
            $("#supplementary").html(supplementary).parent().removeClass('hide');
        }else{
            $("#supplementary").parent().addClass('hide');
        }
        this.setupListernerFor(this.model, "attachmentList", _.bind(function () {
            attachments = this.model.get("attachmentList") || [];
            if(attachments.length > 0){
                $("#attachments").parent().removeClass('hide');
                $("#attachments ul").empty();
                attachments.each(function (attachment) {
                    var view = new MOOC.views.Attachment({
                        model: attachment
                    });
                    $("#attachments ul").append(view.render());
                });
            }else{
                $("#attachments").parent().addClass('hide');
            }
        }, this));
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
                url,
				title;
            if (_.isUndefined(aux)) {
                $(selector).addClass("disabled");
            } else {
                url = "unit" + unit.get("id") + "/kq" + aux.get("id");
                if (!next && aux.has("question")) {
                    var question = aux.get("questionInstance");
                    if(question.get("solution_media_content_id") || question.get("solutionText")) {
                        url += "/a";
                    }else{
                        url += "/q";
                    }
                } else if (!next && aux.has("peer_review_assignment")) {
                    url += "/p";
                } else if (!next && aux.has("asset_availability")) {
                    url += "/as";
                }
                return {"url": url, "title": aux.get("title")};
            }
        };

        $(selector).unbind("click");

        if (/#[\w\/]+\/q/.test(path)) { // Viewing question
            target = next ? "answer" : "same";
        } else if (/#[\w\/]+\/as/.test(path)) { // Viewing asset availability
            target = next ? "next" : "same";
        } else if (/#[\w\/]+\/p/.test(path)) { // Viewing peer review
            target = next ? "next" : "same";
        } else if (/#[\w\/]+\/a/.test(path)) { // Viewing answer
            target = next ? "next" : "exercise";
        } else { // Viewing kq
            target = next ? "exercise" : "prev";
        }
        if (target === "exercise" && !kq.has("question") && !kq.has("peer_review_assignment") && !kq.has("asset_availability")) {
            target = "next";
        }
        if (target === "answer"){
            var question = kq.get("questionInstance")
            if(!question.get("solution_media_content_id") && !question.get("solutionText")) {
                target = "next";
            }
        }

        switch (target) {
        case "exercise":
            url = "unit" + unit.get("id") + "/kq" + kq.get("id");
            if (kq.has("question")) {
                url += "/q";
            } else if (kq.has("peer_review_assignment")) {// peer review
                url += "/p";
            } else if (kq.has("asset_availability")) {//asset availability
                url += "/as";
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
			if(next){
				$(selector + " .title").html(MOOC.trans.classroom.endOfUnit);
			}else{
				$(selector + " .title").html(MOOC.trans.classroom.startOfUnit);
			}
        } else {
			var urltext,
				title;
			if (_.isObject(url)) {
				urltext = url.url;
				$(selector + " .title").html(url.title);
			}else{
				urltext = url;
			}

			switch(target){
				case "next":
				case "prev":
					$(selector).removeClass("disabled");
					$(selector).attr('href', urltext).click(function (e) {
                        e.preventDefault();
						MOOC.router.navigate($(this).attr('href'), { trigger: true });
					});
					break;
				case "exercise":
					$("#kq-q-showq").attr('href', urltext).click(function(e){
                        e.preventDefault();
						MOOC.router.navigate($(this).attr('href'), { trigger: true });
					}).removeClass('hide');
					$(selector).addClass("disabled");
					break;
				case "answer":
                    $("#kq-q-showa").attr('href', urltext).click(function(e){
                        e.preventDefault();
                        MOOC.router.navigate($(this).attr('href'), { trigger: true });
                    }).removeClass('hide');
                    $(selector).addClass("disabled");
                    break;
				case "same":
					$(selector).addClass("disabled");
			}
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
                        solution_media_content_type: data.solution_media_content_type,
                        solution_media_content_id: data.solution_media_content_id,
                        iframe_code: data.iframe_code,
                        use_last_frame: data.use_last_frame
                    });
                if (data.solution_text !== "") {
                    question.set("solutionText", data.solution_text);
                }
                kqObj.set("questionInstance", question);
                // Load Options for Question
                MOOC.ajax.getOptionsByQuestion(question.get("id"), function (data, textStatus, jqXHR) {
                    var options = _.map(data.objects, function (opt) {
                        return new MOOC.models.Option(_.pick(opt, "id", "optiontype", "x", "y", "width", "height", "solution", "text", "feedback", "order", "name"));
                    });
                    question.set("optionList", new MOOC.models.OptionList(options));
                });
                // Load Answer for Question
                MOOC.ajax.getAnswerByQuestion(question.get("id"), function (data, textStatus, jqXHR) {
                    var obj, replies, answer, unit;
                    unit = MOOC.models.course.getByKQ(kqObj.get("id"));
                    if (data.objects.length === 1) {
                        obj = data.objects[0];
                        replies = _.map(obj.replyList, function (reply) {
                            return new MOOC.models.Reply(_.pick(reply, "option", "value"));
                        });
                        answer = new MOOC.models.Answer({
                            course_id: parseInt(MOOC.models.course.courseId, 10),
                            unit_id: parseInt(unit.get("id"), 10),
                            kq_id: parseInt(kqObj.get("id"), 10),
                            question_id: parseInt(question.get('id'), 10),
                            date: obj.date,
                            replyList: new MOOC.models.ReplyList(replies)
                        });
                        answer.local = false;
                    } else {
                        answer = new MOOC.models.Answer({
                            course_id: parseInt(MOOC.models.course.courseId, 10),
                            unit_id: parseInt(unit.get("id"), 10),
                            kq_id: parseInt(kqObj.get("id"), 10),
                            question_id: parseInt(question.get('id'), 10),
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
                    available_to: data.available_to,
                    can_be_booked: data.can_be_booked,
                    max_reservations_pending: data.max_reservations_pending,
                    max_reservations_total: data.max_reservations_total,
                    knowledgeQuantumInstance: kqObj
                });

                kqObj.set('assetAvailabilityInstance', assetAvailabilityObj);
            });
        }
    },

    loadExercise: function (evt) {
        "use strict";
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
                    unit = MOOC.models.course.getByKQ(this.model),
                    removeCallback;

                $("#kq-title").html(this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH));
                if (!(/[\w\/]+\/q/.test(path))) {
                    path = path + "/q";
                    MOOC.router.navigate(path, { trigger: false });
                }
                this.setEventForNavigation("#kq-previous", unit, this.model, false);
                this.setEventForNavigation("#kq-next", unit, this.model, true);

                removeCallback = function () {
                    $("#kq-video").empty();

                    if (_.isUndefined(view)) {
                        view = new MOOC.views.Question({
                            model: question,
                            el: $("#kq-video")[0]
                        });
                        MOOC.views.questionViews[question.get("id")] = view;
                    }
                    view.render();

                    callback();
                };

                this.renderExtraTabs();

                if (MOOC.views.lastPlayerView) {
                    MOOC.views.lastPlayerView.destroyPlayer(removeCallback);
                    MOOC.views.lastPlayerView = null;
                } else {
                    removeCallback();
                }
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
                    unit = MOOC.models.course.getByKQ(this.model),
                    removeCallback;

                $("#kq-title").html(this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH));
                if (!(/[\w\/]+\/p/.test(path))) {
                    path = path + "/p";
                    MOOC.router.navigate(path, { trigger: false });
                }

                this.setEventForNavigation("#kq-previous", unit, this.model, false);
                this.setEventForNavigation("#kq-next", unit, this.model, true);

                removeCallback = function () {
                    $("#kq-video").empty();

                    if (_.isUndefined(view)) {
                        view = new MOOC.views.PeerReviewAssignment({
                            model: peerReviewObj,
                            el: $("#kq-video")[0]
                        });
                        MOOC.views.peerReviewAssignmentViews[peerReviewObj.get("id")] = view;
                    }
                    view.render();

                    callback();
                };

                this.renderExtraTabs();

                if (MOOC.views.lastPlayerView) {
                    MOOC.views.lastPlayerView.destroyPlayer(removeCallback);
                    MOOC.views.lastPlayerView = null;
                } else {
                    removeCallback();
                }
            }, this));
        }

        async.series(toExecute);

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
                path = window.location.hash.substring(1),
                view = MOOC.views.assetViews[assetAvailability.get("id")],
                removeCallback;

            assetAvailability.set("_assetList", this.model.get("_assetList"));
            $("#kq-title").html(this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH));

            if (!(/[\w\/]+\/as/.test(path))) {

                path = path + "/as";
                MOOC.router.navigate(path, { trigger: false });
            }

            this.setEventForNavigation("#kq-previous", unit, this.model, false);
            this.setEventForNavigation("#kq-next", unit, this.model, true);

            removeCallback = function () {
                $("#kq-video").empty();

                if (_.isUndefined(view)) {
                    view = new MOOC.views.Asset({
                        model: assetAvailability,
                        el: $("#kq-video")[0]
                    });
                    MOOC.views.assetViews[assetAvailability.get("id")] = view;
                }
                view.render();

                callback();
            };

            this.renderExtraTabs();

            if (MOOC.views.lastPlayerView) {
                MOOC.views.lastPlayerView.destroyPlayer(removeCallback);
                MOOC.views.lastPlayerView = null;
            } else {
                removeCallback();
            }
        }, this));

        async.series(toExecute);

        return this;
    },

    loadSolution: function () {
        "use strict";
        var toExecute = [];

        toExecute.push(_.bind(function (callback) {
            _.bind(this.destroyVideo, this)();
            callback();
        }, this));

        if (!this.model.has("questionInstance")) {
            toExecute.push(async.apply(this.setupListernerFor, this.model, "questionInstance"));
        }

        toExecute.push(_.bind(function (callback) {
            var unit = MOOC.models.course.getByKQ(this.model),
                questionInstance = this.model.get("questionInstance"),
                html = "",
                iframe_template;

            if (questionInstance.has("solutionText")) {
                html = "<div class='solution-wrapper white mathjax'>" + questionInstance.get("solutionText") + "</div>";
            } else if (questionInstance.has("solution_media_content_type")) {
                iframe_template = _.template(questionInstance.get('iframe_code'));
                html = iframe_template({ height: '372px', width: '620px', allowfullscreen: true, controls: true, origin: MOOC.host });
            } else {
                MOOC.alerts.show(MOOC.alerts.INFO, MOOC.trans.api.solutionNotReadyTitle, MOOC.trans.api.solutionNotReady);
            }

            $("#kq-video").removeClass("question").html(html);
            $("#kq-video").css("height", "auto");

			//$("#kq-q-buttons").addClass("hide");
			$("#kq-q-showq").addClass("hide");
			$("#kq-q-showkq").addClass("hide");
			$("#kq-q-submit").addClass("hide");
			$("#kq-q-showa").addClass("hide");

            $("#kq-next-container").addClass("offset4");
            $("#kq-title").html(this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH));

            this.renderExtraTabs();

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

        if (sendHistoryEntry){
            sendHistoryEntry(MOOC.models.course.courseId);
        }

        return this;
    },

    destroyVideo: function () {
        "use strict";
        var node = $("#kq-video"),
            height = node.css("height");

        if (!_.isUndefined(height)) {
            node.css("height", height);
        }
        node.empty();
    }
});

MOOC.views.kqViews = {};

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
            this.$el.html(html);
            this.$el.addClass("use_last_frame");
        }else{
            this.$el.append($('fieldset'));
        }

        this.$el.addClass("question");

        //$("#kq-q-buttons").removeClass("hide");
		$("#kq-q-showkq").removeClass("hide");
		$("#kq-q-submit").removeClass("hide");
		$("#kq-q-showq").addClass("hide");
        if(this.model.get("solution_media_content_type") || this.model.get("solutionText")){
		    $("#kq-q-showa").removeClass("hide");
        }else{
            $("#kq-q-showa").addClass("hide");
        }

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

        if (sendHistoryEntry){
            sendHistoryEntry(MOOC.models.course.courseId);
        }

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
                option: parseInt(view.model.get("id"), 10),
                value: value
            });
        });
        if (replies.length > 0) {
            answer.set('replyList', new MOOC.models.ReplyList(replies));
            answer.set('date', new Date());

            fetch_solutions = self.model.get("optionList").any(function (option) {
                return _.isNull(option.get("solution"));
            });

            MOOC.ajax.sendAnswer(answer, function (data, textStatus, jqXHR) {
                if (jqXHR.status === 201 || jqXHR.status === 204) {
                    answer.local = false;
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
                var sorted_options = _.sortBy(data.objects, function(item){return item.order;});
                _.each(sorted_options, function (opt) {
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
    MIN_TEXT_HEIGHT: 20,

    types: {
        l: "textarea",
        t: "text",
        c: "checkbox",
        r: "radio",
        q: "fieldset"
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
            tag = optiontype !== 'q'? "input" : "span",
            content = "",
            attributes = {
                type: this.types[optiontype],
                id: 'option' + this.model.get('id'),
                style: []
            },
            // The scale is required because the question editor is smaller
            // than the classroom question
            scale = 1.1481481, // 620/540 or 372/324
            left = Math.floor(this.model.get('x') * scale),
            top = Math.floor(this.model.get('y') * scale),
            feedbackBtn,
            correct,
            label = this.model.get('text');

        if (optiontype === 't') {
            width = Math.floor(this.model.get('width') * scale) + 'px;';
            height = Math.floor(this.model.get('height') * scale);
            if (height < this.MIN_TEXT_HEIGHT) {
                height = this.MIN_TEXT_HEIGHT;
            }
            height = height + 'px;';
        }

        var domelem = '<div style="top:'+top+'px; left:'+left+'px"';
        if (optiontype !== 'l') {
            attributes.style.push('width: ' + width + 'px;');
            attributes.style.push('height: ' + height + 'px;');
        }else{
            content = this.model.get('text');
        }
        attributes.style = attributes.style.join(' ');
        if (optiontype === 'r') {
            attributes.name = this.model.get('name');
        }

        this.$el.find("#" + attributes.id).parent().next("br").remove();
        this.$el.find("#" + attributes.id).parent().remove();
        this.$el.find("#" + attributes.id + "-fb").remove();


        if (this.reply && this.reply.get('option') === parseInt(this.model.get('id'), 10) && optiontype !== 'l') {
            correct = false;
            if (optiontype === 't') {
                attributes.value = this.reply.get('value');
                if (!(_.isUndefined(solution) || _.isNull(solution))) {
                    correct = this.model.isCorrect(this.reply);
                    attributes['class'] = correct ? 'correct' : 'incorrect';
                    var correctclass = correct ? 'correct' : 'incorrect';
                    domelem += ' class="'+ correctclass +'"';
                }
            } else {
                if (this.reply.get('value')) {
                    attributes.checked = 'checked';
                }
                if (!(_.isUndefined(solution) || _.isNull(solution))) {
                    correct = this.model.isCorrect(this.reply);
                    attributes['class'] = correct ? 'correct' : 'incorrect';
                    var correctclass = correct ? 'correct' : 'incorrect';
                    domelem += ' class="'+ correctclass +'"';
                }
            }

            if (!correct && this.model.has("feedback") && this.model.get("feedback") !== "") {
                feedbackBtn = $("<button class='btn transparent' id='" + attributes.id + "-fb'><img src='/static/img/ECO_icon_info_ayuda.svg'></button>");
                feedbackBtn.css("top", (top - 4) + "px");
                feedbackBtn.css("left", (left - 32) + "px");
                feedbackBtn.popover({
                    trigger: "click",
                    placement: "right",
                    title: MOOC.trans.classroom.clue,
                    content: this.model.get("feedback")
                });
                this.$el.append(feedbackBtn);
            }
        }

        domelem += '>';
        if(optiontype !== 'l'){
            if(optiontype === 't' && label){
                domelem += '<label for="' + attributes.id + '">' + label + '</label>';
            }
            domelem += '<'+tag;
            for (var attribute in attributes){
                if(attributes.hasOwnProperty(attribute)){
                    domelem += ' ' + attribute + '="' + attributes[attribute]+'"';
                }
            }
            domelem += '>'
            if(optiontype !==  't' && label){
                domelem += '<label for="' + attributes.id + '">' + label + '</label>';
            }
        }else{
            domelem += '<p id="'+ attributes.id +'">' + content + '</p>';
        }
        domelem += '</div>';

        var $domelem = $(domelem);
        if(feedbackBtn){
             $domelem.append(feedbackBtn);
        }
        this.$el.append($domelem);
        this.$el.append($('<br/>'));

        return this;
    }
});

MOOC.views.optionViews = {};

MOOC.views.Attachment = Backbone.View.extend({
    events: {
      'click .link': 'send_stats'
    },
    render: function () {
        "use strict";
        var html = "<li><a class='link' href='" + this.model.get("url") + "' target='_blank'>",
            parts = this.model.get("url").split('/');
        html += parts[parts.length - 1];
        html += "</a></li>";
        this.$el.append(html);
        return this.$el;
    },
    send_stats: function(e){
      sendHistoryEntry(MOOC.models.course.courseId, {'delay': 0, 'url': MOOC.host + this.model.get("url")});
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
            //$("#kq-q-buttons").addClass("hide");
			$("#kq-q-showq").addClass("hide");
			$("#kq-q-showkq").addClass("hide");
			$("#kq-q-submit").addClass("hide");
			$("#kq-q-showa").addClass("hide");

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

            //$("#kq-q-buttons").removeClass("hide");
			$("#kq-q-showkq").removeClass("hide");
			$("#kq-q-submit").removeClass("hide");
			$("#kq-q-showq").addClass("hide");
			$("#kq-q-showa").removeClass("hide");

            $("#kq-q-submit").attr("disabled", false);
            $("#kq-q-showkq").off('click').on('click', function () {
                MOOC.router.navigate(kqPath, { trigger: true });
            });
            $("#kq-q-submit").off('click').on('click', this.submit);
            $("#kq-next-container").removeClass("offset4");

            $("#pr-view-criteria").off('click').on('click', this.viewCriteria);
        }

        if (_.isObject(window.MathJax)) {
            _.each(this.$el.find('.mathjax'), function (item) {
                MathJax.Hub.Queue(["Typeset", MathJax.Hub, item]);
            });
        }

        if (sendHistoryEntry){
            sendHistoryEntry(MOOC.models.course.courseId);
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
        $modal.removeClass('hide');
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

MOOC.views.Asset = Backbone.View.extend({
    events: {
        "click button.as-new-reservation": "newReservation"
    },

    checkDate: function (asset, dateText) {
        "use strict";
        var reservationCountList,
            counts,
            key,
            self = this;

        if (this.reservationCounts.hasOwnProperty(dateText)) {
            this.fillWithAvailableTimes(asset, this.reservationCounts[dateText]);
        } else {
            this.getFormModal().find("#as-confirm").addClass("disabled");
            reservationCountList = new MOOC.models.ReservationCountList();
            reservationCountList.fetch({
                data: { 'asset': asset.get('id'),
                        'date': dateText },
                success: function (collection, resp, options) {
                    counts = [];
                    reservationCountList.each(function (count) {
                        key = count.get("reservation_begins").split('T')[1].slice(0, 5);
                        counts[key] = count.get("count");
                    });
                    self.reservationCounts[dateText] = counts;

                    self.fillWithAvailableTimes(asset, counts);
                }
            });
        }
    },

    fillWithAvailableTimes: function (asset, counts) {
        "use strict";
        var key,
            maxBookings,
            currentTime,
            options;


        maxBookings = asset.get('max_bookable_slots') * asset.get('capacity');

        options = [];
        currentTime = new Date('2000-01-01T00:00:00.000Z'); //The day itself is irrelevant
        while (currentTime.getUTCDate() === 1) {
            key = currentTime.toISOString().split('T')[1].slice(0, 5);
            if (!counts.hasOwnProperty(key) || (counts[key] < maxBookings)) {
                options.push("<option>");
                options.push(key);
                options.push("</option>");
            }
            currentTime = new Date(currentTime.getTime() + asset.get("slot_duration") * 60000);
        }
        if (options.length === 0) {
            this.getFormModal().find("#as-confirm").addClass("disabled");
        } else {
            this.getFormModal().find("#as-confirm").removeClass("disabled");
        }
        this.getFormModal().find("#as-fromtime").html(options.join(""));
    },

    initialize: function () {
        "use strict";
        _.bindAll(this, "render", "getFormModal", "submit", "beforeShowDay",
                  "confirmedSubmit", "checkDate", "fillWithAvailableTimes");
    },

    modal: undefined,
    formModal: undefined,
    reservationCounts: [],
    occupationInformation: [],

    downloadOccupationInformation: function (asset, year, month) {
        "use strict";
        var occupationInformationList,
            occupationInfo,
            self = this;

        occupationInformationList = new MOOC.models.OccupationInformationList();
        occupationInformationList.fetch({
            data: { 'asset': asset.get('id'),
                    'month': month,
                    'year': year },
            async: false,
            success: function (collection, resp, options) {
                occupationInfo = new Array(31);

                occupationInformationList.each(function (element) {
                    occupationInfo[element.get("day")] = element.get("occupation");
                });

                if (!self.occupationInformation.hasOwnProperty(year)) {
                    self.occupationInformation[year] = [];
                }

                self.occupationInformation[year][month] = occupationInfo;
            }
        });
    },

    beforeShowDay: function (asset, date) {
        "use strict";
        var couldDownload,
            month,
            year,
            occupation;

        month = date.getMonth() + 1;
        year = date.getFullYear();
        couldDownload = true;
        if (!(this.occupationInformation.hasOwnProperty(year) && this.occupationInformation[year].hasOwnProperty(month))) {
            this.downloadOccupationInformation(asset, year, month);
            couldDownload = (this.occupationInformation.hasOwnProperty(year) && this.occupationInformation[year].hasOwnProperty(month));
        }

        if (!couldDownload) {
            return [true, ""];
        }

        occupation = this.occupationInformation[year][month][date.getDate()];
        if (occupation >= 1) {
            return [true, "red"];
        }
        if (occupation > 0.8) {
            return [true, "orange"];
        }
        if (occupation > 0.5) {
            return [true, "yellow"];
        }
        return [true, "green"];
    },

    getFormModal: function () {
        "use strict";
        if (_.isUndefined(this.formModal)) {
            this.formModal = $("#new-reservation-form");
            this.formModal.modal({
                show: false,
                backdrop: "static",
                keyboard: false
            });
        }
        return this.formModal;
    },

    render: function () {
        "use strict";
        var html,
            buttonId,
            divId,
            canBeBooked;

        html = [];

        html.push("<h3>" + MOOC.trans.classroom.asRequisites + "</h3>");
        html.push("<div id='availability-information' class='solution-wrapper white'>");
        html.push("<div class='row'>");
        html.push("<div class='span3'><ul><li>" + MOOC.trans.classroom.asDates + "<ul>");
        html.push("<li>" + MOOC.trans.classroom.asDatesFrom + this.model.get("available_from") + "</li>");
        html.push("<li>" + MOOC.trans.classroom.asDatesTo + this.model.get("available_to") + "</li>");
        html.push("</ul></li></ul></div><div class='span3'><ul><li>");
        html.push(MOOC.trans.classroom.asLimits + "<ul>");
        html.push("<li>" + MOOC.trans.classroom.asMaxPending + this.model.get("max_reservations_pending") + "</li>");
        html.push("<li>" + MOOC.trans.classroom.asMaxTotal + this.model.get("max_reservations_total") + "</li>");
        html.push("</ul></li></ul></div></div></div>");

        canBeBooked = this.model.get("can_be_booked");

        if (!canBeBooked) {
            html.push("<br /><div class=\"alert\">");
            html.push(MOOC.trans.classroom.asCannotBook);
            html.push("</div>");
        }

        html.push("<h3>" + MOOC.trans.classroom.asAssetList + "</h3>");
        this.model.get("_assetList").each(function (asset) {
            buttonId = "reservationnew-" + asset.get("id");
            divId = "asset-information-" + asset.get("id");
            html.push("<div class='solution-wrapper white'>");
            html.push("<div id='" + divId + "'>");
            html.push("<h4>" + asset.get("name") + "</h4>");
            html.push(asset.get("description"));
            html.push("<div class=\"row\"><div class=\"span3\">");
            html.push("<ul><li>" + MOOC.trans.classroom.asSlotLength + asset.get("slot_duration") + "</li>");
            html.push("<li>" + MOOC.trans.classroom.asNumberOfSlots + asset.get("max_bookable_slots") + "</li>");
            html.push("<li>" + MOOC.trans.classroom.asCapacity + asset.get("capacity") + "</li>");
            html.push("</ul></div><div class=\"span3\">");
            html.push("<ul><li>" + MOOC.trans.classroom.asInAdvance + "<ul>");
            html.push("<li>" + MOOC.trans.classroom.asReservations + " ");
            html.push(asset.get("reservation_in_advance") + " " + MOOC.trans.classroom.asMinutes + "</li>");
            html.push("<li>" + MOOC.trans.classroom.asCancelations + " ");
            html.push(asset.get("cancelation_in_advance") + " " + MOOC.trans.classroom.asMinutes + "</li>");
            html.push("</ul></li></ul></div></div></div><p class=\"align-right\">");
            if (canBeBooked) {
                html.push("<button type=\"button\" class=\"btn btn-primary as-new-reservation\" id=\"" + buttonId + "\">");
                html.push(MOOC.trans.classroom.asBook);
                html.push("</button>");
            }
            html.push("</p></div><br />");
        });

        this.$el.html(html.join(""));

        $("#kq-q-showkq").addClass("hide");
        $("#kq-q-submit").addClass("hide");

        return this;
    },

    newReservation: function (evt) {
        "use strict";
        var assetId = parseInt(evt.target.getAttribute('id').split('-')[1], 10),
            assetList = this.model.get("_assetList"),
            formModal = this.getFormModal(),
            assetDivId = "#asset-information-" + assetId,
            actionURL,
            baseURL = document.URL,
            formContent,
            asset,
            firstDate,
            lastDate,
            defaultDate,
            currentTime,
            self = this;

        asset = assetList.find(function (candidate) {
            return (parseInt(candidate.get("id"), 10) === assetId);
        });

        evt.preventDefault();
        evt.stopPropagation();

        formModal.find("#new-asset-reservation-availability-information").html(this.$el.find("#availability-information").html());
        formModal.find("#new-asset-reservation-asset-information").html(this.$el.find(assetDivId).html());

        firstDate = this.model.get("available_from");

        lastDate = this.model.get("available_to");

        if (new Date(firstDate) < (new Date())) {
            defaultDate = new Date();
        } else {
            defaultDate = firstDate;
        }

        formContent = [];
        formContent.push("<div class=\"row\">");
        formContent.push("<div class=\"span3\"><p><label for=\"as-date\">" + MOOC.trans.classroom.asBookDate + "</label>");
        formContent.push("<input type=\"text\" class=\"input-medium\" name=\"reservation_date\" id=\"as-date\">");
        formContent.push("</p></div><div class=\"span3\"><p><label for=\"as-fromtime\">");
        formContent.push(MOOC.trans.classroom.asBookTime + "</label>");
        formContent.push("<select class=\"input-small\" name=\"reservation_time\" id=\"as-fromtime\">");

        formContent.push("</select></p></div></div>");

        baseURL = document.URL.split('#')[0];
        if (baseURL.slice(-1) === "/") {
            baseURL = baseURL.slice(0, baseURL.length - 1);
        }
        baseURL = baseURL.split('/').slice(0, -1).join('/');

        actionURL = baseURL + "/reservations/" + this.model.get("knowledgeQuantumInstance").get("id");
        actionURL += "/" + assetId + "/new";

        formModal.find("#new-asset-reservation-form-content").html(formContent.join(""));
        formModal.find("#new-asset-reservation-form").attr("action", actionURL);

        formModal.find("#as-date").datepicker({dateFormat: "yy-mm-dd",
            minDate: firstDate,
            maxDate: lastDate,
            defaultDate: defaultDate,
            onSelect: function (dateText) {
                self.checkDate(asset, dateText);
            },
            beforeShowDay: function (date) {
                return self.beforeShowDay(asset, date);
            }
            });

        this.submit();
    },

    submit: function () {
        "use strict";
        var modal = this.getFormModal();
        modal.find("#as-confirm").off("click").on("click", _.bind(function () {
            if (!modal.find("#as-confirm").hasClass("disabled")) {
                this.confirmedSubmit();
                modal.modal("hide");
            }
        }, this));
        modal.find("#as-confirm").addClass("disabled");
        modal.modal("show");
    },

    confirmedSubmit: function () {
        "use strict";
        this.getFormModal().find("#new-asset-reservation-form")[0].submit();
    }
});

MOOC.views.assetViews = {};
