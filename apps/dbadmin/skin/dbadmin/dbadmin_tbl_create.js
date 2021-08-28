var _bse = "{{D['_bse']}}";

// 새 DB 테이블 만들기 관련 -----------------------------------------------------------------------------------
function type_select(sel) {   var html = $("#insert-type-select").html(); $(sel).html( html );}
function null_select(sel) {   var html = $("#insert-null-select").html(); $(sel).html( html );}
function option_select(sel) { var html = $("#insert-option-select").html(); $(sel).html( html );}
function insert_new_field() { var html = $("#insert-field-row").html(); $("#create-tbl-div").append(html);}
function make_create_qry() {
    var temp;
    $("#create-tbl-div").children().each(function(index,element){
       temp = show_sql(element); if(!temp) return false ;
    });
}

function show_sql(obj) {
    var sel = $(obj).find("div"); 
    temp0 = $(sel).eq(0).text();    if(temp0 == '') {h_dialog.notice('field name is missing'); return false;}
    temp1 = $(sel).eq(1).text();
    temp2 = $(sel).eq(2).text();    if (temp2 == 'NULL') temp2 = '';
    temp3 = $(sel).eq(3).text();    
    if (temp3 == 'Default') temp3 = ''
    else { 
        if(temp1 == 'INTEGER')   temp3 = "DEFAULT " + parseInt(temp3) ; 
        else if(temp1 == 'REAL') temp3 = "DEFAULT " + parseFloat(temp3) ; 
        else temp3 = "DEFAULT "+temp3 ; 
    }
   
    var temp = temp0 + ' ' + temp1 + ' ' + temp2 + ' ' + temp3 + ' '  
    $(sel).eq(6).text(temp);
    return temp;
}

function send_create_qry() {
    var tbl_name = $("#tbl-name").val(); 
    if(! tbl_name) { h_dialog.notice("DB 테이블 명칭이 없습니다"); return;}
    make_create_qry();
    var temp = new Array();
    var unqkey = new Array();
    var idxkey = new Array();

    $(".each-qry").each(function(index,element){ 
        temp[index] = $(element).text();
       if($(element).prev().prev().text() == 'UNIQUE') unqkey.push($(element).prev().prev().prev().prev().prev().prev().text());
       if($(element).prev().prev().text() == 'INDEX')  idxkey.push($(element).prev().prev().prev().prev().prev().prev().text());
    });

    var qry = temp.join(',');
    qry = qry.substr(0,qry.length-1);
    qry = "CREATE TABLE "+tbl_name+" ( "+qry+" ) ; ";

    var _now = new Date().getTime();
    
    if(unqkey.length) {
        var temp2=''
        unqkey.forEach(function(val){temp2 += "CREATE UNIQUE INDEX unq_"+_now+"_"+val+" ON "+tbl_name+" ("+val+") ; " });
        qry += temp2;
    }

    if(idxkey.length) {
        var temp2=''
        idxkey.forEach(function(val){temp2 += "CREATE INDEX idx_"+_now+"_"+val+" ON "+tbl_name+" ("+val+") ; " });
        qry += temp2;
    }

    var url = _bse + "dbadmin/qry_commit_many";
    data = {'qry':qry}
    $.post(url,data).done(function(data){location.replace(_bse + "dbadmin/create_tbl");});
}

$("#create-tbl-div").sortable({cancel:'[contenteditable],.notsort'});
// ----------------------------------------------------------------------------------------------------------------