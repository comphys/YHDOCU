import requests
import time
import inspect
from datetime import datetime
from zoneinfo import ZoneInfo

# requests.post(매개변수)
# data(딕션너리,리스트형,바이트,파일객체) for application/x-www-form-urlencoded 또는 폼데이터
# json(딕션너리,json 직렬화 가능한 객체)
# params (dict,bytes) URL 쿼리 스트링에 포함될 데이터, get 요청에 사용, post 요청인경우도 url 뒤에 ?key=value 형태일 경우에 사용
# 숫자식별코드 : 아멕스(0066), 나스닥(0024), 뉴욕증권(0023)

class MERITZ :

    def __init__(self,SYS) :
        self.DB      = SYS.DB
        # 기본 작동 서버는 스마트폰임
        self.root    = '/data/data/com.termux/files/home/YHDOCU'
        self.maca    = 'A475B980D0CA'
        self.host    = 'https://openapi.imeritz.com:9443'
        self.change_account('01')

    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")  
        with open(self.root+"/logs/meritzapi.log","a",encoding="utf-8") as f:
            f.write(f"<span class='who-time'>{hour_now} :</span> {str}\n")

    # 게정 변경 opt = '01'|'02'|'03'
    def change_account(self,opt) :
        self.appname = 'meritz-app'+opt
        self.secname = 'meritz-sec'+opt
        self.tkname  = 'meritz-token'+opt
        self.tktime  = 'meritz-time'+opt
        self.account = opt

    # rest api를 호출하고 결과를 리턴한다. 에러 발생 시 False를 리턴하고 응답메세지는 로그로 남긴다. 
    def rst_api(self,mean,endp,params,retry_count=0,max_retries=3) :

        caller_frame = inspect.currentframe().f_back
        caller_name = caller_frame.f_code.co_name

        if retry_count >= max_retries: self.log(self.account+" API 시도 최대 횟수를 초과했습니다."); return False

        if  not (token:=self.DB.store(self.tkname) if int(self.DB.store(self.tktime)) > int(time.time()) + 60 else self.get_token()) :
            self.log("token을 가져오지 못하였습니다.")
            return False

        headers={'Content-Type':'application/json;charset=UTF-8','authorization':f'Bearer {token}','mac_address':self.maca}
        resp=requests.get(self.host+endp, headers=headers,params=params) if mean=='get' else requests.post(self.host+endp,headers=headers,json=params)

        # 오류 판단 
        if  not (body:=resp.json()) : 
            self.log(f"{caller_name} :: {resp.status_code} 데이타를 가져오는데 실폐하였습니다.")
            return False
        
        if  not (code:=body.get('rsp_cd')) : 
            if resp.status_code == 200 : self.log(f"{resp.status_code} [{code}] : API 손상 {resp.text}")
            else : self.log(f"{caller_name} :: {resp.status_code} [{code}] : 전송 계층 실패 {resp.text}")
            return False

        # 응답이 성공적일 때
        elif code in ['0000','0001','5620','5762','5766','5820','5822','00000'] :
            if (rows:= body.get('data') or []) : 
                return rows
            else :    
                return None
        
        elif code == 'EGW00200' : 
            self.log(self.account+" 초당 호출 한도가 초과되었습니다.") 
            time.sleep(1.0)
            return self.rst_api(mean,endp,params,retry_count + 1, max_retries)
        
        elif code == 'EGW00123' : 
            self.log(self.account+" 기간이 만료된 토큰입니다.")
            return False
        
        else :
            self.log(f"{caller_name} :: {resp.status_code} [{code}] : {body}")
            return False

    # 토큰을 가져온다. rest_api 에서 호출하며 별도로 호출하지는 않는다. 재발급을 요청하더라도 서버에서 유효기간이 만료되지 않았을 경우 기존의 토큰을 넘겨준다.    
    def get_token(self) :
        # 서버에 발급된 유효시간 내의 토큰이 있을 경우, 서버는 갱신요청 시 기존 토큰을 반환한다.
        self.log(self.account+" 토큰을 발급합니다.")
        para={'grant_type':'client_credentials','client_id':self.DB.store(self.appname),'client_secret':self.DB.store(self.secname),'scope':'login'}
        resp=requests.post(self.host+'/oauth2/token', headers={'content-type':'application/x-www-form-urlencoded'},data=para)
        if  (rst:=resp.json()) :
            exp=datetime.strptime(rst['expires_date'],"%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("Asia/Seoul")).timestamp()
            self.DB.store(self.tkname,rst['access_token'])
            self.DB.store(self.tktime,str(int(exp)))
            return rst['access_token']
        else : 
            return False
    
    # 토큰을 폐기한다. 
    def revoke_token(self) :
        self.log(self.account+" 토큰을 폐기합니다.")
        token=self.DB.store(self.tkname)
        para={'client_id':self.DB.store(self.appname),'client_secret':self.DB.store(self.secname), 'scope':'login','token_type_hint':'access_token','token':token}
        resp=requests.post(self.host+'/oauth2/revoke',headers={'Content-Type':'application/x-www-form-urlencoded'},data=para)
        if  resp.json() :
            self.DB.store(self.tkname,'')
            self.DB.store(self.tktime,'0')
            return True
        else : 
            return False        

    # 현재의 실시간 가격 정보를 리턴한다 (메리츠 api의 특이점 이용, 주간장, 애프터장 모두 해당이다. 3번 계좌의 1주는 이를 위해 항상 남겨두자.)
    def get_current_price(self) :
        oldc = self.account
        self.change_account('03')
        if  (rst:=self.rst_api('get','/accounts/v1/me/overseas/holdings',{})) :
            self.change_account(oldc)
            return {'종목':rst[0]['ovrs_stck_symb_iscd'],'현재가격':rst[0]['psnt_prc'],'환율':rst[0]['exrt']}
        else : 
            self.change_account(oldc)
            return rst

    # 특정날자의 ohlc 정보를 가져온다 date 형태는 20260101 형식이다. 
    def get_ohlc(self,date) :
        para={'mrkt_div_code':'OV','mrkt_cls_code':'AX','iscd':'SOXL','dely_rltm_cls_code':'1','mod_stpr_cls_code':'1','from':date,'to':date}
        if (rst:=self.rst_api('get','/market/v1/overseas/candles/days',para)) :
            rt=rst[0] 
            return {'날자':rt['date'],'시가':rt['oprc'],'고가':rt['hprc'],'저가':rt['lprc'],'종가':rt['prpr'],'거래량':rt['acml_vol'],'증감':rt['prdy_ctrt']}
        else : 
            return rst
    
    # 계좌의 보유주식에 대한 현황을 가져온다. 
    def get_account_balance(self) :
        rpr = []
        if (rst:=self.rst_api('get','/accounts/v1/me/overseas/holdings',{})) :
            for rt in rst :
                pr = {'종목':rt['ovrs_stck_symb_iscd'],'수량':f"{float(rt['rmnd_dqty']):.0f}",'매도가능':f"{float(rt['seln_able_dqty']):.0f}",
                    '현재가격':f"{float(rt['psnt_prc']):.2f}",'평균단가':f"{float(rt['avrg_unpr']):.4f}",
                    '평가금액':f"{float(rt['frcr_vltn_amt']):.2f}",'평가손익':f"{float(rt['vltn_prls_camt']):.2f}",'평가수익률':f"{float(rt['vltn_ert']):.2f}",
                    '매입금액':f"{float(rt['byov_camt']):.2f}",'환율':f"{float(rt['exrt']):.2f}"
                    }
                rpr.append(pr)
            return rpr
        else : 
            return rst
    
    # 예약된 현황을 기져온다.  
    def get_reserved_order(self,date,code='1') : # code 0 전체, 1 전체(취소분제외), 2(예약상태인 건만)
        para={'iqry_sta_date':date,'iqry_fin_date':date,'seln_byov_clcd':'0','iqry_cls_code':'2','iqry_idnt_clcd':code,'tday_deal_yn':'N'}
        if (rst:=self.rst_api('get','/trading/v1/overseas/reserved-orders',para)) :
            pr = []
            for r in rst :
                pr.append({'종목코드':r['ovrs_stck_symb_iscd'],'접수일자':r['rsev_acpt_date'],'접수번호':r['rsev_acpt_srno'],'매매구분':r['seln_byov_clcd'],'호가유형':r['rsev_aspr_tpcd'],
                        '주문수량':r['odqt'],'주문가격':r['ovrs_stck_oder_prc'],'예약시간구분':r['oder_rsev_hour_clcd'],'주문시작':r['oder_sta_date']
                        })
            return pr
        else : 
            return rst
    
    # 예약주문 매수를 실행한다(LOC 주문을 기본으로 한다).
    def do_reserved_buy(self,symbol,qty,price,date,check) :
        para={'ovrs_stck_symb_iscd':symbol,'ovrs_exch_vndr_idno':'0066','rsev_aspr_tpcd':'5','odqt':qty,'ovrs_stck_oder_prc':price,
              'warn_cnfr_yn':check,'oder_rsev_cls_code':'1','oder_rsev_hour_clcd':'0',
              'oder_sta_date':date,'oder_fin_date':date}
        if (rst:=self.rst_api('post','/trading/v1/overseas/reserved-orders/buy',para)) :
            # 경고 안내 메세지가 없을 경우 예약번호를 리턴
            if rst['warn_msg'] =='' : return rst['oder_rsev_mst_no']
            else : self.log(rst['warn_msg'])
        else : 
            return rst

    # 예약주문 매도를 실행한다(LOC 주문을 기본으로 한다).
    def do_reserved_sell(self,symbol,qty,price,date,check) :
        para={'ovrs_stck_symb_iscd':symbol,'ovrs_exch_vndr_idno':'0066','rsev_aspr_tpcd':'5','odqt':qty,'ovrs_stck_oder_prc':price,
              'warn_cnfr_yn':check,'oder_rsev_cls_code':'1','oder_rsev_hour_clcd':'0',
              'oder_sta_date':date,'oder_fin_date':date,}
        if (rst:=self.rst_api('post','/trading/v1/overseas/reserved-orders/sell',para)) :
            # 경고 안내 메세지가 없을 경우 예약번호를 리턴
            if rst['warn_msg'] =='' : return rst['oder_rsev_mst_no']
            else : self.log(rst['warn_msg'])
        else : 
            return rst

    # 예약된 주문을 취소한다.
    def do_reserved_cancel(self,date,orno) :
        # date 는 접수일자 임
        para={'oder_rsev_mst_date':date,'oder_rsev_mst_no':orno}
        if (rst:=self.rst_api('post','/trading/v1/overseas/reserved-orders/cancel',para)) :
            return True
        else :
            return rst

    # 실시간 매도 주문을 실행한다. code = '01'지정가|'05'시장가|'32'LOC|'35'Limit VWAP|'36'Limit TWAP ccode = '0'시장가,지정가|'7'종가
    def do_real_sell(self,qty,price,code,ccode) :
        para={'ovrs_stck_symb_iscd':'SOXL','ovrs_exch_vndr_idno':'0066','oder_cls_code':code,
              'odqt':qty,'ovrs_stck_oder_prc':price,'oder_cond_cls_code':ccode}
        if (rst:=self.rst_api('post','/trading/v1/overseas/orders/sell',para)) :
            # 경고 안내 메세지가 없을 경우 예약번호를 리턴
            if rst['warn_msg'] =='' : return rst['oder_no']
            else : self.log(rst['warn_msg'])
        else : 
            return rst

    # 실시간 매수 주문을 실행한다. code = '01'지정가|'05'시장가|'32'LOC|'35'Limit VWAP|'36'Limit TWAP ccode = '0'시장가,지정가|'7'종가
    def do_real_buy(self,qty,price,code,ccode) :
        para={'ovrs_stck_symb_iscd':'SOXL','ovrs_exch_vndr_idno':'0066','oder_cls_code':code,
              'odqt':qty,'ovrs_stck_oder_prc':price,'oder_cond_cls_code':ccode}
        if (rst:=self.rst_api('post','/trading/v1/overseas/orders/buy',para)) :
            # 경고 안내 메세지가 없을 경우 예약번호를 리턴
            if rst['warn_msg'] =='' : return rst['oder_no']
            else : self.log(rst['warn_msg'])
        else : 
            return rst
    
    # 주문을 취소한다. 코드(oder_cond_cls_code)는 주문구분코드(oder_cls_code)가 01·05·35~38이면 0, 31·33이면 2, 32·34이면 7 이어야 합니다.
    def do_real_cancel(self,date,ordnum,qty,code='0') :
        para={'oder_date':date,'orgl_oder_no':ordnum,'oder_cond_cls_code':code,'odqt':qty}
        if (rst:=self.rst_api('post','/trading/v1/overseas/orders/cancel',para)) :
            return True
        else : 
            return rst

    # 당일 체결 현황을 보여준다
    def get_orders_today(self,done,bs) : # done(체결여부) 0 전체, 1 체결 2 미체결 / bs(매수매도) 0 전체, 1 매도, 2 매수
        para={'cntg_cls_code':done,'seln_byov_clcd':bs}
        if (rst:=self.rst_api('get','/trading/v1/overseas/orders/today',para)) :
            pr = []
            for r in rst :
                pr.append({'종목코드':r['ovrs_stck_symb_iscd'],'매매구분':r['seln_byov_clcd'],'호가유형':r['aspr_type_code'],
                        '주문수량':str(r['odqt']),'주문가격':f"{float(r['ovrs_stck_oder_prc']):.2f}",'체결수량':r['cntg_qty'],'체결가격':f"{float(r['cntg_crnc_prc']):.2f}",
                        '주문시간':r['oder_exec_ymdh'],'주문상태':r['ovrs_stck_oder_stat_cls_code'],'주문일자':r['oder_date'],'주문번호':r['oder_no']
                        })
            return pr
        else : 
            return rst

    # 현금 잔고 현황을 가져온다. 주문가능한 금액을 원화 및 달러로 가져온다.
    def get_money_balance(self) : 
        pr = {}
        # get 외화($) 예수금
        if (rst:=self.rst_api('get','/accounts/v1/me/overseas/currencies',{})) :
            for r in rst :
                if r['crcd'] == 'USD' and float(r['estm_frcr_amt']) > 0 : pr={'달러예수금':r['estm_frcr_amt'],'평가환율':r['vltn_exrt'],'원화환산':r['excl_wncr_vltn_amt']}

        # get 원화 예수금
        if (rst:=self.rst_api('get','/accounts/v1/me/deposit',{})) :
            if pr :
                pr['원화예수금'] = rst['oder_able_cash_amt']
                통합달러 = round(float(pr['달러예수금']) + float(pr['원화예수금'])/float(pr['평가환율']),2)
                통합원화 = round(float(pr['원화예수금']) + float(pr['달러예수금'])*float(pr['평가환율']),2)
                pr['통합달러'] = f"{통합달러:.2f}"
                pr['통합원화'] = f"{통합원화:.0f}"
                pr = {k: (v if isinstance(v, str) else str(v)) for k, v in pr.items()}
            else : 
                원화금액 = str(rst['oder_able_cash_amt'])
                평가환율 = self.get_current_price()['환율']
                통합달러 = f"{float(원화금액)/float(평가환율):.2f}"
                pr = {'달러예수금':'0.00','평가환율':평가환율,'원화환산':'0','원화예수금':원화금액,'통합달러':통합달러,'통합원화':원화금액}
            return pr
        else : 
            return rst
    
    # 해외 영업일 조회 다음 정규장에 해당하는 날자를 가져온다. 현재 정규장이 시작되었으면 다음 정규장의 날자를 가져온다. 
    def get_market_date(self) :
        if  (rst:=self.rst_api('get','/reference/v1/overseas/market-days',{'ovrs_exch_vndr_idno':'0066'})) :
            return rst['bsop_date']
        else : 
            return rst