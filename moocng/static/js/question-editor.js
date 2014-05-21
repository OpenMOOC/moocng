/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, jQuery, _ */

// Copyright 2012 UNED
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

(function ($, Backbone, _) {
    "use strict";

    if (_.isUndefined(window.MOOC)) {
        window.MOOC = {};
    }

    MOOC.models = {};

    MOOC.models.Option = Backbone.Model.extend({
        defaults: function () {
            return {
                optiontype: 't',
                x: 0,
                y: 0,
                width: 100,
                height: 12,
                solution: '',
                text: "",
                feedback: ""
            };
        },

        url: function () {
            var url = MOOC.models.Option.__super__.url.call(this);
            if (url.charAt(url.length - 1) !== '/') {
                url += '/';
            }
            return url;
        }
    });

    MOOC.models.OptionList  = Backbone.Collection.extend({
        model: MOOC.models.Option,

        url: function () {
            var url = MOOC.models.OptionList.__super__.url.call(this);
            if (url.charAt(url.length - 1) !== '/') {
                url += '/';
            }
            return url;
        }
    });

    MOOC.views = {};

    MOOC.views.defaultSize = 14; // For checkboxes and radios

    MOOC.views.OptionView = Backbone.View.extend({
        tagName: 'span',
        className: 'option',
        padding: 5,
        handlePadding: 20,
        option_types: {
            'l': 'textarea',
            't': 'text',
            'c': 'checkbox',
            'r': 'radio'
        },

        initialize: function () {
            _.bindAll(this, 'render', 'drag', 'start', 'stop',
                      'select', 'unselect', 'is_out', 'change');
            this.model.bind("change", this.render, this);

            this.parent_view = this.options.parent_view;
            this.parent_width = this.options.parent_width;
            this.parent_height = this.options.parent_height;
        },

        render: function () {
            var optiontype = this.model.get('optiontype'),
                sol = this.model.get('solution'),
                tag = "input",
                content = "",
                attributes = {
                    type: this.option_types[optiontype],
                    value: sol,
                    style: [
                        "width: " + this.model.get("width") + "px;",
                        "height: " + this.model.get("height") + "px;"
                    ].join(" ")
                },
                size = {};

            if (optiontype === 'c' || optiontype === 'r') {
                attributes.style = [
                    "width: " + MOOC.views.defaultSize + "px;",
                    "height: " + MOOC.views.defaultSize + "px;"
                ].join(" ");

                if (optiontype === 'r') {
                    attributes.name = "radio";
                }

                if ((_.isString(sol) && sol.toLowerCase() === 'true') || (_.isBoolean(sol) && sol)) {
                    attributes.checked = 'checked';
                }
            } else if (optiontype === 'l') {
                tag = attributes.type;
                content = this.model.get("text");
                delete attributes.type;
                delete attributes.value;
                attributes.cols = this.model.get("width");
                attributes.rows = this.model.get("height");
                attributes.style = [];
                attributes.style.push('resize:none;');
                attributes.style.push('line-height: 20px;');
            }

            this.$el.empty().append(this.make(tag, attributes, content));
            size = this.calculate_size();
            this.$el
                .width(size.width + this.padding * 2 + this.handlePadding)
                .height(size.height + this.padding * 2)
                .css({
                    left: (this.model.get('x') - this.padding) + "px",
                    top: (this.model.get('y') - this.padding) + "px",
                    padding: this.padding + "px",
                    position: 'absolute'
                })
                .draggable({
                    drag: this.drag,
                    start: this.start,
                    stop: this.stop
                })
                .find(tag).change(this.change);

            return this;
        },

        is_out: function (position) {
            var size = this.calculate_size();
            return ((position.left + this.padding) < 0
                    || (position.top + this.padding) < 0
                    || (position.left + size.width + (2 * this.padding)) > this.parent_width
                    || (position.top + size.height + (2 * this.padding)) > this.parent_height);
        },

        drag: function () {
            var position = this.$el.position();
            if (this.is_out(position)) {
                this.$el.addClass('out');
            } else {
                this.model.set("x", position.left + this.padding);
                this.model.set("y", position.top + this.padding);
                this.$el.removeClass('out');
            }
        },

        calculate_size: function () {
            var optiontype = this.model.get('optiontype'),
                width = this.model.get("width"),
                height = this.model.get("height");

            if (optiontype === 'l') {
                width = (8.1 * width) + 10;
                height = (20 * height) + 10;
            }
            return {
                width: width,
                height: height

            };
        },

        start: function () {
            this.parent_view.select_option(this.el);
        },

        stop: function () {
            var position = this.$el.position();
            if (this.is_out(position)) {
                this.model.unbind("change", this.render);
                this.model.destroy();
                MOOC.router.navigate("", {trigger: true});
            } else {
                this.model.set("x", position.left + this.padding);
                this.model.set("y", position.top + this.padding);
                this.model.save();
            }
        },

        select: function () {
            this.$el.addClass('selected');
        },

        unselect: function () {
            this.$el.removeClass('selected');
        },

        change: function () {
            var $input = this.$el.find('input'),
                optiontype = this.model.get('optiontype'),
                value = "",
                prop = "solution";
            if (optiontype === 'l') {
                $input = this.$el.find("textarea");
                prop = "text";
            }
            if (optiontype === 'c' || optiontype === 'r') {
                value = _.isUndefined($input.attr('checked')) ? false : true;
                if (value && optiontype === 'r') {
                    // Update the solution stored in the other radio models
                    $("input[type=radio]").filter(function (idx, radio) {
                        return radio !== $input[0];
                    }).trigger("change");
                }
            } else {
                value = $input.val();
            }
            this.start();
            this.model.set(prop, value);
            this.model.save();
        }

    });

    MOOC.views.OptionPropertiesView = Backbone.View.extend({
        events: {
            "click #remove-option": "remove_option"
        },

        initialize: function () {
            _.bindAll(this, 'close', 'render', 'reset', 'remove_option',
                      'change_property_handler', 'change_property',
                      'unbind_change');
            this.model.bind("change", _.bind(function () {
                this.unbind_change();
                this.render();
            }, this), this);
        },

        close: function () {
            this.model.unbind("change", this.render);
            this.unbind();
            this.unbind_change();
            this.undelegateEvents();
        },

        render: function () {
            var optiontype = this.model.get('optiontype'),
                solution = this.model.get('solution');

            if ((optiontype === 'c' || optiontype === 'r') && _.isString(solution)) {
                solution = solution.toLowerCase() === "true";
            }

            this.$el
                .find('#option-id').html(this.model.get('id')).end()
                .find('#option-optiontype').change(this.change_property_handler(['optiontype', false])).val(this.model.get('optiontype')).end()
                .find('#option-solution').change(this.change_property_handler(['solution', false])).val(solution).end()
                .find('#option-feedback').change(this.change_property_handler(['feedback', false])).val(this.model.get("feedback")).end()
                .find('#option-x').change(this.change_property_handler(['x', true])).val(this.model.get('x')).end()
                .find('#option-y').change(this.change_property_handler(['y', true])).val(this.model.get('y'));

            if (optiontype === 'c' || optiontype === 'r') {
                this.$el
                    .find('#option-width').attr("disabled", "disabled").val(this.model.get('width')).end()
                    .find('#option-height').attr("disabled", "disabled").val(this.model.get('height'));
            } else {
                this.$el
                    .find('#option-width').attr("disabled", false).change(this.change_property_handler(['width', true])).val(this.model.get('width')).end()
                    .find('#option-height').attr("disabled", false).change(this.change_property_handler(['height', true])).val(this.model.get('height'));
            }

            if (optiontype === 'l') {
                this.$el
                    .find("#option-solution").val(this.model.get("text")).end()
                    .find("#solution-title").addClass("hide").end()
                    .find("#content-title").removeClass("hide");
                this.$el.find("#option-feedback").parent().parent().addClass("hide");
            } else {
                this.$el
                    .find("#solution-title").removeClass("hide").end()
                    .find("#content-title").addClass("hide");
                this.$el.find("#option-feedback").parent().parent().removeClass("hide");
            }
        },

        unbind_change: function () {
            this.$el.find("#option-optiontype").unbind('change');
            this.$el.find("#option-solution").unbind('change');
            this.$el.find("#option-feedback").unbind('change');
            this.$el.find("#option-x").unbind('change');
            this.$el.find("#option-y").unbind('change');
            this.$el.find("#option-width").unbind('change');
            this.$el.find("#option-height").unbind('change');
        },

        change_property_handler: function (args) {
            return _.bind(function (evt) {
                this.change_property.apply(this, args);
            }, this);
        },

        remove_option: function () {
            this.model.destroy();
            MOOC.router.navigate("", {trigger: true});
        },

        reset: function () {
            this.$el
                .find('#option-id').html('').end()
                .find('#option-optiontype').val('').end()
                .find('#option-solution').val('').end()
                .find('#option-feedback').val('').end()
                .find('#option-x').val('').end()
                .find('#option-y').val('').end()
                .find('#option-width').val('').end()
                .find('#option-height').val('');
        },

        change_property: function (prop, numerical) {
            var value = this.$el.find("#option-" + prop).val(),
                self = this;
            if (value) {
                if (numerical) {
                    value = parseInt(value, 10);
                } else if (value.toLowerCase() === "true" && this.model.get("optiontype") === 'r') {
                    // Update the solution stored in the other radio models
                    _.each(
                        MOOC.views.current_index_view.collection.filter(function (model) {
                            return model.get("optiontype") === 'r' && model.get("id") !== self.model.get("id");
                        }),
                        function (radio) {
                            radio.set(prop, false);
                        }
                    );
                }

                if (this.model.get("optiontype") === 'l' && prop === "solution") {
                    prop = "text";
                }

                this.model.set(prop, value);
                this.model.save();
            }
        }

    });

    // In this variable we store the current properties view
    // so we can clean up stuff when we switch the view
    MOOC.views.current_properties_view = null;

    MOOC.views.Index = Backbone.View.extend({
        events: {
            "click #add-option": "create_option",
            "click fieldset span ": "option_click",
            "click fieldset span input": "option_click"
        },

        initialize: function () {
            var $img, url, width, height;

            _.bindAll(this, 'render', 'add', 'remove',
                      'create_option', 'select_option', 'option_click');

            this.$fieldset = this.$el.find("fieldset");

            // internal state
            this._rendered = false;

            // create an array of option views to keep track of children
            this._optionViews = [];

            // add each option to the view
            this.collection.each(this.add);

            // bind this view to the add and remove events of the collection
            this.collection.bind("add", this.add);
            this.collection.bind("remove", this.remove);
        },

        render: function () {
            var self = this;
            this._rendered = true;

            this.$fieldset.empty();
            _(this._optionViews).each(function (ov) {
                self.$fieldset.append(ov.render().el);
            });

            return this;
        },

        add: function (option) {
            var ov = new MOOC.views.OptionView({
                model: option,
                parent_view: this,
                parent_width: this.$fieldset.width(),
                parent_height: this.$fieldset.height()
            });
            this._optionViews.push(ov);

            if (this._rendered) {
                this.$fieldset.append(ov.render().el);
            }
        },

        remove: function (option) {
            var view_to_remove = _(this._optionViews).select(function (ov) {
                return ov.model === option;
            })[0];
            this._optionViews = _(this._optionViews).without(view_to_remove);

            if (this._rendered) {
                view_to_remove.remove();
            }
        },

        create_option: function () {
            var settings = {},
                option;
            settings.optiontype = this.$el.find("#option-optiontype-creation").val();
            if (settings.optiontype === 'l') {
                settings.width = 50;
                settings.height = 3;
            }
            option = new MOOC.models.Option(settings);
            this.collection.add(option);
            option.save();
        },

        select_option: function (option_element) {
            var selected = null;
            _(this._optionViews).each(function (ov) {
                if (ov.el === option_element) {
                    ov.select();
                    selected = ov;
                } else {
                    ov.unselect();
                }
            });
            if (selected !== null) {
                MOOC.router.navigate("option" + selected.model.get('id'),
                                     {trigger: true});
            }
        },

        option_click: function (event) {
            var target = event.target;
            if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
                target = target.parentNode;
            }
            this.select_option(target);
        }
    });

    MOOC.views.current_index_view = null;

    MOOC.App = Backbone.Router.extend({
        index: function () {
            if (MOOC.views.current_index_view === null) {
                MOOC.views.current_index_view = new MOOC.views.Index({
                    collection: MOOC.models.options,
                    el: $("#content-main")[0]
                });
            }

            MOOC.views.current_index_view.render();

            if (MOOC.views.current_properties_view !== null) {
                MOOC.views.current_properties_view.close();
                MOOC.views.current_properties_view.reset();
                MOOC.views.current_properties_view = null;
            }
        },

        option: function (opt) {
            var view = new MOOC.views.OptionPropertiesView({
                model: MOOC.models.options.get(parseInt(opt, 10)),
                el: $("#option-properties")[0]
            });

            if (MOOC.views.current_properties_view !== null) {
                MOOC.views.current_properties_view.close();
            }

            MOOC.views.current_properties_view = view;
            MOOC.views.current_properties_view.render();
        }
    });

    MOOC.init = function (url, options) {
        var path = window.location.pathname,
            $fieldset = $("#content-main fieldset"),
            $img = $("img.last-frame");

        MOOC.models.options = new MOOC.models.OptionList();
        MOOC.models.options.reset(options);
        MOOC.models.options.url = url;

        if ($img.length > 0) {
            $fieldset.css({ "background-image": "url(" + $img.attr("src") + ")" });
            $img.remove();
        }

        MOOC.router = new MOOC.App();
        MOOC.router.route("", "index");
        MOOC.router.route("option:option", "option");
        Backbone.history.start({root: path});

        MOOC.router.navigate("", {trigger: true});
    };
}(jQuery, Backbone, _));
