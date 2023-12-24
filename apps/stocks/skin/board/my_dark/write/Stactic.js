var 진행일자 = $("input[name='add0']" ).val();

var 입금액수,출금액수,현재잔액,현금비중
//  --------------------------------------------------
var 매수금액, 매도금액, 변동수량, 현수익률
var 마감금액, 레버가치, 보유수량, 레버비중
var 평균단가, 매도누적, 매수누적, 현매수금
var 연속상승, 연속하락, 종가변동, 현재손익
//  --------------------------------------------------
var 현재시즌, 일매수금, 매수수량, 매도수량
var 경과일수, 기초수량, 매수가격, 매도가격

var 가치합계, 입금합계, 출금합계, 양도세금
var 진행상황, 수수료등, 누적수료, 보존금액
//  ---------------------------------------------------
var 분할횟수, 큰단가치, 비중조절, 첫매가치, 둘매가치, 회수기한, 강매시작, 평단가치, 위매비중, 위매시점
var 자산분배
//  ---------------------------------------------------
var AutoCalculated = true

if(uri('method')=='write' && 진행일자 !='None') { AutoCalculated = false; $("#notice-calculated").addClass('notice-calculated'); load_value();} 

function client_calculate() {
	if(AutoCalculated) {h_dialog.notice("계산이 완료된 상태입니다."); return;}
	// do the Math : Cash Part
	입금액수 = ctv('add1','f'); 
	출금액수 = ctv('add2','f'); 
	현재잔액+= 입금액수 - 출금액수; 
	입금합계+= 입금액수; 
	출금합계+= 출금액수; 

	// do the Math : Leverage Part
	if(-변동수량 == 보유수량) { 현재손익 = 매도금액 - 현매수금; }
	보유수량 += 변동수량; 
	현매수금 += 매수금액;
	매도누적 += 매도금액; 매수누적 += 매수금액;

	수수료등  = commission(매수금액,1); 
	수수료등 += commission(매도금액,2);
	누적수료 += 수수료등; 

	현재잔액 = 현재잔액 - 매수금액 + 매도금액 - 수수료등 - 출금액수; 
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

	가치합계 = 현재잔액 + 레버가치;
	현금비중 = (현재잔액 / 가치합계)*100; 
	레버비중 = (레버가치/가치합계)*100; 

	if( 변동수량 <  0) {
		진행상황 = '전량매도'; 
		if(현재손익 < 0) { 진행상황='전략매도' } else { 진행상황='전량매도'}
		현재시즌 += 1; 
	} else { 
		진행상황 = '일반매수'
		tomorrow_sell(); 
		tomorrow_buy();
		if(경과일수==1) {진행상황 = '첫날매수'; 누적수료=수수료등;} 
	}	
	
	if(경과일수==0) rebalance();
	//  출력파트
	vtc('add1',입금액수,2);		vtc('add2',출금액수,2);		vtc('add3',현재잔액,2);		vtc('add4',현금비중,2);      

	vtc('add8',현수익률,2);
	vtc('add14',마감금액,-1);	vtc('add15',레버가치,2);	vtc('add9',보유수량,0);     vtc('add16',레버비중,2);
	vtc('add7',평균단가,4);	    vtc('sub15',매도누적,2);	vtc('sub14',매수누적,2);    vtc('add6',현매수금,2);
	vtc('sub5',연속상승,-1);	vtc('sub6',연속하락,-1);	vtc('sub28',종가변동,1);    vtc('add18',현재손익,2);    

	vtc('sub1',현재시즌,0);     vtc('sub4',일매수금,0);     vtc('sub2',매수수량,0);     vtc('sub3',매도수량,0);
	vtc('sub12',경과일수,0);    vtc('sub18',기초수량,0);    vtc('sub19',매수가격,2);    vtc('sub20',매도가격,2);
	vtc('add17',가치합계,2);    vtc('sub25',입금합계,2);    vtc('sub26',출금합계,2);    vtc('sub11',양도세금,2);
	vtc('sub29',진행상황,-2);   vtc('sub30',수수료등,2);    vtc('sub31',누적수료,2);    vtc('sub32',보존금액,1);

	h_dialog.notice("변동사항 계산을 완료하였습니다");
	AutoCalculated = true; 
	$("#notice-calculated").removeClass('notice-calculated');
}



