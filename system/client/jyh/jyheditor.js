var docuSelected = null;
var docuSelectedType ='';
var JYHEDITOR_status = false;

var JYHEDITOR = {
	mini_mode		: false, 
	reply_mode		: false,
	agent			: navigator.userAgent.toLowerCase(),
	docuRange		: null,
	copiedStyle  : null,
	tempDivHTML	 : '',
	spanStyle1	 : '',
	spanStyle2   : 'font-style:italic',
	spanStyle3   : 'text-decoration:underline',
	spanStyle4   : 'text-decoration:line-through',
	cloneTemp	 : null,
	classTemp    : null,

/* 
    START AND EVENT BIND START
*/
	start  : function(n) {
		this.mini_mode = false; 
		this.reply_mode = false;
		this.rootID = n; 
		this.docu = $id(n); if(this.docu == null) { alert("주어진 편집영역을 발견하지 못하였습니다"); return; }
		this.docu.setAttribute('contenteditable',true);
		//document.execCommand('enableObjectResizing', null, false);
		//document.execCommand('enableInlineTableEditing', null, false);
		//document.execCommand("insertBrOnReturn", false, true); // works only in firefox

		//$(this.docu).keydown(function(e){ if(e.keyCode == 13 ) { JYHEDITOR.clearDocuSelect(); } });
		
		$(document).on('keydown',null,'esc',function(){ JYHEDITOR.clearDocuSelect(); JYHEDITOR.clearDialog(); return false; })
			.on('keydown',null,'backspace', function(e) { if(e.target.id == '') return false; else return true;})
			.on('keydown',null,'f1', function(e){ var itxt = Storage.r('InsertToWriteBody'); JYHEDITOR.ihtml(itxt);  return false; })
			.on('keydown',null,'f2', function(e){ JYHEDITOR.insertCh('bbr');  return false; })
			.on('keydown',null,'f3', function(e){ JYHEDITOR.insertCh('nbsp');	return false; })
			.on('keydown',null,'f4', function(e){ JYHEDITOR.insertCh('br');		return false; })
			.on('keydown',null,'f5', function(e){ JYHEDITOR.dialog('스타일 편집','editor_style','ajax'); return false; })
			.on('keydown',null,'f6', function(e){ JYHEDITOR.copyStyle();  return false; })
			.on('keydown',null,'f7', function(e){ JYHEDITOR.pasteStyle(); return false; })
			.on('keydown',null,'f8', function(e){ JYHEDITOR.clearStyle(); return false; })
			.on('keydown',null,'f9', function(e){ JYHEDITOR.dialog('HTML 편집','editor_html','ajax'); return false; })
		//	.on('keydown',null,'f10',function(e){ JYHEDITOR.copyToTemplate(); return false; })
			.on('keydown',null,'f12',function(e){ JYHEDITOR.appendToPage('p'); return false; })

			.on('keydown',null,'shift+left',	function(e){ JYHEDITOR.PmarginMove('marginLeft',-1); return false; })
			.on('keydown',null,'shift+right',	function(e){ JYHEDITOR.PmarginMove('marginLeft',1);	 return false; })
			.on('keydown',null,'shift+up',		function(e){ JYHEDITOR.PmarginMove('marginTop',-1);	 return false; })
			.on('keydown',null,'shift+down',	function(e){ JYHEDITOR.PmarginMove('marginTop',1);	 return false; })
			.on('keydown',null,'shift+esc',	function(e){ JYHEDITOR.removeSelected(); JYHEDITOR.clearDocuSelect(); return false; })
			.on('keydown',null,'shift+alt',	function(e){ JYHEDITOR.removeFile(); return false; })

			.on('keydown',null,'ctrl+1',	 function(e){ JYHEDITOR.dialog('클래스 편집','editor_class','ajax'); return false; })
			.on('keydown',null,'ctrl+2',	 function(e){ JYHEDITOR.class_CP('copy');  return false; })
			.on('keydown',null,'ctrl+3',	 function(e){ JYHEDITOR.class_CP('paste'); return false; })
			.on('keydown',null,'ctrl+shift', function(e){ JYHEDITOR.dialog('속성 편집','editor_attr','ajax'); return false; })
			.on('keydown',null,'ctrl+t',	 function(e){ JYHEDITOR.dialog('첨부파일 위치 수정','editor_fattr','ajax'); return false; })
			.on('keydown',null,'ctrl+up',	 function(e){ JYHEDITOR.selectUpScope();	 return false; })
			.on('keydown',null,'ctrl+down',  function(e){ JYHEDITOR.selectDnScope();	 return false; })
			.on('keydown',null,'ctrl+left',	 function(e){ JYHEDITOR.selectLtScope();	 return false; })
			.on('keydown',null,'ctrl+right', function(e){ JYHEDITOR.selectRtScope();	 return false; })
			.on('keydown',null,'ctrl+z',	 function(e){ JYHEDITOR.rangeControl(); JYHEDITOR.removeTag(); return false; })
			
			.on('keydown',null,'alt+1', function(e){ JYHEDITOR.cloneCopy(); return false; })
			.on('keydown',null,'alt+2', function(e){ JYHEDITOR.clonePaste('before'); return false; })
			.on('keydown',null,'alt+3', function(e){ JYHEDITOR.clonePaste('append'); return false; })
			.on('keydown',null,'alt+4', function(e){ JYHEDITOR.clonePaste('after'); return false; })
			.on('keydown',null,'alt+t', function(e){ JYHEDITOR.UserTable(); return false; })

			.on('keydown',null,'shift+f1', function(e){ JYHEDITOR.UserFunc1(); return false; })	
			.on('keydown',null,'ctrl+s',   function(e){ JYHEDITOR.UserFunc2(); return false; })
			.on('keydown',null,'alt+a',    function(e){ JYHEDITOR.UserAlt();  return false; })
			.on('keydown',null,'ctrl+a',   function(e){ JYHEDITOR.UserCtrl(); return false; })
			.on('keydown',null,'alt+z',    function(e){ JYHEDITOR.clearInTag(); return false; })
			.on('keydown',null,'alt+f1',   function(e){ JYHEDITOR.dialog('이미지툴입니다','editor_imgtool','ajax',{x:'870px',y:'150px'}); return false; });
//			.on('keydown',null,'alt+6', function(e){ JYHEDITOR.applyDefinedMacro(6); return false; })
//			.on('keydown',null,'alt+7', function(e){ JYHEDITOR.applyStyleToSelected('7'); return false; })
//			.on('keydown',null,'alt+8', function(e){ JYHEDITOR.applyStyleToSelected('8'); return false; })
//			.on('keydown',null,'alt+9', function(e){ JYHEDITOR.applyStyleToSelected('9'); return false; });	
		
		$(this.docu).on("contextmenu", function(e){e.preventDefault(); } )
					.on("contextmenu", "*",   
							function(e) { e.preventDefault(); e.stopPropagation(); 
								JYHEDITOR.rangeControl();
								if( JYHEDITOR.rangeControl('text') ) show_Menu('textToTag'); 
								else JYHEDITOR.handleSelect(this);})
     				.on("mouseover", "span",   function( ) { $(this).addClass('hover_SPAN'); }).on("mouseout",  "span",   function( ) { $(this).removeClass('hover_SPAN'); })
					.on("mouseover", "[data-myfile],[data-myimage]",function(){$(this).addClass('hover_file');}).on("mouseout","[data-myfile],[data-myimage]",function(){$(this).removeClass('hover_file');});
		$("#selectedMarkR").on("click",function() { JYHEDITOR.selectedMark(true);  });
		$("#selectedMarkL").click(function(){JYHEDITOR.clearDocuSelect();});
		Storage.a('OpendDialogId','');
		JYHEDITOR_status = true;

	},
	stop : function(n) { 
		if(n) this.docu = $id(n); 
		this.clearDocuSelect();  $(document).off('keydown');
		this.docu.setAttribute('contenteditable',false);
		$(this.docu).off("contextmenu");
		this.docu = null; 
		this.clearDialog();
		JYHEDITOR_status = false;
	},

	imgTool : function(n) {
		var tag = docuSelected.tagName;
		var sel = $(docuSelected);
		if(tag == 'IMG') {
			var typ = 'image';
			var src = sel.attr("src")+'/'+sel.text();
			var url = src.replace('/DOCU_ROOT',DOCU_ROOT); 
 		}
		else if (tag == 'SPAN' || sel.attr("data-myimage") ){
			var typ = 'span';
			var url = sel.attr("data-myimage")+'/'+sel.text();
			var src = url.replace(DOCU_ROOT,'/DOCU_ROOT');
		}
		else return; 
		h_dialog.alert("type="+typ+"<br>url="+url+"<br>src="+src)
	},
/* 
    START AND EVENT BIND END
*/

	fontSize : function(op) {
			var osize = $(docuSelected).css('fontSize');
			var nsize = (op)? parseInt(osize) + 2 : parseInt(osize) - 2;
			nsize = nsize + 'px';
			$(docuSelected).css('fontSize',nsize);
			this.selectedMark();
	},

	lineSize : function(op) {
			var osize = $(docuSelected).css('lineHeight');
			var nsize = (op)? parseInt(osize) + 2 : parseInt(osize) - 2;
			nsize = nsize + 'px';
			$(docuSelected).css('lineHeight',nsize);
			this.selectedMark();
	},

	rangeControl	: function( option, i) { 
		switch(option) { 
			case 'text'		:  return this.docuRange.toString(); 
			case 'object'	:  return this.docuRange.cloneContents(); 
			case 'insert'	:  this.docuRange.deleteContents(); if(typeof i == 'object') this.docuRange.insertNode(i); 
																else if(typeof i =='string') this.docuRange.insertNode( document.createTextNode(i) );break; 
			default			:  this.docuRange = window.getSelection().getRangeAt(0);}
	},
	
	handleSelect	: function(ele) { 
		this.rangeControl();
		if( this.rangeControl('text') ) {
			this.whichScope = ele.tagName;	
			if( docuSelected != null ) { 
				docuSelected = null; docuSelectedType = ''; 
				$("#TAG_STRUCTURE").html('');
			} 
			return; 
		}
		if( ! ele ) return; 
		
		var etype = ele.tagName; 
		docuSelected = ele; 
		docuSelectedType = etype;
		this.tagStructure();	
	},

	tagStructure	: function() {
						var result = new Array();
						var toStop = '#' + this.rootID;
						$(docuSelected).parentsUntil( toStop ).each(function(i) {
							result[i] = (this.id)?  '<b>'+this.tagName +'</b>['+this.id+']&nbsp':'<b>'+this.tagName +'</b>&nbsp';
						});
						
						result.reverse();
						
						var curTagName;
							if(result.length) curTagName = result.join("> ") + '> <b>' + docuSelected.tagName +'</b>';
							else curTagName ='<b>'+ docuSelected.tagName +'</b>';
						$("#TAG_STRUCTURE").html(curTagName);
						this.selectedMark();
	},
	
	selectedMark: function(op=false) {
						if( docuSelectedType == 'TD' || docuSelectedType == 'TR' || docuSelectedType == 'TH') {
							
							var mTop  = $(docuSelected).closest('table').get(0).offsetTop + docuSelected.offsetTop+'px';
							var mHigh = docuSelected.offsetHeight + 'px';

						}else if( docuSelectedType == 'TBODY') { 
							var mTop  = $(docuSelected).closest('table').get(0).offsetTop + 'px';
							var mHigh = $(docuSelected).closest('table').get(0).offsetHeight + 'px';						
						}else { 
							var mTop  = docuSelected.offsetTop + 'px';
							var mHigh = docuSelected.offsetHeight + 'px';
						}
						if(op) { 
							JYHEDITOR.cloneCopy();
							JYHEDITOR.class_CP('copy');
							JYHEDITOR.copyStyle();
							$("#choicedMark").css({ 'top': mTop, 'height': mHigh}).text(docuSelectedType).show(); 
						}else {
							$("#selectedMarkL").css({ 'top': mTop, 'height': mHigh}).text(docuSelectedType).show();
							$("#selectedMarkR").css({ 'top': mTop, 'height': mHigh}).text(docuSelectedType).show();
						}
						if( $id("editor_imgtool") ) editorImgtool_refresh();
	},
	

	clearDocu		: function()	{this.docu.innerHTML = ''; this.clearDocuSelect(); },

	clearInTag		: function()    {$(docuSelected).html('');},

	clearStyle		: function() { if( docuSelected == null ) return; $(docuSelected).removeAttr('style'); },
	
	PmarginMove	    : function(key,val) {var cMargin = $( docuSelected ).css( key ); var nMargin = parseInt( cMargin ) + val + 'px'; $( docuSelected ).css( key,nMargin);this.selectedMark();},
	
	
	cssPS : function( css ) {
		if(! docuSelected ) {h_dialog.notice('선택된 요소가 없습니다',{pos:'LT',x:30,y:70}); return;}
		var cssType, cssVal; 
		switch( css ) {
			case 'bold'			: cssType = 'fontWeight';		cssVal = '700';			break;
			case 'italic'		: cssType = 'fontStyle';		cssVal = 'italic';		break;
			case 'underline'	: cssType = 'textDecoration';	cssVal = 'underline';	break;
			case 'line-through'	: cssType = 'textDecoration';	cssVal = 'line-through';break;
			case 'justify'		: cssType = 'textAlign';		cssVal = 'justify';		break;
			case 'left'			: cssType = 'textAlign';		cssVal = 'left';		break;
			case 'center'		: cssType = 'textAlign';		cssVal = 'center';		break;
			case 'right'		: cssType = 'textAlign';		cssVal = 'right';		break;
		}
		($(docuSelected).css(cssType)== cssVal )?	$(docuSelected).css(cssType,'') : $(docuSelected).css(cssType,cssVal) ;   
	},

	cloneCopy : function() {
		if(! docuSelected ) {h_dialog.notice('선택된 요소가 없습니다',{pos:'LT',x:30,y:70}); return;}
		var temp = $("<div>"); 
		$(temp).append($(docuSelected).clone());
		this.cloneTemp = $(temp).html();
	},
	
	clonePaste : function(op) {
		var targetObj = (! docuSelected )? this.docu : docuSelected; 
		if(! this.cloneTemp ) return;
		if(docuSelectedType=='TD' || docuSelectedType=='TH') return;
		switch ( op ){
			case  'append' : 
				if(docuSelectedType=='TR') break;
				$(targetObj).append(this.cloneTemp) ; break;
			case  'after'  : $(targetObj).after(this.cloneTemp) ; break;
			case  'before' : $(targetObj).before(this.cloneTemp) ; break;
			default :$(targetObj).append(this.cloneTemp) ; 
		}
		this.selectedMark();
	},
	class_CP : function(op) { 
		if(! docuSelected ) {h_dialog.notice('선택된 요소가 없습니다',{pos:'LT',x:30,y:70}); return;} 
		if(op == 'copy') { this.classTemp = $(docuSelected).attr('class'); }
		else {
			if(! this.classTemp ) {h_dialog.notice('선택된 클래스가 없습니다',{pos:'LT',x:30,y:70}); return;}
			$(docuSelected).attr('class',this.classTemp);
		}
	},

	spanStyle : function( op ) { 
		this.rangeControl(); 
		if( ! this.rangeControl('text') ) {h_dialog.notice('선택된 대상이 없습니다',{pos:'LT',x:30,y:40}); return;}
		switch ( op ){
			case  1 : this.makeTag('span',this.spanStyle1); break;
			case  2 : this.makeTag('span',this.spanStyle2); break;
			case  3 : this.makeTag('span',this.spanStyle3); break;
			case  4 : this.makeTag('span',this.spanStyle4); break;
			default : var tag = prompt("생성할 태그를 입력하세요"); if(!tag) return; this.makeTag(tag); 
		}
	},
	
	insertCh : function( op ) {
		if( ! docuSelected ) { h_dialog.alert("선택된 태그영역이 없습니다"); return; }
		var afterContents = '';
		var beforContents = '';
		switch ( op ){
			case  'nbsp' : afterContents = '&nbsp;';	$(docuSelected).after(afterContents);	break;
			case  'br'   : afterContents = '<br>\n';		$(docuSelected).after(afterContents);	break;
			case  'bbr'  : beforContents = '<br>\n';		$(docuSelected).before(beforContents);	break;
			default : var tag = prompt("생성할 태그를 입력하세요"); if(!tag) return; this.makeTag(tag); 
		}
	},


	addStyle : function( op ) { 
		if( ! docuSelected ) { h_dialog.alert("선택된 태그영역이 없습니다"); return; }
		var style = {};
		
		style.id    = 'ALT-'+ op; 
		if( Storage.r(style.id) !== null ) {h_dialog.alert('이미 정의된 키입니다'); return;}
	
		style.title = prompt("스타일 명을 입력해 주세요"); if(style.title == null) return; 
		
		style.style = $(docuSelected).attr('style'); 
		
		Storage.a( style.id, style ); 
	},

	applyDefinedMacro	: function(op) {
		switch(op) {
			case 5 : if( ! docuSelected ) return;
					 appendMacro  = '<span data-myfile="">파일명교체요망</span> '; 
					 $(docuSelected).append(appendMacro); break;
			case 6 : appendMacro  = '<span class="block0">타이틀입력</span><p class="pbox0">내용입력</p>'; 
					 if( docuSelected ) $(docuSelected).after(appendMacro); else $(this.docu).append(appendMacro); break;
		}
	},

	applyStyleToSelected: function(op) {
		var getStyleID = 'ALT-' + op ; 
		if( Storage.r(getStyleID) === null ) { h_dialog.alert(getStyleID+" 키의 스타일이 저장되지 않았습니다"); return; }
		
		var getStyleCookie = JSON.parse( Storage.r( getStyleID ) );
		var getStyleSty = getStyleCookie.style; 
	
		this.rangeControl(); 
		if( this.rangeControl('text') ) {
			var tagObj		= document.createElement( 'span' ); 
			var appendObj	= this.rangeControl('object');
			$( tagObj ).append( appendObj ).attr('style',getStyleSty); 
			this.rangeControl('insert', tagObj ); 				
		} else {
			if( ! docuSelected ) return;
			$(docuSelected).attr('style',getStyleSty);
		}
		this.selectedMark();
	},

	ihtml: function(html){	
		var sel, range;
		if (window.getSelection) {
			sel = window.getSelection();
			if (sel.getRangeAt && sel.rangeCount) {
				range = sel.getRangeAt(0);
				range.deleteContents();
				var el = document.createElement("div");
				el.innerHTML = html;
				var frag = document.createDocumentFragment(), node, lastNode;
				while ( (node = el.firstChild) ) {
					lastNode = frag.appendChild(node);
				}
				range.insertNode(frag);
				
				// Preserve the selection
				if (lastNode) {
					range = range.cloneRange();
					range.setStartAfter(lastNode);
					range.collapse(true);
					sel.removeAllRanges();
					sel.addRange(range);
				}
			}
		} 
	},
	
	blockTag : function() {
		var tag = prompt("태그(Block Type)를 입력해 주세요");
		this.cmd('formatBlock',tag); 
		JYHEDITOR.clearDocuSelect();
	},

	cmd: function(c,val) {	
		if(c=='bold'||c=='underline'||c=='strikethrough'||c=='justifyleft'||c=='justifycenter'||c=='justifyright'||c=='formatBlock'){	
			this.rangeControl(); 
			if(! this.rangeControl('text')) {h_dialog.notice('선택된 대상이 없습니다',{pos:'LT',y:20}); return;}
		} 
		this.docu.focus(); 
		document.execCommand(c,false,val); 
	},

	link : function()
	{	
		this.rangeControl(); 
		var selectedText = this.rangeControl('text');  
		var $this = this; 
		if(!selectedText) { h_dialog.notice('선택된 대상이 없습니다',{pos:'LT',x:720,y:20}); return; }
		h_dialog.prompt('링크될 주소를 입력하세요',{overlay:false, width:380,
			buttons : [
				{text:'생성', call: function(idx){ 
						var selectionContents = $this.rangeControl('object'); 
						var src = $('#h_prompt_' + idx).val();  
						var s_link = document.createElement("span");
						$(s_link).attr('data-folder',src).append(selectionContents); 
						$this.rangeControl('insert',s_link); 
						h_dialog.close(idx);
				}},
				h_dialog.close_button
			]
		});
	},	

	hyperlink : function(html)
	{	
		switch(html) {
			case 'folder_link' :  
				var selectionContents = this.rangeControl('object');
				var s_link = document.createElement("span");
				var src = Storage.r('TargetFolderName'); if(! src ) { h_dialog.alert('저장된 링크가 없습니다'); break;}
				$(s_link).attr('data-folder',src).append(selectionContents); 
				this.rangeControl('insert',s_link); 
				break;
			case 'url_link' :  
				var selectionContents = this.rangeControl('object');
				var s_link = document.createElement("a");
				var src = prompt('주소를 입력하세요');
				$(s_link).attr({href:src,target:'_blank'}).append(selectionContents); 
				this.rangeControl('insert',s_link); 
				break;
			case 'img_thumb' :  
				var selectionContents = this.rangeControl('object');
				var s_link = document.createElement("img");
				var src = Storage.r('FileManagerUserImageURL'); if(! src ) { h_dialog.alert('저장된 링크가 없습니다'); break;}
				$(s_link).attr({src:src,'class':'img-thumbs'}); 
				this.rangeControl('insert',s_link); 
				break;
		}
		$('#textToTag').hide();
	},

	makeTag: function(tag,style) {

		var tagValue = {SPAN:0, P:1, DIV:2};
		var scopeVal = tagValue[tag]; if(tag == 'DIV') scopeVal = 1;
				
		if( scopeVal >= tagValue[this.whichScope] ) { h_dialog.alert('현재 영역에서는 구역을 설정할 수 없습니다'); $('#textToTag').hide(); return; }
		var tagObj		= document.createElement( tag ); 
		var appendObj	= this.rangeControl('object');
		$( tagObj ).append( appendObj );
		if( style ) $(tagObj).attr('style',style); 
		this.rangeControl('insert', tagObj ); 

		$('#textToTag').hide();
	},

	makeAnchor : function() {
		if( ! this.rangeControl('text') ) {h_dialog.notice('선택된 대상이 없습니다',{pos:'LT',x:30,y:40}); return;}
		$('#selectedMenu').hide();
		var tagObj		= document.createElement( 'a' ); 
		var appendObj	= this.rangeControl('object');
		$( tagObj ).append( appendObj );
		var name = prompt(this.rangeControl('text'));
		if( name ) $(tagObj).attr('name',name); else return; 
		this.rangeControl('insert', tagObj ); 
	},

	removeTag : function() {
		var text = this.rangeControl('text');
		if( ! text ) {h_dialog.notice('선택된 대상이 없습니다',{pos:'LT',x:30,y:40}); return;}
		this.rangeControl('insert', text ); 
	},

	clearDocuSelect	: function() { if(docuSelected != null ) {	docuSelected = null; docuSelectedType = ''; }
								   $("#TAG_STRUCTURE").html('');$("#selectedMarkL").hide(); $("#selectedMarkR").hide(); $("#choicedMark").hide();
								   this.classTemp = null; this.copiedStyle = null;
	},

	copyStyle		: function() { if(! docuSelected ) return;  this.copiedStyle = $(docuSelected).attr('style'); },

	pasteStyle		: function() { if(! docuSelected || ! this.copiedStyle ) return; $(docuSelected).attr('style',this.copiedStyle); this.selectedMark();},

	removeSelected	: function() { if(! docuSelected ) return; 
		if(docuSelectedType == 'TD' || docuSelectedType == 'TH') return;
		$(docuSelected).remove(); $("#selectedMarkL").hide();$("#selectedMarkR").hide();},

	removeFile		: function() { if(! docuSelected ) return; 

			var f_name = $.trim($(docuSelected).text());
			var f_path = $.trim($(docuSelected).attr("data-myfile"));
			var d_file = f_path + '/' + f_name;
			var posturl = uri('linkurl') + 'board-ajax/body_file_delete';

			h_dialog.confirm( f_name + ' 파일을 삭제합니다',
				{ 
				  overlay:false,x:mouse_X, y:mouse_Y, 
				  buttons:  [
								{text : '취소하기', call: function(a) { h_dialog.close(a); return; }},
								{text : '삭제하기', call: function(a) { h_dialog.close(a);
									$.post( posturl, { d_file : d_file}).done( 
										function(data) { if(data=='DEL_OK') {h_dialog.notice('해당파일을 삭제하였습니다');  JYHEDITOR.removeSelected();}}); 
									}}
							]
			});
			 
  	},

	copyToTemplate : function() {
		if(! docuSelected ) { h_dialog.alert('선택된 구간이 없습니다'); return;}

		var tempDiv = document.createElement( 'div' );
		var cloneHTML = $(docuSelected).clone(); 
		
		if( ! $id('editor_template_save')) {
			this.tempDivHTML =  $( tempDiv ).append( cloneHTML ).html(); 
			open_dialog('템플릿으로 편집하기','editor_template_save','ajax',{x:1000, y:120}); 
		} else {
			$("#templateDiv").append( cloneHTML ); 
		}
		this.clearDocuSelect(); 
	},
	
	styleManager: function() {
		open_dialog('스타일관리자','editor_style_manager','ajax',{x:340, y:320}); 
	},

	appendToPage	: function(op) {
		var appendStr = '';
		switch(op) {
			case 'table' : appendStr  = "<div><table class='table table-bordered'>"; 
						   appendStr += "<tr class='table-th'><th>T</th><th>T</th><th>T</th></tr>"; 
						   appendStr += "<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>"; 
						   appendStr += "<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>"; 
						   appendStr += "</table></div>"; break;
			case 'p'	 : appendStr  = "<p>New Paragraph</p>";	break;
			case 'ul'    : appendStr  = "<ul><li> 리스트 </li>"; break;
			case 'ol'    : appendStr  = "<ol><li> 리스트 </li>"; break;
			case 'div'	 : appendStr  = "<div>New DIV element</div>";	break; 
		}

		if(! docuSelected ) $(this.docu).append( appendStr ); 
		else {
			if( docuSelectedType == 'TD' || docuSelectedType == 'TR' || docuSelectedType == 'TBODY') {
				$(docuSelected).closest('div').after( appendStr );
			}
			else {
				$(docuSelected).after( appendStr );
			}
		}
	},
	
	selectUpScope	: function() { if( ! docuSelected ) return; var newOBJ  = null; newOBJ = $(docuSelected).parent().get(0); if( newOBJ.id == this.rootID ) return; this.handleSelect(newOBJ);},
	selectDnScope	: function() { if( ! docuSelected ) return;	var newOBJ  = null; newOBJ = $(docuSelected).children().get(0); if(! newOBJ ) return; this.handleSelect(newOBJ);},
	selectLtScope	: function() { if( ! docuSelected ) return; var newOBJ  = null; newOBJ = $(docuSelected).prev().get(0); this.handleSelect(newOBJ);},
	selectRtScope	: function() { if( ! docuSelected ) return; var newOBJ  = null; newOBJ = $(docuSelected).next().get(0); this.handleSelect(newOBJ);},

	dialog : function(title,idx,imode,opt=null) { 
		if( $id(idx) ) {
			switch(idx) {
				case 'editor_html'	  : editorHtml_refresh(); break;
				case 'editor_style'	  : editorStyle_refresh(); break;
				case 'editor_class'	  : editorClass_refresh(); break;
				case 'editor_imgtool' : editorImgtool_refresh(); break;
				case 'editor_fattr'	  : file_location_check(); break;
				default : h_dialog.close(idx);
			}
		}
		else {
			open_dialog(title,idx,imode,opt); 
		}
	},

	clearDialog : function() {
		var opend_arr = Storage.r('OpendDialogId').split('##');
		opend_arr.forEach(function(item){h_dialog.close(item);});
	},

	UserFunc1 : function() { return; },
	UserFunc2 : function() { return; },
	UserAlt   : function() { return; },
	UserCtrl  : function() { return; },
	UserTable : function() { return; },
// Table 조작

	addRowCol : function(op) {
		var tr  = $(docuSelected).closest('table').find('tr');
		var idx = $(docuSelected).index();
	
		switch(op) {
			case 'left' :
				$(tr).children("th").eq(idx).before("<th>T</th>");
				$(tr).each(function(){$(this).children("td").eq(idx).before("<td>&nbsp;</td>")});
				break;
			case 'right':
				$(tr).children("th").eq(idx).after("<th>T</th>");
				$(tr).each(function(){$(this).children("td").eq(idx).after("<td>&nbsp;</td>")});
				break;
			case 'col':
				$(tr).children("th").eq(idx).remove();
				$(tr).each(function(){$(this).children("td").eq(idx).remove()});
				break;
			case 'row':
				$(docuSelected).parent().remove();
				break;
			case 'up': case 'down' :
				var cur_tr = $(docuSelected).parent(); 
				var temp = $("<div>"); $(temp).append($(cur_tr).clone()); $(temp).find("td").each(function(){$(this).html('&nbsp;');});	var cloneTemp = $(temp).html();
				if(op == 'up') $(cur_tr).before(cloneTemp); else $(cur_tr).after(cloneTemp);
				break;
		}
	},

// Mini Editor
	miniInit	: function(n)	{
		this.docu = $id(n);this.docu.setAttribute('contenteditable',true);
		this.mini_mode = true;
	},
	miniClose	: function( )	{
		this.docu.setAttribute('contenteditable',false);
		this.docu = null;	this.mini_mode = false;
	},
/* 
	html encode & decode
*/
	htmlencode : function(str) { if (typeof(str)=="string")
		{
			var str_convert = html_pretty(str); 
			var map = {'&': '&amp;','<': '&lt;','>': '&gt;','"': '&quot;',"'": '&#039;'}; 
			str = str_convert.replace(/[&<>"']/g, function(m) { return map[m]; });
		} 
		return str;
	},
	htmldecode : function(str) {if (typeof(str)=="string"){str=str.replace(/&gt;/ig, ">").replace(/&lt;/ig, "<").replace(/&#039;/g, "'").replace(/&quot;/ig, '"').replace(/&amp;/ig, '&');}	return str;	}
} 
/* ************************************************************************************************
	END of JYHEDITOR
************************************************************************************************* */