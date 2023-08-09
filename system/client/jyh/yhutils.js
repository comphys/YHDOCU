// *************************************************************************************************
// Core Utils / AUTHOR : Jung Yong Hoon 
// *************************************************************************************************

mouse_X=0; mouse_Y=0; page_X = 0; page_Y = 0;
$(document).mousedown( function(e) { mouse_X = e.clientX; mouse_Y = e.clientY; page_X = e.pageX; page_Y=e.pageY; }); 

function $id(id) {	return document.getElementById(id); }

/*
	function uri : 현재 주소줄의 정보를 리턴함
	주소줄 형식  : http://example.com/app/control/method/seg0/seg1/seg2
	parameters   : 값이 정수일 경우 uri(0)은 seg0을 리턴함
*/
function uri(parameter){
	var segment = location.pathname.replace(/^\/|\/$/g,''),pair,key,value,qry={}; 
	segment=decodeURIComponent(segment); 
	segment = segment.split('/'); 
	var cnt = segment.length;
	if(segment.length > 3){ 
		for(var i=3; i < segment.length; i++) { 
			if(segment[i].indexOf('=') != -1){ 
				pair=segment[i].split('='); key=pair[0];value = pair[1];qry[key] = value;
			}
		}
	} 
	
	if(typeof parameter == 'number' && parameter % 1 == 0) { var seg = parameter + 3; return (segment[seg])? segment[seg]: false;}
	
	switch(parameter){
		case 'app': return segment[0]; 
		case 'control': return segment[1]; 
		case 'method':return (segment[2])? segment[2]:'index';
		case 'gets':return segment
		case 'base' : return location.protocol+'//'+location.hostname; 
		case 'linkurl' : return '/'+ segment[0] + '/';
		case 'last' : return segment[cnt-1];
		case 'thispage' : return '/'+ segment[0] + '/' + segment[1] + '/' + segment[2] + '/';
		default: 
			if (parameter in qry) return qry[parameter];
			else return '';
	}
}
// *************************************************************************************************
// toggle() was removed since jquery1.9, below is alternative to toggle(f1,f2,f3...)
// *************************************************************************************************
$.fn.toggleClick=function(){ 
	var functions=arguments, iteration=0; 
	return this.click(function(){ functions[iteration].apply(this,arguments); 
	iteration= (iteration+1) %functions.length; 
});}
// *************************************************************************************************
// Date format ex : console.log(new Date().format("yyyy년 MM월 dd일 a/p hh시 mm분 ss초"));
// *************************************************************************************************
Date.prototype.format = function(f) {
	if (!this.valueOf()) return " ";
	var weekName = ["일요일", "월요일", "화요일", "수요일", "목요일", "금요일", "토요일"];
	var d = this;
	return f.replace(/(yyyy|yy|MM|dd|E|hh|mm|ss|a\/p)/gi, function($1) {
		switch ($1) { case "yyyy": return d.getFullYear();
					  case "yy": return (d.getFullYear() % 1000).zf(2);
					  case "MM": return (d.getMonth() + 1).zf(2);
					  case "dd": return d.getDate().zf(2);
					  case "E": return weekName[d.getDay()];
					  case "HH": return d.getHours().zf(2);
					  case "hh": return ((h = d.getHours() % 12) ? h : 12).zf(2);
					  case "mm": return d.getMinutes().zf(2);
					  case "ss": return d.getSeconds().zf(2);
					  case "a/p": return d.getHours() < 12 ? "오전" : "오후";
					  default: return $1;
					 }
			});
};
String.prototype.string = function(len){var s = '', i = 0; while (i++ < len) { s += this; } return s;};
String.prototype.zf = function(len){return "0".string(len - this.length) + this;};
Number.prototype.zf = function(len){return this.toString().zf(len);};

