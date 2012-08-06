/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _ */

if (typeof MOOC === 'undefined') {
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
            progress;
        this.$el.parent().children().removeClass("active");
        this.$el.addClass("active");

        $("#unit-title").html(this.model.get("title"));

        html = '<div class="progress progress-info"><div class="bar complete" style="width: 0%;"></div></div>';
        html += '<div class="progress progress-success"><div class="bar correct" style="width: 0%;"></div></div>';
        $("#unit-progress").html(html);
        progress = this.model.calculateProgress();
        $("#unit-progress").find("div.bar.complete").css("width", progress + "%");
        $("#unit-progress").find("div.bar.correct").css("width", (progress - 24) + "%");

        html = '';
        this.model.get("knowledgeQuantumList").each(function (kq) {
            html += "<li><b>" + kq.get("title") + "</b></li>";
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