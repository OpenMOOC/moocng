/*jslint vars: false, browser: true, nomen: true */
/*global MOOC:true, _, jQuery, Backbone */

// Copyright 2013 UNED
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

    MOOC.models = {};

    MOOC.models.KnowledgeQuantum = Backbone.Model.extend({
        defaults: function () {
            return {
                id: -1,
                title: "",
                passed: -1,
                submitted: -1,
                reviews: -1,
                reviewers: -1,
                viewed: -1
            };
        },

        getData: function () {
            var result = {
                viewed: this.get("viewed")
            };

            if (this.get("submitted") >= 0) {
                result.submitted = this.get("submitted");
            }
            if (this.get("passed") >= 0) {
                result.passed = this.get("passed");
            }
            if (this.get("reviews") >= 0) {
                result.reviews = this.get("reviews");
            }
            if (this.get("reviewers") >= 0) {
                result.reviewers = this.get("reviewers");
            }

            return result;
        }
    });

    MOOC.models.KnowledgeQuantumList = Backbone.Collection.extend({
        model: MOOC.models.KnowledgeQuantum,
        unit: null,

        url: function () {
            if (!_.isNull(this.unit)) {
                return MOOC.ajax.getAbsoluteUrl("kqs/") + "?unit=" + this.unit.get("id");
            }
            return ""; // ERROR
        }
    });

    MOOC.models.Unit = Backbone.Model.extend({
        defaults: function () {
            return {
                id: -1,
                title: "",
                passed: -1,
                started: -1,
                completed: -1,

                kqs: new MOOC.models.KnowledgeQuantumList()
            };
        },

        getData: function () {
            var result = {
                started: this.get("started"),
                completed: this.get("completed")
            };

            if (this.get("passed") >= 0) {
                result.passed = this.get("passed");
            }

            return result;
        },

        initialize: function () {
            this.get("kqs").unit = this;
        },

        getKQByID: function (kqID) {
            kqID = parseInt(kqID, 10);
            return this.get("kqs").find(function (kq) {
                return kq.get("id") === kqID;
            });
        }
    });

    MOOC.models.UnitList = Backbone.Collection.extend({
        model: MOOC.models.Unit,
        url: function () {
            return MOOC.ajax.getAbsoluteUrl("units/");
        }
    });

    MOOC.models.Course = Backbone.Model.extend({
        defaults: function () {
            return {
                enrolled: -1,
                passed: -1,
                started: -1,
                completed: -1,

                slug: undefined,
                units: new MOOC.models.UnitList()
            };
        },

        getData: function () {
            var result = {
                enrolled: this.get("enrolled"),
                started: this.get("started"),
                completed: this.get("completed")
            };

            if (this.get("passed") >= 0) {
                result.passed = this.get("passed");
            }

            return result;
        },

        getUnitByID: function (unitID) {
            unitID = parseInt(unitID, 10);
            return this.get("units").find(function (unit) {
                return unit.get("id") === unitID;
            });
        },

        getKQByID: function (unitID, kqID) {
            var unit = this.getUnitByID(unitID);
            if (_.isUndefined(unit)) {
                return undefined;
            }
            return unit.getKQByID(kqID);
        }
    });

}(jQuery, Backbone, _));
