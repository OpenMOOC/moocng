/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _ */

if (typeof MOOC === 'undefined') {
    window.MOOC = {};
}

MOOC.models = {};

MOOC.models.Option = Backbone.Model.extend({
    defaults: function () {
        "use strict";
        return {
            optiontype: null,
            x: null,
            y: null,
            answer: null,
            lastAnswerDate: null
        };
    }
});

MOOC.models.OptionList  = Backbone.Collection.extend({
    model: MOOC.models.Option
});

MOOC.models.Question = Backbone.Model.extend({
    defaults: function () {
        "use strict";
        return {
            lastFrame: null, // of the KnowledgeQuantum's video
            solution: null,
            optionList: null
        };
    }
});

MOOC.models.KnowledgeQuantum = Backbone.Model.extend({
    defaults: function () {
        "use strict";
        return {
            order: -1,
            title: null,
            videoID: null,
            question: null, // Optional
            questionInstance: null,
            completed: false,
            correct: null
        };
    }
});

MOOC.models.KnowledgeQuantumList  = Backbone.Collection.extend({
    model: MOOC.models.KnowledgeQuantum,

    comparator: function (kq) {
        "use strict";
        return kq.get("order");
    },

    getByPosition: function (position) {
        "use strict";
        return this.find(function (kq) {
            return position === kq.get("order");
        });
    }
});

MOOC.models.Unit = Backbone.Model.extend({
    defaults: function () {
        "use strict";
        return {
            order: -1,
            knowledgeQuantumList: null,
            title: ""
        };
    },

    calculateProgress: function (conditions) {
        "use strict";
        var kqs = this.get("knowledgeQuantumList").length,
            progress = this.get("knowledgeQuantumList").where(conditions);
        return (progress.length * 100) / kqs;
    }
});

MOOC.models.UnitList = Backbone.Collection.extend({
    model: MOOC.models.Unit,

    getByKQ: function (kqID) {
        "use strict";
        return this.find(function (unit) {
            var kq = unit.get("knowledgeQuantumList");
            if (kq === null) {
                return false;
            }
            kq = kq.get(kqID);
            return typeof kq !== "undefined";
        });
    }
});

MOOC.models.course = new MOOC.models.UnitList();
