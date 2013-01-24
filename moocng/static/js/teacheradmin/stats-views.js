/*jslint vars: false, browser: true, nomen: true */
/*global MOOC:true, _, jQuery, Backbone */

// Copyright 2013 Rooter Analysis S.L.
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

(function ($, Backbone, _) {
    "use strict";

    MOOC.views = {};

    MOOC.views.Course = Backbone.View.extend({
        events: {},

        initialize: function () {
            _.bindAll(this, "render", "destroy");
        },

        render: function () {
            // TODO
        },

        destroy: function () {
            // TODO
        }
    });

    MOOC.views.Unit = Backbone.View.extend({
        events: {},

        initialize: function () {
            _.bindAll(this, "render", "destroy");
        },

        render: function () {
            // TODO
        },

        destroy: function () {
            // TODO
        }
    });

    MOOC.views.KnowledgeQuantum = Backbone.View.extend({
        events: {},

        initialize: function () {
            _.bindAll(this, "render", "destroy");
        },

        render: function () {
            // TODO
        },

        destroy: function () {
            // TODO
        }
    });

}(jQuery, Backbone, _));