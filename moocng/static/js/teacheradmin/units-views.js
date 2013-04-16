/*jslint vars: false, browser: true, nomen: true, regexp: true */
/*global MOOC:true, _, jQuery, Backbone, tinyMCE, async, MEDIA_CONTENT_TYPES */

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

        checkRequiredAux = function ($el) {
            var result = true;
            $el.find("[required=required]").each(function (idx, elem) {
                elem = $(elem);
                if (elem.is(":visible") && $.trim(elem.val()) === "") {
                    result = false;
                }
            });
            return result;
        },

        checkMediaContentId = function ($el) {
            var content_id,
                content_type,
                patterns,
                result_kqmedia,
                result_question;

            patterns = {
                'youtube': [
                    /youtube\.com\/watch[#\?].*\?v=([^"\& ]+)/,
                    /youtube\.com\/embed\/([^"\&\? ]+)/,
                    /youtube\.com\/v\/([^"\&\? ]+)/,
                    /youtube\.com\/\?v=([^"\& ]+)/,
                    /youtu\.be\/([^"\&\? ]+)/,
                    /gdata\.youtube\.com\/feeds\/api\/videos\/([^"\&\? ]+)/,
                    /^([^"\&\? ]+)$/
                ],
                'vimeo': [
                    /vimeo\.com\/(\d+)/,
                    /vimeo\.com\/video\/(\d+)/,
                    /vimeo\.com\/groups\/.+\/videos\/(\d+)/,
                    /vimeo\.com\/channels\/.+#(\d+)/,
                    /^(\d+)$/
                ],
                'scribd': [
                    /scribd\.com\/doc\/(\d+)\/.*/,
                    /^(\d+)$/
                ],
                'prezi': [
                    /prezi\.com\/([a-zA-Z0-9\-]+)\/.*/,
                    /^([a-zA-Z0-9\-]+)$/
                ]
            };

            result_kqmedia = false;
            $("#kqmedia_content_id").each(function (idx, elem) {
                content_id = $(elem).val();
                content_type = $("#kqmedia_content_type").val();

                if (!$(elem).is(':visible')) {
                    result_kqmedia = true;
                }

                _.each(patterns[content_type], function (pattern) {
                    if (content_id.match(pattern) !== null) {
                        result_kqmedia = true;
                    }
                });
            });

            result_question = false;
            $("#questionmedia_content_id").each(function (idx, elem) {
                content_id = $(elem).val();
                content_type = $("#questionmedia_content_type").val();

                if (!$(elem).is(':visible')) {
                    result_question = true;
                }

                _.each(patterns[content_type], function (pattern) {
                    if (content_id.match(pattern) !== null) {
                        result_question = true;
                    }
                });
            });

            return result_kqmedia && result_question;
        },

        stripTags = function (str) {
            return str.replace(/<\/?[^>]+>/ig, '');
        },

        getCookie = function (name) {
            var cookieValue = null,
                cookies,
                i,
                cookie;

            if (document.cookie && document.cookie !== '') {
                cookies = document.cookie.split(';');
                for (i = 0; i < cookies.length; i += 1) {
                    cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },

        csrftoken = getCookie("csrftoken"),

        tinyMCEOptions = {
            mode: "exact",
            plugins: "paste,searchreplace",
            theme: "advanced",
            theme_advanced_resizing : true,
            theme_advanced_toolbar_location: "top",
            theme_advanced_buttons1: "bold,italic,underline,strikethrough,separator,link,unlink,separator,undo,redo,copy,paste,separator,cleanup,separator,bullist,numlist",
            theme_advanced_buttons2: "",
            theme_advanced_buttons3: ""
        },

        invert = function (obj) {
            var result = {},
                key;
            for (key in obj) {
                if (obj.hasOwnProperty(key)) {
                    if (_.has(obj, key)) {
                        result[obj[key]] = key;
                    }
                }
            }
            return result;
        },

        confirmationModal,
        showConfirmationModal = function (callback) {
            if (_.isUndefined(confirmationModal)) {
                confirmationModal = $("#confirm-delete-action").modal({ show: false });
            }
            confirmationModal.find(".btn-danger").off("click").on("click", function (evt) {
                confirmationModal.modal("hide");
                callback();
            });
            confirmationModal.modal("show");
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
                var node = this.$el,
                    listNode;
                $(".viewport").addClass("hide");
                node.html("<div id='unit-list-container'></div>");
                listNode = node.find('#unit-list-container');
                this.model.each(function (unit) {
                    var view = MOOC.views.unitViews[unit.get("id")],
                        el = $("<div id='unit" + unit.get("id") + "' class='unit ui-widget ui-widget-content ui-helper-clearfix ui-corner-all status-" + unit.get("status") + "'></div>")[0];
                    listNode.append(el);
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
                $("#unit-list-container").off("sortstop")
                    .sortable(sortableOptions)
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
                        MOOC.ajax.showLoading();
                        view.model.save("order", pos + 1, {
                            success: function () {
                                MOOC.ajax.hideLoading();
                            },
                            error: function () {
                                MOOC.ajax.hideLoading();
                            }
                        });
                    }
                });
            },

            addUnit: function (evt) {
                var unit = new MOOC.models.Unit();
                MOOC.ajax.showLoading();
                unit.save(null, {
                    success: function (model, response) {
                        MOOC.models.course.add(model);
                        model.set("new", true);
                        MOOC.ajax.hideLoading();
                        MOOC.router.navigate("unit" + model.get("id"), {
                            trigger: true
                        });
                    },
                    error: function () {
                        MOOC.ajax.hideLoading();
                        MOOC.ajax.showAlert("generic");
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
                    "addKQ", "getStatusLabel");
            },

            getStatusLabel: function () {
                return {
                    p: "label-success",
                    l: "label-info",
                    d: ""
                }[this.model.get("status")];
            },

            render: function () {
                var node = this.$el,
                    sortOpts,
                    sortedKQs,
                    header,
                    add,
                    html;

                header = "<span class='badge " + MOOC.unitBadgeClasses[this.model.get("type")] +
                    "' title='" + MOOC.trans.unit[this.model.get("type")] + "'>" +
                    this.model.get("type").toUpperCase() + "</span> " +
                    "<span class='label " + this.getStatusLabel() + "'>" +
                    MOOC.trans.unit[this.model.get("status")] + "</span> " +
                    "<h3>" + this.model.get("title") + "</h3>" +
                    "<button class='btn pull-right edit' title='" + MOOC.trans.edit +
                    " " + MOOC.trans.unit.unit + "'><i class='icon-edit'></i> " +
                    MOOC.trans.edit + "</button>";
                add = "<button class='btn pull-right add'><i class='icon-plus'></i> " +
                    MOOC.trans.add + " " + MOOC.trans.kq.kq + "</button>";
                html = inlineb({ classes: "drag-handle" });
                html += inlineb(block(header, { classes: "header" }),
                                block("", { classes: "kq-container" }),
                                block(add),
                                { classes: "unit-right" });
                node.html(html);

                node = node.find(".kq-container");
                if (this.model.has("knowledgeQuantumList")) {
                    sortedKQs = this.model.get("knowledgeQuantumList").sortBy(function (kq) {
                        return kq.get("order");
                    });
                    _.each(sortedKQs, function (kq) {
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
                        MOOC.ajax.showLoading();
                        model.save("order", pos + 1, {
                            success: function () {
                                MOOC.ajax.hideLoading();
                            },
                            error: function () {
                                MOOC.ajax.hideLoading();
                            }
                        });
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
                MOOC.ajax.showLoading();
                kq.save(null, {
                    success: function (model, response) {
                        MOOC.ajax.hideLoading();
                        model.set("new", true);
                        model.set("order", response.order);
                        MOOC.router.navigate("kq" + model.get("id"), {
                            trigger: true
                        });
                    },
                    error: function () {
                        this.model.get("knowledgeQuantumList").remove(kq);
                        MOOC.ajax.hideLoading();
                        MOOC.ajax.showAlert("generic");
                    }
                });
            }
        }),

        unitViews: {},

        KQ: Backbone.View.extend({
            events: {
                "click button.kqedit": "toKQEditor",
                "click a.thumbnail": "openVideoPlayer"
            },

            initialize: function () {
                _.bindAll(this, "render", "toKQEditor");
            },

            render: function () {
                var html,
                    header,
                    iframe,
                    video_thumbnail,
                    thumbnail_url,
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
                if (this.model.has("peer_review_assignment")) {
                    header += "<span class='badge badge-inverse peerreview " +
                        "pull-right' title='" + MOOC.trans.kq.prTooltip +
                        "'>" + MOOC.trans.kq.pr + "</span>";
                }
                if (this.model.has("asset_availability")) {
                    header += "<span class='badge badge-inverse peerreview " +
                        "pull-right' title='" + MOOC.trans.kq.assetTip +
                        "'>" + MOOC.trans.kq.asset + "</span>";
                }

                thumbnail_url = this.model.get("thumbnail_url");

                video_thumbnail = "";
                if (thumbnail_url) {
                    video_thumbnail = "<a class='thumbnail' data-toggle='modal' href='#player-" + this.model.id + "'>" +
                                  "<img src='" + this.model.get("thumbnail_url") + "'/></a>";
                }

                data = "<p>" + MOOC.trans.kq.teacher_comments + ": " +
                    truncate(_.escape(stripTags(this.model.get("teacher_comments")))) + "</p>" +
                    "<p>" + MOOC.trans.kq.supplementary_material + ": " +
                    truncate(_.escape(stripTags(this.model.get("supplementary_material")))) + "<p/>";


                html = inlineb({ classes: "drag-handle" }) +
                    inlineb(video_thumbnail, { style: "margin-left: 30px;" }) +
                    inlineb(block(header), block(data), { classes: "kq-right" });

                this.$el.html(html);
            },

            toKQEditor: function (evt) {
                MOOC.router.navigate("kq" + this.model.get("id"), {
                    trigger: true
                });
            },

            openVideoPlayer: function (evt) {
                var iframe_template,
                    iframe,
                    context,
                    modal_template;

                modal_template = _.template($("#modal-video-player-tpl").html());
                iframe_template = _.template(this.model.get("iframe_code"));
                iframe = iframe_template({ width: '620px', height: '372px', allowfullscreen: false, controls: false, origin: MOOC.host });

                context = {
                    title: this.model.get("title"),
                    iframe_code: iframe
                };

                $("#media-player").html(modal_template(context));
                $("#media-player").modal("show");
                $("#media-player").on('hidden', function (evt) {
                    $(evt.target).html("");
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
                this.$el
                    .find("input#title").val(this.model.get("title")).end()
                    .find("select#type").val(this.model.get("type")).end()
                    .find("select#type").trigger("change").end()
                    .find("input#weight").val(this.model.get("weight"));
                this.$el.find("input[type=radio][name=status]").each(_.bind(function (idx, elem) {
                    elem = $(elem);
                    var id = elem.attr("id").split('-')[1],
                        active = this.model.statuses[this.model.get("status")];
                    if (id === active) {
                        elem.attr("checked", "checked");
                    } else {
                        elem.attr("checked", false);
                    }
                }, this));

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
                    MOOC.ajax.showAlert("required");
                    return;
                }
                MOOC.ajax.showLoading();

                var status;
                this.model.unset("new");
                this.model.set("title", $.trim(this.$el.find("input#title").val()));
                this.model.set("type", this.$el.find("select#type").val());
                status = this.$el.find("input[type=radio][name=status]:checked").attr("id").split('-')[1];
                this.model.set("status", invert(this.model.statuses)[status]);
                this.model.set("weight", parseInt(this.$el.find("input#weight").val(), 10));
                this.model.set("start", this.$el.find("input#start_date").val());
                this.model.set("deadline", this.$el.find("input#end_date").val());
                this.model.save(null, {
                    success: function () {
                        MOOC.ajax.hideLoading();
                        MOOC.ajax.showAlert("saved");
                    },
                    error: function () {
                        MOOC.ajax.hideLoading();
                        MOOC.ajax.showAlert("generic");
                    }
                });
            },

            remove: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                var cb = _.bind(function () {
                    MOOC.ajax.showLoading();
                    MOOC.models.course.remove(this.model);
                    this.model.destroy({
                        success: function () {
                            MOOC.ajax.hideLoading();
                            MOOC.router.navigate("", { trigger: true });
                        },
                        error: function () {
                            MOOC.ajax.hideLoading();
                            MOOC.ajax.showAlert("generic");
                        }
                    });
                }, this);
                showConfirmationModal(cb);
            },

            goBack: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                if (this.model.has("new")) {
                    MOOC.ajax.showAlert("unsaved");
                    return;
                }
                MOOC.router.navigate("", { trigger: true });
            }
        }),

        unitEditorView: undefined,

        KQEditor: Backbone.View.extend({
            events: {
                "click button#addquestion": "addQuestion",
                "click button#addpeerreviewassignment": "addPeerReviewAssignment",
                "click button#addcriterion": "addCriterion",
                "click button#force-process": "forceProcess",
                "click button#dont-use-last-frame": "useBlankCanvas",
                "click button#use-last-frame": "useLastFrame",
                "click button#delete-question": "removeQuestion",
                "click button#delete-peer-review-assignment": "removePeerReviewAssignment",
                "click button#use-solution-video-btn": "toggleSolution",
                "click button#use-solution-text-btn": "toggleSolution",
                "click button#go2options": "go2options",
                "click button#save-kq": "save",
                "click button#delete-kq": "remove",
                "click button.removecriterion": "removePeerReviewCriterion",
                "click button.back": "goBack",
                "click button#addassetavailability": "addAssetAvailability",
                "click button#delete-asset-availability": "removeAssetAvailability",
                "change select#kqmedia_content_type": "redrawCanGetLastFrame",
                "click button.removeasset": "removeAssetOfAvailability"
            },

            initialize: function () {
                _.bindAll(this, "render", "save", "remove", "goBack",
                    "checkRequired", "useBlankCanvas", "useLastFrame",
                    "toggleSolution", "addQuestion", "addPeerReviewAssignment",
                    "addCriterion", "forceProcess", "removeQuestion",
                    "removePeerReviewAssignment", "go2options", "addAssetAvailability",
                    "removeAssetAvailability");
            },

            render: function () {
                var $attachments,
                    question,
                    options,
                    assignment,
                    criterionList,
                    criterionListDiv,
                    assetAvail,
                    assetList,
                    content_type,
                    can_get_last_frame,
                    assetListDiv,
                    self;

                $(".viewport").addClass("hide");
                while (tinyMCE.editors.length > 0) {
                    tinyMCE.editors[0].remove();
                }
                this.$el.html($("#edit-kq-tpl").text());

                this.$el.find("input#kqtitle").val(this.model.get("title"));
                this.$el.find("select#kqmedia_content_type").val(this.model.get("media_content_type"));
                this.$el.find("input#kqmedia_content_id").val(this.model.get("media_content_id"));
                this.$el.find("input#kqweight").val(this.model.get("weight"));

                if (this.model.has("questionInstance")) {
                    question = this.model.get("questionInstance");
                    this.$el.find("#noquestion").addClass("hide");
                    /* A KQ can only have a question OR a peer review, so if it has
                       a question, the peer review assignment creation button should
                       be hidden as well */
                    this.$el.find("#nopeerreviewassignment").addClass("hide");
                    this.$el.find("#question-tab").removeClass("hide");
                    this.$el.find("#question img").attr("src", question.get("lastFrame"));
                    if (question.has("solution_media_content_id") && question.get("solution_media_content_id") !== "") {
                        this.$el.find("button#use-solution-video-btn").trigger("click");
                    } else if (question.has("solutionText") && question.get("solutionText") !== "") {
                        this.$el.find("button#use-solution-text-btn").trigger("click");
                    } else {
                        // Default
                        this.$el.find("button#use-solution-video-btn").trigger("click");
                    }
                    if (question.has("solution_media_content_type") && question.get("solution_media_content_type") !== "") {
                        this.$el.find("#questionmedia_content_type").val(question.get("solution_media_content_type"));
                    }
                    if (question.has("solution_media_content_id") && question.get("solution_media_content_id") !== "") {
                        this.$el.find("#questionmedia_content_id").val(question.get("solution_media_content_id"));
                    }
                    this.$el.find("textarea#solution-text").val(question.get("solutionText"));
                    if (!question.get("use_last_frame")) {
                        this.$el.find("#last-frame").addClass("hide");
                        this.$el.find("#no-last-frame").removeClass("hide");
                    }
                    content_type = this.model.get('media_content_type');
                    can_get_last_frame = MEDIA_CONTENT_TYPES[content_type].can_get_last_frame;
                    if (!can_get_last_frame) {
                        this.$el.find("#last-frame").addClass("hide");
                        this.$el.find("#no-last-frame").addClass("hide");
                        this.$el.find("#cant-last-frame").removeClass("hide");
                    }
                    if (question.get("lastFrame").indexOf("no-image.png") >= 0) {
                        this.$el.find("#question img").css("margin-bottom", "10px");
                        $("button#force-process").removeClass("hide");
                    }
                }

                if (this.model.has("peer_review_assignment") && this.model.has("peerReviewAssignmentInstance")) {
                    assignment = this.model.get("peerReviewAssignmentInstance");
                    this.$el.find("#peer-review-assignment-tab").removeClass("hide");
                    this.$el.find("#nopeerreviewassignment").addClass("hide");
                    /* A KQ can only have a question OR a peer review, so if it has
                       a peer review assignment, the question creation button should
                       be hidden as well */
                    this.$el.find("#noquestion").addClass("hide");
                    this.$el.find("#reviewdescription").val(assignment.get("description"));
                    this.$el.find("#reviewminreviews").val(assignment.get("minimum_reviewers"));
                    criterionList = assignment.get("_criterionList");
                    criterionListDiv = this.$el.find("#reviewcriterions");
                    self = this;
                    criterionListDiv.empty();
                    criterionList.each(function (criterion) {
                        var criterionDivId,
                            titleInputId,
                            descriptionInputId,
                            removeBtnId,
                            titleInput,
                            titleLabel,
                            descriptionInput,
                            descriptionLabel,
                            removeBtn,
                            criterionDiv;

                        criterionDivId = "criterion-" + criterion.get("id");
                        titleInputId = "criteriontitle-" + criterion.get("id");
                        descriptionInputId = "criteriondescription-" + criterion.get("id");
                        removeBtnId = "criterionremove-" + criterion.get("id");

                        titleInput = "<input type=\"text\" name=\"" + titleInputId + "\" id=\"" + titleInputId + "\" maxlength=\"100\" class=\"input-large\" required=\"required\" />";
                        titleLabel = "<label for=\"" + titleInputId + "\" class=\"required\">" + MOOC.trans.evaluationCriterion.title + "</label>";
                        descriptionInput = "<input type=\"text\" name=\"" + descriptionInputId + "\" id=\"" + descriptionInputId + "\" maxlength=\"200\" class=\"input-xlarge\" required=\"required\" />";
                        descriptionLabel = "<label for=\"" + descriptionInputId + "\" class=\"required\">" + MOOC.trans.evaluationCriterion.description + "</label>";
                        removeBtn = "<button id=\"" + removeBtnId + "\" class=\"removecriterion btn btn-danger\">" + MOOC.trans.evaluationCriterion.remove + "</button>";
                        criterionDiv = "<div id=\"" + criterionDivId + "\">"
                                       + "<div class=\"row mb10\"> <div class=\"span3\">" + titleLabel + titleInput + "</div>"
                                       + "<div class=\"span4\">" + descriptionLabel + descriptionInput + "</div></div>"
                                       + "<div class=\"row mb20\"><div class=\"align-right span10\">" + removeBtn + "</div></div></divZ";

                        criterionListDiv.append(criterionDiv);
                        criterionListDiv.find("#" + titleInputId).val(criterion.get("title"));
                        criterionListDiv.find("#" + descriptionInputId).val(criterion.get("description"));
                    });
                }

                if (this.model.has("asset_availability") && this.model.has("assetAvailabilityInstance")) {
                    assetAvail = this.model.get("assetAvailabilityInstance");
                    this.$el.find("#asset-availability-tab").removeClass("hide");
                    this.$el.find("#noassetavailability").addClass("hide");
                    this.$el.find("#availablefrom").val(assetAvail.get("available_from"));
                    this.$el.find("#availableto").val(assetAvail.get("available_to"));
                    assetList = assetAvail.get("_assetList");

                    assetListDiv = this.$el.find("#assets");
                    self = this;
                    assetListDiv.empty();
                    assetList.each(function (asset) {
                        var assetDivId,
                            nameInputId,
                            removeBtnId,
                            nameInput,
                            nameLabel,
                            removeBtn,
                            assetDiv;

                        assetDivId = "asset-" + asset.get("id");
                        nameInputId = "assetname-" + asset.get("id");
                        removeBtnId = "assetremove-" + asset.get("id");

                        nameInput = "<h3 class=\"input-large\" id=\"" + nameInputId + "\" ></h3>";
                        removeBtn = "<button id=\"" + removeBtnId + "\" class=\"removeasset btn btn-danger\">" + MOOC.trans.asset.remove + "</button>";
                        assetDiv = "<div id=\"" + assetDivId + "\">"
                                       + "<div> <div class=\"span4\">" + nameInput + "</div>"
                                       + "<div class=\"row mb20\"><div class=\"align-right span10\">" + removeBtn + "</div></div></divZ";

                        assetListDiv.append(assetDiv);
                        assetListDiv.find("#" + nameInputId).text(asset.get("name"));
                    });

                }

                $attachments = this.$el.find("#attachment-list");
                if (this.model.get("attachmentList").length > 0) {
                    this.model.get("attachmentList").each(function (attachment) {
                        var view = new MOOC.views.Attachment({
                            model: attachment,
                            el: $attachments.find("tbody")[0]
                        });
                        view.render();
                    });
                } else {
                    $attachments.addClass("hide");
                    this.$el.find("#attachment-empty").removeClass("hide");
                }

                this.$el.find("textarea#kqsupplementary").val(this.model.get("supplementary_material"));
                this.$el.find("textarea#kqcomments").val(this.model.get("teacher_comments"));
                options = _.extend(_.clone(tinyMCEOptions), {
                    width: "380", // bootstrap span5
                    elements: "kqsupplementary, kqcomments, reviewdescription"
                });
                tinyMCE.init(options);
                options = _.extend(_.clone(tinyMCEOptions), {
                    width: "780", // bootstrap span10
                    height: "250",
                    elements: "solution-text"
                });
                tinyMCE.init(options);
                $("#kq-editor").removeClass("hide");
                return this;
            },

            redrawCanGetLastFrame: function (event) {
                var target,
                    content_type,
                    can_get_last_frame,
                    question;

                target = $(event.currentTarget);
                content_type = target.val();
                can_get_last_frame = MEDIA_CONTENT_TYPES[content_type].can_get_last_frame;
                question = this.model.get('questionInstance');
                if (!can_get_last_frame) {
                    this.$el.find("#last-frame").addClass("hide");
                    this.$el.find("#no-last-frame").addClass("hide");
                    this.$el.find("#cant-last-frame").removeClass("hide");
                } else {
                    if (question.get("use_last_frame")) {
                        this.$el.find("#last-frame").removeClass("hide");
                    } else {
                        this.$el.find("#no-last-frame").removeClass("hide");
                    }
                    this.$el.find("#cant-last-frame").addClass("hide");
                }
            },

            // Returns true if all required fields are filled, false otherwise
            checkRequired: function () {
                return checkRequiredAux(this.$el);
            },

            save: function (evt, callback) {
                evt.preventDefault();
                evt.stopPropagation();
                if (!this.checkRequired()) {
                    MOOC.ajax.showAlert("required");
                    return;
                }
                if (!checkMediaContentId()) {
                    MOOC.ajax.showAlert("media_content_id");
                    return;
                }
                MOOC.ajax.showLoading();

                var steps = [],
                    self = this,
                    question,
                    assignment,
                    criterionList,
                    criterionListSaveTasks,
                    assetAvail,
                    content_type,
                    can_get_last_frame,
                    attachCB;

                this.model.unset("new");
                this.model.set("title", $.trim(this.$el.find("input#kqtitle").val()));
                this.model.set("media_content_id", $.trim(this.$el.find("input#kqmedia_content_id").val()));
                this.model.set("media_content_type", this.$el.find("select#kqmedia_content_type").val());
                this.model.set("weight", parseInt(this.$el.find("input#kqweight").val(), 10));
                this.model.set("supplementary_material", tinyMCE.get("kqsupplementary").getContent());
                this.model.set("teacher_comments", tinyMCE.get("kqcomments").getContent());

                if (this.model.has("questionInstance")) {
                    question = this.model.get("questionInstance");
                    content_type = this.$el.find("select#kqmedia_content_type").val();
                    can_get_last_frame = MEDIA_CONTENT_TYPES[content_type].can_get_last_frame;
                    if (!can_get_last_frame) {
                        question.set("use_last_frame", false);
                    }

                    if (this.$el.find("#use-solution-video-btn").is(".active")) {
                        question.set("solution_media_content_type", this.$el.find("#questionmedia_content_type").val());
                        question.set("solution_media_content_id", this.$el.find("#questionmedia_content_id").val());
                        question.set("solutionText", null);
                    } else {
                        question.set("solution_media_content_type", null);
                        question.set("solution_media_content_id", null);
                        question.set("solutionText", tinyMCE.get("solution-text").getContent());
                    }

                    steps.push(function (asyncCB) {
                        question.save(null, {
                            success: function () { asyncCB(); },
                            error: function () { asyncCB("Error saving question"); }
                        });
                    });
                }

                steps.push(function (asyncCB) {
                    self.model.save(null, {
                        success: function () { asyncCB(); },
                        error: function () { asyncCB("Error saving KQ"); }
                    });
                });

                if (this.model.has("peerReviewAssignmentInstance")) {
                    criterionListSaveTasks = [];
                    assignment = this.model.get("peerReviewAssignmentInstance");
                    if (assignment.has("id")) {
                        assignment.set("description", tinyMCE.get("reviewdescription").getContent());
                        assignment.set("minimum_reviewers", parseInt(this.$el.find("input#reviewminreviews").val(), 10));
                    }

                    steps.push(function (asyncCB) {
                        assignment.save(null, {
                            success: function () {
                                asyncCB();
                            },
                            error: function () {
                                asyncCB("Error saving peer review assignment");
                            }
                        });
                    });

                    criterionList = assignment.get("_criterionList");
                    criterionList.each(function (criterion) {
                        var titleInputId,
                            descriptionInputId;

                        titleInputId = "criteriontitle-" + criterion.get("id");
                        descriptionInputId = "criteriondescription-" + criterion.get("id");
                        criterion.set("title", $.trim(self.$el.find("#" + titleInputId).val()));
                        criterion.set("description", $.trim(self.$el.find("#" + descriptionInputId).val()));

                        criterionListSaveTasks.push(function (asyncCB) {
                            criterion.save(null, {
                                success: function () {
                                    asyncCB();
                                },
                                error: function () {
                                    asyncCB("Error saving peer review assignment evaluation criterion");
                                }
                            });
                        });
                    });

                    steps.push(function (asyncCB) {
                        async.parallel(criterionListSaveTasks, asyncCB);
                    });
                }

                if (this.model.has("assetAvailabilityInstance")) {
                    assetAvail = this.model.get("assetAvailabilityInstance");
                    if (!this.$el.find("#asset-availability").is(".hidden")) {
                        assetAvail.set("available_from", this.$el.find("#availablefrom").val());
                        assetAvail.set("available_to", this.$el.find("#availableto").val());
                    }
                    steps.push(function (asyncCB) {
                        assetAvail.save(null, {
                            success: function () {
                                asyncCB();
                            },
                            error: function () {
                                asyncCB("Error saving Asset Availability");
                            }
                        });
                    });
                }

                // Look for attachments
                if (this.$el.find("div.fileupload input[type='file']").val() !== "") {
                    steps.push(function (asyncCB) {
                        var input = self.$el.find("div.fileupload input[type='file']")[0],
                            fakeForm;
                        if (input.files) {
                            fakeForm = new FormData();
                            fakeForm.append("attachment", input.files[0]);
                            $.ajax(window.location.pathname + "attachment/?kq=" + self.model.get("id"), {
                                type: "POST",
                                headers: {
                                    "X-CSRFToken": csrftoken
                                },
                                data: fakeForm,
                                processData: false,
                                contentType: false,
                                success: function () { asyncCB(); },
                                error: function () { asyncCB("Error saving attachment"); }
                            });
                        } else {
                            asyncCB("Error with attachment, FileAPI not supported");
                        }
                    });

                    steps.push(function (asyncCB) {
                        $.ajax(MOOC.ajax.host + "attachment/?format=json&kq=" + self.model.get("id"), {
                            success: function (data, textStatus, jqXHR) {
                                var attachmentList = new MOOC.models.AttachmentList(
                                    _.map(data.objects, function (attachment) {
                                        return {
                                            id: parseInt(attachment.id, 10),
                                            url: attachment.attachment
                                        };
                                    })
                                );
                                self.model.set("attachmentList", attachmentList);
                                asyncCB();
                            },
                            error: function () { asyncCB("Error saving attachment"); }
                        });
                    });

                    attachCB = function () {
                        self.render();
                        self.$el.find("#attachments-tab a").trigger("click");
                    };
                }

                async.series(steps, function (err, results) {
                    if (!_.isUndefined(callback)) {
                        callback();
                    } else {
                        if (err) {
                            MOOC.ajax.showAlert("generic");
                        } else {
                            MOOC.ajax.showAlert("saved");
                        }
                        if (!_.isUndefined(attachCB)) {
                            attachCB();
                        }
                        MOOC.ajax.hideLoading();
                    }
                });
            },

            remove: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                var cb = _.bind(function () {
                    MOOC.ajax.showLoading();
                    var unit = MOOC.models.course.getByKQ(this.model.get("id")),
                        model = this.model;
                    model.destroy({
                        success: function () {
                            unit.get("knowledgeQuantumList").remove(model);
                            MOOC.ajax.hideLoading();
                            MOOC.router.navigate("", { trigger: true });
                        },
                        error: function () {
                            MOOC.ajax.hideLoading();
                            MOOC.ajax.showAlert("generic");
                        }
                    });
                }, this);
                showConfirmationModal(cb);
            },

            addQuestion: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                if (!this.checkRequired()) {
                    MOOC.ajax.showAlert("required");
                    return;
                }
                if (!checkMediaContentId()) {
                    MOOC.ajax.showAlert("media_content_id");
                    return;
                }
                var question = new MOOC.models.Question(),
                    view = this;
                this.model.set("questionInstance", question);
                this.save(evt, _.bind(function () {
                    this.render();
                    this.$el.find("#question-tab a").trigger("click");
                    MOOC.ajax.hideLoading();
                }, this));
            },

            addCriterion: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                if (!this.checkRequired()) {
                    MOOC.ajax.showAlert("required");
                    return;
                }

                if (!checkMediaContentId()) {
                    MOOC.ajax.showAlert("media_content_id");
                    return;
                }

                var self,
                    assignment,
                    assignmentUrl,
                    assignmentId,
                    criterionList,
                    newCriterion;

                self = this;
                assignment = this.model.get("peerReviewAssignmentInstance");
                assignmentUrl = assignment.url();
                newCriterion = new MOOC.models.EvaluationCriterion();

                this.save(evt, function () {
                    newCriterion.set("assignment", assignmentUrl);
                    newCriterion.save(null, {
                        success: function () {
                            criterionList = new MOOC.models.EvaluationCriterionList();
                            assignmentUrl = assignmentUrl.split('/');

                            assignmentId = parseInt(assignmentUrl.pop(), 10);
                            while (_.isNaN(assignmentId)) {
                                assignmentId = parseInt(assignmentUrl.pop(), 10);
                            }

                            assignment.get("_criterionList").fetch({
                                data: { 'assignment': assignmentId },
                                success: function () {
                                    self.render();
                                    self.$el.find("form li.active").removeClass("active");
                                    self.$el.find("form fieldset.active").removeClass("active");
                                    self.$el.find("#peer-review-assignment-tab").addClass("active");
                                    self.$el.find("#peer-review-assignment").addClass("active");
                                    MOOC.ajax.hideLoading();
                                },
                                error: function () {
                                    MOOC.ajax.hideLoading();
                                    MOOC.ajax.showAlert("generic");
                                }
                            });
                        },
                        error: function () {
                            MOOC.ajax.hideLoading();
                            MOOC.ajax.showAlert("generic");
                        }
                    });

                });
            },

            addPeerReviewAssignment: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                if (!this.checkRequired()) {
                    MOOC.ajax.showAlert("required");
                    return;
                }
                if (!checkMediaContentId()) {
                    MOOC.ajax.showAlert("media_content_id");
                    return;
                }
                var peer_review_assignment,
                    self;

                peer_review_assignment = new MOOC.models.PeerReviewAssignment();
                peer_review_assignment.set("kq", this.model.url().replace('/privkq', '/kq'));
                peer_review_assignment.set("description", "");
                peer_review_assignment.set("minimum_reviewers", "0");
                peer_review_assignment.set("_criterionList", new MOOC.models.EvaluationCriterionList());
                this.model.set("peerReviewAssignmentInstance", peer_review_assignment);

                self = this;
                this.save(evt, _.bind(function () {
                    self.model.fetch({
                        success: function () {
                            var reviewUrl,
                                createdId;
                            reviewUrl = self.model.get("peer_review_assignment").split("/");
                            createdId = reviewUrl.pop();

                            while (_.isNaN(parseInt(createdId, 10))) {
                                createdId = reviewUrl.pop();
                            }

                            self.model.get("peerReviewAssignmentInstance").set("id", parseInt(createdId, 10));
                            self.render();
                            MOOC.ajax.hideLoading();
                        },
                        error: function () {
                            MOOC.ajax.hideLoading();
                            MOOC.ajax.showAlert("generic");
                        }
                    });
                }, this));
            },

            addAssetAvailability: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                if (!this.checkRequired()) {
                    MOOC.ajax.showAlert("required");
                    return;
                }
                var asset_availability,
                    self,
                    date;

                asset_availability = new MOOC.models.AssetAvailability();
                asset_availability.set("kq", this.model.url().replace('/privkq', '/kq'));
                date = new Date();
                asset_availability.set("available_from", date.toISOString().split('T')[0]);
                date.setMonth(date.getMonth() + 1);
                asset_availability.set("available_to", date.toISOString().split('T')[0]);
                asset_availability.set("assets", []);
                asset_availability.set("_assetList", new MOOC.models.AssetList());
                this.model.set("assetAvailabilityInstance", asset_availability);

                self = this;
                this.save(evt, _.bind(function () {
                    self.model.fetch({
                        success: function () {
                            var assetAvailUrl,
                                createdId;
                            assetAvailUrl = self.model.get("asset_availability").split("/");
                            createdId = assetAvailUrl.pop();
                            while (_.isNaN(parseInt(createdId, 10))) {
                                createdId = assetAvailUrl.pop();
                            }
                            self.model.get("assetAvailabilityInstance").set("id", parseInt(createdId, 10));
                            self.render();
                            MOOC.ajax.hideLoading();
                        },
                        error: function () {
                            MOOC.ajax.hideLoading();
                            MOOC.ajax.showAlert("generic");
                        }
                    });
                }, this));
            },

            forceProcess: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                MOOC.ajax.showLoading();
                $.ajax(window.location.pathname + "forcevideoprocess/?kq=" + this.model.get("id"), {
                    success: function () {
                        MOOC.ajax.hideLoading();
                        MOOC.ajax.showAlert("forced");
                    },
                    error: function () {
                        MOOC.ajax.hideLoading();
                        MOOC.ajax.showAlert("generic");
                    }
                });
            },

            useBlankCanvas: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                var question = this.model.get("questionInstance");
                this.$el.find("#last-frame").addClass("hide");
                this.$el.find("#no-last-frame").removeClass("hide");
                question.set("use_last_frame", false);
            },

            useLastFrame: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                var question = this.model.get("questionInstance");
                this.$el.find("#last-frame").removeClass("hide");
                this.$el.find("#no-last-frame").addClass("hide");
                question.set("use_last_frame", true);
            },

            toggleSolution: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                var id = evt.target.id,
                    toShow = id.split("-btn")[0],
                    toHide = "use-solution-video";
                if (toShow.indexOf("video") > 0) {
                    toHide = "use-solution-text";
                }
                this.$el.find("#" + toShow).removeClass("hide");
                this.$el.find("#" + toShow + "-btn").addClass("active");
                this.$el.find("#" + toHide).addClass("hide");
                this.$el.find("#" + toHide + "-btn").removeClass("active");
            },

            removeQuestion: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();

                var view = this,
                    cb = function () {
                        MOOC.ajax.showLoading();
                        view.model.get("questionInstance").destroy({
                            success: function () {
                                view.model.set("questionInstance", null);
                                view.model.set("question", null);
                                view.model.save(null, {
                                    success: function () {
                                        MOOC.ajax.hideLoading();
                                        view.render();
                                    },
                                    error: function () {
                                        MOOC.ajax.hideLoading();
                                        MOOC.ajax.showAlert("generic");
                                    }
                                });
                            },
                            error: function () {
                                MOOC.ajax.hideLoading();
                                MOOC.ajax.showAlert("generic");
                            }
                        });
                    };

                showConfirmationModal(cb);
            },

            removePeerReviewAssignment: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();

                var view = this,
                    cb = function () {
                        MOOC.ajax.showLoading();
                        view.model.get("peerReviewAssignmentInstance").destroy({
                            success: function () {
                                view.model.set("peerReviewAssignmentInstance", null);
                                view.model.set("peer_review_assignment", null);
                                view.model.save(null, {
                                    success: function () {
                                        MOOC.ajax.hideLoading();
                                        view.render();
                                    },
                                    error: function () {
                                        MOOC.ajax.hideLoading();
                                        MOOC.ajax.showAlert("generic");
                                    }
                                });
                            },
                            error: function () {
                                MOOC.ajax.hideLoading();
                                MOOC.ajax.showAlert("generic");
                            }
                        });
                    };

                showConfirmationModal(cb);
            },

            removePeerReviewCriterion: function (evt) {
                evt.stopPropagation();
                evt.preventDefault();

                var self = this,
                    cb;

                cb = function () {
                    var criterionId = parseInt(evt.target.getAttribute('id').split('-')[1], 10),
                        criterionList = self.model.get("peerReviewAssignmentInstance").get("_criterionList"),
                        criterion = criterionList.find(function (candidate) {
                            return (parseInt(candidate.get("id"), 10) === criterionId);
                        });

                    MOOC.ajax.showLoading();
                    criterion.destroy({
                        success: function () {
                            var assignment = self.model.get("peerReviewAssignmentInstance"),
                                criterionList = assignment.get("_criterionList"),
                                criterionDivId = "criterion-" + criterion.get("id");
                            criterionList.remove(criterion);
                            self.$el.find("#" + criterionDivId).remove();
                            MOOC.ajax.hideLoading();
                        },
                        error: function () {
                            MOOC.ajax.hideLoading();
                            MOOC.ajax.showAlert("generic");
                        }
                    });
                };

                showConfirmationModal(cb);
            },

            removeAssetAvailability: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();

                var view = this,
                    cb = function () {
                        MOOC.ajax.showLoading();
                        view.model.get("assetAvailabilityInstance").destroy({
                            success: function () {
                                view.model.set("assetAvailabilityInstance", null);
                                view.model.set("asset_availability", null);
                                view.model.save(null, {
                                    success: function () {
                                        MOOC.ajax.hideLoading();
                                        view.render();
                                    },
                                    error: function () {
                                        MOOC.ajax.hideLoading();
                                        MOOC.ajax.showAlert("generic");
                                    }
                                });
                            },
                            error: function () {
                                MOOC.ajax.hideLoading();
                                MOOC.ajax.showAlert("generic");
                            }
                        });
                    };

                showConfirmationModal(cb);
            },

            removeAssetOfAvailability: function (evt) {
                evt.stopPropagation();
                evt.preventDefault();

                var self = this,
                    cb;

                cb = function () {
                    var assetId = parseInt(evt.target.getAttribute('id').split('-')[1], 10),
                        assetInstance,
                        assets,
                        assetToRemove,
                        assetUrl,
                        asset_availability = self.model.get("assetAvailabilityInstance"),
                        assetList = asset_availability.get("_assetList"),
                        asset = assetList.find(function (candidate) {
                            return (parseInt(candidate.get("id"), 10) === assetId);
                        }),
                        assetDivId = "asset-" + asset.get("id");

                    MOOC.ajax.showLoading();

                    assetList.remove(asset);
                    assetInstance = self.model.get("assetAvailabilityInstance");
                    assets = assetInstance.get("assets");
                    assetUrl = asset.url().replace('/privasset', '/asset');
                    assets.splice(assets.indexOf(assetUrl), 1);
                    assetInstance.set("assets", assets);
                    assetInstance.save();

                    self.$el.find("#" + assetDivId).remove();
                    MOOC.ajax.hideLoading();

                };

                showConfirmationModal(cb);
            },

            go2options: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                var model = this.model,
                    callback = function () {
                        window.open("question/" + model.get("id"), "_self");
                    };
                this.save(evt, callback);
            },

            goBack: function (evt) {
                evt.preventDefault();
                evt.stopPropagation();
                if (this.model.has("new")) {
                    MOOC.ajax.showAlert("unsaved");
                    return;
                }
                MOOC.router.navigate("", { trigger: true });
            }
        }),

        kqEditorView: undefined,

        Attachment: Backbone.View.extend({
            events: {
                "click i.icon-remove": "remove"
            },

            initialize: function () {
                _.bindAll(this, "render", "remove");
            },

            render: function () {
                var html = "<tr id='attachment-" + this.model.get("id") + "'><td><a href='" + this.model.get("url") + "' target='_blank'>",
                    parts = this.model.get("url").split('/');
                html += parts[parts.length - 1];
                html += "</a></td><td class='center'><i class='icon-remove pointer'></i></td></tr>";
                this.$el.append(html);
                return this;
            },

            remove: function (evt) {
                var $el = $(evt.target).parent().parent(),
                    cb = function () {
                        var id = $el.attr("id").split('-')[1],
                            rows = $el.parent().find("tr").length;
                        MOOC.ajax.showLoading();
                        $.ajax(window.location.pathname + "attachment/?attachment=" + id, {
                            type: "DELETE",
                            headers: {
                                "X-CSRFToken": csrftoken
                            },
                            success: function () {
                                var $table = $el.parent().parent();
                                $el.fadeOut().remove();
                                MOOC.ajax.hideLoading();
                                MOOC.ajax.showAlert("saved");
                                if (rows === 1) {
                                    $table.hide().parent().find("#attachment-empty").show();
                                }
                            },
                            error: function () {
                                MOOC.ajax.hideLoading();
                                MOOC.ajax.showAlert("generic");
                            }
                        });
                    };
                showConfirmationModal(cb);
            }
        })
    };
}(jQuery, Backbone, _));
