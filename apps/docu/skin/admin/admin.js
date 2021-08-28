// /////////////////////////////////////////////////////////////////////////////////////////////////
// YH ADMIN
////////////////////////////////////////////////////////////////////////////////////////////////////
$(document).ready(function(){ 
	$(".colorpicker").on('click' , function(e) {  var idx = $(this).attr('name'); open_colorpicker(idx); });	
});

function open_colorpicker(idx) {
	
	var url = uri('linkurl') + 'admins-ajax/colorpicker/name='+idx; 
	h_dialog.load(url,{	id:'colorPicker', x:mouse_X -400,y: mouse_Y - 200, footer:false, width: 356, height: 210,h_title:'Color Picker by JYH', close_btn :true});
}

function selectC(sel,target){ var selector = "input[name='"+ target + "']";	$( selector ).val(sel.value);	}

function select_dbfield(sel,target) {
	selectC(sel,target);
	var posturl = uri('linkurl') + 'admin-ajax/dbfield';
	$.post( posturl, { db_tbl : sel.value }).done(function(data) { $("input[name='input_sel']").val(data); });
}

function select_dbinput(sel,target) {
	selectC(sel,target);
	var posturl1 = uri('linkurl') + 'admin-ajax/dbfield';
	$.post( posturl1, { db_tbl : sel.value }).done(function(data) { $("input[name='input_sel']").val(data); });

	var posturl2 = uri('linkurl') + 'admin-ajax/dbinput';
	$.post( posturl2, { db_tbl : sel.value }).done(function(data) { $("#csv-data").html(data); });
}

function select_dbwork(sel,target){
	selectC(sel,target);
	var op = sel.value; 
	switch(op) {
		case 'SELECT' : $("#div_set").hide(); $("#div_key").hide(); $("#div_val").hide(); $("#div_qry").hide();
		                $("#div_sel").show(); $("#div_wre").show(); break;
		case 'UPDATE' : $("#div_set").show(); $("#div_key").hide(); $("#div_val").hide(); $("#div_qry").hide();
		                $("#div_sel").hide(); $("#div_wre").show(); break;
		case 'INSERT' : $("#div_set").hide(); $("#div_key").show(); $("#div_val").show(); $("#div_qry").hide();
		                $("#div_sel").hide(); $("#div_wre").hide(); break;
		case 'QUERY'  : $("#div_set").hide(); $("#div_key").hide(); $("#div_val").hide(); $("#div_qry").show();
		                $("#div_sel").hide(); $("#div_wre").hide(); break;					
	}
}

function output_dbwork() {
	var op = $("input[name='input_op']").val(); if(!op) return; 
	var posturl = uri('linkurl') +  'admin-ajax/dboutput';
	var post_val = {};
	switch(op) {
		case 'SELECT' : post_val = { db_tbl : $("input[name='input_tbl']").val(), db_sel : $("input[name='input_sel']").val(), db_wre : $("input[name='input_wre']").val() }; break;
		case 'UPDATE' : post_val = { db_tbl : $("input[name='input_tbl']").val(), db_set : $("input[name='input_set']").val(), db_wre : $("input[name='input_wre']").val() }; break;
		case 'INSERT' : post_val = { db_tbl : $("input[name='input_tbl']").val(), db_key : $("input[name='input_key']").val(), db_val : $("input[name='input_val']").val() }; break;
		case 'QUERY'  : post_val = { db_qry : $("input[name='input_qry']").val() }; break;
	}
	post_val.op = op; 
	post_val.db_lmt = $("input[name='input_lmt']").val(); 
	$.post(posturl , post_val).done( function(data) { $("#db_output").html(data); }); 
}

function output_dbinput() {
	var tbl = $("input[name='input_tbl']").val(); if(!tbl) return; 
	var fld = $("input[name='input_sel']").val(); if(!fld) return; 
	var posturl = uri('linkurl') +  'admin-ajax/csv_to_db';
	var post_val = {};
	post_val.tbl = tbl;
	post_val.fld = fld;
	$.post(posturl , post_val).done( function(data) { $("#csv-data").html(data); }); 
}

function bkup_op(sel){
	var op = sel.value; 
	if(op=='ALL') $("#backup_op").hide();
	if(op=='TABLE' || op=='STRUCTURE' || op=='TBL_SET') $("#backup_op").show();
}

function bkup_work(op,fsql,sel) {
	var posturl = uri('linkurl') + 'admin-ajax/dbbakup';
	var post_val = {};
	if(op=='del') {
		post_val = { operation : 'delete' , fsql : fsql }; 
		h_dialog.confirm('정말로 삭제하시겠습니까?', 
			{ x : mouse_X - 240, y : mouse_Y - 80,
			  buttons : [
				{ text : '삭제', 
				  call : function(a) {
							$.post(posturl , post_val).done( function() { $(sel).parent().parent().remove(); });
							h_dialog.close(a);
						}
				},
				{ text : '취소', call : function(a) {h_dialog.close(a);} }
			  ]	
			}
		);
	}

	if(op=='rst') {
		post_val = { operation : 'restore' , fsql : fsql }; 
		h_dialog.confirm('정말로 복원하시겠습니까?', 
			{ x : mouse_X - 240, y : mouse_Y - 80,
			  buttons : [
				{ text : '복원', call : function(a) {$.post(posturl , post_val);	h_dialog.close(a);}},
				{ text : '취소', call : function(a) {h_dialog.close(a);} }
			  ]	
			}
		);
	}
}

function check_FormInput(f)
{
	var i, addnum='' ;
	if(arguments.length == 0) { h_dialog.alert("글쓰기 폼의 전달인자가 빠졌습니다."); return true; }
	else {
			for(i=1; i < arguments.length ; i+= 2){ 
				if(!f[arguments[i]].value) { 
					f[arguments[i]].focus(); 
					h_dialog.notice("<span style='color:#ff0000;font-weight:bold'>"+arguments[i+1] + "</span> 을 입력하여 주십시오."); 
					return true; 
				}
			}
	}
}