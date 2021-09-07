// /////////////////////////////////////////////////////////////////////////////////////////////////
// YH PLUGIN
////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function(){ 

}); // END OF DOCUMENT READY
//

function send_to_mobile() {
	var channel = $("select[name='send-to-mobile-channel']").val();
	var text = $("#send-to-mobile-text").html();
	text = text.replaceAll("</div>","").replaceAll("<div>","\n");
	var posturl = uri('linkurl') + 'boards-sms/post_slack';
	$.post( posturl, {text:text,channel:channel}).done( function(data) { h_dialog.notice(data); });	
}

function send_to_mobile_file() {
	var posturl = uri('linkurl') + 'boards-ajax/file_select';
	$.post( posturl, { f_path : DOCU_ROOT}).done( function(data) { 
		if(data) {
			var channel = $("select[name='send-to-mobile-channel']").val();
			var posturl = uri('linkurl') + 'boards-sms/post_slack_file';
			$.post( posturl, {up_file:data,channel:channel}).done( function(rst) { h_dialog.notice(rst+" 파일이 전송되었습니다",{notice_stop:true}); });
			h_dialog.notice("[ "+data+" ] 파일 전송을 시작합니다",{notice_stop:true})	
		} 
	});	
}