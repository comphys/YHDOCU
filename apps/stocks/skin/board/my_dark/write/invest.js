var 진행일자 = $("input[name='add0']" ).val();

if(uri('method')=='write' && 진행일자 !='None') { var AutoCalulated = false; $("#notice-calculated").addClass('notice-calculated'); load_value(); } 
else var AutoCalulated = true;

var 입금액수,출금액수,현재잔액,현금비중
//  --------------------------------------------------
var 매수금액, 매도금액, 변동수량, 현수익률
var 마감금액, 레버가치, 보유수량, 레버비중
var 평균단가, 매도누적, 매수누적, 현매수금
var 연속상승, 연속하락, 현재손익, 회복전략
//  --------------------------------------------------
var 가용잔액, 배당합계, 입금합계, 전투자금
var 추가자금, 출금합계, 가치합계, 전수익률
var 현재시즌, 일매수금, 매수수량, 매도수량
var 경과일수, 기초수량, 매수가격, 매도가격
var 진행상황, 수수료등, 누적수료, 보존금액
//  ---------------------------------------------------
var 분할횟수, 큰단가치, 비중조절, 첫매가치, 둘매가치, 회수기한, 강매시작, 평단가치, 위매비중, 위매시점
var 자산배분
//  ---------------------------------------------------
var 찬스설정 = false

function client_calculate(opt=1) {if(AutoCalulated) {h_dialog.notice("계산이 완료된 상태입니다."); return;}

	//  do the Math : Cash Part
	입금액수 = ctv('add1','f'); 
	출금액수 = ctv('add2','f'); 
	현재잔액+= 입금액수 - 출금액수; 
	입금합계+= 입금액수; 
	출금합계+= 출금액수; 
	전투자금 = 입금합계-출금합계;

	//  do the Math : Leverage Part
	매수금액 =ctv('add11','f'); 
	매도금액 =ctv('add12','f');  
	변동수량 =ctv('add5','i'); 
	마감금액 =ctv('add14','f');

	if(-변동수량 == 보유수량) { 현재손익 = 매도금액 - 현매수금;}
	
	보유수량 += 변동수량; 
	현매수금 += 매수금액;
	매도누적 += 매도금액; 매수누적 += 매수금액;

	수수료등  = commission(매수금액,1); 
	수수료등 += commission(매도금액,2); 
	누적수료 += 수수료등; 

	현재잔액 = 현재잔액 - 매수금액 + 매도금액 - 수수료등; 
	레버가치 = 보유수량 * 마감금액;

	if( 보유수량 == 0) {
	   	평균단가 = 0.0; 
	    현수익률 = (매도금액*현매수금)? (매도금액/현매수금 -1)*100 : 0.0; 
		현매수금=0.0; 
	} else {  
		평균단가 = 현매수금/보유수량; 
		현수익률 =(마감금액/평균단가 -1)*100 ; 
		현재손익 = 레버가치 - 현매수금; 
	}

	//  do the Math : INVEST Strategy
	가용잔액 = ctv('add19','f'); 
	추가자금 = ctv('add20','f'); 
	현재시즌 = ctv('sub1','i');  
	경과일수 = ctv('sub12','i'); 
	일매수금 = ctv('sub4','i');  
	기초수량 = ctv('sub18','i');

	가치합계 = 현재잔액 + 레버가치;
	전수익률 = (가치합계 / 전투자금 - 1) * 100; 
	현금비중 = (현재잔액 / 가치합계)*100; 
	레버비중 = (레버가치/가치합계)*100; 
	가용잔액 = 가용잔액 + 매도금액 - 매수금액;
	추가자금 = 추가자금 - 출금액수 - 수수료등;

	if(가용잔액 < 0) { 추가자금 += 가용잔액; 가용잔액 = 0.0; }
	
	if(보유수량==0) {

		if( 매도금액) { 
			진행상황 = '전량매도'; 
			if(현재손익 < 0) { 진행상황='전략매도'; 회복전략 = 위매시점;} 
			else {진행상황='전량매도'; 회복전략 = 0.0}
			현재시즌 += 1; 경과일수 = 0; 
			rebalance();
	    }
		else { 수수료등 = 0.0; 누적수료 = 0.0;}		

		기초수량 = 매수수량 = Math.ceil(일매수금/마감금액);
		매수가격 = 마감금액 * 큰단가치; 
		매도수량 = 0;
		매도가격 = 매수가격+0.01; 

	} else { 
		진행상황 = '일반매수'
		경과일수+= 1; 
		tomorrow_sell(opt); 
		tomorrow_buy(opt);
		if(경과일수==1) {진행상황 = '첫날매수'; 누적수료=수수료등;} 
	}


	//  출력파트
	vtc('add1',입금액수,2);		vtc('add2',출금액수,2);		vtc('add3',현재잔액,2);		vtc('add4',현금비중,2);      

	vtc('add11',매수금액,2);	vtc('add12',매도금액,2);	vtc('add5',변동수량,0); 	vtc('add8',현수익률,2);
	vtc('add14',마감금액,-1);	vtc('add15',레버가치,2);	vtc('add9',보유수량,0);     vtc('add16',레버비중,2);
	vtc('add7',평균단가,4);	    vtc('sub15',매도누적,2);	vtc('sub14',매수누적,2);    vtc('add6',현매수금,2);
	vtc('sub5',연속상승,-1);	vtc('sub6',연속하락,-1);	vtc('add18',현재손익,2);    vtc('sub7',회복전략,1);

	vtc('add19',가용잔액,2);    vtc('sub11',배당합계,2);    vtc('sub25',입금합계,2);    vtc('sub27',전투자금,2);
	vtc('add20',추가자금,2);    vtc('sub26',출금합계,2);    vtc('add17',가치합계,2);    vtc('sub28',전수익률,2);
	vtc('sub1',현재시즌,0);     vtc('sub4',일매수금,0);     vtc('sub2',매수수량,0);     vtc('sub3',매도수량,0);
	vtc('sub12',경과일수,0);    vtc('sub18',기초수량,0);    vtc('sub19',매수가격,2);    vtc('sub20',매도가격,2);
	vtc('sub29',진행상황,-2);   vtc('sub30',수수료등,2);    vtc('sub31',누적수료,2);    vtc('sub32',보존금액,-1);

	h_dialog.notice("변동사항 계산을 완료하였습니다");
	AutoCalulated = true; 
	$("#notice-calculated").removeClass('notice-calculated');
}

