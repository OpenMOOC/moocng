/*jslint vars: false, browser: true, nomen: true */
/*global MOOC:true, _, jQuery, Backbone, d3, nv */

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

(function ($, Backbone, _, d3, nv) {
    "use strict";

    var renderPie = function (viewport, labels, values) {
            var data = [];
            _.each(labels, function (label, index) {
                data.push({
                    key: label,
                    y: values[index]
                });
            });
            nv.addGraph(function () {
                var chart = nv.models.pieChart()
                        .x(function (d) { return d.key; }) // label
                        .y(function (d) { return d.y; }) // value
                        .showLegend(true)
                        .showLabels(true)
                        .labelType("percent")
                        .pieLabelsOutside(false)
                        .labelThreshold(.02);

                d3.select(viewport).append("svg")
                    .datum(data)
                    .transition().duration(1200)
                    .call(chart);

                nv.utils.windowResize(chart.update);

                chart.pie.dispatch.on("elementClick", function(e) {
                    var label = e.label.replace(' ','-').toLowerCase();
                    var href = $('#'+label).attr('href');
                    if (href)
                        window.location.href=href;
                });

                return chart;
            });
        },

        renderMultiBar = function (viewport, data, callback) {
            nv.addGraph(function () {
                var chart = nv.models.multiBarChart();

                if (!_.isUndefined(callback)) {
                    chart = callback(chart);
                }

                d3.select(viewport).append("svg")
                    .datum(data)
                    .transition().duration(750)
                    .call(chart);

                nv.utils.windowResize(chart.update);
                return chart;
            });
        },

        renderLine = function (viewport, data, yDomain, callback) {
            nv.addGraph(function () {
                var chart = nv.models.lineChart(),
                    showLegend = true;

                if (data.length === 1) {
                    showLegend = false;
                }

                chart = chart.showLegend(showLegend)
                    .yDomain(yDomain);
                if (!_.isUndefined(callback)) {
                    chart = callback(chart);
                }

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
        initialize: function () {
            _.bindAll(this, "render", "destroy");
            this.template = _.template($("#course-tpl").text());
        },

        render: function () {
            var data = this.model.getData(),
                chartData,
                unitsNav,
                aux;
            this.$el.html(this.template(this.model.toJSON()));

            if (!_.isUndefined(data.passed)) {
                this.$el.find("#passed").removeClass("hide");
                renderPie(
                    this.$el.find("#passed .viewport")[0],
                    [MOOC.trans.notPassed, MOOC.trans.passed],
                    [data.enrolled - data.passed, data.passed]
                );
            } else {
                // Just two pies
                this.$el.find("#started").removeClass("span3").addClass("span5");
                this.$el.find("#completed").removeClass("span3").addClass("span5");
            }

            renderPie(
                this.$el.find("#started .viewport")[0],
                [MOOC.trans.notStarted, MOOC.trans.started],
                [data.enrolled - data.started, data.started]
            );

            renderPie(
                this.$el.find("#completed .viewport")[0],
                [MOOC.trans.notCompleted, MOOC.trans.completed],
                [data.enrolled - data.completed, data.completed]
            );

            chartData = [{
                key: MOOC.trans.evolution,
                values: [
                    { x: 0, y: data.enrolled },
                    { x: 1, y: data.started }
                ]
            }];

            // If the course has no threshold then there is no passed field
            if (!_.isUndefined(data.passed)) {
                chartData[0].values.push({ x: 2, y: data.passed });
            }

            chartData[0].values.push({ x: 3, y: data.completed });

            aux = {
                0: MOOC.trans.enrolled,
                1: MOOC.trans.started,
                2: MOOC.trans.passed,
                3: MOOC.trans.completed
            };

            renderLine(
                this.$el.find("#tendencies .viewport")[0],
                chartData,
                [0, data.enrolled],
                function (chart) {
                    chart.xAxis
                        .tickSubdivide(false)
                        .tickFormat(function (t) {
                            return aux[t];
                        })
                        .rotateLabels(-30);
                    return chart;
                }
            );

            chartData = [{
                key: MOOC.trans.started,
                values: []
            }, {
                key: MOOC.trans.completed,
                values: []
            }];

            // If the course doesn't have a passed field then the units doesn't
            // have it either
            if (!_.isUndefined(data.passed)) {
                chartData.push({
                    key: MOOC.trans.passed,
                    values: []
                });
            }

            unitsNav = this.$el.find("#units-navigation");

            this.model.get("units").each(function (unit, idx) {
                var title = unit.get("title");

                chartData[0].values.push({
                    x: title,
                    y: unit.get("started")
                });
                chartData[1].values.push({
                    x: title,
                    y: unit.get("completed")
                });
                if (chartData.length > 2) {
                    chartData[2].values.push({
                        x: title,
                        y: unit.get("passed")
                    });
                }

                unitsNav.append("<li><a href='#unit" + unit.get("id") + "'>" + MOOC.trans.unit + " " + idx + ": " + title + "</a></li>");
            });

            if (unitsNav.find("li").length === 0) {
                unitsNav.prev().addClass("disabled").click(function (evt) {
                    evt.preventDefault();
                    evt.stopPropagation();
                });
            }

            renderMultiBar(
                this.$el.find("#units .viewport")[0],
                chartData,
                function (chart) {
                    chart.xAxis.tickFormat(function (t) {
                        if (t.length > 15) {
                            return t.substring(0, 12) + "...";
                        }
                        return t;
                    });
                    return chart;
                }
            );
        },

        destroy: function () {
            this.$el.html("");
        }
    });

    MOOC.views.Students = Backbone.View.extend({
        initialize: function () {
            _.bindAll(this, "render", "destroy");
            this.template = _.template($("#students-tpl").text());
        },

        render: function () {
            var data = this.model.getData(),
                chartData,
                unitsNav,
                aux;
            this.$el.html(this.template(this.model.toJSON()));

            if (!_.isUndefined(data.passed)) {
                this.$el.find("#passed").removeClass("hide");
                renderPie(
                    this.$el.find("#passed .viewport")[0],
                    [MOOC.trans.notPassed, MOOC.trans.passed],
                    [data.enrolled - data.passed, data.passed]
                );
            } else {
                // Just two pies
                this.$el.find("#started").removeClass("span3").addClass("span5");
                this.$el.find("#completed").removeClass("span3").addClass("span5");
            }

            renderPie(
                this.$el.find("#started .viewport")[0],
                [MOOC.trans.notStarted, MOOC.trans.started],
                [data.enrolled - data.started, data.started]
            );

            renderPie(
                this.$el.find("#completed .viewport")[0],
                [MOOC.trans.notCompleted, MOOC.trans.completed],
                [data.enrolled - data.completed, data.completed]
            );

            var countryValues = Object.keys(data.byCountry).map(function (key) {
                return data.byCountry[key];
            });
            renderPie(
                this.$el.find("#country .viewport")[0],
                Object.keys(data.byCountry),
                countryValues
            );

            var languageValues = Object.keys(data.byLanguage).map(function (key) {
                return data.byLanguage[key];
            });
            renderPie(
                this.$el.find("#language .viewport")[0],
                Object.keys(data.byLanguage),
                languageValues
            );

            var genderValues = Object.keys(data.byGender).map(function (key) {
                return data.byGender[key];
            });
            renderPie(
                this.$el.find("#gender .viewport")[0],
                Object.keys(data.byGender),
                genderValues
            );

            var ageValues = Object.keys(data.byAge).map(function (key) {
                return data.byAge[key];
            });
            renderPie(
                this.$el.find("#age .viewport")[0],
                Object.keys(data.byAge),
                ageValues
            );

            var map = L.map('map').setView([50, 0], 3);
            var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
            var osmAttrib='Map data © <a href="http://openstreetmap.org" target="_blank">OpenStreetMap</a> contributors';
            L.tileLayer(osmUrl, {minZoom: 1, maxZoom: 14, attribution: osmAttrib}).addTo(map);
            var markers = new L.MarkerClusterGroup();
            for (var i in data.byLocations){
                markers.addLayer(new L.Marker(new L.LatLng(data.byLocations[i].lat, data.byLocations[i].lon)));
            }
            map.addLayer(markers);
        },

        destroy: function () {
            this.$el.html("");
        }
    });

    MOOC.views.Teachers = Backbone.View.extend({
        initialize: function () {
            _.bindAll(this, "render", "destroy");
            this.template = _.template($("#teachers-tpl").text());
        },

        render: function () {
            var data = this.model.getData(),
                chartData,
                unitsNav,
                aux;
            this.$el.html(this.template(this.model.toJSON()));

            var countryValues = Object.keys(data.byCountry).map(function (key) {
                return data.byCountry[key];
            });
            renderPie(
                this.$el.find("#country .viewport")[0],
                Object.keys(data.byCountry),
                countryValues
            );

            var languageValues = Object.keys(data.byLanguage).map(function (key) {
                return data.byLanguage[key];
            });
            renderPie(
                this.$el.find("#language .viewport")[0],
                Object.keys(data.byLanguage),
                languageValues
            );

            var genderValues = Object.keys(data.byGender).map(function (key) {
                return data.byGender[key];
            });
            renderPie(
                this.$el.find("#gender .viewport")[0],
                Object.keys(data.byGender),
                genderValues
            );

            var ageValues = Object.keys(data.byAge).map(function (key) {
                return data.byAge[key];
            });
            renderPie(
                this.$el.find("#age .viewport")[0],
                Object.keys(data.byAge),
                ageValues
            );

            var orgValues = Object.keys(data.byOrganization).map(function (key) {
                return data.byOrganization[key];
            });
            renderPie(
                this.$el.find("#organization .viewport")[0],
                Object.keys(data.byOrganization),
                orgValues
            );
        },

        destroy: function () {
            this.$el.html("");
        }
    });

    MOOC.views.Unit = Backbone.View.extend({
        initialize: function () {
            _.bindAll(this, "render", "destroy");
            this.template = $("#unit-tpl").text();
        },

        render: function () {
            this.$el.html(this.template);
            var data = this.model.getData(),
                self = this,
                kqsNav,
                chartData,
                aux;

            aux = this.$el.find("#unit-title");
            aux.text(aux.text() + this.model.get("title"));

            if (!_.isUndefined(data.passed)) {
                this.$el.find("#passed").removeClass("hide");
                renderPie(
                    this.$el.find("#passed .viewport")[0],
                    [MOOC.trans.notPassed, MOOC.trans.passed],
                    [data.started - data.passed, data.passed]
                );
            } else {
                // Just one pies
                this.$el.find("#completed").removeClass("span5").addClass("span10");
            }

            renderPie(
                this.$el.find("#completed .viewport")[0],
                [MOOC.trans.notCompleted, MOOC.trans.completed],
                [data.started - data.completed, data.completed]
            );

            chartData = [{
                key: MOOC.trans.evolution,
                values: [
                    { x: 0, y: data.started },
                    { x: 1, y: data.completed }
                ]
            }];

            if (!_.isUndefined(data.passed)) {
                chartData[0].values.push({ x: 2, y: data.passed });
            }

            aux = {
                0: MOOC.trans.started,
                1: MOOC.trans.completed,
                2: MOOC.trans.passed
            };

            renderLine(
                this.$el.find("#tendencies .viewport")[0],
                chartData,
                [0, data.started],
                function (chart) {
                    chart.xAxis
                        .tickSubdivide(false)
                        .tickFormat(function (t) {
                            return aux[t];
                        })
                        .rotateLabels(-30);
                    return chart;
                }
            );

            chartData = [{
                key: MOOC.trans.viewed,
                values: []
            }, {
                key: MOOC.trans.submitted,
                values: []
            }, {
                key: MOOC.trans.passed,
                values: []
            }];

            kqsNav = this.$el.find("#kqs-navigation");

            this.model.get("kqs").each(function (kq, idx) {
                var title = kq.get("title"),
                    kqId = kq.get("id"),
                    aux;

                kq = kq.getData();

                chartData[0].values.push({
                    x: title,
                    y: kq.viewed
                });

                // Some kqs doesn't have a question
                aux = kq.submitted;
                if (_.isUndefined(aux)) {
                    aux = 0;
                }
                chartData[1].values.push({
                    x: title,
                    y: aux
                });

                // Some kqs doesn't have a question
                aux = kq.passed;
                if (_.isUndefined(aux)) {
                    aux = 0;
                }
                chartData[2].values.push({
                    x: title,
                    y: aux
                });

                if (!_.isUndefined(kq.submitted)) {
                    kqsNav.append("<li><a href='#unit" + self.model.get("id") + "/kq" + kqId + "'>" + MOOC.trans.nugget + " " + idx + ": " + title + "</a></li>");
                }
            });

            if (kqsNav.find("li").length === 0) {
                kqsNav.prev().addClass("disabled").click(function (evt) {
                    evt.preventDefault();
                    evt.stopPropagation();
                });
            }

            renderMultiBar(
                this.$el.find("#kqs .viewport")[0],
                chartData,
                function (chart) {
                    chart.xAxis.tickFormat(function (t) {
                        if (t.length > 15) {
                            return t.substring(0, 12) + "...";
                        }
                        return t;
                    });
                    return chart;
                }
            );
        },

        destroy: function () {
            this.$el.html("");
        }
    });

    MOOC.views.KnowledgeQuantum = Backbone.View.extend({
        initialize: function () {
            _.bindAll(this, "render", "destroy");
            this.template = $("#kq-tpl").text();
        },

        render: function () {
            this.$el.html(this.template);
            var data = this.model.getData(),
                chartData,
                aux,
                labels;

            this.$el.find("#go-back").attr("href", "#unit" + this.model.collection.unit.get("id"));

            aux = this.$el.find("#kq-title");
            aux.text(aux.text() + this.model.get("title"));

            renderPie(
                this.$el.find("#submitted .viewport")[0],
                [MOOC.trans.notSubmitted, MOOC.trans.submitted],
                [data.viewed - data.submitted, data.submitted]
            );

            if (!_.isUndefined(data.passed)) {
                this.$el.find("#submitted").removeClass("span10").addClass("span5");
                this.$el.find("#passed").removeClass("hide");
                renderPie(
                    this.$el.find("#passed .viewport")[0],
                    [MOOC.trans.notPassed, MOOC.trans.passed],
                    [data.viewed - data.passed, data.passed]
                );
            }

            aux = [
                { x: 0, y: data.viewed },
                { x: 1, y: data.submitted }
            ];
            labels = {
                0: MOOC.trans.viewed,
                1: MOOC.trans.submitted
            };
            if (!_.isUndefined(data.reviewers)) {
                aux.push({ x: aux.length, y: data.reviewers });
                labels[aux.length - 1] = MOOC.trans.reviewers;
            }
            if (!_.isUndefined(data.passed)) {
                aux.push({ x: aux.length, y: data.passed });
                labels[aux.length - 1] = MOOC.trans.passed;
            }

            chartData = [{
                key: MOOC.trans.evolution,
                values: aux
            }];

            renderLine(
                this.$el.find("#tendencies .viewport")[0],
                chartData,
                [0, data.viewed],
                function (chart) {
                    chart.xAxis
                        .tickSubdivide(false)
                        .tickFormat(function (t) {
                            return labels[t];
                        })
                        .rotateLabels(-30);
                    return chart;
                }
            );

            if (!_.isUndefined(data.reviews)) {
                this.$el
                    .find("#tendencies")
                        .find(".viewport").addClass("mb20").end()
                        .find("#reviews").removeClass("hide")
                            .find("strong").text(data.reviews);
            }
        },

        destroy: function () {
            this.$el.html("");
        }
    });

}(jQuery, Backbone, _, d3, nv));