// *************************************************************************************************
// h_dialog, AUTHOR : Jung Yong Hoon 
// *************************************************************************************************
var h_dialog = {
// BASIC SETTINGS ---------------------------------------------------------------------------------
	opt_basic :	{	
					css				: 'basic', 	
					type			: 'alert',
					width			: '',	
					height			: '',
					maxHeight		: '',
					header			: true, close_btn : false,
					footer			: true, 
					drag			: true,	
					overlay			: false,
					over_opacity	: false,
					over_close		: false,
					pos				: false, x : 0, y : 0,
					url				: false, 
					buttons			: false,
					h_title			: 'JYH Alert Ver 1.0',
					b_title			: 'This is a JYH Alert',  
					f_title			: '&nbsp',
					notice_stop		: false
				},
// INIT -------------------------------------------------------------------------------------------
	init  : function() {	
				var $m = this ;
				var idx = this.id;
				var option = this.opt; 
			//  포지션 기본 값 설정
				if(!option.pos && !option.x && !option.y)  option.pos ='center';
				else if(!option.pos && (option.x || option.y))  option.pos = 'LT'; 
				
				var dialog_css	= 'h_dialog_' + option.css ;
	
				$("<div>", { id  :  idx, class : dialog_css, css : {position:'fixed', display:'none', zIndex : '2000' }}).appendTo("body");
				this.dialog		= $id(idx);
	
				if(option.overlay && ! $id('overlay_idx')) {
					$("<div>", { id  :  'overlay_idx' , class : 'h_dialog_overlay'}).appendTo("body");
					this.overlay   = $id('overlay_idx');
					if(option.over_opacity) $(this.overlay).css({opacity: option.over_opacity});
					if(option.over_close  ) $(this.overlay).on('click', function() {h_dialog.close(idx);});
				}
				
				var x = option.x, y = option.y;
				
				if(option.type=='notice'){
					if( !$id('h_dialog_noticeWrap') ) $("<div>", { id  : 'h_dialog_noticeWrap', css : {position:'fixed', display:'none', zIndex :'2000'}}).appendTo("body");
					if(option.pos == 'LT' || option.pos == 'center')  $('#h_dialog_noticeWrap').css({left:x,	right:'auto',top: y, bottom : 'auto'});
					else if(option.pos == 'LB') $('#h_dialog_noticeWrap').css({left:x,	  right:'auto',top:'auto',bottom : y});
					else if(option.pos == 'RT') $('#h_dialog_noticeWrap').css({left:'auto',right:x,	 top: y,	bottom : 'auto'});
					else if(option.pos == 'RB') $('#h_dialog_noticeWrap').css({left:'auto',right:x,	 top:'auto',bottom : y});
				}
	
// HEADER PART --------------------------------------------------------------------------------------------------------------------------------------
				if(option.header) { 
					var header_id = idx + '_header'; 
					var header_css		= 'h_dialog_' + option.css + '_header'	;
					$(this.dialog).append("<div id='" + header_id + "' class='"+ header_css +"'>"+ option.h_title +"</div>"); 
					this.header = $id(header_id);
					if(option.close_btn) {
						var close_btn_css = 'h_dialog_' + option.css + '_close_btn'	;
						$("<div class='"+ close_btn_css +"'>&nbsp;</div>").click(function(){h_dialog.close(idx);}).appendTo(this.header);
					}
				}
// BODY PART ----------------------------------------------------------------------------------------------------------------------------------------
				var content_id = idx + '_content'; 
				var content_css		= 'h_dialog_' + option.css + '_content' ;
				$(this.dialog).append("<div id='" + content_id + "' class='"+ content_css +"'></div>"); 
				this.content = $id(content_id);
				
				if( option.width || option.height) $(this.content).css({width: option.width, height: option.height});
				if( option.maxHeight) $(this.content).css({maxHeight: option.maxHeight});
				
				switch( option.type ) {
					case 'alert' :	
					case 'confirm'	: 
					case 'notice'	:
						this.content.innerHTML = option.b_title ; 
						break;

					case 'ajax' :
						$(this.content).load(option.url).css('padding','0px');
						break;

					case 'iframe' :
						$(this.content).css({padding:0});
						this.content.innerHTML = "<iframe src='" + option.url +"' width='100%' height='100%' style='overflow:auto;border:0;'></iframe>" ; 
						break;
					
					case 'prompt' :
						var prompt_css	= 'h_dialog_' + option.css + '_prompt'	;
						var prompt_id = 'h_prompt_' +  idx;
						var btn_css = 'h_dialog_basic_btn1';
						$(this.content).append("<input id='" + prompt_id + "' class='"+ prompt_css + "' type='text' placeholder='"+option.b_title+"'>&nbsp;");
						var button = "<div style='margin: 10px -15px -10px -15px;text-align:center;border-top: 1px outset black; padding: 5px 15px; background-color:#c7d6da;'>";
						button += "<button id='" + prompt_id + "_btn01" + "' class='"+ btn_css +"'>입력</button>&nbsp;&nbsp;";
						button += "<button id='" + prompt_id + "_btn02" + "' class='"+ btn_css +"'> 취소</button>";
						button += "</div>";
						$(this.content).append(button);
						$('#'+prompt_id + "_btn01").on('click',function(){option.doit(idx);}); 
						$('#'+prompt_id + "_btn02").on('click',function(){h_dialog.close(idx);}); 
						$('#'+prompt_id).on('keydown', function(event){ if(event.which == 13) option.doit(idx); });
						break;
		
					case 'image' :
						var img = option.img;
						var url = img.src; 
						var i_width = img.width, i_height = img.height;
						var w_width = $(window).width(), w_height = $(window).height(); 

						var ratio=0; 
											
						if(i_width  >= w_width -20 ) { ratio = (w_width-20)/i_width;   i_width  = w_width  -20; i_height = Math.ceil(i_height * ratio);}
						if(i_height >= w_height -20) { ratio = (w_height-20)/i_height; i_height = w_height -20; i_width  = Math.ceil(i_width * ratio); }

						var image = $("<img>", { src: url, width : i_width, height:i_height});
						$(image).appendTo( this.content );

						var image_L = $("<div>", {css:{position:'absolute',top:0,left:0,width:'50%',height:'100%'}}); 
						var image_R = $("<div>", {css:{position:'absolute',top:0,right:0,width:'50%',height:'100%'}});
						$(image_L).appendTo( this.content );
						$(image_R).appendTo( this.content );

						$(image_L).contextmenu( function(e) {
							e.preventDefault(); 
							$('#' + idx).animate({opacity:0},500,function(){ $(this).remove(); });
							if( --imageIndex < 0 ) imageIndex = imageRotate.length -1 ;
							h_dialog.image( imageRotate[ imageIndex ] );					
						}).dblclick( function() {winopen2(url);});

						$(image_R).contextmenu( function(e) {
							e.preventDefault(); 
							$('#' + idx).animate({opacity:0},500,function(){ $(this).remove(); });
							if( ++imageIndex >= imageRotate.length ) imageIndex = 0;
							h_dialog.image( imageRotate[ imageIndex ] );					
						}).dblclick( function() {winopen2(url);});
											
						if( ratio ) {
							var $thisContent = this.content;
							var $thisDialog  = this.dialog;
							var imgResizeDiv = $("<div style='position:absolute;right:10px;bottom:10px;width:34px;height:34px'></div>");
							var imgResize    = $("<img src='/sys/jyh/fullexpand.gif' />");
						
							$(imgResize).click(function(e){ 
								e.stopPropagation();
								$(image).css({width: img.width, height: img.height});
								var	x =     ( $(window).width() -  img.width )  / 2 ;
								var	y =     ( $(window).height() - img.height)  / 2 ;
								$($thisDialog).css({left  : x, top : y});
								$(imgResizeDiv).remove();
							});
							
							$(imgResize).appendTo( imgResizeDiv);
							$(imgResizeDiv).appendTo( this.content );
						}
						break;
				} // END OF SWITCH

// FOOTER PART--------------------------------------------------------------------------------------------------------------------------------------
				if(option.footer) { 
					var footer_id = idx + '_footer'; 
					var footer_css		= 'h_dialog_' + option.css + '_footer'	;
					$(this.dialog).append("<div id='" + footer_id + "'	class='"+ footer_css +"'>"+ option.f_title +"</div>"); 
					this.footer = $id(footer_id);
					
					$.each(option.buttons, function(index,val) {
						var ix = index + 1; 
						var btn_css    = 'h_dialog_' + option.css + '_btn' + ix ;
						var btn_id     =  idx + '_btn' + ix; 
						$($m.footer).append("<button id='" + btn_id + "' class='"+ btn_css +"'>"+ val.text +"</button>&nbsp;");
						$('#'+btn_id).on('click',function(){val.call(idx);}); 
					});
				}
// POSITIONING --------------------------------------------------------------------------------------------------------------------------------------
				if(option.pos == 'center') {
					x =     ( $(window).width() -  $(this.dialog).width())  / 2   ;
					y =     ( $(window).height() - $(this.dialog).height()) / 2   ;
					$(this.dialog).css({left  : x, top : y});
				}
				else if(option.pos == 'LT')	 $(this.dialog).css({left:x,	 right:'auto',top: y,	 bottom : 'auto'});
				else if(option.pos == 'LB')	 $(this.dialog).css({left:x,	 right:'auto',top:'auto',bottom : y});
				else if(option.pos == 'RT')	 $(this.dialog).css({left:'auto',right:x,	  top: y,	 bottom : 'auto'});
				else if(option.pos == 'RB')	 $(this.dialog).css({left:'auto',right:x,	  top:'auto',bottom : y});
				
				if(option.type == 'notice') {
					$(this.dialog).css({position:'relative', left:'', top:'', bottom:'', right:'', marginBottom: 10, cursor:'pointer'});
				}
	},

	open : function(opt) {
				$m = this; 
				if(!opt.id) { 
					var d = new Date; 	
					this.id = d.getTime(); 
				}
				else { this.id = opt.id; if($id(this.id)) return; }

				this.opt = {}; 
				$.extend(this.opt, this.opt_basic, opt); 

				this.init();
				
				if(this.opt.drag && (this.opt.pos =='center' || this.opt.pos =='LT')) {	$(this.dialog).draggable({handle:$m.header});}
				if(this.opt.overlay) { 	$(this.overlay).show(); } 
				
				if(this.opt.type == 'notice') {
					$('#h_dialog_noticeWrap').show().append(this.dialog);
					if(! this.opt.notice_stop) {
						$(this.dialog).show().animate({opacity:1},2000).animate({opacity:0.1},1000,function() { $(this).remove(); });
					} else { $(this.dialog).show(); }

					$(this.dialog).click(function(){$(this).remove();}).mouseover(function () { $(this).stop().css('opacity','1'); });
				}
				else if(this.opt.type == 'image' )  { 
					$(this.dialog).click(function(e) { h_dialog.close(this.id);});
					$(this.dialog).show(400); 
				}
				else { $(this.dialog).show(); }

				var opened = Storage.r('OpendDialogId');
			    var addnew = (opened + this.id + '##').replace('undefined','').replace('null','');
			    Storage.a('OpendDialogId',addnew);
	},

	close : function(idx) {
				var dialog = $id(idx);
				if(! dialog ) return;
				else { 
					   var opened = Storage.r('OpendDialogId');
					   var delone = (opened)? opened.replace(idx+'##','') : '';
					   Storage.a('OpendDialogId',delone);	
					   $( dialog ).animate({opacity:0,top:0},300,function(){ $( dialog ).remove(); });
					   if(this.opt.overlay) $('#overlay_idx').animate({opacity:0},300,function(){ $(this).remove(); });	
				}
	},
// [ PUBLIC METHOD ]---------------------------------------------------------------------------------------------------------------------------------	
	close_button  : {text:'닫기',call:function(a){h_dialog.close(a);}},
	cancel_button : {text:'취소',call:function(a){h_dialog.close(a);}},

	alert  : function(str,a) { 
				var o = { type :'alert', overlay : true, b_title : str, buttons :[this.close_button]}; 
				if(typeof a == 'object') $.extend(o,a); 
				this.open(o);	
	},
	confirm: function(str,a) { 	
				var o = { type :'confirm', h_title :'JYH Confirm Ver 1.0', overlay : true, b_title : str, 
						  buttons :[{text:'확인',call:function(idx){alert(idx);}},	this.close_button  ]	
						}; 
				if(typeof a == 'object') $.extend(o,a); 
				this.open(o);
	},
	prompt : function(str,a) { 
				var o = { type : 'prompt', overlay : true, h_title : str, footer:false};
				if(typeof a == 'object') $.extend(o,a); 
				this.open(o);
	},
	iframe : function(str,a) { 
				var o = { type :'iframe', url : str,h_title : 'JYH IFRAME ver 1.0',buttons :[this.close_button] };   
				if(typeof a == 'object') $.extend(o,a); 
				this.open(o);
	},
	load   : function(str,a) {
				var o = { type :'ajax',  url : str, h_title : 'JYH AJAX ver 1.0',buttons :[this.close_button] }; 
				if(typeof a == 'object') $.extend(o,a); 
				this.open(o);
	},
	notice : function(str,a) { 
				var o = { type:'notice', css:'notice', header : false, footer : false, b_title : str, drag : false, pos:'LT',x:10,y:20};
				if(typeof a == 'object') $.extend(o,a); 
				this.open(o);
	},
	image  : function(src,a) {
				var myImage = new Image();
				myImage.onload = function() { 
					var o = { type :'image', img : myImage, css:'image', header:false, footer:false,overlay:true,x:10,y:10};
					if(typeof a == 'object') $.extend(o,a);
					h_dialog.open(o);
				}
				myImage.src = src;

	},
	cover : function(a) {
				var o = { over_close:false, over_opacity:0.6 }; 
				if(typeof a == 'object') $.extend(o,a);
				$("<div>", { id  :  'overlay_only' , class : 'h_dialog_overlay'}).appendTo("body").show();
			//	$( '<i class="fa fa-spinner fa-5x fa-spin"></i>' ).appendTo( "#overlay_only" );
				$( '<div id="progress_index">123</div>' ).appendTo( "#overlay_only" );
				if(o.over_opacity) $("#overlay_only").css({opacity: o.over_opacity});
				if(o.over_close  ) $("#overlay_only").on('click', function() {$('#overlay_only').animate({opacity:0},300,function(){ $("#overlay_only").remove(); });});
	},
	closeCover : function() { $('#overlay_only').animate({opacity:0},300,function(){ $('#overlay_only').remove(); }); }
};