function check_buy() {
    vtc('add5',0,0); 
	vtc('add11',0,2);
    if( 경과일수 == 0 ) { 
        if(마감금액 <= 매수가격){ 
			기초수량 = Math.ceil(일매수금/전일종가);  
			vtc('add5', 기초수량,0); 
			vtc('add11',마감금액 * 기초수량, 2);  }
    } else if(마감금액 <= 매수가격 ) { 
		vtc('add5', 매수수량,0); 
		vtc('add11',마감금액 * 매수수량, 2); 
	}
}

function check_sell() {
    vtc('add12',0, 2);
    if( 경과일수 == 0 ) return;
    if( 마감금액 >= 매도가격 ) {
		vtc('add5', -매도수량,0); 
		vtc('add12', 마감금액 * 매도수량, 2);}
}

function tomorrow_sell(opt) {
	
	매수수량 = Math.ceil(기초수량 * (경과일수*비중조절 +1));
	매도가격 = 평균단가 * 첫매가치;
	if( 매수수량 * 전일종가 > 가용잔액 + 추가자금) { 
		매도가격 = 평균단가 * 둘매가치; 
	}
	if( 회복전략 && (경과일수 +1 <= 회수기한)) {
		매도가격 = 평균단가 * (회복전략/100 +1);
	}
	if(경과일수 +1 >= 강매시작) {
		매도가격 = 평균단가 * 강매가치;
	}
	if(찬스설정) {매도가격 = ctv('sub20','f');}
	else if(opt==2) { 매도가격 = s_load('LS','f')} // LS JBODY['LS'] from 쓰기_CHANCE.py 
	매도가격 = round_up(매도가격);
	매도수량 = 보유수량;
}

function tomorrow_buy(opt) {

	매수가격 = 마감금액 * 평단가치; 
	매수수량 = Math.ceil(기초수량 * (경과일수*비중조절 +1));

	if( 매수수량 * 마감금액 > 가용잔액 + 추가자금) { 
		매수수량 = 기초수량 * 위매비중; 
		진행상황 = '매수제한'; }
	if( 매수수량 * 마감금액 > 가용잔액 + 추가자금) { 
		매수수량 = 0; 
		진행상황 = '매수금지'; }
	if(매수가격 >= 매도가격) 매수가격 = 매도가격 - 0.01;
	if(찬스설정) { 
		매수가격 = ctv('sub19','f'); 
		매수수량 = ctv('sub2','i'); 
	} else if(opt==2) {
		매수가격 = s_load('LB','f'); // LS JBODY['LB'] from 쓰기_CHANCE.py 
	}
}   


