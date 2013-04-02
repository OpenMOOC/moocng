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
        var iframe,
            player;

        iframe = $('#vimeoplayer')[0];
        player = $f(iframe);
        // When the player is ready, add listeners for pause, finish, and playProgress
        player.addEvent('ready', function () {
            player.addEvent('finish', function (event) {
                MOOC.players_listener.trigger('mediaContentFinished', view);
            });
        });
    }
});
