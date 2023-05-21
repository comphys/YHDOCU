var 진행일자 = $("input[name='add0']" ).val();

if(uri('method')=='write' && 진행일자 !='None') { var AutoCalulated = false; $("#notice-calculated").addClass('notice-calculated'); load_value(); } 
else var AutoCalulated = true;

var 입금,출금,잔액,현금비중
//
var 매수금1,매도금1,변동수량1,배당금
var 종가1, 배당가치, 보유수량1,배당비중
var 평균단가1, 매도누적1, 매수누적1, 현매수금1
//
var 매수금2,매도금2,변동수량2,현수익률
var 종가2, 레버가치,보유수량2,레버비중
var 평균단가2, 매도누적2, 매수누적2, 현매수금2
var 연속상승, 연속하락, 현재손익, 회복전략
//
var 가용잔액, 배당합계, 입금합계, 전투자금
var 추가자금, 출금합계, 가치합계, 전수익률
var 현재시즌, 일매수금, 매수수량, 매도수량
var 경과일수, 기초수량, 매수가격, 매도가격
var 진행상황, 수수료등, 누적수수료, 보존금액

var 분할횟수, 큰단가치, 비중조절, 첫매가치, 둘매가치, 회수기한, 강매시작, 평단가치, 위매비중, 위매시점

function client_calculate() {
	if(AutoCalulated) {h_dialog.notice("계산이 완료된 상태입니다."); return; }
//  현금투자 부분 계산
	입금 = ctv('add1','f'); 출금 = ctv('add2','f'); 
	잔액 = 잔액 + 입금 - 출금; 입금합계 += 입금; 출금합계 -= 출금; 전투자금 = 입금합계 - 출금합계;
//  JEPG 부분 계산
	매수금1=ctv('add5','f'); 매도금1=ctv('add6','f');  변동수량1=ctv('sub8','i'); 배당금=ctv('sub10','f'); 
	보유수량1 += 변동수량1;   현매수금1+=매수금1; 
	
	매도누적1 += 매도금1; 매수누적1 += 매수금1;
	수수료등 = commission(매수금1,1); 수수료등 += commission(매도금1,2); 

	if(보유수량1 == 0) {평균단가1=0.0; 현매수금1=0.0; } else { 평균단가1 = 현매수금1/보유수량1;}
	잔액 = 잔액 - 매수금1 + 매도금1 + 배당금 - 수수료등; 배당합계+=배당금
	배당가치 = 보유수량1 * 종가1
//  SOXL 부분 계산
	매수금2=ctv('add11','f'); 매도금2=ctv('add12','f');  변동수량2=ctv('sub9','i'); 
	if(-변동수량2 == 보유수량2) { 현재손익 = 매도금2 - 현매수금2;}
	보유수량2 += 변동수량2; 현매수금2 += 매수금2;

	매도누적2 += 매도금2; 매수누적2 += 매수금2;
	수수료등 += commission(매수금2,1); 수수료등 += commission(매도금2,2); 누적수수료 += 수수료등; 

	잔액 = 잔액 - 매수금2 + 매도금2 - 수수료등; 
	레버가치 = 보유수량2 * 종가2;

	if(보유수량2 == 0) {평균단가2=0.0; 
		현수익률  = (매도금2*현매수금2)? (매도금2/현매수금2 -1)*100 : 0.0; 
		현매수금2=0.0; } 
	else { 평균단가2 = 현매수금2/보유수량2; 현수익률  = ( 종가2/평균단가2 -1)*100 ; 현재손익 = (종가2 - 평균단가2) * 보유수량2; }
//  투자전략 부분 계산
	가치합계 = 잔액 + 배당가치 + 레버가치;
	전수익률 = (가치합계 / 전투자금 - 1) * 100; 
	현금비중 = (잔액 / 가치합계)*100; 배당비중 = (배당가치/가치합계)*100; 레버비중 = (레버가치/가치합계)*100; 
	
	가용잔액 = 가용잔액 + 매도금2 - 매수금2;
	추가자금 = 추가자금 - 수수료등;

	if(가용잔액 < 0) { 추가자금 += 가용잔액; 가용잔액 = 0.0; }
	
	if(보유수량2==0) {

		if(매도금2) { 
			진행상황 = '전량매도'; 
			if(현재손익 < 0) { 진행상황='전략매도'; 회복전략 = 위매시점;} else {진행상황='전량매도'; 회복전략 = 0.0}
			현재시즌 += 1; 경과일수 = 0; 
			rebalance();
	    }
		else { 수수료등 = 0.0; 누적수수료 = 0.0;}		

		기초수량=매수수량 = Math.ceil(일매수금/종가2);
		매수가격 = 종가2 * 큰단가치; 
		매도수량 = 0;
		매도가격 = 매수가격+0.01; 

	} else { 
		경과일수 += 1; normal_sell(); normal_buy();
		진행상황 = (경과일수==1)? '첫날매수' : '일반매수';
	}


//  출력파트
	c_print('add1',입금,2);			c_print('add2',출금,2);		       c_print('add3',잔액,2);			c_print('add4',현금비중,2);      

	c_print('add5',매수금1,2);		c_print('add6',매도금1,2);		   c_print('sub8',변동수량1,0);     c_print('sub10',배당금,2);
	v_print('add8',종가1,2);		c_print('add9',배당가치,2);		  c_print('add7',보유수량1,0);      c_print('add10',배당비중,2);
	c_print('sub21',평균단가1,4);	c_print('sub22',매도누적1,2);	   c_print('sub23',매수누적1,2);    c_print('sub24',현매수금1,2);

	c_print('add11',매수금2,2);		c_print('add12',매도금2,2);		   c_print('sub9',변동수량2,0);     c_print('sub33',현수익률,2);
	v_print('add14',종가2,2);		c_print('add15',레버가치,2);	   c_print('add13',보유수량2,0);    c_print('add16',레버비중,2);
	c_print('sub16',평균단가2,4);	c_print('sub15',매도누적2,2);	   c_print('sub14',매수누적2,2);    c_print('sub17',현매수금2,2);
	v_print('sub5',연속상승,0);	    v_print('sub6',연속하락,0);	       c_print('add18',현재손익,2);     c_print('sub7',회복전략,1);

	c_print('add19',가용잔액,2);    c_print('sub11',배당합계,2);       c_print('sub25',입금합계,2);     c_print('sub27',전투자금,2);
	c_print('add20',추가자금,2);    c_print('sub26',출금합계,2);       c_print('add17',가치합계,2);     c_print('sub28',전수익률,2);
	c_print('sub1',현재시즌,0);     c_print('sub4',일매수금,0);        c_print('sub2',매수수량,0);      c_print('sub3',매도수량,0);
	c_print('sub12',경과일수,0);    c_print('sub18',기초수량,0);       c_print('sub19',매수가격,2);     c_print('sub20',매도가격,2);
	v_print('sub29',진행상황,3);    c_print('sub30',수수료등,2);       c_print('sub31',누적수수료,2);   v_print('sub32',보존금액,0);

	h_dialog.notice("변동사항 계산을 완료하였습니다");
	AutoCalulated = true; $("#notice-calculated").removeClass('notice-calculated');
}

