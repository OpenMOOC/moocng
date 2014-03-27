/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _, interpolate, gettext */

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

if (_.isUndefined(window.MOOC)) {
    window.MOOC = {};
}

MOOC.views = {};

MOOC.views.PRR_DESCRIPTION_MAX_LENGTH = 140;

MOOC.views.capitalize = function (text) {
    "use strict";
    return text.charAt(0).toUpperCase() + text.slice(1);
};

MOOC.views.Unit = Backbone.View.extend({

    initialize: function () {
        "use strict";
        var unit = this.model, collection = unit.get('knowledgeQuantumList');
        this._kqViews = collection.map(function (kq) {
            var kqView = MOOC.views.kqViews[kq.id], reviews = null;
            if (_.isUndefined(kqView)) {
                if (kq.get('peer_review_assignment') !== null) {
                    reviews = unit.getPeerReviewReviewsForKq(kq);
                }

                MOOC.views.kqViews[kq.id] = new MOOC.views.KnowledgeQuantum({
                    model: kq,
                    id: "kq" + kq.id,
                    reviews: reviews
                });
                kqView = MOOC.views.kqViews[kq.id];
            }
            return kqView;
        });
    },

    delegateEventsInSubViews: function () {
        "use strict";
        _(this._kqViews).each(function (kqView) {
            kqView.delegateEventsInSubViews();
        });
        this.delegateEvents();
    },

    undelegateEventsInSubViews: function () {
        "use strict";
        _(this._kqViews).each(function (kqView) {
            kqView.undelegateEventsInSubViews();
        });
        this.undelegateEvents();
    },

    render: function () {
        "use strict";
        var html,
            progress,
            helpText;

        this.$el.parent().children().removeClass("active");
        this.$el.addClass("active");

        $("#unit-title").html(this.model.get("title"));

        html = '<div class="progress progress-info" title="' + gettext('completed') + '"><div class="bar completed" style="width: 0%;"></div></div>';
        $("#unit-progress-bar").html(html);
        progress = this.model.calculateProgress({ completed: true });
        helpText = "<div><span>" + Math.round(progress) + "% " + gettext('completed') + "</span></div>";
        $("#unit-progress-bar").find("div.bar.completed").css("width", progress + "%");

        $("#unit-progress-text").html(helpText);

        $("#unit-kqs").empty();
        _(this._kqViews).each(function (kqView) {
            $("#unit-kqs").append(kqView.render().el);
        });

        return this;
    }
});

MOOC.views.unitViews = {};

