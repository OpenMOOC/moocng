/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _ */

if (typeof MOOC === 'undefined') {
    window.MOOC = {};
}

MOOC.views = {};

MOOC.views.Unit = Backbone.View.extend({
    events: {
        "click li.kq": "showKQ"
    },

    render: function () {
        "use strict";
        var html = '<div class="accordion-inner"><ol>';
        this.model.get("knowledgeQuantumList").each(function (kq) {
            html += '<li id="kq' + kq.get("id") + '" class="kq">' + kq.get("title") + '</li>';
        });
        html += '</ol></div>';
        this.$el.html(html);
        return this;
    },

    showKQ: function (evt) {
        "use strict";
        var kq = evt.target.id.split("kq")[1];
        MOOC.router.navigate(this.id + "/kq" + kq, { trigger: true });
    }
});

MOOC.views.unitViews = {};

MOOC.views.KnowledgeQuantum = Backbone.View.extend({
    render: function () {
        "use strict";
        var width = $("#kq-video").css("width"),
            height,
            html,
            unit,
            order,
            kq;

        if (width.indexOf('p') > 0) {
            width = parseInt(width.split('p')[0], 10);
        } else {
            width = parseInt(width, 10);
        }

        height = Math.round((width * 6) / 10);

        html = '<iframe width="100%" height="' + height + '" src="';
        html += 'http://www.youtube.com/embed/' + this.model.get("videoID");
        html += '" frameborder="0" allowfullscreen></iframe>';
        $("#kq-video").html(html);
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
    }
});

MOOC.views.kqViews = {};