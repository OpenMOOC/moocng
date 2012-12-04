/*jslint vars: false, browser: true, nomen: true */
/*global MOOC:true, _, jQuery, Backbone */

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

(function ($, Backbone, _) {
    "use strict";

    MOOC.views = {
        List: Backbone.View.extend({
            events: {},

            render: function () {
                var node = this.$el;
                node.html("");
                this.model.each(function (unit) {
                    var view = MOOC.views.unitViews[unit.get("id")],
                        el = $("<p class='unit'></p>")[0];
                    node.append(el);
                    if (_.isUndefined(view)) {
                        view = new MOOC.views.Unit({
                            model: unit,
                            id: "unit" + unit.get("id"),
                            el: el
                        });
                        MOOC.views.unitViews[unit.get("id")] = view;
                    } else {
                        view.set("el", el);
                    }
                    view.render();
                });
                return this;
            }
        }),

        listView: undefined,

        Unit: Backbone.View.extend({
            events: {},

            render: function () {
                var node = this.$el,
                    html;
                html = "<span class='drag-handle'></span><h3>" + this.model.get("title") + "</h3>" +
                    "<button class='btn'><i class='icon-edit'></i></button>" +
                    "<div class='kq-containter'></div>" +
                    "<button class='btn'><i class='icon-plus'></i></button>";
                node.html(html);
                node = node.find("div.kq-containter");
                this.model.get("knowledgeQuantumList").each(function (kq) {
                    var view = MOOC.views.kqViews[kq.get("id")],
                        el = $("<p class='kq'></p>")[0];
                    node.append(el);
                    if (_.isUndefined(view)) {
                        view = new MOOC.views.KQ({
                            model: kq,
                            id: "kq" + kq.get("id"),
                            el: el
                        });
                        MOOC.views.kqViews[kq.get("id")] = view;
                    } else {
                        view.set("el", el);
                    }
                    view.render();
                });
                return this;
            }
        }),

        unitViews: {},

        KQ: Backbone.View.extend({
            events: {},

            render: function () {
                var node = this.$el,
                    html;
                html = "<span class='drag-handle'></span><h4>" + this.model.get("title") + "</h4>" +
                    "<iframe width='110px' height='80px' src='//www.youtube.com/embed/" +
                    this.model.get("videoID") + "?rel=0&controls=0&origin=" +
                    MOOC.host + "' frameborder='0'></iframe>" +
                    "<button class='btn'><i class='icon-edit'></i></button>";
                if (this.model.has("question")) {
                    html += "<span class='badge badge-inverse'><i class='icon-white icon-question-sign'></i></span>";
                }
                html += "<img class='video-thumbnail' />";
                node.html(html);
            }
        }),
        kqViews: {},

        UnitEditor: Backbone.View.extend({}),
        unitEditorViews: {},

        KQEditor: Backbone.View.extend({}),
        kqEditorViews: {}
    };
}(jQuery, Backbone, _));