(function($){ 
	var YH_liveRename={ 
		init:function(){ 
			return this.each(function(){ 
				var f_oname; 
				// F1 key : 112, ESC key : 27, F5 : 116 (copy), F6 : 117 (move)
				$(this).on('dblclick', function() { 
						var f_name = $(this).text();
						insert_to_wbody(f_name);
						f_oname=(F_PATH)? F_PATH+'/'+f_name:f_name; $("#temporary_file").text(f_oname); 
						Storage.a('CopyPasteFile',f_oname);$(this).attr('contenteditable',true).addClass('rename-edit-on').focus();}); 
				$(this).on('keydown', function(event) { 
					if(event.which == 27)  {$(this).attr('contenteditable',false).removeClass('rename-edit-on');} 
					if(event.which == 13)  {$(this).attr('contenteditable','false').removeClass('rename-edit-on'); 
						var posturl = uri('linkurl') + 'filemanager/file_rename'; 
						var f_rname = $(this).text(); 
						$.post( posturl, { f_oname : f_oname, f_rname : f_rname } ).done(function(){list_renew();});}
					if(event.which == 116) { event.preventDefault(); Copy_Move_file(this,'copy'); } 
					if(event.which == 117) { event.preventDefault(); Copy_Move_file(this,'move'); } 
				}   
				);  // end of keydown

				}); // end of each
				},  // end of init

		clear:function(){ return this.each(function(){ $(this).off(); });}};	

$.fn.liveRename =function(method) { if(YH_liveRename[method]) { return YH_liveRename[method].apply(this,Array.prototype.slice.call(arguments,1));} else if(typeof method === 'object' || ! method){ return YH_liveRename.init.apply( this,arguments);} else { $.error( 'Method ' +method+' does not exist on jQuery.comma');}};})(jQuery);

$(document).ready(function(){ $(".list-file-edit").liveRename(); 
	var temp_file   = Storage.r('CopyPasteFile');    $('#temporary_file').text(temp_file);
	var temp_folder = Storage.r('TargetFolderName'); if(temp_folder) temp_folder=temp_folder.replace(ROOT,'HOME'); $('#temporary_folder').text(temp_folder);
});

$(document).ready(function(){
	$("#exp_title").on("contextmenu", function(e) {	e.preventDefault();	$("#contextMenu").css({left:mouse_X, top:mouse_Y }).toggle();}).on("click",function(){$("#contextMenu").hide();});
	$("#bottom-tool-bar").on("contextmenu", function(e) {e.preventDefault(); $("#contextMenu2").css({left:mouse_X}).toggle();}).on("click",function(){$("#contextMenu2").hide();});

	$(".file-icon").click(function(){ var sel = $(this).parent().next(); file_run(sel); }); 

	$(".file-delete").click(function(){	var $this = $(this); var f_name = $this.parent().prev().prev().prev().text();	f_name = $.trim(f_name);var ax_file = uri('linkurl')+"filemanager/del_file" ;	var post_val = {};post_val = { operation : 'del_file' , f_name : f_name }; 	h_dialog.confirm("<span style='color:red'>" + f_name +"</span> 파일을 정말로 삭제하시겠습니까?",{x: mouse_X - 400, y: mouse_Y - 70, 	buttons	: [{ text : '삭제', call : function(a) {$.post(ax_file , post_val).done(function(data) {if(data=='delete_ok') $this.parent().parent().remove();	});	h_dialog.close(a);}},h_dialog.cancel_button]});});

	$(".file-down").click(function(){ $(this).css("color","red"); });

	$(".file-tool").click(function(){ var sel = $(this).parent().prev().prev().prev(); file_tool(sel); });

	fileDropDown();
});