function ctv(key,opt='f') { a = $("input[name='"+key+"']" ).val();   if(!a) return 0 ;  a = a.replace(/,/g,'');  if(opt=='i') return parseInt(a);  else return parseFloat(a);}

function check_buy() {
    c_print('sub9',0,0); c_print('add11',0, 2);
    if( 경과일수 ==0 ) { 
        if(종가2 <= 매수가격){ 기초수량 = Math.ceil(일매수금/전일종가);  c_print('sub9',기초수량,0); c_print('add11', 종가2 * 기초수량, 2);  }
    } else if(종가2 <= 매수가격 ) { c_print('sub9',매수수량,0); c_print('add11', 종가2 * 매수수량, 2); }
}

function check_sell() {
    c_print('add12',0, 2);
    if( 경과일수 == 0 ) return;
    if( 종가2 >= 매도가격 ) {c_print('sub9',-매도수량,0); c_print('add12', 종가2 * 매도수량, 2);}
}

function rebalance() { total = 가용잔액 + 추가자금; 가용잔액 = parseInt((total * 2)/3); 추가자금 = parseInt(total - 가용잔액); 	일매수금 = parseInt(가용잔액/분할횟수); }

function normal_sell() {
	매수수량 = Math.ceil(기초수량 * (경과일수*비중조절 +1));
	매도가격 = 평균단가2 * 첫매가치;
	if(매수수량 * 전일종가 > 가용잔액 + 추가자금) { 매도가격 = 평균단가2 * 둘매가치; }
	if(회복전략 && (경과일수 +1 <= 회수기한)) {매도가격 = 평균단가2 * (회복전략/100 +1);}
	if(경과일수 +1 >= 강매시작) {매도가격 = 평균단가 * 강매가치;}
	매도가격 = round_up(매도가격);
	매도수량 = 보유수량2;	 
}

function normal_buy() {
	매수가격 = 종가2 * 평단가치;
	매수수량 = Math.ceil(기초수량 * (경과일수*비중조절 +1));

	if(매수수량 * 종가2 > 가용잔액 + 추가자금) { 매수수량 = 기초수량 * 위매비중; 진행상황 = '매수제한'; }
	if(매수수량 * 종가2 > 가용잔액 + 추가자금) { 매수수량 = 0; 진행상황 = '매수금지'; }
	if(매수가격 >= 매도가격) 매수가격 = 매도가격 - 0.01;
}


