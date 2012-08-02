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
        // TODO
    }
});

MOOC.views.unitViews = {};

MOOC.views.KnowledgeQuantum = Backbone.View.extend({
//         html = '<iframe width="770" height="433" src="';
//         html += 'http://www.youtube.com/embed/' + kq.get("videoID");
//         html += '" frameborder="0" allowfullscreen></iframe>';
//         $("#kq-video").html(html);
});