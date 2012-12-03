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

MOOC.models = {};

MOOC.models.Activity = Backbone.Model.extend({
    defaults: {
        kqs: []
    },

    url: function () {
        "use strict";
        return MOOC.ajax.getAbsoluteUrl('activity/') + this.get('id') + '/';
    },

    addKQ: function (kq, callback) {
        "use strict";
        if (!_.include(this.get('kqs'), kq)) {
            this.set('kqs', _.union(this.get('kqs'), [kq]));
            if (_.isUndefined(callback)) {
                this.save();
            } else {
                this.save("kqs", this.get("kqs"), { success: callback });
            }
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

    /**
     * Returns:
     *  true if correct
     *  false if incorrect
     *  undefined if can't be corrected yet, because the deadline hasn't been
     *               reached, there is no solution data
     */
    isCorrect: function (reply) {
        "use strict";
        var solution = this.get('solution'),
            optiontype = this.get('optiontype'),
            result;

        if (_.isUndefined(solution) || _.isNull(solution)) {
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

    /**
     * Returns:
     *  true if correct
     *  false if incorrect
     *  undefined if can't be corrected yet, because the deadline hasn't been
     *               reached, there is no solution data
     */
    isCorrect: function () {
        "use strict";
        var answer = this.get("answer"),
            unknown = false,
            correct = false;

        if (_.isUndefined(answer) || _.isNull(answer)) { return; }

        unknown = this.get('optionList').any(function (opt) {
            return _.isUndefined(opt.isCorrect(answer.getReply(opt.get('id'))));
        });
        if (unknown) { return; }

        return this.get('optionList').all(function (opt) {
            return opt.isCorrect(answer.getReply(opt.get('id')));
        });
    },

    isActive: function () {
        "use strict";
        var id = this.id,
            unit;

        unit = MOOC.models.course.find(function (u) {
            var knowledgeQuantumList = u.get("knowledgeQuantumList");
            if (_.isNull(knowledgeQuantumList)) { return false; }
            return knowledgeQuantumList.any(function (kq) {
                var url = kq.get("question");
                if (_.isNull(url)) { return false; }
                url = url.split('/');
                url = url[url.length - 2];
                return url === id;
            });
        });

        if (!_.isUndefined(unit) && unit.get("type") !== 'n' && this.has("solution")) {
            return false;
        }
        return true;
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

MOOC.models.Attachment = Backbone.Model.extend({
    defaults: function () {
        "use strict";
        return {
            url: null
        };
    }
});

MOOC.models.AttachmentList = Backbone.Collection.extend({
    model: MOOC.models.Attachment
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
            correct: null,
            attachmentList: null,
            normalized_weight: 0
        };
    },

    truncateTitle: function (maxLength) {
        "use strict";
        var title = this.get("title"),
            idx;

        if (title.length > maxLength) {
            title = title.substr(0, maxLength);
            idx = title.lastIndexOf(' ');
            if (idx > 0) {
                title = title.substring(0, idx);
            } else {
                title = title.substring(0, maxLength - 3);
            }
            title += "...";
        }
        return title;
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
            title: "",
            type: ''
        };
    },

    url: function () {
        "use strict";
        return MOOC.ajax.getAbsoluteUrl("unit/") + this.get("id") + "/";
    },

    parse: function (resp, xhr) {
        "use strict";
        return {
            id: parseInt(resp.id, 10),
            order: resp.order,
            title: resp.title,
            type: resp.unittype
        };
    },

    calculateProgress: function (conditions) {
        "use strict";
        var kqs = this.get("knowledgeQuantumList").length,
            progress = this.get("knowledgeQuantumList").where(conditions),
            result = 0;

        _.each(progress, function (kq) {
            result += kq.get("normalized_weight");
        });

        if (!_.isNumber(result) || _.isNaN(result)) {
            result = 0;
        }
        return result;
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
    },

    url: function () {
        "use strict";
        return MOOC.ajax.getAbsoluteUrl("unit/");
    },

    parse: function (resp, xhr) {
        "use strict";
        return resp.objects;
    }
});

MOOC.models.course = new MOOC.models.UnitList();
