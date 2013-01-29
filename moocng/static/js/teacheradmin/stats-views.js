/*jslint vars: false, browser: true, nomen: true */
/*global MOOC:true, _, jQuery, Backbone, d3, nv */

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

(function ($, Backbone, _, d3, nv) {
    "use strict";

    var renderPie = function (viewport, labels, values, key) {
            var data = _.zip(labels, values);
            if (_.isUndefined(key)) {
                key = "";
            }
            nv.addGraph(function () {
                var chart = nv.models.pieChart()
                    .x(function (d) { return d[0]; }) // label
                    .y(function (d) { return d[1]; }) // value
                    .showLegend(true)
                    .showLabels(false);

                d3.select(viewport).append("svg")
                    .datum([{
                        key: key,
                        values: data
                    }]).transition().duration(1200)
                    .call(chart);

                nv.utils.windowResize(chart.update);
                return chart;
            });
        },

        renderBar = function (viewport, labels, values, key) {
            var data = _.zip(labels, values);
            if (_.isUndefined(key)) {
                key = "";
            }
            nv.addGraph(function () {
                var chart = nv.models.discreteBarChart()
                    .x(function (d) { return d[0]; }) // label
                    .y(function (d) { return d[1]; }) // value
                    .staggerLabels(false)
                    .tooltips(true)
                    .showValues(true);

                d3.select(viewport).append("svg")
                    .datum([{
                        key: key,
                        values: data
                    }]).transition().duration(750)
                    .call(chart);

                nv.utils.windowResize(chart.update);
                return chart;
            });
        },

        renderMultiBar = function (viewport, data) {
            nv.addGraph(function () {
                var chart = nv.models.multiBarChart();

                d3.select(viewport).append("svg")
                    .datum(data)
                    .transition().duration(750)
                    .call(chart);

                nv.utils.windowResize(chart.update);
                return chart;
            });
        };

    MOOC.views = {};

    MOOC.views.Course = Backbone.View.extend({
        events: {},

        initialize: function () {
            _.bindAll(this, "render", "destroy");
            this.template = $("#course-tpl").text();
        },

        render: function () {
            var data = this.model.getData();
            this.$el.html(this.template);

            if (!_.isUndefined(data.passed)) {
                this.$el.find("#passed").removeClass("hide");
                renderPie(
                    this.$el.find("#passed .viewport")[0],
                    [MOOC.trans.course.notPassed, MOOC.trans.course.passed],
                    [data.enrolled - data.passed, data.passed]
                );
            } else {
                // Just two pies
                this.$el.find("#started").removeClass("span3").addClass("span5");
                this.$el.find("#completed").removeClass("span3").addClass("span5");
            }

            renderPie(
                this.$el.find("#started .viewport")[0],
                [MOOC.trans.course.notStarted, MOOC.trans.course.started],
                [data.enrolled - data.started, data.started]
            );

            renderPie(
                this.$el.find("#completed .viewport")[0],
                [MOOC.trans.course.notCompleted, MOOC.trans.course.completed],
                [data.enrolled - data.completed, data.completed]
            );

            renderBar(
                this.$el.find("#tendencies .viewport")[0],
                [MOOC.trans.course.enrolled, MOOC.trans.course.started, MOOC.trans.course.completed, MOOC.trans.course.passed],
                [data.enrolled, data.started, data.completed, data.passed]
            );

            data = [{
                key: MOOC.trans.course.started,
                values: []
            }, {
                key: MOOC.trans.course.completed,
                values: []
            }, {
                key: MOOC.trans.course.passed,
                values: []
            }];

            this.model.get("units").each(function (unit, idx) {
                data[0].values.push({
                    x: unit.get("title"),
                    y: unit.get("started")
                });
                data[1].values.push({
                    x: unit.get("title"),
                    y: unit.get("completed")
                });
                data[2].values.push({
                    x: unit.get("title"),
                    y: unit.get("passed")
                });
            });

            renderMultiBar(this.$el.find("#units .viewport")[0], data);
        },

        destroy: function () {
            this.$el.html("");
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

}(jQuery, Backbone, _, d3, nv));