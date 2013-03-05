/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _ */

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

MOOC.views.capitalize = function (text) {
    "use strict";
    return text.charAt(0).toUpperCase() + text.slice(1);
};

MOOC.views.Unit = Backbone.View.extend({

    initialize: function () {
        "use strict";
        var collection = this.model.get('knowledgeQuantumList');
        this._kqViews = collection.map(function (kq) {
            var kqView = MOOC.views.kqViews[kq.id];
            if (_.isUndefined(kqView)) {
                MOOC.views.kqViews[kq.id] = new MOOC.views.KnowledgeQuantum({
                    model: kq,
                    id: "kq" + kq.id
                });
                kqView = MOOC.views.kqViews[kq.id];
            }
            return kqView;
        });
    },

    render: function () {
        "use strict";
        var html,
            progress,
            helpText;

        this.$el.parent().children().removeClass("active");
        this.$el.addClass("active");

        $("#unit-title").html(this.model.get("title"));

        html = '<div class="progress progress-info" title="' + MOOC.trans.progress.completed + '"><div class="bar completed" style="width: 0%;"></div></div>';
        html += '<div class="progress progress-success" title="' + MOOC.trans.progress.correct + '"><div class="bar correct" style="width: 0%;"></div></div>';
        $("#unit-progress-bar").html(html);

        progress = this.model.calculateProgress({ completed: true });
        helpText = "<div><span>" + Math.round(progress) + "% " + MOOC.trans.progress.completed + "</span></div>";
        $("#unit-progress-bar").find("div.bar.completed").css("width", progress + "%");

        progress = this.model.calculateProgress({ completed: true, correct: true });
        helpText += "<div><span>" + Math.round(progress) + "% " + MOOC.trans.progress.correct + "</span></div>";
        $("#unit-progress-bar").find("div.bar.correct").css("width", progress + "%");

        $("#unit-progress-text").html(helpText);


        $("#unit-kqs").empty();
        _(this._kqViews).each(function (kqView) {
            $("#unit-kqs").append(kqView.render().el);
        });

        return this;
    }
});

MOOC.views.unitViews = {};

MOOC.views.KnowledgeQuantum = Backbone.View.extend({
    tagName: "li",

    render: function () {
        "use strict";
        var html = [
                "<b>" + this.model.truncateTitle(40) + "</b>"
            ];
        if (this.model.get('completed')) {
            if (this.model.get("correct")) {
                html.push('<span class="badge badge-success pull-right"><i class="icon-ok icon-white"></i> ' + MOOC.views.capitalize(MOOC.trans.progress.correct) + '</span>');
            } else {
                html.push('<span class="badge badge-important pull-right"><i class="icon-remove icon-white"></i> ' + MOOC.trans.progress.incorrect + '</span>');
            }
        } else {
            html.push('<span class="badge pull-right">' + MOOC.trans.progress.pending + '</span>');
        }

        this.$el.attr("title", this.model.get('title'));
        this.$el.html(html.join(""));
        return this;
    }
});

MOOC.views.kqViews = {};
