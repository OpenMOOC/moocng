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
            var result = MOOC.trans.nothing;
            if (text.length > 0) {
                result = text.substring(0, 100) + "...";
            }
            return result;
        },

        sortableOptions = {
            placeholder: "ui-state-highlight",
            handle: ".drag-handle",
            opacity: 0.7
        },

        showAlert = function (id) {
            $("#" + id).removeClass("hide");
            setTimeout(function () {
                $("#" + id).addClass("hide");
            }, MOOC.alertTime);
        };

    MOOC.views = {
        List: Backbone.View.extend({
            events: {
                "click button#addUnit": "addUnit"
            },

            initialize: function () {
                _.bindAll(this, "render", "sortingHandler", "addUnit");
            },

            render: function () {
                var node = this.$el;
                $(".viewport").addClass("hide");
                node.html("");
                this.model.each(function (unit) {
                    var view = MOOC.views.unitViews[unit.get("id")],
                        el = $("<div id='unit" + unit.get("id") + "' class='unit ui-widget ui-widget-content ui-helper-clearfix ui-corner-all'></div>")[0];
                    node.append(el);
                    if (_.isUndefined(view)) {
                        view = new MOOC.views.Unit({
                            model: unit,
                            id: "unit" + unit.get("id"),
                            el: el
                        });
                        MOOC.views.unitViews[unit.get("id")] = view;
                    } else {
                        view.setElement(el);
                    }
                    view.render();
                });
                node.append(block("<button id='addUnit' class='btn' title='" +
                    MOOC.trans.add + " " + MOOC.trans.unit.unit +
                    "'><i class='icon-plus'></i> " + MOOC.trans.add +
                    "</button>", { classes: "mb20 align-right" }));
                $("#units-container").off("sortstop").sortable(sortableOptions)
                    .on("sortstop", this.sortingHandler);
                $("#units-container").removeClass("hide");
                return this;
            },

            sortingHandler: function (evt, ui) {
                if (!ui.item.hasClass("unit")) {
                    return;
                }

                var container = ui.item.parent();
                container.children().each(function (pos, node) {
                    var id = parseInt(node.id.split("unit")[1], 10),
                        view = MOOC.views.unitViews[id];
                    if (view.model.get("order") !== pos + 1) {
                        view.model.save("order", pos + 1);
                    }
                });
            },

            addUnit: function (evt) {
                var unit = new MOOC.models.Unit();
                unit.save(null, {
                    success: function (model, response) {
                        MOOC.models.course.add(model);
                        MOOC.router.navigate("unit" + model.get("id"), {
                            trigger: true
                        });
                    },
                    error: function () {
                        showAlert("generic");
                    }
                });

            }
        }),

        listView: undefined,

        Unit: Backbone.View.extend({
            events: {
                "click button.edit": "toUnitEditor",
                "click button.add": "addKQ"
            },

            initialize: function () {
                _.bindAll(this, "render", "sortingHandler", "toUnitEditor", "addKQ");
            },

            render: function () {
                var node = this.$el,
                    sortOpts,
                    header,
                    add,
                    html;

                header = "<h3>" + this.model.get("title") + "</h3>" +
                    "<button class='btn pull-right edit' title='" + MOOC.trans.edit +
                    " " + MOOC.trans.unit.unit + "'><i class='icon-edit'></i> " +
                    MOOC.trans.edit + "</button>";
                add = "<button class='btn pull-right add' title='" + MOOC.trans.add +
                    " " + MOOC.trans.kq.kq + "'><i class='icon-plus'></i> " +
                    MOOC.trans.add + "</button>";
                html = inlineb({ classes: "drag-handle" });
                html += inlineb(block(header),
                                block("", { classes: "kq-container" }),
                                block(add),
                                { classes: "unit-right" });
                node.html(html);

                node = node.find(".kq-container");
                if (this.model.get("knowledgeQuantumList")) {
                    this.model.get("knowledgeQuantumList").each(function (kq) {
                        var view = MOOC.views.kqViews[kq.get("id")],
                            el = $("<div id='kq" + kq.get("id") + "' class='kq ui-widget ui-widget-content ui-helper-clearfix ui-corner-all'></div>")[0];
                        node.append(el);
                        if (_.isUndefined(view)) {
                            view = new MOOC.views.KQ({
                                model: kq,
                                id: "kq" + kq.get("id"),
                                el: el
                            });
                            MOOC.views.kqViews[kq.get("id")] = view;
                        } else {
                            view.setElement(el);
                        }
                        view.render();
                    });
                }
                sortOpts = _.defaults({
                    connectWith: ".kq-container",
                    dropOnEmpty: true
                }, sortableOptions);
                $(".kq-container").off("sortstop").sortable(sortOpts)
                    .on("sortstop", this.sortingHandler);
                return this;
            },

            sortingHandler: function (evt, ui) {
                if (!ui.item.hasClass("kq")) {
                    return;
                }

                var container = ui.item.parent(),
                    newUnitNode = container.parent().parent(),
                    newUnitID = parseInt(newUnitNode[0].id.split("unit")[1], 10),
                    kqID = parseInt(ui.item[0].id.split("kq")[1], 10),
                    oldUnitObj = MOOC.models.course.getByKQ(kqID),
                    newUnitObj,
                    newUnitKQList,
                    kqObj;

                kqObj = oldUnitObj.get("knowledgeQuantumList").find(function (kq) {
                    return kq.get("id") === kqID;
                });
                oldUnitObj.get("knowledgeQuantumList").remove(kqObj);

                newUnitObj = MOOC.models.course.find(function (unit) {
                    return unit.get("id") === newUnitID;
                });
                newUnitKQList = newUnitObj.get("knowledgeQuantumList");
                newUnitKQList.add(kqObj);

                container.children().each(function (pos, node) {
                    var id = parseInt(node.id.split("kq")[1], 10),
                        model;
                    model = newUnitKQList.find(function (kq) {
                        return kq.get("id") === id;
                    });
                    if (model.get("order") !== pos + 1 || model.get("id") === kqID) {
                        model.save("order", pos + 1);
                    }
                });
            },

            toUnitEditor: function (evt) {
                MOOC.router.navigate("unit" + this.model.get("id"), {
                    trigger: true
                });
            },

            addKQ: function (evt) {
                // TODO
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

                header = "<h4>" + this.model.get("title") + "</h4><button " +
                    "class='btn pull-right' title='" + MOOC.trans.edit + " " +
                    MOOC.trans.kq.kq + "'><i class='icon-edit'></i> " +
                    MOOC.trans.edit + "</button>";
                if (this.model.has("question")) {
                    header += "<span class='badge badge-inverse question " +
                        "pull-right'><i class='icon-white icon-question-sign'>" +
                        "</i></span>";
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

        UnitEditor: Backbone.View.extend({
            events: {
                "change select#type": "changeType",
                "click button#save-unit": "save",
                "click button#delete-unit": "remove",
                "click button.back": "goBack"
            },

            initialize: function () {
                _.bindAll(this, "render", "changeType", "save", "remove", "goBack");
            },

            formatDate: function (date) {
                var aux = date.getFullYear() + "-";
                if (date.getMonth() < 9) {
                    aux += "0";
                }
                aux += (date.getMonth() + 1) + "-";
                if (date.getDate() < 10) {
                    aux += "0";
                }
                aux += date.getDate();
                return aux;
            },

            render: function () {
                $(".viewport").addClass("hide");
                this.$el.html($("#edit-unit-tpl").text());
                this.$el.find("input#title").val(this.model.get("title"));
                this.$el.find("select#type").val(this.model.get("type"));
                this.$el.find("select#type").trigger("change");
                this.$el.find("input#weight").val(this.model.get("weight"));
                if (!_.isNull(this.model.get("start"))) {
                    this.$el.find("input#start_date").val(this.formatDate(this.model.get("start")));
                }
                if (!_.isNull(this.model.get("deadline"))) {
                    this.$el.find("input#end_date").val(this.formatDate(this.model.get("deadline")));
                }
                $("#unit-editor").removeClass("hide");
                return this;
            },

            changeType: function (evt) {
                if ($(evt.target).val() !== 'n') {
                    $("#dates").removeClass("hide");
                } else {
                    $("#dates").addClass("hide");
                }
            },

            save: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                this.model.set("title", this.$el.find("input#title").val());
                this.model.set("type", this.$el.find("select#type").val());
                this.model.set("weight", parseInt(this.$el.find("input#weight").val(), 10));
                this.model.set("start", this.$el.find("input#start_date").val());
                this.model.set("deadline", this.$el.find("input#end_date").val());
                this.model.save(null, {
                    success: function () {
                        showAlert("saved");
                    },
                    error: function () {
                        showAlert("generic");
                    }
                });
            },

            remove: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                MOOC.models.course.remove(this.model);
                this.model.destroy({
                    success: function () {
                        MOOC.router.navigate("", { trigger: true });
                    },
                    error: function () {
                        showAlert("generic");
                    }
                });
            },

            goBack: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                MOOC.router.navigate("", { trigger: true });
            }
        }),

        unitEditorViews: {},

        KQEditor: Backbone.View.extend({}),
        kqEditorViews: {}
    };
}(jQuery, Backbone, _));