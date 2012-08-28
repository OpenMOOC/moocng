/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _ */

if (_.isUndefined(window.MOOC)) {
    window.MOOC = {};
}

MOOC.models = {};

MOOC.models.Activity = Backbone.Model.extend({
    defaults: {
        kqs: []
    },

    url: function () {
        "use strict";
        return MOOC.ajax.getAbsoluteUrl('activity/') + this.get('id') + '/';
    },

    addKQ: function (kq) {
        "use strict";
        if (!_.include(this.get('kqs'), kq)) {
            this.set('kqs', _.union(this.get('kqs'), [kq]));
            this.save();
        }
    },

    hasKQ: function (kq) {
        "use strict";
        return _.include(this.get('kqs'), String(kq));
    }
});

MOOC.models.Option = Backbone.Model.extend({
    defaults: function () {
        "use strict";
        return {
            optiontype: 't',
            x: 0,
            y: 0,
            width: 100,
            height: 12,
            solution: null
        };
    },

    isCorrect: function (reply) {
        "use strict";
        var solution = this.get('solution'),
            optiontype = this.get('optiontype'),
            result;

        if (_.isUndefined(solution) || solution === null) {
            return;
        }

        if (optiontype === 't') {
            result = solution === reply.get('value');
        } else {
            if (solution === 'True') {
                result = reply.get('value') === true;
            } else {
                result = reply.get('value') === false;
            }
        }

        return result;
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
            optionList: null,
            answer: null
        };
    },

    isCorrect: function () {
        "use strict";
        var answer = this.get("answer");
        if (_.isUndefined(answer) || answer === null) {
            return;
        }

        return this.get('optionList').all(function (opt) {
            return opt.isCorrect(answer.getReply(opt.get('id')));
        });
    }
});

/* An answer is a student submission to a question */
MOOC.models.Answer = Backbone.Model.extend({
    defaults: {
        date: null,
        replyList: null
    },

    /* Return a reply which option is opt_id or null otherwise */
    getReply: function (opt_id) {
        "use strict";
        var replies = this.get('replyList'),
            result = null;
        if (replies) {
            result = replies.find(function (reply) {
                return reply.get('option') === opt_id;
            });
        }
        return result;
    }
});

/* A reply is a student value for an option */
MOOC.models.Reply = Backbone.Model.extend({
    defaults: {
        option: null,
        value: null
    }
});

MOOC.models.ReplyList = Backbone.Collection.extend({
    model: MOOC.models.Reply
});

MOOC.models.KnowledgeQuantum = Backbone.Model.extend({
    defaults: function () {
        "use strict";
        return {
            order: -1,
            title: null,
            videoID: null,
            teacher_comments: null,
            supplementary_material: null,
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
            if (_.isNull(kq)) {
                return false;
            }
            kq = kq.get(kqID);
            return !_.isUndefined(kq);
        });
    }
});

MOOC.models.course = new MOOC.models.UnitList();
