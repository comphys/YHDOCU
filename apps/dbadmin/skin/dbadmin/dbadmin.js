var _bse = "{{D['_bse']}}";

(function($){ var YH_liveEdit={ 
    init:function(){ 
        return this.each(function(){ 
            var ori = $(this).text(); 
            var sel = this;
            $(this).on('dblclick', function() { 
                // $(this).text('');  
                $(this).attr('contenteditable',true).addClass('field-edit-on').focus();}); 
                $(this).on('keydown', function(event) { if(event.which == 27) {
                    $(this).attr('contenteditable',false).removeClass('field-edit-on');
                    $(this).text(ori)
                } 
                if(event.which == 13) { $(this).attr('contenteditable',false).removeClass('field-edit-on'); 
                var tbl = uri(0); 
                var no  = $(this).parent().children("td:first").attr("data-no");
                var key = $(this).attr('data-fid');	
                var val = $(this).text(); 
                var data = {'tbl':tbl, 'no':no, 'key':key, 'val' : val}
                var posturl = _bse + 'dbadmin/tbl_live_edit'; 
                $.post(posturl,data,null,'json').done(function(data){
                    if(data.err == 'error' ) { $(sel).text(ori); h_dialog.notice(data.msg);}
                    else if(val=='null') $(sel).text('None');
                });}});});}, 
                clear:function(){ return this.each(function(){ $(this).off(); });}};	
                $.fn.liveEdit =function(method) { 
                    if(YH_liveEdit[method]) { 
                        return YH_liveEdit[method].apply(this,Array.prototype.slice.call(arguments,1));} 
                        else if(typeof method === 'object' || ! method){ 
                            return YH_liveEdit.init.apply( this,arguments);} 
                            else { $.error( 'Method ' +method+' does not exist');}};})(jQuery);


$('.liveEdit').liveEdit();

$("#dbInput").click(function(){
    var url = uri('_bse') + 'dbadmin/tbl_dbinput/' + uri(0) 
    winopen(url,x=600,y=500,title='JYH_DB_INPUT')
});

$("#tbl-structure").click(function(){
    var url = uri('_bse') + 'dbadmin/tbl_structure/' + uri(0)
    winopen(url,x=600,y=400,'tbl1')
});

$("[data-no]").dblclick(function(){
    $(this).parent().css("backgroundColor",'black')
    var no = $(this).attr('data-no');
    var url = _bse + "dbadmin/tbl_delete_row";
    data = {'no':no, 'tbl':uri(0)}
    self = this;
	h_dialog.confirm(no + ' 행을 정말 삭제하시겠습니까?',
		{  x:mouse_X+50, y:mouse_Y+20, over_opacity:0.01, h_title :'다시 확인해 주세요',
           buttons: 
            [
                {text : '돌아가기', call: function(a) { $(self).parent().css("backgroundColor",''); h_dialog.close(a); }},
                {text : '삭제하기', call: function(a) {$.post(url,data).done(function(data){location.reload()});}}
			]
	});    
    
});

$('.text-content').click(function(){
    var no  = $(this).parent().children("td:first").attr("data-no");
    var content = $(this).children("div");
    //var html = htmldecode($(content).text());
    html = $(content).text()
    h_dialog.alert(html,{h_title:no+'번 본문 내용',x:mouse_X-50,y:mouse_Y+10,width:800,height:500});
});

function htmldecode(str) {
    if (typeof(str)=="string") {
        str=str.replace(/&gt;/ig, ">").replace(/&lt;/ig, "<").replace(/&#039;/g, "'").replace(/&quot;/ig, '"').replace(/&amp;/ig, '&');	
    }
    return str;	
}

function send_qry_execute(opt) {
    var qry = $("#qry-text").val();
    var rst = $("#qry-result");
    var url = _bse + "dbadmin/qry_execute";
    var method = 'reload'
    if ((qry.indexOf("SELECT") != -1) ||  (qry.indexOf("PRAGMA") != -1)) method = 'show' ;
    data = {'qry':qry,'opt':opt}
    $.post(url,data).done(function(data){
      if(method == 'show')  $(rst).val(data); else location.reload(); 
    });
}

function delete_table(opt) {  var tbl = $("#work_tbl"+opt).val(); $("#qry-text").val("DROP TABLE "+tbl); }
function select_table(opt) {  var tbl = $("#work_tbl"+opt).val(); $("#qry-text").val("SELECT * FROM "+tbl+" WHERE 1"); }
function struct_table(opt) {  
    var tbl = $("#work_tbl"+opt).val();
    var url = uri('_bse') + 'dbadmin/tbl_structure/' + tbl
    winopen(url,x=600,y=400,'tbl_structure' + opt)
}
function index_table()  {  $("#qry-text").val("SELECT name,tbl_name FROM sqlite_master WHERE type='index'"); }
function get_file_name(){  $.ajax( _bse + "docufiles/get_file_name").done(function(data){alert(data)}) }
function rename_table(opt) {  var tbl = $("#work_tbl"+opt).val(); $("#qry-text").val("ALTER TABLE "+tbl+" RENAME TO  temp_table"); }
function copy_dbtable() {
    tbl1 = $("#work_tbl1").val();
    tbl2 = $("#work_tbl2").val();
    var url = _bse + "dbadmin/copy_dbtable";
    data = {'tbl1':tbl1, 'tbl2':tbl2}
    $.post(url,data).done(function(data){$("#qry-text").val(data);})
}
function delete_index(opt) {  var tbl = $("#work_tbl"+opt).val(); $("#qry-text").val("DROP INDEX IF EXISTS unq_"+tbl+"_"); }
function clear_work() {  $("#qry-text").val(''); $("#qry-result").val('');  }
