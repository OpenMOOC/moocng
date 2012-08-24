/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _, YT, async */

if (_.isUndefined(window.MOOC)) {
    window.MOOC = {};
}

MOOC.views = {};

MOOC.views.Unit = Backbone.View.extend({
    events: {
        "click li span.kq": "showKQ",
        "click li span.q": "showQ",
        "click li span.a": "showA"
    },

    render: function () {
        "use strict";
        var html = '<div class="accordion-inner kqContainer"><ol>';
        this.model.get("knowledgeQuantumList").each(function (kq) {
            html += '<li id="kq' + kq.get("id") + '"><span class="kq label label-success">' + kq.get("title") + '</span>';
            if (kq.has("question")) {
                html += ' <span class="q label">' + MOOC.trans.classroom.q + '</span> ';
                html += '/ <span class="a label">' + MOOC.trans.classroom.a + '</span>';
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
    }
});

MOOC.views.unitViews = {};

MOOC.views.KnowledgeQuantum = Backbone.View.extend({
    render: function () {
        "use strict";
        var height = this.getVideoHeight(),
            player,
            html,
            unit,
            order,
            kq,
            kqObj,
            comments,
            supplementary;

        html = '<iframe id="ytplayer" width="100%" height="' + height + 'px" ';
        html += 'src="http://www.youtube.com/embed/' + this.model.get("videoID");
        html += '" frameborder="0" allowfullscreen></iframe>';
        $("#kq-video").html(html);

        $("#kq-q-buttons").addClass("hide");
        $("#kq-next-container").addClass("offset4");

        if (this.model.has("question")) {
            kqObj = this.model;
            // Load Question Data
            MOOC.ajax.getResource(kqObj.get("question"), function (data, textStatus, jqXHR) {
                var aux = _.pick(data, "id", "last_frame", "solutionID"),
                    question = new MOOC.models.Question({
                        id: aux.id,
                        lastFrame: aux.last_frame,
                        solution: aux.solutionID
                    });
                kqObj.set("questionInstance", question);
                // Load Options for Question
                MOOC.ajax.getOptionsByQuestion(question.get("id"), function (data, textStatus, jqXHR) {
                    var options = _.map(data.objects, function (opt) {
                        return new MOOC.models.Option(_.pick(opt, "id", "optiontype", "x", "y", "width", "height", "solution"));
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
            this.repeatedlyCheckIfPlayer();
        }

        $("#kq-title").html(this.model.get("title"));

        unit = MOOC.models.course.getByKQ(this.model.get("id"));
        $("#unit-selector").find("div.collapse").removeClass("in");
        $("#unit" + unit.get("id")).addClass("in");

        this.setEventForNavigation("#kq-previous", unit, this.model, false);
        this.setEventForNavigation("#kq-next", unit, this.model, true);

        this.$el.parent().children().removeClass("active");
        this.$el.addClass("active");

        comments = this.model.get("teacher_comments") || '';
        $("#comments").html(comments);

        supplementary = this.model.get("supplementary_material") || '';
        $("#suplementary").html(supplementary);

        return this;
    },

    getVideoHeight: function () {
        "use strict";
        var width = $("#kq-video").css("width"),
            height;

        if (width.indexOf('p') > 0) {
            width = parseInt(width.split('p')[0], 10);
        } else {
            width = parseInt(width, 10);
        }
        height = Math.round((width * 6) / 10);
        if (height < 200) {
            height = 200;
        }

        return height;
    },

    setEventForNavigation: function (selector, unit, kq, next) {
        "use strict";
        var path = window.location.hash,
            order = kq.get("order"),
            getUrlForOtherKQ,
            target,
            url;

        getUrlForOtherKQ = function (position, answer) {
            var aux = unit.get("knowledgeQuantumList").getByPosition(position),
                url;
            if (_.isUndefined(aux)) {
                $(selector).addClass("disabled");
            } else {
                url = "unit" + unit.get("id") + "/kq" + aux.get("id");
                if (answer && aux.has("question")) {
                    url += "/a";
                }
                return url;
            }
        };

        $(selector).unbind("click");

        if (/#[\w\/]+\/q/.test(path)) { // Viewing question
            target = next ? "answer" : "same";
        } else if (/#[\w\/]+\/a/.test(path)) { // Viewing answer
            target = next ? "next" : "question";
        } else { // Viewing kq
            target = next ? "question" : "prev";
        }
        if (target === "question" && !kq.has("question")) {
            target = "next";
        }

        switch (target) {
        case "question":
            url = "unit" + unit.get("id") + "/kq" + kq.get("id") + "/q";
            break;
        case "answer":
            url = "unit" + unit.get("id") + "/kq" + kq.get("id") + "/a";
            break;
        case "next":
            url = getUrlForOtherKQ(order + 1, false);
            break;
        case "prev":
            url = getUrlForOtherKQ(order - 1, true);
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

    repeatedlyCheckIfPlayer: function (callback) {
        "use strict";
        if (MOOC.YTready) {
            this.player = new YT.Player("ytplayer", {
                events: {
                    onStateChange: _.bind(this.loadQuestion, this)
                }
            });
            if (!_.isUndefined(callback)) {
                callback();
            }
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

    loadQuestion: function (evt) {
        "use strict";
        if (evt.data === YT.PlayerState.ENDED) {
            var toExecute = [];

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
                    destroyPlayer = _.bind(function () {
                        this.player.destroy();
                        this.player = null;
                    }, this),
                    data = {
                        kq: this.model.get("id")
                    },
                    path = window.location.hash.substring(1),
                    unit = MOOC.models.course.getByKQ(this.model);

                if (!(/[\w\/]+\/q/.test(path))) {
                    path = path + "/q";
                    MOOC.router.navigate(path, { trigger: false });
                }
                this.setEventForNavigation("#kq-previous", unit, this.model, false);
                this.setEventForNavigation("#kq-next", unit, this.model, true);

                MOOC.ajax.updateUserActivity(data);

                if (_.isUndefined(view)) {
                    view = new MOOC.views.Question({
                        model: question,
                        el: $("#kq-video")[0]
                    });
                    MOOC.views.questionViews[question.get("id")] = view;
                }
                // We need to destroy the iframe with a callback because the
                // question view needs to read the width/height of the video
                view.render(destroyPlayer);
            }, this));

            async.series(toExecute);
        }

        return this;
    },

    loadSolution: function () {
        "use strict";
        var toExecute = [];

        toExecute.push(_.bind(this.repeatedlyCheckIfPlayer, this));
        toExecute.push(_.bind(function (callback) {
            this.player.destroy();
            this.player = null;
            callback();
        }, this));

        if (!this.model.has("questionInstance")) {
            toExecute.push(async.apply(this.setupListernerFor, this.model, "questionInstance"));
        }

        toExecute.push(_.bind(function (callback) {
            var height = this.getVideoHeight(),
                html;

            html = '<iframe id="ytplayer" width="100%" height="' + height + 'px" ';
            html += 'src="http://www.youtube.com/embed/' + this.model.get("questionInstance").get("solution");
            html += '" frameborder="0" allowfullscreen></iframe>';
            $("#kq-video").html(html);
            $("#kq-q-buttons").addClass("hide");
            $("#kq-next-container").addClass("offset4");

            callback();
        }, this));

        async.series(toExecute);

        return this;
    }
});

MOOC.views.kqViews = {};

MOOC.views.Question = Backbone.View.extend({
    render: function (destroyPlayer) {
        "use strict";
        var width = this.$el.children().css("width"),
            height = this.$el.children().css("height"),
            kqPath = window.location.hash.substring(1, window.location.hash.length - 2), // Remove trailing /q
            html = '<img src="' + this.model.get("lastFrame") + '" ';

        html += 'alt="' + this.model.get("title") + '" style="max-width: ' + width;
        html += '; height: ' + height + ';" />';
        destroyPlayer();
        this.$el.html(html);

        $("#kq-q-buttons").removeClass("hide");
        $("#kq-q-showkq").click(function () {
            MOOC.router.navigate(kqPath, { trigger: true });
        });
        $("#kq-q-submit").click(_.bind(function () {
            this.submitAnswer(this.model);
        }, this));
        $("#kq-next-container").removeClass("offset4");

        this.model.get("optionList").each(function (opt) {
            var view = MOOC.views.optionViews[opt.get("id")];
            if (_.isUndefined(view)) {
                view = new MOOC.views.Option({
                    model: opt,
                    el: $("#kq-video")[0]
                });
                MOOC.views.optionViews[opt.get("id")] = view;
            }
            view.render();
        });

        return this;
    },

    submitAnswer: function (question) {
        "use strict";
        var answer = question.get('answer'), replies;

        replies = question.get("optionList").map(function (opt) {
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
        answer.set('replyList', replies);
        answer.set('date', new Date());

        MOOC.ajax.sendAnswer(answer, question.get('id'), function (data, textStatus, jqXHR) {
            if (jqXHR.status === 201) {
                answer.set('id', question.get('id'));
                question.set('answer', answer);

                MOOC.alerts.show(MOOC.alerts.SUCCESS,
                                 MOOC.trans.classroom.answersSent,
                                 MOOC.trans.classroom.answersSentMsg);
            }
        });
    }
});

MOOC.views.questionViews = {};

MOOC.views.Option = Backbone.View.extend({
    types: {
        t: "text",
        c: "checkbox",
        r: "radio"
    },

    render: function () {
        "use strict";
        var optiontype = this.model.get('optiontype'),
            answer = this.model.get('answer'),
            attributes = {
                type: this.types[optiontype],
                id: 'option' + this.model.get('id'),
                style: [
                    'top: ' + this.model.get('y') + 'px;',
                    'left: ' + this.model.get('x') + 'px;',
                    'width: ' + this.model.get('width') + 'px;',
                    'height: ' + this.model.get('height') + 'px;'
                ].join(' ')
            };
        if (optiontype === 'r') {
            attributes.name = 'radio';
        }
        if (answer) {
            if (optiontype === 't') {
                attributes.value = answer;
            } else {
                if (answer === 'True') {
                    attributes.checked = 'checked';
                }
            }
        }
        this.$el.append(this.make('input', attributes));
        return this;
    }
});

MOOC.views.optionViews = {};
