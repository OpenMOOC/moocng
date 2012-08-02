/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _ */

if (typeof MOOC === 'undefined') {
    window.MOOC = {};
}

MOOC.models = {};

MOOC.models.KnowledgeQuantum = Backbone.Model.extend({
    defaults: function () {
        "use strict";
        return {
            title: null,
            videoID: null
        };
    }
});

MOOC.models.KnowledgeQuantumList  = Backbone.Collection.extend({
    model: MOOC.models.KnowledgeQuantum
});

MOOC.models.Unit = Backbone.Model.extend({
    defaults: function () {
        "use strict";
        return {
            order: -1,
            knowledgeQuantumList: null
        };
    }
});

MOOC.models.UnitList = Backbone.Collection.extend({
    model: MOOC.models.Unit
});

MOOC.models.course = new MOOC.models.UnitList();

MOOC.models.init = function () {
    "use strict";
    $("#unit-selector div.collapse").each(function (idx, node) {
        var id = node.id.split("unit")[1];
        MOOC.models.course.add(new MOOC.models.Unit({
            order: idx,
            id: parseInt(id, 10)
        }));
    });
};