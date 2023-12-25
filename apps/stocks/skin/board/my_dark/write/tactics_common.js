// -------------------------------------------------------------------------------------------------------------------------
// 공통함수
// -------------------------------------------------------------------------------------------------------------------------


function vtc(pos,num,weigh) { 
	if(pos=='0000') return; 
	if(weigh==-2) $("input[name='"+pos+"']").val(num);	else {$("input[name='"+pos+"']").val(num.toFixed(weigh)).comma('init');}
}
function commission(mm,opt) {
	if(opt==1) { return (parseInt(mm*0.07)/100);}	
	else if(opt==2) { m1 = parseInt(mm*0.07)/100; m2=Math.round(mm*0.0008)/100; return m1+m2;}
}
function ctv(key,opt='f') {a=$("input[name='"+key+"']" ).val(); if(!a) return 0 ;  a = a.replace(/,/g,'');  if(opt=='i') return parseInt(a);  else return parseFloat(a);}

function round_up(n,decimals=2){ multiplier = 10 ** decimals;   return Math.ceil(n * multiplier) / multiplier; }

function show_add_info(opt) {
	let title=''
	let content=''
    
	if(opt==1) {
		title = "일자별 매수수량"		
		bs = ctv('sub18','i') 
		if(! bs) bs = ctv('sub2','i')
		sum = 0
		for(i=0;i<15;i++) {
			tmp = Math.ceil(bs*(i*1.25 +1))
			sum += tmp
			content += "<span style='display:inline-block;width:40px;text-align:right'>"+(i+1)+"일 :</span>"
			content += "<span style='display:inline-block;width:50px;text-align:right'>"+tmp.toLocaleString('ko-KR')+" :</span>" 
			content += "<span style='display:inline-block;width:50px;text-align:right'>"+sum.toLocaleString('ko-KR')+"</span><br>" 
		}
	} else if(opt==2) {
		title = "매수가격 참고표"		
		bs = ctv('add7','f')
		if(! bs) bs = ctv('add14','f') 
		sum = 0
		for(i=1;i<21;i++) {
			tmp = (bs * (1-i/100)).toFixed(2)
			content += "<span style='display:inline-block;width:50px;text-align:right'>-"+i+"% :</span>"
			content += "<span style='display:inline-block;width:70px;text-align:right'>"+tmp+"</span><br>" 
		}
	} else if(opt==3) {
		title = "매도가격 참고표"		
		bs = ctv('add7','f')
		if(! bs) bs = ctv('add14','f') 
		sum = 0
		for(i=1;i<21;i++) {
			tmp = (bs * (1+i/100)).toFixed(2)
			content += "<span style='display:inline-block;width:50px;text-align:right'>"+i+"% :</span>"
			content += "<span style='display:inline-block;width:70px;text-align:right'>"+tmp+"</span><br>" 
		}
	} else if(opt==4) {
		title = "종가기준 참고표"		
		bs = ctv('add14','f')
		for(i=1;i<21;i++) {
			tmp = (bs * (1-i/100)).toFixed(2)
			content += "<span style='display:inline-block;width:50px;text-align:right'>-"+i+"% :</span>"
			content += "<span style='display:inline-block;width:70px;text-align:right'>"+tmp+"</span><br>" 
		}
	}
	$("#add-info .add-info-title").html(title);
	$("#add-info .add-info-content").html(content);
	$("#add-info").toggle()
}

function show_unit_buy(opt) {
	var n = Math.abs(ctv('add5','i'))
	var div = 0
	if(opt == 1) { div = ctv('add11','f')} else {div = ctv('add12','f')}
	
	h_dialog.notice((div/n).toFixed(2))
}