function load_value() {
    if( AutoCalculated ) return;
        // 현금투자 - 변수선언
        현재잔액= s_load('add3','f');
             
        // SOXL - 변수선언
		매수금액= 0.00; 				   매도금액 = 0.00; 				   변동수량 = 0
        마감금액= s_load('add14','f','G'); 보유수량 = s_load('add9','i');      전일종가 = s_load('add14','f')
        평균단가= s_load('add7','f');      매도누적 = s_load('sub15','f');     매수누적 = s_load('sub14','f');  현매수금= s_load('add6','f');
        연속상승= s_load('sub5','i','G');  연속하락 = s_load('sub6','i','G');  종가변동 = s_load('sub28','f','G');
        // 투자전략 - 변수선언
		현재시즌= s_load('sub1','i');      일매수금 = s_load('sub4','i');      매수수량 = 0;   매도수량 = 0; 
		경과일수= s_load('sub12','i','G'); 기초수량 = s_load('sub18','i');     매수가격 = s_load('sub19','f','G');  매도가격 = s_load('sub20','f','G'); 
		입금합계=s_load('sub25','f');      출금합계 = s_load('sub26','f');     양도세금 = s_load('sub11','f');
        누적수료= s_load('sub31','f');     보존금액 = s_load('sub32','f');     
		// 회복전략 값은 V전략에서만 존재하고 이 값을 가이드 에게서 가져옴
		회복전략= s_load('sub7','f','G');            
                
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
		위매비중=s_load('add25','i','S');
		위매시점=s_load('add22','f','S'); 

        // 현금투자
        vtc('add1',0,2); vtc('add2',0,2); 
          
        // SOXL
		vtc('add11',0.00,2);       vtc('add12',0.00,2);                vtc('add5',0,0);
        check_buy(); check_sell();
        vtc('add14',마감금액,2);    vtc('add15',마감금액*보유수량,0);    vtc('add9',보유수량,0);
        vtc('add7',평균단가,4);     vtc('sub15',매도누적,2);            vtc('sub14',매수누적,2);    vtc('add6',현매수금,2);
        vtc('sub5',연속상승,0);     vtc('sub6',연속하락,0);             vtc('sub28',종가변동,1);    vtc('sub32',보존금액,1);
    
        // 투자전략
		vtc('sub1',현재시즌,0);     vtc('sub4',일매수금,0); 
		vtc('sub12',경과일수,0);    vtc('sub18',기초수량,0); 
        vtc('sub25',입금합계,2);    vtc('sub26',출금합계,2);  vtc('sub11',양도세금,2);  
        vtc('sub31',누적수료,2);    
		
		vtc('add10',JBODY['add10'],-2);

		// 찬스가격 설정

}

function check_sell() {
	let 매도량 = s_load('sub3','i'); let 매도가 = s_load('sub20','f')
	if(마감금액 >= 매도가) { 
		변동수량 = -매도량; 매도금액 = 마감금액 * 매도량;
		vtc('add5', 변동수량); vtc('add12',매도금액, 2);} 
}

function check_buy() {
	let 매수량 = s_load('sub2','i'); let 매수가 = s_load('sub19','f')
	if(마감금액 <= 매수가) { 
		변동수량 = 매수량; 매수금액 =  마감금액 * 매수량
		vtc('add5', 변동수량,0); vtc('add11',매수금액, 2);	} 
}

function tomorrow_sell() {
	
	if( 경과일수 == 0) {
		매도수량 = 0;
		매도가격 = 마감금액;
	} else {
		매도수량 = 보유수량;
	}
}

function tomorrow_buy() {
	if( 경과일수 == 0) {
		매수수량 = 0;
		매수가격 = round_up(마감금액*큰단가치,2)
	} else if(경과일수 == 1) {
		매수수량 = 0
		매수가격 = 마감금액
		수수료등 = 0.0 
		누적수료 = 0.0
	} else if(경과일수 >=2 && 보유수량 <= 기초수량) {
		찬스수량 = 0
		days = Math.min(경과일수+2,6)
		for(i=0;i<days;i++) {찬스수량 += Math.ceil(기초수량 * (i*비중조절+1))}
		cp05 = take_chance(-5.0);
		cp10 = take_chance(-10.0);
		찬스가격 = (회복전략 > 0.0)? cp05 : cp10
		찬스가격 = Math.min(매수가격,찬스가격) 
		매수수량 = 찬스수량
		매수가격 = 찬스가격
	} else {
		매수수량 = Math.ceil(기초수량 * (경과일수*비중조절+1))

		if(매수수량*매수가격 > 현재잔액) {
			매수수량 = 기초수량 * 위매비중
			진행상황 = '매수제한'
		}
		if(매수수량*매수가격 > 현재잔액) {
			매수수량 = 0
			진행상황 = '매수금지'
		}	
	}
}   


function take_chance(p){
	let H = s_load('add9','i','G');
	let n = s_load('sub2','i','G');
	let A = s_load('add6','f','G');
	if(H==0) return 0;	
	let N = H+n;
	k = N/(1+p/100);
	return round_up(A/(k-n),2)
}

function s_load(key,opt,opt2='B') {
	if(opt2=='B')      { a=JBODY[key] } 
	else if(opt2=='S') { a=JSTRG[key] }  
	else if(opt2=='G') { a=GBODY[key] }  
	if(!a) return 0 ;  
	a = a.replace(/,/g,'');  
	if(opt=='i') return parseInt(a);  else return parseFloat(a); 
}
function rebalance() { 일매수금 = parseInt(parseInt(현재잔액*2/3)/분할횟수); 기초수량=Math.ceil(일매수금/마감금액);}
function back_restore() {let 매수금액 = s_load('add11','f');  현재잔액 += 매수금액; 매수금 = 0.00; vtc('add11',매수금액,2);	}
function reset_value() {
    var reset_key = ['add1','add2','add3','add4',
					'add11','add12','add5','add8','add14','add15','add9','add16',
					'add7','sub15','sub14','add6','sub5','sub6','sub28','add18',
					'sub1','sub4','sub2','sub3','sub12','sub18','sub19','sub20',
					'add17','sub25','sub26','sub11','sub29','sub30','sub31','sub7']

    for(i=0;i<reset_key.length;i++) { $("input[name='"+reset_key[i]+"']" ).val(''); }
	AutoCalculated = false; $("#notice-calculated").addClass('notice-calculated');
	load_value();
}