function s_load(key,opt,opt2='B') {if(opt2=='B') { a=JBODY[key]} else if(opt2=='S') { a=JSTRG[key] } else if(opt2=='D') { a=J_DIV[key] } else if(opt2=='L') { a=J_LEV[key] }  if(!a) return 0 ;  a = a.replace(/,/g,'');  if(opt=='i') return parseInt(a);  else return parseFloat(a); }
function c_print(pos,num,weigh) { $("input[name='"+pos+"']").val(num.toFixed(weigh)).comma('init');}
function commission(mm,opt) {if(opt==1) { return (parseInt(mm*0.07)/100);}	else if(opt==2) { m1 = parseInt(mm*0.07)/100; m2=Math.round(mm*0.00229)/100; return m1+m2;}}
function v_print(pos,num,weigh) { if(weigh==3) $("input[name='"+pos+"']").val(num); }


function back_restore() {
	let 매수금   = s_load('add11','f');
	let 가용잔액 = s_load('add19','f');
	가용잔액 += 매수금; 매수금 = 0.00; 
	c_print('add11',매수금,2);
	c_print('add19',가용잔액,2);
}


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
		bs = ctv('sub16','f')
		if(! bs) bs = ctv('add14','f') 
		sum = 0
		for(i=1;i<21;i++) {
			tmp = (bs * (1-i/100)).toFixed(2)
			content += "<span style='display:inline-block;width:50px;text-align:right'>-"+i+"% :</span>"
			content += "<span style='display:inline-block;width:70px;text-align:right'>"+tmp+"</span><br>" 
		}
	} else if(opt==3) {
		title = "매도가격 참고표"		
		bs = ctv('sub16','f')
		if(! bs) bs = ctv('add14','f') 
		sum = 0
		for(i=1;i<21;i++) {
			tmp = (bs * (1+i/100)).toFixed(2)
			content += "<span style='display:inline-block;width:50px;text-align:right'>"+i+"% :</span>"
			content += "<span style='display:inline-block;width:70px;text-align:right'>"+tmp+"</span><br>" 
		}
	}
	$("#add-info .add-info-title").html(title);
	$("#add-info .add-info-content").html(content);
	$("#add-info").toggle()
}

function show_unit_buy(opt) {
	var n = Math.abs(ctv('sub9','i'))
	var div = 0
	if(opt == 1) { div = ctv('add11','f')} else {div = ctv('add12','f')}
	
	h_dialog.notice((div/n).toFixed(2))
}

function initiate_basic() {
	let theDay  = $("input[name='add0']").val();
	let Balance = $("input[name='add3']").val();
	if(theDay=='None') {h_dialog.notice('날자를 선택하여 주세요'); return;}
	if(!Balance) {h_dialog.notice('잔액을 입력하여 주세요'); return;}
	
	let posturl = uri('linkurl')+ 'boards-guide/initiate_basic/'+uri(0)

	postData = {theDay:theDay, Balance:Balance}
	$.post( posturl, postData).done(function(data) {
		var ans = JSON.parse(data);
		for(let i in ans) { $("input[name='"+i+"']" ).val(ans[i]); }
	});
	AutoCalulated = true; $("#notice-calculated").removeClass('notice-calculated');
}	

function reset_value() {
    var reset_key = ['add1','add2','add3','add4',
                    'add5','add6','sub8','sub10','add8','add9','add7','add10','sub21','sub22','sub23','sub24',
                    'add11','add12','sub9','sub33','add14','add15','add13','add16','sub16','sub15','sub14','sub17','sub5','sub6','add18','sub7',
                    'add19','sub11','sub25','sub27','add20','sub26','add17','sub28','sub1','sub4','sub2','sub3','sub12','sub18','sub19','sub20','sub29','sub30','sub31','sub32']

    for(i=0;i<reset_key.length;i++) { $("input[name='"+reset_key[i]+"']" ).val(''); }
	AutoCalulated = false; $("#notice-calculated").addClass('notice-calculated');
	load_value();
}


