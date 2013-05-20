/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _, YT */

if (_.isUndefined(window.MOOC)) {
    window.MOOC = {};
}
if (_.isUndefined(MOOC.views)) {
    MOOC.views = {};
}
if (_.isUndefined(MOOC.views.players)) {
    MOOC.views.players = {};
}

MOOC.views.players.Youtube = Backbone.View.extend({
    el: $('#ytplayer'),

    initialize: function (options) {
        "use strict";
        this.kq = options.kq;
        _.bindAll(this, "onPlayerStateChange", "onPlayerReady");
        this.player = new YT.Player("ytplayer", {
            events: {
                'onReady': this.onPlayerReady,
                'onStateChange': this.onPlayerStateChange
            }
        });
    },

    onPlayerStateChange: function (event) {
        "use strict";
        if (event.data === 0) {
            MOOC.players_listener.trigger('mediaContentFinished', MOOC.views.kqViews[this.kq]);
        }
    },

    onPlayerReady: function () {
        "use strict";
        this.player.unMute();
    },

    destroyPlayer: function (callback) {
        "use strict";
        var player = this.player;
        player.mute();
        player.stopVideo();
        $(player.getIframe()).hide();
        setTimeout(function () { // IE HACK
            player.destroy();
            callback();
        }, 1000);
        this.player = null;
    }
});

MOOC.views.players.Youtube.test = function (node) {
    "use strict";
    return $(node).find("#ytplayer").length > 0;
};
