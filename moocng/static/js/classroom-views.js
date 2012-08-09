/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _, YT */

if (typeof MOOC === 'undefined') {
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
        var html = '<div class="accordion-inner"><ol>';
        this.model.get("knowledgeQuantumList").each(function (kq) {
            html += '<li id="kq' + kq.get("id") + '"><span class="kq">' + kq.get("title") + '</span>';
            if (kq.has("question")) {
                html += ' <span class="q">Q</span> / <span class="a">A</span>';
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
        var width = $("#kq-video").css("width"),
            height,
            player,
            html,
            unit,
            order,
            kq,
            kqObj;

        if (width.indexOf('p') > 0) {
            width = parseInt(width.split('p')[0], 10);
        } else {
            width = parseInt(width, 10);
        }
        height = Math.round((width * 6) / 10);
        if (height < 200) {
            height = 200;
        }

        html = '<iframe id="ytplayer" width="100%" height="' + height + 'px" ';
        html += 'src="http://www.youtube.com/embed/' + this.model.get("videoID");
        html += '" frameborder="0" allowfullscreen></iframe>';
        $("#kq-video").html(html);

        if (this.model.has("question")) {
            kqObj = this.model;
            // Load Question Data
            MOOC.ajax.getResource(kqObj.get("question"), function (data, textStatus, jqXHR) {
                var question = new MOOC.models.Question(_.pick(data, "id", "last_frame", "solution"));
                kqObj.set("questionInstance", question);
                // Load Options for Question
                MOOC.ajax.getOptionsByQuestion(question.get("id"), function (data, textStatus, jqXHR) {
                    var options = _.map(data.objects, function (opt) {
                        return new MOOC.models.Option(_.pick(opt, "id", "optiontype", "x", "y"));
                    });
                    question.set("optionList", new MOOC.models.OptionList(options));
                });
            });
            this.waitForPlayer();
        }

        $("#kq-title").html(this.model.get("title"));

        unit = MOOC.models.course.getByKQ(this.model.get("id"));
        $("#unit" + unit.get("id")).collapse("show");
        order = this.model.get("order");
        $("#kq-previous").unbind("click");
        $("#kq-next").unbind("click");

        kq = unit.get("knowledgeQuantumList").getByPosition(order - 1);
        this.navigate("#kq-previous", unit, kq);
        kq = unit.get("knowledgeQuantumList").getByPosition(order + 1);
        this.navigate("#kq-next", unit, kq);

        this.$el.parent().children().removeClass("active");
        this.$el.addClass("active");

        return this;
    },

    navigate: function (selector, unit, kq) {
        "use strict";
        if (typeof kq === "undefined") {
            $(selector).addClass("disabled");
        } else {
            $(selector).removeClass("disabled");
            $(selector).click(function (evt) {
                MOOC.router.navigate("unit" + unit.get("id") + "/kq" + kq.get("id"), { trigger: true });
            });
        }
    },

    player: null,

    waitForPlayer: function () {
        "use strict";
        if (MOOC.YTready) {
            this.player = new YT.Player("ytplayer", {
                events: {
                    onStateChange: _.bind(this.loadQuestion, this)
                }
            });
        } else {
            setTimeout(_.bind(this.waitForPlayer, this), 500);
        }
    },

    waitFor: function (model, property, callback) {
        "use strict";
        // TODO loading indicator
        model.on("change", function (evt) {
            if (this.has(property)) {
                this.off("change");
                callback(this.get(property));
            }
        }, model);
    },

    loadQuestion: function (evt) {
        "use strict";
        if (evt.data === YT.PlayerState.ENDED) {
            var view = this,
                player = this.player,
                title = this.model.get("title"),
                lq = function (question) {
                    var width = $("#kq-video").children().css("width"),
                        height = $("#kq-video").children().css("height"),
                        html = '<img src="' + question.get("last_frame") + '" ';
                    html += 'alt="' + title + '" style="max-width: ' + width;
                    html += '; height: ' + height + ';" />';
                    player.destroy();
                    $("#kq-video").html(html);

                    question.get("optionList").each(function (opt) {
                        if (typeof MOOC.views.optionViews[opt.get("id")] === "undefined") {
                            MOOC.views.optionViews[opt.get("id")] = new MOOC.views.Option({
                                model: opt,
                                el: $("#kq-video")[0]
                            });
                        }
                        MOOC.views.optionViews[opt.get("id")].render();
                    });
                },
                lo = function (question) {
                    if (question.has("optionList")) {
                        lq(question);
                    } else {
                        view.waitFor(question, "optionList", lq);
                    }
                },
                question;

            if (this.model.has("questionInstance")) {
                lo(this.model.get("questionInstance"));
            } else {
                this.waitFor(this.model, "questionInstance", lo);
            }
        }
    }
});

MOOC.views.kqViews = {};

MOOC.views.Option = Backbone.View.extend({
    types: {
        i: "text",
        c: "checkbox",
        r: "radio"
    },

    render: function () {
        "use strict";
        var html = "<input type='" + this.types[this.model.get("optiontype")] + "' ",
            node;
        html += "style='top: " + this.model.get("y") + "px; left: " + this.model.get("x") + "px;' ";
        if (this.model.get("optiontype") === 'r') {
            html += "name='radio' ";
        }
        html += "/>";
        node = $(html)[0];
        this.$el.append(node);
        return this;
    }
});

MOOC.views.optionViews = {};
