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

    initialize: function (view) {
        "use strict";
        this.view = view;
        this.try_to_initialize_until_success();
    },
    try_to_initialize_until_success: function () {
        "use strict";
        var iframe,
            player,
            that = this;

        try {
            iframe = $('#vimeoplayer')[0];
            player = $f(iframe);
            // When the player is ready, add listeners for pause, finish, and playProgress
            player.addEvent('ready', function () {
                player.addEvent('finish', function (event) {
                    MOOC.players_listener.trigger('mediaContentFinished', that.view);
                });
            });
        } catch (err) {
            setTimeout(this.try_to_initialize_until_success, 1000);
        }
    }
});
