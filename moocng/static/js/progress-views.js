/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _ */

// Copyright 2012 Rooter Analysis S.L.
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

    render: function () {
        "use strict";
        var html,
            progress,
            helpText;

        this.$el.parent().children().removeClass("active");
        this.$el.addClass("active");

        $("#unit-title").html(this.model.get("title"));

        html = '<div class="progress progress-info" title="' + MOOC.trans.progress.completed + '"><div class="bar completed" style="width: 0%;"></div></div>';
        html += '<div class="progress progress-success" title="' + MOOC.trans.progress.correct + '"><div class="bar correct" style="width: 0%;"></div></div>';
        $("#unit-progress-bar").html(html);

        progress = this.model.calculateProgress({ completed: true });
        helpText = "<div><span>" + Math.round(progress) + "% " + MOOC.trans.progress.completed + "</span></div>";
        $("#unit-progress-bar").find("div.bar.completed").css("width", progress + "%");

        progress = this.model.calculateProgress({ completed: true, correct: true });
        helpText += "<div><span>" + Math.round(progress) + "% " + MOOC.trans.progress.correct + "</span></div>";
        $("#unit-progress-bar").find("div.bar.correct").css("width", progress + "%");

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

    render_badge: function (minimum_reviewers) {
        "use strict";
        var icon = '', score = 0, badge_class = '';

        if (this.reviews.length < minimum_reviewers) {
            icon = '<i class="icon-exclamation-sign icon-white" title="' + MOOC.trans.progress.score_dont_apply + '"></i> ';
        }

        badge_class = (score >= 2.5) ? 'success' : 'important';

        return '<span class="badge badge-' + badge_class + ' pull-right">' + icon + score + '</span>';
    },

    render: function () {
        "use strict";
        var html = [
                "<b>" + this.model.truncateTitle(40) + "</b>"
            ],
            peer_review,
            minimum_reviewers;

        if (this.reviews !== null) {
            minimum_reviewers = this.model.get('peerReviewAssignmentInstance').get('minimum_reviewers');

            html.push(this.render_badge(minimum_reviewers));

            if (this.reviews.length > 0) {
                html.push('<table class="table table-stripped table-bordered">');
                html.push('<caption>' + MOOC.trans.progress.current_reviews + '</caption>');
                html.push('<thead><tr>');
                html.push('<th>#</th><th>' + MOOC.trans.progress.date + '</th><th>Score</th>');
                html.push('</tr></thead>');
                html.push('<tbody></tbody>');
                html.push('</table>');
            } else {
                html.push('<p>' + MOOC.trans.progress.no_reviews_yet + '</p>');
            }

            html.push('<p>' + MOOC.trans.progress.minimum_reviews + ': <strong>' +  minimum_reviewers + '</strong></p>');
        } else {

            if (this.model.get('completed')) {
                if (this.model.get("correct")) {
                    html.push('<span class="badge badge-success pull-right"><i class="icon-ok icon-white"></i> ' + MOOC.views.capitalize(MOOC.trans.progress.correct) + '</span>');
                } else {
                    html.push('<span class="badge badge-important pull-right"><i class="icon-remove icon-white"></i> ' + MOOC.trans.progress.incorrect + '</span>');
                }
            } else {
                html.push('<span class="badge pull-right">' + MOOC.trans.progress.pending + '</span>');
            }
        }

        this.$el.attr("title", this.model.get('title'));
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
        html.push('<td>' + this.model.get('created')  + '</td>');
        html.push('<td><a class="btn btn-small pull-right" href="#"><i class="icon-eye-open"></i> View details</a>' + this.model.get('score')  + '</td>');

        this.$el.html(html.join(""));
        return this;
    },

    show_details: function (event) {
        "use strict";
        var criteria = '';
        event.preventDefault();

        criteria = _.map(this.model.get('criteria'), function (criterion, index) {
            var html = ["<tr>"], criterionObj = null;
            criterionObj = this.peerReviewAssignment.get('_criterionList').at(index);
            html.push("<td>" + (index + 1) + "</td>");
            html.push("<td>" + criterionObj.get('description') + "</td>");
            html.push("<td>" + criterion[1] + "</td>");
            html.push("</tr>");
            return html.join("");
        }, this);

        $("#review-details-modal")
            .find("time").text(this.model.get('created')).end()
            .find("tbody").html(criteria.join("")).end()
            .find("blockquote").text(this.model.get('comment')).end()
            .modal('show');
    }
});

MOOC.views.peerReviewReviewViews = {};
