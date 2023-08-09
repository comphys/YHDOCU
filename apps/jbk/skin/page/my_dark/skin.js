// /////////////////////////////////////////////////////////////////////////////////////////////////
// YH PLUGIN
////////////////////////////////////////////////////////////////////////////////////////////////////
// JYH JQUERY PLUGIN :: comma { init : put comma and bind keyup event, put_comma, clear : remove ',' }
(function($){ var YH_comma={ init:function(){ return this.each(function(){$(this).comma('put_comma'); $(this).on("keyup", YH_comma.put_comma );});}, put_comma:function(){ var $this = $(this); var tmp=$this.val().split('.'); var minus=false; var str=new Array(); if(tmp[0].indexOf('-') >= 0){ minus=true;tmp[0]=tmp[0].substring(1, tmp[0].length);} var v=tmp[0].replace(/,/gi,''); for(var i=0;i<=v.length;i++){ str[str.length]=v.charAt(v.length-i); if(i%3==0 && i!=0 && i!=v.length){ str[str.length]='.';}} str=str.reverse().join('').replace(/\./gi,',');if(minus) str ='-'+str; tmp=(tmp.length==2)? str+'.'+tmp[1]:str; var chx = tmp.replace(/,/gi,''); if ((isNaN(chx) && chx !='-') || chx ==' ' ) {$this.val(''); return;}	$this.val(tmp);},clear:function(){ var tmp=$(this).val(); tmp=tmp.replace(/,/gi,''); $(this).val(tmp);}};$.fn.comma =function(method) {if(YH_comma[method]) { return YH_comma[method].apply(this,Array.prototype.slice.call(arguments,1));}else if(typeof method === 'object' || ! method){ return YH_comma.init.apply( this,arguments);}else{ $.error( 'Method ' +method+' does not exist on jQuery.comma');}};})(jQuery);

$(document).ready(function(){ 
	$(".i-date").Zebra_DatePicker({format:'Y-m-d', offset:[-150,280], first_day_of_week : 0}); 
	$(".i-number").comma('init');
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

function open_backtest_folder() {
	var _fol = '';
	var url = uri('linkurl')+'filemanager/move/개인자료/주식투자/백테스트';

	winopen2(url,1200,640);	
}