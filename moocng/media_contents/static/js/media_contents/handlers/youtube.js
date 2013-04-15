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

function triggerFinish(event) {
    "use strict";
    if (event.data === 0) {
        MOOC.players_listener.trigger('mediaContentFinished', event.target.view);
    }
}

MOOC.views.players.Youtube = Backbone.View.extend({
    el: $('#ytplayer'),
    initialize: function (view) {
        "use strict";
        this.view = view;
        this.try_to_initialize_until_success();
    },
    try_to_initialize_until_success: function () {
        "use strict";
        try {
            this.player = new YT.Player('ytplayer');
            this.player.addEventListener("onStateChange", "triggerFinish");
            this.player.view = this.view;
        } catch (err) {
            setTimeout(this.try_to_initialize_until_success, 1000);
        }
    }
});