MOOC.views.KnowledgeQuantum = Backbone.View.extend({
    tagName: "li",

    initialize: function (options) {
        "use strict";
        var pra = this.model.get('peerReviewAssignmentInstance');
        this.reviews = options.reviews;

        this._prrViews = _.map(this.reviews, function (review, index) {
            var prrView = MOOC.views.peerReviewReviewViews[review.id];
            if (_.isUndefined(prrView)) {

                MOOC.views.peerReviewReviewViews[review.id] = new MOOC.views.PeerReviewReview({
                    model: review,
                    index: index,
                    peerReviewAssignment: pra
                });
                prrView = MOOC.views.peerReviewReviewViews[review.id];
            }
            return prrView;
        });
    },

    delegateEventsInSubViews: function () {
        "use strict";
        _(this._prrViews).each(function (prrView) {
            prrView.delegateEvents();
        });
        this.delegateEvents();
    },

    undelegateEventsInSubViews: function () {
        "use strict";
        _(this._prrViews).each(function (prrView) {
            prrView.undelegateEvents();
        });
        this.undelegateEvents();
    },

    render_badge: function (minimum_reviewers) {
        "use strict";
        var icon = '', badge_class = '', title_attr = '', score_obj = null, score_text = '';

        if (this.reviews.length < minimum_reviewers) {
            icon = '<span class="icon-exclamation-sign icon-white"></span> ';
            title_attr = ' title="' + gettext('This score will not be applied to your final score until you get the minimum number of reviews') + '"';
        }

        score_obj = this.model.get('peer_review_score');

        if (_.isNull(score_obj)) {
            score_text = '';
            badge_class = 'important';
        } else {
            score_text = score_obj.toFixed(2);
            badge_class = (score_obj >= 5) ? 'success' : 'important';
        }

        return '<span class="badge badge-' + badge_class + ' pull-right"' + title_attr + '>' + icon + score_text + '</span>';
    },

    render_pending_badge: function () {
        "use strict";
        return '<span class="badge pull-right">' + MOOC.views.capitalize(gettext('pending')) + '</span>';
    },

    render_normal_kq: function () {
        "use strict";
        var html = [];
        if (this.model.get('completed')) {
            if (this.model.get("correct")) {
                html.push('<span class="badge badge-success pull-right"><span class="icon-ok icon-white"></span> ' + MOOC.views.capitalize(gettext('correct')) + '</span>');
            } else {
                html.push('<span class="badge badge-important pull-right"><span class="icon-remove icon-white"></span> ' + MOOC.views.capitalize(gettext('incorrect')) + '</span>');
            }
        } else {
            html.push(this.render_pending_badge());
        }
        return html.join('');
    },

    render_peer_review_kq: function () {
        "use strict";
        var html = [], pra = null, submission = null, author_reviews = 0, minimum_reviewers = 0;
        pra = this.model.get('peerReviewAssignmentInstance');

        minimum_reviewers = pra.get('minimum_reviewers');

        if (this.model.get('completed')) {
            html.push(this.render_badge(minimum_reviewers));
        } else {
            html.push(this.render_pending_badge());
        }

        if (this.model.has("_peerReviewSubmissionInstance")) {
            submission = this.model.get("_peerReviewSubmissionInstance");
        }

        if (submission !== null) {
            author_reviews = submission.get('author_reviews');

            if (this.reviews.length > 0) {
                html.push('<table class="table table-stripped table-bordered">');
                html.push('<caption>' + gettext('Reviews of your submission') + '</caption>');
                html.push('<thead><tr>');
                html.push('<th>#</th>');
                html.push('<th>' + gettext('Date') + '</th>');
                html.push('<th>' + gettext('Score') + ' </th>');
                html.push('</tr></thead>');
                html.push('<tbody></tbody>');
                html.push('</table>');
            } else {
                html.push('<p>' + gettext('You have not received any review yet') + '</p>');
            }

            html.push("<p>");
            html.push(interpolate(gettext("You have sent %(sent_reviews)s reviews of the %(mandatory_reviews)s mandatory reviews."), {
                sent_reviews: author_reviews,
                mandatory_reviews: minimum_reviewers
            }, true));
            html.push("</p>");

            if (author_reviews < minimum_reviewers) {
                html.push("<p><a href='" + MOOC.peerReview.urls.prReview + "#kq" + this.model.get("id") + "'>" + gettext('Do more reviews') + "</a>.</p>");
            }

        }
        return html.join("");
    },

    render: function () {
        "use strict";
        var html = ["<strong>" + this.model.truncateTitle(40) + "</strong>"];

        this.$el.attr("title", this.model.get('title'));

        if (this.reviews !== null) {
            html.push(this.render_peer_review_kq());
        } else {
            html.push(this.render_normal_kq());
        }

        this.$el.html(html.join(""));

        if (this.reviews !== null) {
            _.each(this._prrViews, function (prrView) {
                this.$('table tbody').append(prrView.render().el);
            }, this);
        }

        return this;
    }
});

MOOC.views.kqViews = {};


MOOC.views.PeerReviewReview = Backbone.View.extend({
    tagName: "tr",

    events: {
        "click td a": "show_details"
    },

    initialize: function (options) {
        "use strict";
        this.index = options.index;
        this.peerReviewAssignment = options.peerReviewAssignment;
    },

    render: function () {
        "use strict";
        var html = [];

        html.push('<td>' + (this.index + 1)  + '</td>');
        html.push('<td>' + this.model.get('created').format('LLLL')  + '</td>');
        html.push('<td><a class="btn btn-small pull-right" href="#"><span class="icon-eye-open"></span> ' + gettext('View details') + '</a>' + this.model.get('score')  + '</td>');

        this.$el.html(html.join(""));
        return this;
    },

    show_details: function (event) {
        "use strict";
        var criteria = '';
        event.preventDefault();

        criteria = _.map(this.model.get('criteria'), function (criterion, index) {
            var html = ["<tr>"], criterionObj = null, description;

            criterionObj = this.peerReviewAssignment.get('_criterionList').at(index);
            description = MOOC.models.truncateText(criterionObj.get('description'), MOOC.views.PRR_DESCRIPTION_MAX_LENGTH);

            html.push("<td>" + (index + 1) + "</td>");
            html.push("<td><p>" + criterionObj.get('title') + "</p>");
            html.push("<p><small>" + description + "</small></p></td>");
            html.push("<td>" + criterion[1] + "</td>");
            html.push("</tr>");
            return html.join("");
        }, this);

        $("#review-details-modal")
            .find("time").text(this.model.get('created').format('LLLL')).end()
            .find("tbody").html(criteria.join("")).end()
            .find(".final-score").text(this.model.get('score')).end()
            .find("blockquote pre").text(this.model.get('comment')).end()
            .modal('show');
    }
});

MOOC.views.peerReviewReviewViews = {};
