// /////////////////////////////////////////////////////////////////////////////////////////////////
// YH PLUGIN
////////////////////////////////////////////////////////////////////////////////////////////////////
// JYH JQUERY PLUGIN :: comma { init : put comma and bind keyup event, put_comma, clear : remove ',' }
(function($){ var YH_comma={ init:function(){ return this.each(function(){$(this).comma('put_comma'); $(this).on("keyup", YH_comma.put_comma );});}, put_comma:function(){ var $this = $(this); var tmp=$this.val().split('.'); var minus=false; var str=new Array(); if(tmp[0].indexOf('-') >= 0){ minus=true;tmp[0]=tmp[0].substring(1, tmp[0].length);} var v=tmp[0].replace(/,/gi,''); for(var i=0;i<=v.length;i++){ str[str.length]=v.charAt(v.length-i); if(i%3==0 && i!=0 && i!=v.length){ str[str.length]='.';}} str=str.reverse().join('').replace(/\./gi,',');if(minus) str ='-'+str; tmp=(tmp.length==2)? str+'.'+tmp[1]:str; var chx = tmp.replace(/,/gi,''); if ((isNaN(chx) && chx !='-') || chx ==' ' ) {$this.val(''); return;}	$this.val(tmp);},clear:function(){ var tmp=$(this).val(); tmp=tmp.replace(/,/gi,''); $(this).val(tmp);}};$.fn.comma =function(method) {if(YH_comma[method]) { return YH_comma[method].apply(this,Array.prototype.slice.call(arguments,1));}else if(typeof method === 'object' || ! method){ return YH_comma.init.apply( this,arguments);}else{ $.error( 'Method ' +method+' does not exist on jQuery.comma');}};})(jQuery);

// JYH JQUERY PLUGIN :: liveEdit { init : bind click and keydown, clear : unbind all event }
(function($){ var YH_liveEdit={ init:function(){ return this.each(function(){ $(this).on('dblclick', function() { liveEdit_ori_val = $(this).text(); $(this).attr('contenteditable',true); $(this).addClass('list-edit-on');});$(this).on('keydown', function(e) { if(e.which == 13) { $(this).attr('contenteditable',false); $(this).removeClass('list-edit-on'); var bid = uri(0); var no  = $(this).attr('data-no'); var fid = $(this).attr('data-fid');	var val = $(this).text(); var posturl = uri('linkurl') + 'boards-ajax/live_edit'; $.post(posturl, { bid : bid, no : no, fid : fid, val: val});}if(e.which==27) { $(this).text(liveEdit_ori_val); $(this).attr('contenteditable',false); $(this).removeClass('list-edit-on'); }});});}, clear:function(){ return this.each(function(){ $(this).off(); });}}; $.fn.liveEdit =function(method) {if(YH_liveEdit[method]) { return YH_liveEdit[method].apply(this,Array.prototype.slice.call(arguments,1));} else if(typeof method === 'object' || ! method){ return YH_liveEdit.init.apply( this,arguments);} else { $.error( 'Method ' +method+' does not exist on jQuery.comma');}};})(jQuery);

var sms_selected