function load_value() {
    if( AutoCalulated ) return;
        // 현금투자 - 변수선언
        잔액= s_load('add3','f');
        // JEPQ - 변수선언
        종가1= s_load('add3','f','D'); 보유수량1    = s_load('add7','i'); 
        평균단가1= s_load('sub21','f');  매도누적1 = s_load('sub22','f');  매수누적1= s_load('sub23','f');  현매수금1= s_load('sub24','f');
        // SOXL - 변수선언
        종가2=s_load('add3','f','L');  보유수량2 = s_load('add13','i');  전일종가 = s_load('add14','f')
        평균단가2=s_load('sub16','f');  매도누적2 = s_load('sub15','f');  매수누적2 = s_load('sub14','f');  현매수금2= s_load('sub17','f');
        연속상승= s_load('add9','i','L');  연속하락= s_load('add10','i','L'); 회복전략 = s_load('sub7','f');
        // 투자전략 - 변수선언
        가용잔액=s_load('add19','f');  배당합계 = s_load('sub11','f');  입금합계=s_load('sub25','f');  전투자금=s_load('sub27','f');  
        추가자금=s_load('add20','f');  출금합계 = s_load('sub26','f');   
        현재시즌=s_load('sub1','i');   일매수금 = s_load('sub4','i');  매수수량 = s_load('sub2','i');  매도수량 = s_load('sub3','i'); 
        경과일수=s_load('sub12','i');  기초수량 = s_load('sub18','i');  매수가격 = s_load('sub19','f');  매도가격 = s_load('sub20','f'); 
        누적수수료 = s_load('sub31','f');  보존금액 = s_load('sub32','f');
		// 전략변수
		분할횟수=s_load('add2','i','S');  
		큰단가치=s_load('add5','f','S');  큰단가치 = 1 + 큰단가치/100;
		비중조절=s_load('add3','f','S');  비중조절 = 1 + 비중조절/100; 
		첫매가치=s_load('add9','f','S');  첫매가치 = 1 + 첫매가치/100;
		둘매가치=s_load('add10','f','S'); 둘매가치 = 1 + 둘매가치/100;
		회수기한=s_load('add11','i','S');
		강매시작=s_load('add17','i','S');
		강매가치=s_load('add18','f','S'); 강매가치 = 1 + 강매가치/100;
		평단가치=s_load('add4','f','S');  평단가치 = 1 + 평단가치/100;
		위매비중=s_load('add25','f','S');
		위매시점=s_load('add22','f','S'); 

        // 현금투자
        c_print('add1',0,2); c_print('add2',0,2); c_print('add3',잔액,2);
        // 배당투자
        c_print('add5',0,2); c_print('add6',0,2);  c_print('sub8',0,0); c_print('sub10',0,2);
        c_print('add8',종가1,2); c_print('add9',종가1 * 보유수량1,2); c_print('add7',보유수량1,0);
        c_print('sub21',평균단가1,4); c_print('sub22',매도누적1,2); c_print('sub23',매수누적1,2); c_print('sub24',현매수금1,2);
        // SOXL
        check_buy(); check_sell();
        c_print('add14',종가2,2);  c_print('add15',종가2*보유수량2,0); c_print('add13',보유수량2,0);
        c_print('sub16',평균단가2,4); c_print('sub15',매도누적2,2); c_print('sub14',매수누적2,2); c_print('sub17',현매수금2,2);
        c_print('sub5',연속상승,0); c_print('sub6',연속하락,0); c_print('sub7',회복전략,1);
    
        // 투자전략
        c_print('add19',가용잔액,2);  c_print('sub11',배당합계,2); c_print('sub25',입금합계,2);  c_print('sub27',전투자금,2); 
        c_print('add20',추가자금,2);  c_print('sub26',출금합계,2);
        c_print('sub1',현재시즌,0);  c_print('sub4',일매수금,0); 
        c_print('sub12',경과일수,0); c_print('sub18',기초수량,0); 
        c_print('sub31',누적수수료,2); c_print('sub32',보존금액,0); 
    }

// =========================================================================================================================================================

function money_inout() {
	let 입금     = ctv('add1','f');
    let 출금     = ctv('add2','f');
	let 잔액     = ctv('add3','f');
	let 배당가치 = ctv('add9','f');
	let 레버가치 = ctv('add15','f');
	let 입금합계 = ctv('sub25','f');
	let 출금합계 = ctv('sub26','f');
	let 전투자금 = ctv('sub27','f');

	잔액 = 잔액 + 입금 - 출금
	입금합계 += 입금
	출금합계 += 출금
	전투자금 = 입금합계 - 출금합계
	가치합계 = 잔액 + 배당가치 + 레버가치
    비중1 = 잔액/가치합계*100;
    비중2 = 배당가치/가치합계*100;
    비중3 = 레버가치/가치합계*100;
	현수익률 = (가치합계 / 전투자금 - 1) * 100;
	
	c_print("add3",잔액,2);
	c_print("add17",가치합계,2);
	c_print("add4",비중1,2);
    c_print("add10",비중2,2);
    c_print("add16",비중3,2);
	c_print("sub25",입금합계,2);
	c_print("sub26",출금합계,2);
	c_print("sub27",전투자금,2);
	c_print("sub28",현수익률,2);
	h_dialog.notice("입출금을 재반영 하였습니다");
}

function round_up(n,decimals=2){
    multiplier = 10 ** decimals;
    return Math.ceil(n * multiplier) / multiplier;
 }