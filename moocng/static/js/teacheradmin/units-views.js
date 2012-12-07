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
                if (options.style) {
                    result += " style='" + options.style + "'";
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
                options = { classes: "" };
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
        },

        truncate = function (text) {
            if (text.length === 0) {
                return MOOC.trans.nothing;
            } else {
                return text.substring(0, 100) + "...";
            }
        };

    MOOC.views = {
        List: Backbone.View.extend({
            events: {},

            render: function () {
                var node = this.$el;
                node.html("");
                this.model.each(function (unit) {
                    var view = MOOC.views.unitViews[unit.get("id")],
                        el = $("<div class='unit'></div>")[0];
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
                html = inlineb({ classes: "drag-handle" });
                html += inlineb(block(header),
                                block("", { classes: "kq-containter" }),
                                block("<button class='btn pull-right'><i class='icon-plus'></i></button>"),
                                { classes: "unit-right" });
                node.html(html);

                node = node.find(".kq-containter");
                this.model.get("knowledgeQuantumList").each(function (kq) {
                    var view = MOOC.views.kqViews[kq.get("id")],
                        el = $("<div class='kq'></div>")[0];
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
                    header += "<span class='badge badge-inverse question pull-right'><i class='icon-white icon-question-sign'></i></span>";
                }

                iframe = "<iframe width='110px' height='71px' src='//www.youtube.com/embed/" +
                    this.model.get("videoID") + "?rel=0&controls=0&origin=" +
                    MOOC.host + "' frameborder='0'></iframe>";

                data = "<p>" + MOOC.trans.kq.teacher_comments + ": " +
                    truncate(_.escape(this.model.get("teacher_comments"))) + "</p>" +
                    "<p>" + MOOC.trans.kq.supplementary_material + ": " +
                    truncate(_.escape(this.model.get("supplementary_material"))) + "<p/>";

                html = inlineb({ classes: "drag-handle" }) +
                    inlineb(iframe, { style: "margin-left: 30px;" }) +
                    inlineb(block(header), block(data), { classes: "kq-right" });

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