function s_load(key,opt,opt2='B') {if(opt2=='B') { a=JBODY[key]} else if(opt2=='S') { a=JSTRG[key] }  else if(opt2=='H') { a=JHIST[key] }  if(!a) return 0 ;  a = a.replace(/,/g,'');  if(opt=='i') return parseInt(a);  else return parseFloat(a); }
function vtc(pos,num,weigh) { if(weigh==-1) return;	if(weigh==-2) $("input[name='"+pos+"']").val(num);	else {$("input[name='"+pos+"']").val(num.toFixed(weigh)).comma('init');}}
function commission(mm,opt) {if(opt==1) { return (parseInt(mm*0.07)/100);}	else if(opt==2) { m1 = parseInt(mm*0.07)/100; m2=Math.round(mm*0.0008)/100; return m1+m2;}}
function ctv(key,opt='f') {a=$("input[name='"+key+"']" ).val(); if(!a) return 0 ;  a = a.replace(/,/g,'');  if(opt=='i') return parseInt(a);  else return parseFloat(a);}
function rebalance() { total = 가용잔액 + 추가자금; 가용잔액 = parseInt((total * 2)/3); 추가자금 = total - 가용잔액; 일매수금 = parseInt(가용잔액/분할횟수); }
function back_restore() {let 매수금액 = s_load('add11','f'); let 가용잔액 = s_load('add19','f'); 가용잔액 += 매수금액; 매수금 = 0.00; vtc('add11',매수금액,2);	vtc('add19',가용잔액,2);}


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

function initiate_invest() {
	let theDay  = $("input[name='add0']").val();
	let Balance = $("input[name='add3']").val();
	if(theDay=='None') {h_dialog.notice('날자를 선택하여 주세요'); return;}
	if(!Balance) {h_dialog.notice('잔액을 입력하여 주세요'); return;}
	
	let posturl = uri('linkurl')+ 'boards-invest_guide/initiate_invest/'+uri(0)

	postData = {theDay:theDay, Balance:Balance}
	$.post( posturl, postData).done(function(data) {
		var ans = JSON.parse(data);
		for(let i in ans) { $("input[name='"+i+"']" ).val(ans[i]); }
	});
	AutoCalulated = true; $("#notice-calculated").removeClass('notice-calculated');
}	

function initiate_chance() {
	let theDay  = $("input[name='add0']").val();
	let Balance = $("input[name='add3']").val();
	let curQty  = $("input[name='add9']").val();
	let bseQty  = $("input[name='sub18']").val();

	if(theDay=='None') {h_dialog.notice('날자를 선택하여 주세요'); return;}
	if(!Balance) {h_dialog.notice('잔액을 입력하여 주세요'); return;}	

	let posturl = uri('linkurl')+ 'boards-invest_guide/initiate_chance/'+uri(0)
	postData = {theDay:theDay, Balance:Balance,curQty:curQty,bseQty:bseQty}
	$.post( posturl, postData).done(function(data) {
		var ans = JSON.parse(data);
		if(ans['rsp']) { for(let i in ans) { $("input[name='"+i+"']" ).val(ans[i]); } }
		else {
			h_dialog.alert(ans['msg'])
		}
	});
	찬스설정 = true
}


function reset_value() {
    var reset_key = ['add1','add2','add3','add4',
                    'add5','add6','add8','add9','add7',
                    'add11','add12','add5','add8','add14','add15','add9','add16','add7','sub15','sub14','add6','sub5','sub6','add18','sub7',
                    'add19','sub11','sub25','sub27','add20','sub26','add17','sub28','sub1','sub4','sub2','sub3','sub12','sub18','sub19','sub20','sub29','sub30','sub31','sub32']

    for(i=0;i<reset_key.length;i++) { $("input[name='"+reset_key[i]+"']" ).val(''); }
	AutoCalulated = false; $("#notice-calculated").addClass('notice-calculated');
	load_value();
}


