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
                optiontype: null,
                x: null,
                y: null,
                width: null,
                height: null,
                answer: null
            };
        }
    });

    MOOC.models.OptionList  = Backbone.Collection.extend({
        model: MOOC.models.Option
    });

    MOOC.models.options = new MOOC.models.OptionList();

    MOOC.views = {};

    MOOC.views.OptionView = Backbone.View.extend({
        tagName: 'span',
        className: 'option',
        padding: 5,

        initialize: function () {
            _.bindAll(this, 'render', 'stop');
            this.parent_width = this.options.parent_width;
            this.parent_height = this.options.parent_height;
        },

        render: function () {
            var input = this.make("input", {
                type: this.model.get('optiontype'),
                value: this.model.get('answer'),
                style: [
                    "left: " + this.model.get('x') + "px;",
                    "top: " + this.model.get('y') + "px;",
                    "width: " + this.model.get("width") + "px;",
                    "height: " + this.model.get("height") + " px;"
                ].join(" ")
            });
            this.$el.append(input);
            this.$el
                .width(this.model.get("width") + this.padding * 2)
                .css("padding", this.padding + "px");
            this.$el.draggable({
                stop: this.stop
            });
            return this;
        },

        stop: function () {
            var position = this.$el.position();
            if ((position.left + this.padding) < 0
                || (position.top + this.padding) < 0
                || (position.left + this.padding) > this.parent_width
                || (position.top + this.padding) > this.parent_height) {
                this.model.collection.remove(this.model);
            } else {
                this.model.set("x", position.left);
                this.model.set("y", position.top);
            }
        }

    });

    MOOC.views.Index = Backbone.View.extend({
        events: {
            "click #add-option": "create_option"
        },

        initialize: function () {
            var $img, url, width, height;

            _.bindAll(this, 'render', 'add', 'remove', 'create_option');

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
            this.collection.add({
                optiontype: this.$el.find("#option-type").val(),
                x: 0,
                y: 0,
                answer: ''
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

    MOOC.init = function (options) {
        var path = window.location.pathname;

        MOOC.models.options.reset(options);

        MOOC.router = new MOOC.App();
        MOOC.router.route("", "index");
        MOOC.router.route("option:option", "option");
        Backbone.history.start({root: path});

        MOOC.router.navigate("", {trigger: true});
    };
}(jQuery, Backbone, _));
