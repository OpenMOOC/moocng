/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _ */

// Copyright 2012 Rooter Analysis S.L. All rights reserved.
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

MOOC.views.Unit = Backbone.View.extend({
    events: {
        "click": "showUnit"
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

        html = '';
        this.model.get("knowledgeQuantumList").each(function (kq) {
            html += "<li><b>" + kq.get("title") + "</b>";
            if (kq.get("completed")) {
                if (kq.get("correct")) {
                    html += '<span class="badge badge-success pull-right"><i class="icon-ok icon-white"></i> ' + MOOC.trans.progress.correct2 + '</span>';
                } else {
                    html += '<span class="badge badge-important pull-right"><i class="icon-remove icon-white"></i> ' + MOOC.trans.progress.incorrect + '</span>';
                }
            } else {
                html += '<span class="badge pull-right">' + MOOC.trans.progress.pending + '</span>';
            }
            html += "</li>";
        });
        $("#unit-kqs").html(html);

        return this;
    },

    showUnit: function (evt) {
        "use strict";
        if (!this.$el.hasClass("active")) {
            this.render();
        }
    }
});

MOOC.views.unitViews = {};

MOOC.views.KnowledgeQuantum = Backbone.View.extend({
    render: function () {
        "use strict";
        return this;
    }
});

MOOC.views.kqViews = {};