function load_value() {
    if( AutoCalulated ) return;
        // 현금투자 - 변수선언
        현재잔액= s_load('add3','f');
              
        // SOXL - 변수선언
        마감금액= s_load('add3','f','H');  보유수량 = s_load('add9','i');      전일종가 = s_load('add14','f')
        평균단가= s_load('add7','f');      매도누적 = s_load('sub15','f');     매수누적 = s_load('sub14','f');  현매수금= s_load('add6','f');
        연속상승= s_load('add9','i','H');  연속하락 = s_load('add10','i','H'); 회복전략 = s_load('sub7','f');
        // 투자전략 - 변수선언
        가용잔액= s_load('add19','f');     배당합계 = s_load('sub11','f');     입금합계=s_load('sub25','f');    전투자금=s_load('sub27','f');  
        추가자금= s_load('add20','f');     출금합계 = s_load('sub26','f');   
        현재시즌= s_load('sub1','i');      일매수금 = s_load('sub4','i');      매수수량 = s_load('sub2','i');   매도수량 = s_load('sub3','i'); 
        경과일수= s_load('sub12','i');     기초수량 = s_load('sub18','i');     매수가격 = s_load('sub19','f');  매도가격 = s_load('sub20','f'); 
        누적수료= s_load('sub31','f');     보존금액 = s_load('sub32','f');
		// 전략변수
		분할횟수=s_load('add2','i','S');  
		큰단가치=s_load('add5','f','S');   큰단가치 = 1 + 큰단가치/100;
		비중조절=s_load('add3','f','S');   비중조절 = 1 + 비중조절/100; 
		첫매가치=s_load('add9','f','S');   첫매가치 = 1 + 첫매가치/100;
		둘매가치=s_load('add10','f','S');  둘매가치 = 1 + 둘매가치/100;
		회수기한=s_load('add11','i','S');
		강매시작=s_load('add17','i','S');
		강매가치=s_load('add18','f','S');  강매가치 = 1 + 강매가치/100;
		평단가치=s_load('add4','f','S');   평단가치 = 1 + 평단가치/100;
		위매비중=s_load('add25','f','S');
		위매시점=s_load('add22','f','S'); 

        // 현금투자
        vtc('add1',0,2); vtc('add2',0,2); vtc('add3',현재잔액,2);
          
        // SOXL
        check_buy(); check_sell();
        vtc('add14',마감금액,2);    vtc('add15',마감금액*보유수량,0);    vtc('add9',보유수량,0);
        vtc('add7',평균단가,4);     vtc('sub15',매도누적,2);            vtc('sub14',매수누적,2);    vtc('add6',현매수금,2);
        vtc('sub5',연속상승,0);     vtc('sub6',연속하락,0);             vtc('sub7',회복전략,1);
    
        // 투자전략
        vtc('add19',가용잔액,2);    vtc('sub11',배당합계,2);            vtc('sub25',입금합계,2);   vtc('sub27',전투자금,2); 
        vtc('add20',추가자금,2);    vtc('sub26',출금합계,2);
        vtc('sub1',현재시즌,0);     vtc('sub4',일매수금,0); 
        vtc('sub12',경과일수,0);    vtc('sub18',기초수량,0); 
        vtc('sub31',누적수료,2);    vtc('sub32',보존금액,0); 
		vtc('add10',JBODY['add10'],-2);
    }

// =========================================================================================================================================================

function money_inout() {
	let 입금액수 = ctv('add1','f');
    let 출금액수 = ctv('add2','f');
	let 현재잔액 = ctv('add3','f');
	let 레버가치 = ctv('add15','f');
	let 입금합계 = ctv('sub25','f');
	let 출금합계 = ctv('sub26','f');
	let 전투자금 = ctv('sub27','f');

	현재잔액 = 현재잔액 + 입금액수 - 출금액수
	입금합계 += 입금액수
	출금합계 += 출금액수
	전투자금 = 입금합계 - 출금합계
	가치합계 = 현재잔액 + 레버가치
    현금비중 = 현재잔액/가치합계*100;
    레버비중 = 레버가치/가치합계*100;
	전수익률 = (가치합계 / 전투자금 - 1) * 100;
	
	vtc("add3",현재잔액,2);
	vtc("add17",가치합계,2);
	vtc("add4",현금비중,2);
    vtc("add16",레버비중,2);
	vtc("sub25",입금합계,2);
	vtc("sub26",출금합계,2);
	vtc("sub27",전투자금,2);
	vtc("sub28",전수익률,2);
	h_dialog.notice("입출금을 재반영 하였습니다");
}

function round_up(n,decimals=2){
    multiplier = 10 ** decimals;
    return Math.ceil(n * multiplier) / multiplier;
 }

 function hedge_bets(){
	let 현재잔액 = ctv('add3','f'); 
	let 보존금액 = ctv('sub32','f'); 
	let 마감금액 = ctv('add14','f')
	let 투자금액 = 현재잔액 - 보존금액;
	let 가용잔액 = parseInt((투자금액 * 2)/3); 추가자금 = 투자금액 - 가용잔액; 	일매수금 = parseInt(가용잔액/22);
	let 기초수량 = Math.ceil(일매수금/마감금액);

	vtc("add19",가용잔액,2); 
	vtc("add20",추가자금,2); 
	vtc("sub4",일매수금,0); 
	vtc("sub2",기초수량,0); 
	vtc("sub18",기초수량,0);
 }

 function do_rebalance() {

	let 현재잔액 = ctv('add3','f');
	let 현재종가 = ctv('add14','f');
	let 분할횟수 = 22;
	let 가용잔액 = parseInt((현재잔액 * 2)/3); 
	let 추가자금 = 현재잔액 - 가용잔액; 
	let 일매수금 = parseInt(가용잔액/분할횟수);
	let 기초수량 = Math.ceil(일매수금/현재종가);

	vtc("add19",가용잔액,2); 
	vtc("add20",추가자금,2); 
	vtc("sub4",일매수금,0); 
	vtc("sub18",기초수량,0); 
	h_dialog.notice("현재잔액에 대한 리밸런싱을 수행하였습니다");
}