function file_run(sel) {
	var f_name = sel.text();
	f_name = $.trim(f_name);
	if(f_name.match(/\.(php|htm|html|js|css|txt|py)$/i)) {open_edit(f_name); }	
	else if(f_name.match(/\.docu$/i)){
		var f_path = CUR_PATH.replace(ROOT,'DOCU_ROOT')
		f_path = f_path.replace(/\//g,'-');
		var url = 'docueditor/docuopen/p='+f_path+'/f='+f_name;
		var ttt = new Date();winopen(url,950,700,ttt);
	}else if(f_name.match(/\.(jpg|png|gif|jpeg)$/i)) {
		var url = (F_PATH)? F_PATH + '/' + f_name : f_name;
		url = '/DOCU_ROOT/' +  url ;
		var iid = src_filter(f_name);
		if($("#"+iid)) h_dialog.close(iid);
		h_dialog.image(url,{id:iid,overlay:false});
		Storage.a('FileManagerUserImageURL',url);
	}else {
		var ax_file = uri('linkurl')+"filemanager/file_exec" ;
		var post_val = { f_name : f_name };$.post(ax_file,post_val);
	}
}

function insert_to_wbody(f_name) {
	var mydocu = '<span '; 
	if(f_name.match(/\.docu$/i)) { mydocu += 'data-mydocu="'; } 
	else if(f_name.match(/\.(jpg|png|gif|jpeg)$/i))   { mydocu += 'data-myimage="'; } 
	else if(f_name.match(/\.(php|js|html|py|css)$/i)) { mydocu += 'data-myprog="'; } 
	else  { mydocu += 'data-myfile="'; } 
	mydocu += CUR_PATH +'">' + f_name + '</span>';
	Storage.a('InsertToWriteBody',mydocu);
}

function open_dialog(title,src,imode,opt) {
	var url = uri('linkurl') + 'filemanager/dialog='+src+'/imode='+imode;
	var o = {id:src,h_title:title,close_btn:true,footer:false,x:400,y:150};
	if(opt != null) $.extend(o,opt); 
	h_dialog.load(url,o);
}

function file_tool(sel) {
	var f_name = sel.text(); 
	f_name = $.trim(f_name);
	Storage.a('FileTool_FileName',f_name);
	if(f_name.match(/\.(jpg|png|gif|jpeg)$/i)) {
		var url = uri('linkurl') + 'filemanager/dialog/dialog=file_img';
		var o = {id:'FILE_IMAGE',h_title:'썸즈네일 생성',close_btn:true,footer:false,x:mouse_X-320,y:mouse_Y-12};
		h_dialog.load(url,o);
	}	
}


function open_edit(f_name,width,height) {
	var furl = uri('linkurl')+"filemanagers-fedit/open/" + f_name; 
  	if(!width) width='1200';
  	if(!height) height='700';
	var specs = "height="+height+",width="+width+",status=no,menubar=no,location=no,titlebar=no,scrollbars=yes";
	window.open(furl,'_blank', specs);
}

function del_folder() {
	var ax_file = uri('linkurl')+"filemanager/del_file" ;
	var post_val = {};
	post_val = { operation : 'del_folder' }
	$.post(ax_file , post_val).done( function(data) { if(data) location.href= uri('linkurl')+"filemanager/up" ; }); 	
}

function rename_folder() {
	$('#contextMenu').hide();

	var opt ={ 
		x:'350px', y : '80px', b_title:'폴더의 새이름',
		doit: function(a) { 
			var new_folder = $('#h_prompt_' + a).val();
			if( new_folder != '' ) {
				var ax_file = uri('linkurl')+"filemanager/rename_folder" ;
				var post_val = { new_folder : new_folder };
				$.post(ax_file , post_val).done(function(data) { location.href= uri('linkurl')+"filemanager/up" ; }); 
			}
		}
	};
	h_dialog.prompt('폴더의 새이름을 입력하세요',opt);
}

function add_file(op) {
	$('#contextMenu').hide();
	var opt ={ 
		x:'350px', y : '80px', 
		doit : function(a) { 
				var new_name = $('#h_prompt_' + a).val();
				if( new_name !='') { 
					var ax_file = uri('linkurl')+"filemanager/add_file" ;
					var post_val = { operation : op, new_file_name : new_name };
					$.post(ax_file , post_val).done( function(data) {  if(data=="OK") list_renew();});
				}
			}
	};
	var ask = (op=='file')? '새파일 이름을 입력하세요' : '새폴더 이름을 입력하세요';
	opt.b_title = (op=='file')? '새파일 이름' : '새폴더 이름';
	h_dialog.prompt(ask,opt);
}  

function save_ftp_time(sel) {
	var cur_time = $.trim($(sel).text());
	var post_val = {};
	post_val = { ftp_time : cur_time }
	var ax_file = uri('linkurl') + "filemanager/save_config" ;
	$.post(ax_file , post_val).done( function() { list_renew(); });
}

function save_now_time() {
	var d = new Date();
	var cur_time = d.format("yyyy/MM/dd HH:mm:ss");
	var post_val = {};
	post_val = { ftp_time : cur_time }
	var ax_file = uri('linkurl') + "filemanager/save_config" ;
	$.post(ax_file , post_val).done( function() { list_renew(); });
}


// Drag And Drop File Upload

function fileDropDown(){
	var dropZone = $(document);
	//Drag기능 
	dropZone.on('dragenter',function(e){e.stopPropagation();e.preventDefault();dropZone.css('background-color','blue');});
	dropZone.on('dragleave',function(e){e.stopPropagation();e.preventDefault();dropZone.css('background-color','yellow');});
	dropZone.on('dragover', function(e){e.stopPropagation();e.preventDefault();dropZone.css('background-color','red');});
	dropZone.on('drop',     function(e){e.preventDefault();	dropZone.css('background-color','black');
		
		var files = e.originalEvent.dataTransfer.files;
		if(files != null){
			if(files.length < 1){	alert("폴더 업로드 불가");	return;	}
		}
		uploadFile(files);
		});
}


function uploadFile(files){
	var formData = new FormData();
	formData.append('drop_file', files[0]);
	formData.append('save_dir', CUR_PATH);
	h_dialog.cover();
	$.ajax({
		url: uri('linkurl') + 'filemanager/file_dropUp' ,
		data:formData,
		type:'POST',
		enctype:'multipart/form-data',
		processData:false,
		contentType:false,
		cache:false,
		xhr: function() {
				var xhr = $.ajaxSettings.xhr();
				xhr.upload.onprogress = function(e) {
				var percent = (e.loaded * 100 / e.total).toFixed(1) + '%';
                
				$("#progress_index").text(percent); 
			}
			return xhr;
		},
		error  :function(){ h_dialog.closeCover(); h_dialog.alert('파일전송오류로 전송이 되지 않았습니다(ex 개별파일용량 초과)');},
		success:function(){ list_renew();}
	});
}
// ---------------------------------------------------------------------------------------------------------------------


function copy_paste_file(opt) {
	var fname = Storage.r('CopyPasteFile');
	var ax_file = uri('linkurl') + "filemanager/copy_paste_file" ;
	var post_val = {'paste_file': fname, 'opt' : opt };
	$.post(ax_file , post_val).done( function(data) { if(data !="OK") h_dialog.alert(data); else {list_renew();} });
	Clear_temporary('file');
}

function Copy_Move_file(sel,opt) {
	var src =  Storage.r('CopyPasteFile');     if( !src) { h_dialog.alert('파일을 선택하지 않았습니다'); return; }
	var tgt =  Storage.r('TargetFolderName');  if( !tgt) { tgt=''; }
	var ax_file = uri('linkurl') + "filemanager/copy_move_file" ;
	var post_val = {'opt': opt, 'src' : src, 'tgt' : tgt };
	$.post(ax_file , post_val).done( function(data) { if(data !="OK") h_dialog.alert(data); 
		else {
			if(opt == 'copy') $(sel).css('color','blue'); 
			else $(sel).css('text-decoration','line-through'); 
		}
	});
	Clear_temporary('file');
}

function Clear_temporary(opt) {
	if(opt == 'file')   {Storage.d('CopyPasteFile');    $('#temporary_file').text(''); }
	if(opt == 'folder') {Storage.d('TargetFolderName'); $('#temporary_folder').text(''); clipBoard('');}
}


function OpenFolderInWindow(path='') {
	var ax_file = uri('linkurl')+ 'filemanager/openFolderInWindow' ;
	var post_val = { f_path : CUR_PATH + '/' + path };
	$.post(ax_file , post_val); 
}

function bottom_menu(opt) {
	var cur_folder = F_PATH; 
	var cur_folder_name =  cur_folder.replace(ROOT,'HOME');
	switch (opt) {
		case 'saveToTemporary': $("#temporary_folder").text(cur_folder_name); Storage.a('TargetFolderName',cur_folder); clipBoard(cur_folder); break;
		case 'moveToTemporary': var mm = Storage.r('TargetFolderName'); location.href= uri('linkurl')+"filemanager/move/" + mm; break;
	}
}

function list_renew() {
	var dest = uri('linkurl'); 
	dest += (F_PATH)? 'filemanager/move/' + F_PATH : 'filemanager/home';
	location.href = dest;
}