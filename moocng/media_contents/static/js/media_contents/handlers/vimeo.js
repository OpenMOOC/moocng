/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _, $f */

if (_.isUndefined(window.MOOC)) {
    window.MOOC = {};
}
if (_.isUndefined(MOOC.views)) {
    MOOC.views = {};
}
if (_.isUndefined(MOOC.views.players)) {
    MOOC.views.players = {};
}

MOOC.views.players.Vimeo = Backbone.View.extend({
    el: $('#vimeoplayer'),

    initialize: function (options) {
        "use strict";
        this.kq = options.kq;
        this.try_to_initialize_until_success();
    },

    try_to_initialize_until_success: function () {
        "use strict";
        var iframe,
            that = this;

        try {
            iframe = $('#vimeoplayer')[0];
            this.player = $f(iframe);
            // When the player is ready, add listeners for pause, finish, and playProgress
            this.player.addEvent('ready', function () {
                that.player.addEvent('finish', function (event) {
                    MOOC.players_listener.trigger('mediaContentFinished', MOOC.views.kqViews[that.kq]);
                });
            });
        } catch (err) {
            setTimeout(this.try_to_initialize_until_success, 1000);
        }
    },

    destroyPlayer: function (callback) {
        "use strict";
        this.player = null;
        callback();
    }
});

MOOC.views.players.Vimeo.test = function (node) {
    "use strict";
    return $(node).find("#vimeoplayer").length > 0;
};
