var geolocation = null;
var deviceInfo = {
	type: "unknown",
	os: "unknown",
	orientation: "unknown"
};
var geolocation_advised = false;
var geolocation_allowed = undefined;

$(function(){
	// Device Type
    if(device.desktop()){
    	deviceInfo.type = "desktop";
    }else if(device.tablet()){
		deviceInfo.type = "tablet";
    }else if(device.mobile()){
    	deviceInfo.type = "mobile";
    }
	// Device OS
	if(deviceInfo.type != "desktop"){
		if(device.ios()){
			deviceInfo.os = "ios";
		}else if(device.android()){
			deviceInfo.os = "android";
		}else if(device.blackberry()){
			deviceInfo.os = "blackberry";
		}else if(device.windows()){
			deviceInfo.os = "windows";
		}else if(device.fxos()){
			deviceInfo.os = "firefoxos";
		}else if(device.meego()){
			deviceInfo.os = "meego";
		}
	}
	// Orientation
	if(device.landscape()){
		deviceInfo.orientation = "landscape";
	}else if(device.portrait()){
		deviceInfo.orientation = "portrait";
	}

	// Update geolocation
	if(!noGeolocation){
		// Check geolocation permission
		if(window.sessionStorage && window.localStorage){
			geolocation_advised = sessionStorage.getItem('geolocation_advised') == "true";
			geolocation_allowed = localStorage.getItem('geolocation_allowed');
		}

	    if(navigator.geolocation && (geolocation_advised || geolocation_allowed == 'true')){
	        navigator.geolocation.getCurrentPosition(function(position){
	        		localStorage.setItem('geolocation_allowed', true);
	            	geolocation = position;
	        	},function(error){
	        		if (error.code == error.PERMISSION_DENIED)
	        			localStorage.setItem('geolocation_allowed', false);
	        	},{timeout: 2000}
	        );
	    }else{
	    	showGeolocationAdvise();
	    }
	}
});

function getBrowserName(){
    var ua= navigator.userAgent, tem,
    M= ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
    if(/trident/i.test(M[1])){
        tem=  /\brv[ :]+(\d+)/g.exec(ua) || [];
        return 'ie';
    }
    if(M[1]=== 'Chrome'){
        tem= ua.match(/\bOPR\/(\d+)/)
        if(tem!= null) return 'opera';
    }
    M= M[2]? [M[1], M[2]]: [navigator.appName, navigator.appVersion, '-?'];
    //if((tem= ua.match(/version\/(\d+)/i))!= null) M.splice(1, 1, tem[1]);
    //return M.join(' ');
    return M[0];
}

function showGeolocationAdvise(){
	var browser = getBrowserName().toLowerCase();
	if(deviceInfo.type != "desktop"){
		browser = browser+'-'+deviceInfo.os;
	}

	var browserName;
	switch(browser){
		case 'msie': 	browserName = "Internet Explorer";
					 	break;
		case 'safari-ios': 	browserName = "Safari";
							break;
		case 'chrome-ios':
		case 'chrome-android': 	browserName = "Chrome";
		default: 	browserName = getBrowserName();
	}

	var browser_guide = geoadvice_translate.browser_guide[browser];
	var broser_help_link = geoadvice_translate.browser_help_link[browser];
	var video_file = "geolocation_";
	video_file += geolocation_allowed == undefined ? 'firsttime' : 'blocked';
	video_file += '_' + browser;
	video_file += '_en_640';
	video_file +=  browser != 'opera' ? '.mp4' : '.webm';

	var confirmDiv = '<div id="geolocation_advise" class="modal geoadvise"> \
		<div class="modal-header"><a href="#">'+ geoadvice_translate.ok +'</a></div> \
		<div class="modal-body fixedHeight"> \
			<img src="/static/img/geolocation.png"> \
			<h1>'+ geoadvice_translate.greeting +' <span>'+ geoadvice_translate.greeting_2 +'.</span></h1>';
		if(browser_guide){
			confirmDiv += '<div class="video '+ browser +'"><video autoplay loop> \
					<source src="/static/video/'+ video_file +'"> \
				</video></div> \
				<p class="label">'+ geoadvice_translate.video_label +' '+ browserName +'.';
			if(broser_help_link)
				confirmDiv += ' <a href="'+ broser_help_link +'" target="_blank">'+ geoadvice_translate.more_info +'</a>.';
			confirmDiv += '</p></video> \
				<p>'+ geoadvice_translate.browser_details +' '+ browserName +'. '+ browser_guide +'.</p> \
			</div>';
		}
		confirmDiv +='<div class="modal-footer"> \
			<h2>'+ geoadvice_translate.whylocation +'</h2> \
			<p>'+ geoadvice_translate.whylocation_explain +'.</p> \
			</div></div>';
	var $confirmDiv = $(confirmDiv);
	$('body').append($confirmDiv);

    confirmModal = $confirmDiv.modal({
        show: false,
        backdrop: "static",
        keyboard: false
    });
    setTimeout(function(){ confirmModal.modal("show"); }, 1000);

    $confirmDiv.find('.modal-header a').click(function(){
    	confirmModal.modal("hide");
    	navigator.geolocation.getCurrentPosition(function(position){
        		localStorage.setItem('geolocation_allowed', true);
            	geolocation = position;
        	},function(error){
        		if (error.code == error.PERMISSION_DENIED)
        			localStorage.setItem('geolocation_allowed', false);
        	},{timeout: 2000}
        );
    });
	sessionStorage.setItem('geolocation_advised', true);
}

function sendHistoryEntry(course_id, options){
	var currentCourse = course_id;
	var delay = 2500;
	var url = window.location.href;

	options = options || {};
	if(options.delay !== undefined)
		delay = options.delay;
	if(options.url !== undefined)
		url = options.url;

	window.setTimeout(function(){
		if (currentCourse){
			var lat = 0.0;
			var lon = 0.0;
			var data;
			if (geolocation){
				lat = geolocation.coords.latitude;
				lon = geolocation.coords.longitude;
			}
			data = {
				lat: lat,
				lon: lon,
				timestamp: new Date().getTime(),
				url: url,
				dev_type: deviceInfo.type,
				dev_os: deviceInfo.os,
				dev_orientation: deviceInfo.orientation,
				course_id: currentCourse || ''
			};

			$.ajax({
				url: '/api/v1/history/',
				type: 'POST',
	        	contentType: "application/json",
				data: JSON.stringify(data)
			});
		}else{
			console.log('Current course not defined');
		}
	}, delay);
}
