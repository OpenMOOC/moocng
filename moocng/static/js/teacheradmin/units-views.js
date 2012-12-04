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

    var block = function () {
            var result = "<div",
                chunkList = _.toArray(arguments),
                options = _.last(chunkList);
            if (_.isObject(options)) {
                chunkList = _.initial(chunkList);
                if (options.classes) {
                    result += " class='" + options.classes + "'";
                }
            }
            result += ">";
            _.each(chunkList, function (chunk) {
                result += chunk;
            });
            return result + "</div>";
        },

        inlineb = function () {
            var chunkList = _.toArray(arguments),
                options = {
                    classes: ""
                };
            if (_.isObject(_.last(chunkList))) {
                options = _.last(chunkList);
                chunkList = _.initial(chunkList);
                if (_.isUndefined(options.classes)) {
                    options.classes = "";
                }
            }
            options.classes += " inlineb";
            chunkList.push(options);
            return block.apply(null, chunkList);
        };

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
                    header,
                    html;

                header = "<h3>" + this.model.get("title") + "</h3>" +
                    "<button class='btn pull-right'><i class='icon-edit'></i></button>";
                html = inlineb("<span class='drag-handle'></span>");
                html += inlineb(block(header),
                                block("", { classes: "kq-containter" }),
                                block("<button class='btn pull-right'><i class='icon-plus'></i></button>"),
                                { classes: "wide" });
                node.html(html);

                node = node.find(".kq-containter");
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
                var html,
                    header,
                    iframe,
                    data;

                header = "<h4>" + this.model.get("title") + "</h4><button class='btn pull-right'><i class='icon-edit'></i></button>";
                if (this.model.has("question")) {
                    header += "<span class='badge badge-inverse pull-right'><i class='icon-white icon-question-sign'></i></span>";
                }

                iframe = "<iframe width='110px' height='65px' src='//www.youtube.com/embed/" +
                    this.model.get("videoID") + "?rel=0&controls=0&origin=" +
                    MOOC.host + "' frameborder='0'></iframe>";

                data = ""; // TODO

                html = inlineb("<span class='drag-handle'></span>");
                html += inlineb(block(header), inlineb(inlineb(iframe), inlineb(data)), { classes: "wide" });

                this.$el.html(html);
            }
        }),
        kqViews: {},

        UnitEditor: Backbone.View.extend({}),
        unitEditorViews: {},

        KQEditor: Backbone.View.extend({}),
        kqEditorViews: {}
    };
}(jQuery, Backbone, _));