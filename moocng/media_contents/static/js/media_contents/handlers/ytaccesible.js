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

MOOC.views.players.YoutubeAccesible = Backbone.View.extend({
    el: $('#ytplayer'),

    initialize: function (options) {
        "use strict";
        this.kq = options.kq;
        this.transcripts = options.transcripts;
        _.bindAll(this, "onPlayerStateChange", "onPlayerReady", "destroyPlayer");
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
         // IE HACK
        var player = this.player;
        try {
            player.mute();
            player.stopVideo();
        } catch (e) {
            // nothing
        }
        $(player.getIframe()).hide();
        setTimeout(function () {
            try {
                player.destroy();
            } catch (e) {
                // nothing
            }
            callback();
        }, 500);
        this.player = null;
    }
});

MOOC.views.players.YoutubeAccesible.test = function (node) {
    "use strict";
    return $(node).find("#ytplayer").length > 0;
};