$(document).ready(function(){
	window.imageRotate = new Array();
	$("[data-myimage]").each(function(i){ imageRotate[i] = $(this).attr("data-myimage").replace(DOCU_ROOT,'/DOCU_ROOT') +'/'+ $(this).text(); });
	$(".img-thumbs,.img-click").each(function(i){ imageRotate[i] = $(this).attr('src').replace('썸즈네일/',''); });
});

var Storage = {

	l : 'local',
	a : function(name,value) {
		
		var sval = (typeof value == 'object')? JSON.stringify(value) : value;  

		if( this.l == 'local') localStorage.setItem( name, sval ); 
		else sessionStorage.setItem( name, sval ); 
	},

	r : function( name ) {
		if( this.l == 'local' ) return localStorage.getItem( name ); 
		else return sessionStorage.getItem( name ); 
	},

	d : function(name) {  
		if( this.l == 'local' ) localStorage.removeItem( name ); 
		else sessionStorage.removeItem( name ); 
	},
	
	c : function () {
		if( this.l == 'local' ) localStorage.clear(); 
		else sessionStorage.clear(); 
	}
};

function winopen(url,xwidth,ywidth,title) {
	var url = uri('linkurl') + url; 
	xwidth = (typeof xwidth !== 'undefined')? 'width='+ xwidth +',' : 'width=500,';
	ywidth = (typeof ywidth !== 'undefined')? 'height='+ywidth +',' : 'height=400,';
	title  = (typeof title !== 'undefined')? title : 'jyh_window_open';	
	var option = "menubar=0,directories=0,resizable=0,scrollbars=1";
	option = xwidth + ywidth + option; 
	var newWin = window.open( url, title, option); 
	newWin.focus();
}
// title can be one of these '_blank, _parent, _self, _top' 
function winopen2(url,xwidth,ywidth,title) {
	xwidth = (typeof xwidth !== 'undefined')? 'width='+ xwidth +',' : 'width=1024,';
	ywidth = (typeof ywidth !== 'undefined')? 'height='+ywidth +',' : 'height=768,';
	title  = (typeof title !== 'undefined')? title : 'jyh_window_open2';	
	var option = "menubar=0,directories=0,resizable=0,scrollbars=1";
	option = xwidth + ywidth + option; 
	var newWin = window.open( url, title, option); 
	newWin.focus();
}
function clipBoard(msg) {
	var temp = $("<input>");   $("body").append(temp);  temp.val(msg).select();   document.execCommand("copy");  temp.remove();
}

function html_pretty(str) { 
	str=str.replace(/(<br>)([^\n])/g,"$1\n$2")
		   .replace(/<p(.*?)>([^\n])/g,"<p$1>\n$2").replace(/([^\n])<div(.*?)>/g,"$1\n<div$2>\n")
		   .replace(/([^\n])(<img|<span|<li)/g,"$1\n$2")
  		   .replace(/([^\n])(<\/p>)/g,"$1\n$2")
  		   .replace(/([^\n])(<\/div>)/g,"$1\n$2")
		   .replace(/></g,">\n<")
		   .replace(/class=""/g,'');
	return $.trim(str);
}

function src_filter(str) {
	return str.replace(/[\(\)\:\[\]\;\|]/g,'');
}
