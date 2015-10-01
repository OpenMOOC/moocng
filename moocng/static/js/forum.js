$(document).ready(function () {
    $(".addButton").click(function(){
        $(".postFrom").toggle();
        $(this).hide();
    });

    $(".cancelPost").click(function(){
        $(".postFrom").toggle();
        $(".addButton").show();
    });

    var load = true;
    var page = 10;
    $(window).scroll(function() {
        if($(window).scrollTop() + $(window).height() == $(document).height() && load) {
            load = false;
            $.ajax({
                url : "/course/" + course_slug + "/forum/loadMorePosts/" + page,
                success: function(response) {
                    if(response.trim() != ""){
                        $(".posts").append(response)
                        page += 10;
                        load = true;
                    }
                }
            });
        }
    });
});

$(".reply").click(function(e){
    e.preventDefault();
    $(this).parent().parent().parent().parent().removeClass('openEdit').toggleClass('openReply');
});

$(".cancelReply").click(function(e){
    e.preventDefault();
    $(this).parent().parent().parent().parent().parent().toggleClass('openReply');
});

$(".edit").click(function(e){
    e.preventDefault();
    var target = $(e.target);
    if (!target.hasClass('edit')) {
        target = target.parent().parent();
    }
    target.parent().parent().parent().parent().removeClass('openReply').toggleClass('openEdit');
});

$(".cancelEdit").click(function(e){
    e.preventDefault();
    var target = $(e.target);
    target.parent().parent().parent().parent().parent().toggleClass('openEdit');
});

$(".karma a").click(function(e){
    e.preventDefault();
    var target = e.target;
    if (!target.href) {
        target = e.target.parentElement;
    }
    var header = {};
    if(geolocation){
      header = {
        'context_geo_lat': geolocation.coords.latitude,
        'context_geo_lon': geolocation.coords.longitude
      }
    }
    $.ajax({
      url: target.href,
      headers: header,
      complete: function(result){
        if(result !== false){
            var karma_elem = $(target).parent();
            var votes_elem = karma_elem.find('span');
            var vote = $(target).data('vote');
            if(karma_elem.hasClass('upvoted') && vote === -1){
                vote = 0;
            } else if (karma_elem.hasClass('downvoted') && vote === 1) {
                vote = 0;
            }

            votes_elem.html(result);
            switch(vote){
                case 1: karma_elem.addClass('upvoted');
                        break;
                case 0: karma_elem.removeClass('upvoted');
                        karma_elem.removeClass('downvoted');
                        break;
                case -1: karma_elem.addClass('downvoted');
                        break;
            }
        }
      }
    });
});

$(".flag").click(function(e){
    e.preventDefault();
    var target = e.target;
    if (!target.href) {
        target = $(e.target).find('a')[0];
    }
    if (confirm(forum_trans.confirm_flag)){
        $.get(target.href).always(function(){
            location.reload();
        });
    }
});

$(".delete").click(function(e){
    e.preventDefault();
    var target = $(e.target);
    if (!target.attr('href')) {
        target = target.find('a');
    }
    var replies = target.parent().parent().siblings('.subreplies')
    if (!replies.length)
        replies = target.parent().parent().parent().siblings('.replies');
    if (replies.length && replies.children().length){
        alert(forum_trans.cant_delete_children);
    }else{
        if (confirm(forum_trans.confirm_delete)){
            $.get(target.attr('href')).always(function(){
                location.reload();
            });
        }
    }
});

$(".pinned").click(function(e){
    e.preventDefault();
    var target = e.target;
    if (!target.href) {
        target = e.target.parentElement;
    }
    $.get(target.href).always(function(){
        location.reload();
    });
});

$(".repliesToggle").click(function(e){
    //$(this).parent().parent().toggleClass("collapsed");
    $(this).siblings('.subreplies').slideToggle();
});
