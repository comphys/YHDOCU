var editing_mode=false ;
$(document).ready(function() {
	$("#tool-bar-on-off").dblclick(function(e){ e.stopPropagation(); toolbar_toggle();} );

	$("#selectedMarkL").click(function(){JYHEDITOR.clearDocuSelect();});

	$("#tool-bar").on("contextmenu", function(e) {e.preventDefault(); $("#contextMenu").css({left:mouse_X-20,top:mouse_Y}).toggle();}).on("click",function(){$("#contextMenu").hide();});

	$("[data-myfile]").mouseover(function(){$(this).addClass("body-myfile");}).mouseout(function(){$(this).removeClass("body-myfile");}).click(
		function(e){ 
			if(editing_mode) return;
			var _fname = $(this).text();
			var _f_path = $(this).attr("data-myfile");
			var _f_in = _f_path + '/' + _fname;
			if(e.ctrlKey)  {clipBoard(_f_path); h_dialog.notice("<b>"+[_fname]+"</b><span style='color:gray'> path was copied to ClipBoard</span>"); return; }
			else if(e.altKey) {var posturl = uri('linkurl') + 'boards-ajax/win_folder';	$.post(posturl, { exe_file : _f_path }); return;}
			else {
				var posturl = uri('linkurl') + 'boards-ajax/win_exe';
				$.post(posturl, { exe_file : _f_in });
			}
		}
	).on("contextmenu", function(e){
			if(editing_mode) return;
			e.preventDefault();
			var _fol=$(this).attr("data-myfile").replace(DOCU_ROOT+'/','');
			var url = uri('linkurl')+'filemanager/move/'+_fol;	
			winopen2(url,1200,640);
		}
	);

	$("[data-mydocu]").mouseover(function(){$(this).addClass("body-mydocu");}).mouseout(function(){$(this).removeClass("body-mydocu");})
		.click(function(){ var url='docueditor/docuopen/p='+$(this).attr('data-mydocu')+'/f='+$(this).text(); winopen(url,'950','750',$(this).text()); });

	$(".img-thumbs,.img-click").click(function(){ if(editing_mode) return; var url=$(this).attr("src"); url = url.replace('thumb_',''); window.imageIndex = imageRotate.indexOf(url); h_dialog.image(url); });

}); 


function open_dialog(title,src,imode,opt) {
	var ex = new Array("editor_tcolor","editor_sign");
	if ( !ex.includes(src) && ! docuSelected ) {h_dialog.notice("선택된 개체가 없습니다"); return; }
	var xx, yy;
	if(window.innerWidth > 1350) {xx = 900, yy = 50}
	else {xx=300, yy=150}
	var url = uri('linkurl') + 'docueditor/dialog/dialog='+src+'/imode='+imode;
	var o = {id:src,h_title:title,close_btn:true,footer:false,x:xx,y:yy};
	if(opt != null) $.extend(o,opt); 
	h_dialog.load(url,o);
}

function docu_save(op) {
	var file_name='';
	var file_path = $("input[name='docu_path']").val();
	if(op == 'new') { 
		file_name = prompt('새파일 이름을 입력하세요'); 
	}	
	else { file_name = $("input[name='docu_name']").val(); }
	if(!file_name) file_name = prompt("파일이름을 입력하세요");
	if(!file_name.match(/\.docu$/i)) file_name += '.docu';

	var save_txt = $("#A4DOCS").html();	
	var posturl = uri('linkurl') + 'docueditor/save';
	$.post(posturl, { f_name : file_name, f_path : file_path, f_txt : save_txt });

	$("input[name='docu_name']").val(file_name);
	h_dialog.notice('<b>'+file_name +'</b> 파일을 저장하였습니다');
}

function docu_print() {
	JYHEDITOR.clearDocuSelect(); 	$(".rightClickMenu").hide();

	$(".A4h,.A4w").removeClass("page").addClass("page-print"); 
	$("#tool-bar").hide();
	$("#print-icon").hide();
	$("body").attr("style","margin:0; padding:0; background-color:white");
	window.print();
	$("#print-icon").show();
	$("#tool-bar").show();
	$(".A4h,.A4w").removeClass("page-print").addClass("page"); 
	$("body").attr("style","margin:0; padding:0; background-color:#acacac");
}

function open_editor() {
	var furl = uri('linkurl')+'filemanagers-fedit/body_source/mode=docu';
	var specs = "width=1200,height=700,status=no,menubar=no,location=no,titlebar=no,scrollbars=yes";
	window.open(furl,'html_editor', specs);
}

function show_Menu( op ) {
	$(".rightClickMenu").hide();
	$("#" + op ).css({left:mouse_X - 20 , top:mouse_Y + 10}).toggle();
}

function form_basic(opt) {
	switch (opt){
		case  'A4h' : $("#A4DOCS").append('<div class="page A4h"><p>글입력</p></div>');  break;	
		case  'A4w' : $("#A4DOCS").append('<div class="page A4w"><p>글입력</p></div>'); break;
	}
	$("#contextMenu").hide();
	JYHEDITOR.clearDocuSelect();
}

function open_style_edit() {
	var furl = uri('linkurl')+"filemanagers-fedit/open/docuCss.css"; 
	var specs = "height=700,width=1200,status=no,menubar=no,location=no,titlebar=no,scrollbars=yes";
	window.open(furl,'css_editor', specs);
}

var wide_on = false;
function toggle_page_setting() {
	if( ! wide_on ) $("#selectedMarkR,#choicedMark").attr("style","width:310mm");
	else $("#selectedMarkR,#choicedMark").attr("style","");
	wide_on = !wide_on;
	JYHEDITOR.selectedMark();
}

function toolbar_toggle() {
	if(!JYHEDITOR_status) {
		$("#tool-bar").show();JYHEDITOR.start('A4DOCS');
		editing_mode=true; }
	else { $("#tool-bar").hide();JYHEDITOR.stop('A4DOCS'); editing_mode=false;} 
}

JYHEDITOR.UserFunc2 = function() {
	docu_save();
}

JYHEDITOR.UserTable = function() {
	if(docuSelectedType != 'TD') return;
	$("#tableMenu").css({left:mouse_X - 20 , top:mouse_Y }).toggle();
}