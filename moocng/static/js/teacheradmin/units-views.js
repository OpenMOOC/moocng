/*jslint vars: false, browser: true, nomen: true */
/*global MOOC:true, _, jQuery, Backbone, tinyMCE */

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
            var alert = $("#" + id);
            alert.removeClass("hide");
            $("body").animate({ scrollTop: alert.offset().top }, 500);
            setTimeout(function () {
                $("#" + id).addClass("hide");
            }, MOOC.alertTime);
        },

        checkRequiredAux = function ($el) {
            var result = true;
            $el.find("[required=required]").each(function (idx, elem) {
                elem = $(elem);
                if (elem.is(":visible") && elem.val() === "") {
                    result = false;
                }
            });
            return result;
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
                node.append(block("<button id='addUnit' class='btn'>" +
                    "<i class='icon-plus'></i> " + MOOC.trans.add + " " +
                    MOOC.trans.unit.unit + "</button>",
                    { classes: "mb20 align-right" }));
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
                        model.set("new", true);
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
                _.bindAll(this, "render", "sortingHandler", "toUnitEditor",
                    "addKQ");
            },

            render: function () {
                var node = this.$el,
                    sortOpts,
                    header,
                    add,
                    html;

                header = "<span class='badge " + MOOC.unitBadgeClasses[this.model.get("type")] +
                    "'>" + this.model.get("type").toUpperCase() + "</span> " +
                    "<h3>" + this.model.get("title") + "</h3>" +
                    "<button class='btn pull-right edit' title='" + MOOC.trans.edit +
                    " " + MOOC.trans.unit.unit + "'><i class='icon-edit'></i> " +
                    MOOC.trans.edit + "</button>";
                add = "<button class='btn pull-right add'><i class='icon-plus'></i> " +
                    MOOC.trans.add + " " + MOOC.trans.kq.kq + "</button>";
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
                var kq = new MOOC.models.KnowledgeQuantum();
                if (!this.model.has("knowledgeQuantumList")) {
                    this.model.set("knowledgeQuantumList", new MOOC.models.KnowledgeQuantumList());
                }
                this.model.get("knowledgeQuantumList").add(kq);
                kq.save(null, {
                    success: function (model, response) {
                        MOOC.router.navigate("kq" + model.get("id"), {
                            trigger: true
                        });
                    },
                    error: function () {
                        this.model.get("knowledgeQuantumList").remove(kq);
                        showAlert("generic");
                    }
                });
            }
        }),

        unitViews: {},

        KQ: Backbone.View.extend({
            events: {
                "click button.kqedit": "toKQEditor"
            },

            initialize: function () {
                _.bindAll(this, "render", "toKQEditor");
            },

            render: function () {
                var html,
                    header,
                    iframe,
                    data;

                header = "<h4>" + this.model.get("title") + "</h4><button " +
                    "class='btn kqedit pull-right' title='" + MOOC.trans.edit + " " +
                    MOOC.trans.kq.kq + "'><i class='icon-edit'></i> " +
                    MOOC.trans.edit + "</button>";
                if (this.model.has("question")) {
                    header += "<span class='badge badge-inverse question " +
                        "pull-right' title='" + MOOC.trans.kq.question +
                        "'><i class='icon-white icon-question-sign'>" +
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
            },

            toKQEditor: function (evt) {
                MOOC.router.navigate("kq" + this.model.get("id"), {
                    trigger: true
                });
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
                _.bindAll(this, "render", "changeType", "save", "remove",
                    "goBack", "checkRequired");
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

            // Returns true if all required fields are filled, false otherwise
            checkRequired: function () {
                return checkRequiredAux(this.$el);
            },

            save: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                if (!this.checkRequired()) {
                    showAlert("required");
                    return;
                }
                this.model.unset("new");
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
                if (this.model.has("new")) {
                    showAlert("unsaved");
                    return;
                }
                MOOC.router.navigate("", { trigger: true });
            }
        }),

        unitEditorView: undefined,

        KQEditor: Backbone.View.extend({
            events: {
                "click button#addquestion": "addQuestion",
                "click button#force-process": "forceProcess",
                "click button#delete-question": "removeQuestion",
                "click button#go2options": "go2options",
                "click button#save-kq": "save",
                "click button#delete-kq": "remove",
                "click button.back": "goBack"
            },

            initialize: function () {
                _.bindAll(this, "render", "save", "remove", "goBack",
                    "checkRequired");
            },

            render: function () {
                var question;
                $(".viewport").addClass("hide");
                this.$el.html($("#edit-kq-tpl").text());
                this.$el.find("input#kqtitle").val(this.model.get("title"));
                this.$el.find("input#kqvideo").val(this.model.get("videoID"));
                this.$el.find("input#kqweight").val(this.model.get("normalized_weight"));
                if (this.model.has("questionInstance")) {
                    question = this.model.get("questionInstance");
                    this.$el.find("#noquestion").addClass("hide");
                    this.$el.find("#question").removeClass("hide").find("img").attr("src", question.get("lastFrame"));
                    this.$el.find("#questionvideo").val(question.get("solution"));
                    if (question.get("lastFrame").indexOf("no-image.png") >= 0) {
                        this.$el.find("#question img").css("margin-bottom", "10px");
                        $("button#force-process").removeClass("hide");
                    }
                }
                while (tinyMCE.editors.length > 0) {
                    tinyMCE.editors[0].remove();
                }
                this.$el.find("textarea#kqsupplementary").val(this.model.get("supplementary_material"));
                this.$el.find("textarea#kqcomments").val(this.model.get("teacher_comments"));
                tinyMCE.init({
                    mode: "textareas",
                    plugins: "paste,searchreplace",
                    width: "380", // bootstrap span5
                    theme: "advanced",
                    theme_advanced_resizing : true,
                    theme_advanced_toolbar_location: "top",
                    theme_advanced_buttons1: "bold,italic,underline,strikethrough,separator,undo,redo,separator,cleanup,separator,bullist,numlist",
                    theme_advanced_buttons2: "",
                    theme_advanced_buttons3: ""
                });
                $("#kq-editor").removeClass("hide");
                return this;
            },

            // Returns true if all required fields are filled, false otherwise
            checkRequired: function () {
                return checkRequiredAux(this.$el);
            },

            save: function (evt, callback) {
                evt.preventDefault();
                evt.stopPropagation();
                if (!this.checkRequired()) {
                    showAlert("required");
                    return;
                }
                var question;
                this.model.unset("new");
                this.model.set("title", this.$el.find("input#kqtitle").val());
                this.model.set("videoID", this.$el.find("input#kqvideo").val());
                this.model.set("normalized_weight", parseInt(this.$el.find("input#kqweight").val(), 10));
                this.model.set("supplementary_material", tinyMCE.get("kqsupplementary").getContent());
                this.model.set("teacher_comments", tinyMCE.get("kqcomments").getContent());
                if (this.model.has("questionInstance")) {
                    question = this.model.get("questionInstance");
                    question.set("solution", this.$el.find("#questionvideo").val());
                }
                this.model.save(null, {
                    success: function () {
                        showAlert("saved");
                        if (!_.isUndefined(callback)) {
                            callback();
                        } else {
                            if (!_.isUndefined(question)) {
                                question.save();
                            }
                        }
                    },
                    error: function () {
                        showAlert("generic");
                    }
                });
            },

            remove: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                var unit = MOOC.models.course.getByKQ(this.model.get("id")),
                    model = this.model;
                model.destroy({
                    success: function () {
                        unit.get("knowledgeQuantumList").remove(model);
                        MOOC.router.navigate("", { trigger: true });
                    },
                    error: function () {
                        showAlert("generic");
                    }
                });
            },

            addQuestion: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                if (!this.checkRequired()) {
                    showAlert("required");
                    return;
                }
                var question = new MOOC.models.Question(),
                    view = this;
                this.model.set("questionInstance", question);
                this.save(evt, function () {
                    question.save(null, {
                        success: function () {
                            showAlert("saved");
                            view.render();
                        },
                        error: function () {
                            showAlert("generic");
                        }
                    });
                });
            },

            forceProcess: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                $.ajax(window.location.pathname + "forcevideoprocess?kq=" + this.model.get("id"), {
                    success: function () {
                        showAlert("forced");
                    },
                    error: function () {
                        showAlert("generic");
                    }
                });
            },

            removeQuestion: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                var view = this;
                this.model.get("questionInstance").destroy({
                    success: function () {
                        view.model.set("questionInstance", null);
                        view.model.set("question", null);
                        view.model.save(null, {
                            success: function () {
                                view.render();
                            },
                            error: function () {
                                showAlert("generic");
                            }
                        });
                    },
                    error: function () {
                        showAlert("generic");
                    }
                });
            },

            go2options: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                var model = this.model,
                    callback = function () {
                        model.get("questionInstance").save(null, {
                            success: function () {
                                window.open("question/" + model.get("id"), "_self");
                            }
                        });
                    };
                this.save(evt, callback);
            },

            goBack: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                if (this.model.has("new")) {
                    showAlert("unsaved");
                    return;
                }
                MOOC.router.navigate("", { trigger: true });
            }
        }),

        kqEditorView: undefined
    };
}(jQuery, Backbone, _));