$(document).ready(function(){ 
// ------------------------------------------------------------------------------------------------
if(uri('method') == 'list')	{ // LIST PART when Document is ready
// ------------------------------------------------------------------------------------------------
	$("#search_input").on('keydown',  function(event) {if(event.which == 13) list_search(); } );
	$("#search_input2").on('keydown', function(event) {if(event.which == 13) list_search2(); } );
// ------------------------------------------------------------------------------------------------
} else if (uri('method') == 'body') {  // BODY PART when Document is ready
// ------------------------------------------------------------------------------------------------

	$("#toggle_reply").click(function(e){
		if(JYHEDITOR.reply_mode) {$("#YHBreplyDiv").hide(); JYHEDITOR.miniClose(); JYHEDITOR.reply_mode = false}
		else {
			$("#YHBreplyDiv").show(); JYHEDITOR.miniInit("wysiwygYHBreplyEditor"); $("#wysiwygYHBreplyEditor").focus();
			JYHEDITOR.reply_mode = true;
		}
	});

	$("[data-myfile]").mouseover(function(){$(this).addClass("body-myfile");}).mouseout(function(){$(this).removeClass("body-myfile");}).click(
		function(e){ 

			var _fname = $(this).text();
			var _f_path = $(this).attr("data-myfile");
			var _f_in = _f_path + '/' + _fname; 
			if(e.altKey || e.ctrlKey) {var posturl = uri('linkurl') + 'boards-ajax/win_folder';	
				$.post(posturl, { exe_file : _f_path }).done(function(data){if(data=='NFND') h_dialog.notice("?????? ????????? ???????????? ????????????");});}
			else {
				var posturl = uri('linkurl') + 'boards-ajax/win_exe';		
				$.post(posturl, { exe_file : _f_in }).done(function(data){if(data=='NFND') h_dialog.notice("?????? ????????? ???????????? ????????????");});
			}
		}
	).on("contextmenu", function(e){
			e.preventDefault();
			var _fname = $(this).text();
			var url = uri('linkurl')+'filemanager/';
			var _fol=$(this).attr("data-myfile"); 
			if(_fol == DOCU_ROOT) url += 'home';
			else url += 'move/'+_fol.replace(DOCU_ROOT+'/',''); 
			var posturl = uri('linkurl') + 'boards-ajax/checkdir';	
			$.post(posturl, { check : _fol }).done(function(data){
				if(data=='NFND') h_dialog.notice("?????? ????????? ???????????? ????????????");
				else winopen2(url,1200,640);
			});
		}
	);
	
	$("[data-folder]").click(function(e){ 
		if(e.altKey) {var posturl = uri('linkurl') + 'boards-ajax/win_folder'; var f_path= DOCU_ROOT + '/' + $(this).attr("data-folder"); $.post(posturl, { exe_file : f_path }); return;}
		else {var url=uri('linkurl')+'filemanager/move/'+$(this).attr("data-folder"); winopen2(url,1200,640);}
	});

	$("[data-mydocu]").mouseover(function(){$(this).addClass("body-mydocu");}).mouseout(function(){$(this).removeClass("body-mydocu");})
		.click(function(){ var url='docueditor/docuopen/p='+$(this).attr('data-mydocu').replace(/\//g,'-')+'/f='+$(this).text(); winopen(url,'950','750',$(this).text()); }
	);

	$("[data-myprog]").mouseover(function(){$(this).addClass("body-mydocu");}).mouseout(function(){$(this).removeClass("body-mydocu");})
		.click(function(){ var p=$(this).attr('data-myprog').replace(/\//g,'-'); var url='filemanager-fedit/open_path/p='+p+'/f='+$(this).text(); winopen(url,'1200','750',$(this).text()); });

	$("[data-myimage]").mouseover(function(){$(this).addClass("body-myimage");})
		              .mouseout(function(){$(this).removeClass("body-myimage");})
					  .click(function(e){ 
						var f_name = $(this).text(); 
						var f_path = $(this).attr("data-myimage");
						if(e.ctrlKey)  {clipBoard(f_path+'/'+f_name); h_dialog.notice("<b>"+[f_name]+"</b> was copied to ClipBoard"); return; }
						var url= (f_path)? '/DOCU_ROOT'+ f_path.replace(DOCU_ROOT,'') + '/'+ f_name :  '/DOCU_ROOT/'+ f_name;
						window.imageIndex = imageRotate.indexOf(url); h_dialog.image(url); });
						
	$("#search_input2").on('keydown', function(event) {if(event.which == 13) list_search2(); } );

	$(".img-thumbs").click(function(e){ var url=$(this).attr("src"); url = url.replace('????????????/',''); 
		if(e.altKey) {var f_path = url.split('/'); f_path.pop(); f_path =  f_path.join('/'); f_path = f_path.replace('/DOCU_ROOT',DOCU_ROOT); 
					  var posturl = uri('linkurl') + 'boards-ajax/win_folder';	$.post(posturl, { exe_file : f_path }); return;}
		else { window.imageIndex = imageRotate.indexOf(url); h_dialog.image(url); }
	});
// ------------------------------------------------------------------------------------------------
} else if (uri('method') == 'write' || uri('method') == 'modify' || uri('method') == 'add_body'  ) { // WRITE PART 
// ------------------------------------------------------------------------------------------------
	$(".i-date").Zebra_DatePicker({format:'Y/m/d', offset:[-150,280], first_day_of_week : 0}); 
	$(".i-number").comma('init');
	$("#editor-tools-bar").on("contextmenu", function(e) {	e.preventDefault();	$("#contextMenu").css({left:mouse_X-20,top:mouse_Y}).toggle();});	
// ------------------------------------------------------------------------------------------------
} // COMMON PART
// ------------------------------------------------------------------------------------------------
	$(".list-mobile").click(function(){	sms_selected = this; $(this).css("backgroundColor","#2d335b").css("font-weight","bold");open_dialog('???????????????','send_sms','ajax')});
	$(".list-live-edit").liveEdit();
	$(".list-subject").on("click", function() {var sc = $(this).attr('data-href');var page=uri('page'), sort = uri('sort'), sort1 = uri('sort1');var search = uri('search'); search_f = uri('search_f');if(page)  sc += '/page='+page; if(sort)  sc += '/sort='+sort; if(sort1) sc += '/sort1='+sort1;if(search) sc += '/search='+search;if(search_f) sc += '/search_f='+search_f;location.href = sc;});
	$(".list-add").click(function(){ var cell_value = parseInt($(this).text().replace(/[^0-9]/g,"")); var sum_value = parseInt($("#cell-sum").text().replace(/[^0-9]/g,""));if(isNaN(sum_value)) sum_value = 0;if($(this).css("font-weight") == "bold" || $(this).css("font-weight") == "700"){sum_value = Number(sum_value) - Number(cell_value);	$(this).css({ fontWeight:"normal", backgroundColor :""}) ; 	}else {	sum_value = Number(sum_value) + Number(cell_value);	$(this).css({ fontWeight:"bold", backgroundColor:'#e74c3c'}) ; }if(sum_value) { var sum_val = String(sum_value); sum_val = sum_val.replace(/(\d)(?=(?:\d{3})+(?!\d))/g,'$1,'); $("#cell-sum").html(sum_val);}	else $("#cell-sum").html('');});
	$("#send-to-mobile-text").on('keydown',function(e){if(e.which==27) $(this).html('');});
//
//	
}); // END OF DOCUMENT READY
//
//

// ------------------------------------------------------------------------------------------------
if(uri('method') == 'list')	{ 
// ------------------------------------------------------------------------------------------------
function excel_list() {
	var url = uri('linkurl') + 'excel_output/get_list/' + uri(0);
	h_dialog.load(url,{x:mouse_X-200,y:mouse_Y+10}); 
}

function excel_output() {
	var bid = uri(0); 
	var posturl = uri('linkurl') + 'excel_output/index';
	h_dialog.cover();
	$.post( posturl, { bid : bid }).done(function(data) {
		h_dialog.closeCover(); 
		h_dialog.notice(data);} 
	);
}
// ------------------------------------------------------------------------------------------------
} else if (uri('method') == 'body') {  
// ------------------------------------------------------------------------------------------------

// /////////////////////////////////////////////////////////////////////////////////////////////////
// YH EDITOR ??? ????????? html ????????? ??????
////////////////////////////////////////////////////////////////////////////////////////////////////
var REPLYEDITOR = {
	reply : function(sel) {
//		if(JYHEDITOR.small_editor) {JYHEDITOR.miniClose(); $("#YHBreplyDiv").hide();} 
		if(JYHEDITOR.reply_mode) {$("#YHBreplyDiv").hide();JYHEDITOR.miniClose(); JYHEDITOR.reply_mode = false;}
		var targetR = 'reply_' + sel;
		JYHEDITOR.miniInit(targetR)
		var toolbar = "<div id='reply-toolbar'>"
			toolbar += "<div class='btn-group'>";
			toolbar += "<span class='btn-transparent' title='???????????????' onclick=\"JYHEDITOR.rangeControl();JYHEDITOR.dialog('???????????? ??????','editor_color','ajax')\" ><i class='fa fa-pencil'></i></span>";
			toolbar += "<span class='btn-transparent' title='?????????????????????' onclick=\"JYHEDITOR.rangeControl();JYHEDITOR.dialog('?????????????????? ??????','editor_bcolor','ajax')\"><i class='fa fa-tint'></i></span></div>";
			toolbar += "<div class='btn-group'>";
			toolbar += "<span class='btn-transparent' title='?????? ??????' onclick=\"JYHEDITOR.cmd('bold')\"><i class='fa fa-bold'></i></span>";
			toolbar += "<span class='btn-transparent' title='????????????' onclick=\"JYHEDITOR.cmd('italic')\"><i class='fa fa-italic'></i></span>";
			toolbar += "<span class='btn-transparent' title='?????? ??????' onclick=\"JYHEDITOR.cmd('underline')\"><i class='fa fa-underline'></i></span>";
			toolbar += "<span class='btn-transparent' title='???????????????' onclick=\"JYHEDITOR.cmd('strikethrough')\"><i class='fa fa-strikethrough'></i></span></div>";
			toolbar += "<div class='btn-group'>";
			toolbar += "<span class='btn-transparent' title='???????????????' onclick=\"JYHEDITOR.link()\"><i class='fa fa-link'></i></span>";
			toolbar += "<span class='btn-transparent' title='HTML ??????' onclick=\"JYHEDITOR.viewSource()\"><i class='fa fa-edit'></i></span>";
			toolbar += "<span class='btn-transparent' title='?????? ?????????' onclick=\"JYHEDITOR.cmd('removeformat')\"><i class='fa fa-undo'></i></span>";
			toolbar += "<span class='btn-transparent' title='?????? ?????????' onclick=\"JYHEDITOR.clearDocu()\"><i class='fa fa-square-o'></i></span>";
			toolbar += "</div>";
			toolbar += "<div class='btn-group'>";
			toolbar += "<span class='btn-transparent' title='????????????' style='color:#0098e1' onclick=\"modifyReply(" + sel + ")\"><i class='fa fa-hdd-o'></i></span>";
			toolbar += "<span class='btn-transparent' title='????????????' style='color:#FF6F6F'  onclick=\"REPLYEDITOR.reply_cancel()\"><i class='fa fa-sign-out'></i></span>";
			toolbar += "</div>";
			toolbar += "</div>";
		$(JYHEDITOR.docu).parent().prepend(toolbar);
	},
	
	reply_cancel	: function(){if(JYHEDITOR.docu) { $('#reply-toolbar').remove(); JYHEDITOR.miniClose(); }
	}
}

function submitReply(wysiwigeditor,uname)
	{
		var bid = uri(0); 
		var no  = uri('no');
		var docu = $id(wysiwigeditor);
		var replyTxt = docu.innerHTML;
		var posturl = uri('linkurl') + 'boards-ajax/reply_save';
		$.post( posturl, { bid : bid, no : no, uname : uname, replyTxt : replyTxt }).done( function() { location.reload(); }); 
	
	}
function modifyReply(n)
	{
		var bid = uri(0);
		$("#reply-toolbar").remove();
		var docu = JYHEDITOR.docu;
		var replyTxt = docu.innerHTML;
		var posturl = uri('linkurl') + 'boards-ajax/reply_modify';
		$.post(posturl, { bid : bid, rno : n, replyTxt : replyTxt}).done( function(data) { location.reload(); }); 
	
	}

function editReply(sel)
	{
		h_dialog.confirm('????????? ?????? ?????? ?????? ?????? ??? ????????????',
			{ 
			  overlay:false,x:mouse_X-300, y:mouse_Y-50, 
			  buttons:  [
							{text : '????????????', call: function(a) { h_dialog.close(a); }},
							{text : '????????????', call: function(a) { 
								REPLYEDITOR.reply(sel); h_dialog.close(a);
							}},
							{text : '????????????', call: function() { remove_reply(sel); h_dialog.close(a); }}
						]
		});
	}
function remove_reply(sel) {
		var rno = sel;
		var bid = uri(0); 
		var no  = uri('no'); 
		var posturl = uri('linkurl') + 'boards-ajax/reply_delete';
		$.post( posturl, { bid : bid, no : no, rno : rno }).done( function(data) { location.reload(); }); 
}

function delete_confirm(url) 
{	
	$("#contextMenu").hide();
	h_dialog.confirm('????????? ?????? ???????????????????',
		{ 
		   buttons:  [
						{text : '????????????', call: function(a) { h_dialog.close(a); }},
						{text : '????????????', call: function() { location.href = url; }}
					]
	});
}

// ------------------------------------------------------------------------------------------------
} else if (uri('method') == 'write' || uri('method') == 'modify' || uri('method') == 'add_body') { // WRITE PART 
// ------------------------------------------------------------------------------------------------

function show_Menu( op ) {
	$(".rightClickMenu").hide();
	$("#" + op ).css({left:mouse_X - 20 , top:mouse_Y + 10}).toggle();
}


// /////////////////////////////////////////////////////////////////////////////////////////////////
// ?????? ????????? ?????? ??? ??????
// /////////////////////////////////////////////////////////////////////////////////////////////////

function check_FormInput(f)
{
	var i, addnum='' ;
	if(arguments.length == 0) { h_dialog.alert("????????? ?????? ??????????????? ???????????????."); return true; }
	else {
			for(i=1; i < arguments.length ; i+= 2){ 
				if(!f[arguments[i]].value) { 
					f[arguments[i]].focus(); 
					h_dialog.alert("<span style='color:#ff0000;font-weight:bold'>"+arguments[i+1] + "</span> ??? ???????????? ????????????."); 
					return true; 
				}
			}
	}

	$(".i-number").each(function() {$(this).comma('clear'); });
}
// ------------------------------------------------------------------------------------------------
} // COMMON PART
// ------------------------------------------------------------------------------------------------
function sort_go(field){ 

	var sort = uri('sort'), sort1 = uri('sort1'), page = uri('page'), no = uri('no');
	var url  = uri('linkurl') + uri('control') + '/' + uri('method') + '/' + uri(0); 
	if(!page ) page = 1; url += '/page='+page;
	if(!sort && !sort1) url += '/sort='+ field;
	if( sort ) url += '/sort1='+ field; 
	if( sort1) url += '';
	if( no ) url += '/no='+ no;
	location.href = url;
}


function list_search() {
	var search = $("input[name='search_value']").val();
	if(! search ) return;
	var url = uri('linkurl') + 'board/list/' + uri(0) ;
	url += '/search=' + search; 
	location.href = url; 
}

function list_search2() { 
	var search = $("input[name='search_value']").val();
	if(! search ) return;
	var search_f = $("input[name='search_field']").val();
	var url = uri('linkurl') + 'board/list/' + uri(0) ;
	url += '/search=' + search; 
	if(search_f) url += '/search_f=' + search_f;
	location.href = url; 
}

function open_dialog(title,src,imode,opt) {
	var ex = new Array("editor_tcolor","editor_sign","send_sms");
	if ( !ex.includes(src) && ! docuSelected && ! JYHEDITOR.reply_mode) {h_dialog.notice("????????? ????????? ????????????"); return; }
	var xx, yy;
	if(window.innerWidth > 1350) {xx = 880, yy = 50} else {xx=300, yy=150}
	var url = uri('linkurl') + 'boards-editor/dialog/bid='+uri(0)+'/dialog='+src+'/imode='+imode;
	var o = {id:src,h_title:title,close_btn:true,footer:false,x:xx,y:yy};
	if(opt != null) $.extend(o,opt); 
	h_dialog.load(url,o);
}

function open_editor() {
	var furl = uri('linkurl')+'filemanagers-fedit/body_source/bid='+uri(0)+'/no='+uri('no')+'/mode='+uri('method');
	var specs = "width=1200,height=700,status=no,menubar=no,location=no,titlebar=no,scrollbars=yes";
	window.open(furl,'html_editor', specs);
}

function open_folder() {
	var _fol = '';
	var url = uri('linkurl')+'filemanager/';

	if(typeof docuSelected == 'undefined') {url += 'home';}
	else { 
		if($(docuSelected).attr("data-myfile")) {var _fol=$(docuSelected).attr("data-myfile").replace(DOCU_ROOT+'/',''); url += 'move/'+_fol;} 
		else {url += 'home'}
	}

	winopen2(url,1200,640);	
}

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
			$.post( posturl, {up_file:data,channel:channel}).done( function(rst) { h_dialog.notice(rst+" ????????? ?????????????????????",{notice_stop:true}); });
			h_dialog.notice("[ "+data+" ] ?????? ????????? ???????????????",{notice_stop:true})	
		} 
	});	
}