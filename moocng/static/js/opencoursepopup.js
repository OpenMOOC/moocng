function showOpenCourseHelp(){
	var helpDiv = '<div id="helpForm" class="modal geoadvise"> \
        <div class="modal-header"><a href="#" class="close">'+ alwaysopen_translate.ok +'</a></div> \
		<div class="modal-body fixedHeight"> \
			<img src="/static/img/ECO_icon_info_tiempo.svg"> \
			<h1>'+ alwaysopen_translate.greeting +' <span>'+ alwaysopen_translate.greeting_2 +'</span></h1> \
            <p>'+ alwaysopen_translate.info +'</p> \
            <p>'+ alwaysopen_translate.footer +'</p> \
		</div> \
		</div>';
		
	var $helpDiv = $(helpDiv);
	$('body').append($helpDiv);

    helpModal = $helpDiv.modal({
        show: false,
        backdrop: "static",
        keyboard: false
    });
    setTimeout(function(){ helpModal.modal("show"); }, 0);    

    $helpDiv.find('a.close').click(function(){
    	helpModal.modal("hide");
    	setTimeout(function(){ helpModal.remove(); }, 500);
    });
}

$('#alwaysopen_info').click(function(e){
	e.preventDefault();
	showOpenCourseHelp();
});

var opencourses_advised = false;
$(function(){
    var isopencourse = $('#alwaysopen_info').length > 0;
    if(isopencourse){
        if(window.localStorage){
            opencourses_advised = localStorage.getItem('opencourses_advised') == "true";
        }

        if(!opencourses_advised){
            showOpenCourseHelp();
            localStorage.setItem('opencourses_advised', true);
        }
    }
});