/*jslint browser: true, nomen: true */
/*global MOOC: true, Backbone, jQuery, _ */

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
                solution: ''
            };
        }
    });

    MOOC.models.OptionList  = Backbone.Collection.extend({
        model: MOOC.models.Option
    });

    MOOC.views = {};

    MOOC.views.OptionView = Backbone.View.extend({
        tagName: 'span',
        className: 'option',
        padding: 5,
        option_types: {
            't': 'text',
            'c': 'checkbox',
            'r': 'radio'
        },

        initialize: function () {
            _.bindAll(this, 'render', 'drag', 'stop',
                      'select', 'unselect', 'is_out', 'change');
            this.parent_width = this.options.parent_width;
            this.parent_height = this.options.parent_height;

            this.$el.draggable({
                drag: this.drag,
                stop: this.stop
            });
        },

        render: function () {
            var optiontype = this.model.get('optiontype'), attributes = {
                type: this.option_types[optiontype],
                value: this.model.get('solution'),
                style: [
                    "width: " + this.model.get("width") + "px;",
                    "height: " + this.model.get("height") + " px;"
                ].join(" ")
            };
            if (optiontype === 'c' || optiontype === 'r') {
                if (this.model.get('solution') === 'True') {
                    attributes.checked = 'checked';
                }
            } else {
                attributes.value = this.model.get('solution');
            }

            this.$el.empty().append(this.make("input", attributes));
            this.$el
                .width(this.model.get("width") + this.padding * 2)
                .css({
                    left: (this.model.get('x') - this.padding) + "px",
                    top: (this.model.get('y') - this.padding) + "px",
                    padding: this.padding + "px",
                    position: 'absolute'
                })
                .find('input').change(this.change);

            return this;
        },

        is_out: function (position) {
            return ((position.left + this.padding) < 0
                    || (position.top + this.padding) < 0
                    || (position.left + this.padding) > this.parent_width
                    || (position.top + this.padding) > this.parent_height);
        },

        drag: function () {
            var position = this.$el.position();
            if (this.is_out(position)) {
                this.$el.addClass('out');
            } else {
                this.$el.removeClass('out');
            }
        },

        stop: function () {
            var position = this.$el.position();
            if (this.is_out(position)) {
                this.model.destroy();
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
                value = '';
            if (optiontype === 'c' || optiontype === 'r') {
                value = _.isUndefined($input.attr('checked')) ? false : true;
            } else {
                value = $input.val();
            }
            this.model.set("solution", value);
            this.model.save();
        }

    });

    MOOC.views.Index = Backbone.View.extend({
        events: {
            "click #add-option": "create_option",
            "click fieldset span ": "select_option",
            "click fieldset span input": "select_option"
        },

        initialize: function () {
            var $img, url, width, height;

            _.bindAll(this, 'render', 'add', 'remove', 'create_option', 'select_option');

            // Put the img as a background image of the fieldset
            this.$fieldset = this.$el.find("fieldset");
            $img = this.$fieldset.find("img");
            url = $img.attr("src");
            width = $img.width();
            height = $img.height();
            this.$fieldset.width(width).height(height).css({"background-image": "url(" + url + ")"});
            $img.remove();

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
            var option = new MOOC.models.Option({
                optiontype: this.$el.find("#option-type").val()
            });
            this.collection.add(option);
            option.save();
        },

        select_option: function (event) {
            var target = event.target;
            if (target.tagName === 'INPUT') {
                target = target.parentNode;
            }
            _(this._optionViews).each(function (ov) {
                if (ov.el === target) {
                    ov.select();
                } else {
                    ov.unselect();
                }
            });
        }
    });

    MOOC.App = Backbone.Router.extend({
        index: function () {
            var view = new MOOC.views.Index({
                collection: MOOC.models.options,
                el: $("#content-main")[0]
            });
            view.render();
        },

        option: function (opt) {

        }
    });

    MOOC.init = function (url, options) {
        var path = window.location.pathname;
        MOOC.models.options = new MOOC.models.OptionList();
        MOOC.models.options.reset(options);
        MOOC.models.options.url = url;

        MOOC.router = new MOOC.App();
        MOOC.router.route("", "index");
        MOOC.router.route("option:option", "option");
        Backbone.history.start({root: path});

        MOOC.router.navigate("", {trigger: true});
    };
}(jQuery, Backbone, _));
