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
        var html = '<iframe width="770" height="433" src="';
        html += 'http://www.youtube.com/embed/' + this.model.get("videoID");
        html += '" frameborder="0" allowfullscreen></iframe>';
        $("#kq-video").html(html);

        this.$el.parent().children().removeClass("active");
        this.$el.addClass("active");

        return this;
    }
});

MOOC.views.kqViews = {};