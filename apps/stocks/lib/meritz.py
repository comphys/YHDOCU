import requests
from datetime import datetime
from zoneinfo import ZoneInfo

class MERITZ :

    def __init__(self,SYS) :
        self.DB      = SYS.DB
        # 기본 작동 서버는 스마트폰임
        self.root    = '/data/data/com.termux/files/home/YHDOCU'
        self.maca    = 'A475B980D0CA'
        self.host    = 'https://openapi.imeritz.com:9443'
        self.headers = {'Content-Type':'application/json;charset=utf-8'}
        self.change_account('01')


    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")  
        with open(self.root+"/logs/meritzapi.log","a",encoding="utf-8") as f:
            f.write(f"<span class='who-time'>{hour_now} :</span> {str}\n")

    def change_account(self,opt) :
        self.appname = 'meritz-app'+opt
        self.secname = 'meritz-sec'+opt
        self.tkname  = 'meritz-token'+opt
        self.tktime  = 'meritz-time'+opt
        self.account = opt

    def rst_api(self,mean,endp,params) :

        current_time = int(datetime.now().timestamp())
        token_extime = int(self.DB.store(self.tktime))
        if  token_extime < current_time + 60 :
            token = self.get_token()
        else : 
            token = self.DB.store(self.tkname)
        if  not token : 
            self.log("token을 가져오지 못하였습니다.")
            return False
        
        headers = {'Content-Type':'application/json;charset=UTF-8','authorization':f'Bearer {token}','mac_address':self.maca}
        resp = requests.get(self.host+endp, headers=headers,params=params) if mean == 'get' else requests.post(self.host+endp, headers=headers,data=params)

        # 오류 판단 
        body = resp.json()
        if  not body : self.log(f"{resp.status_code} 데이타를 가져오는데 실폐하였습니다."); return False
        
        code = body.get('rsp_cd')
        if not code : 
            if resp.status_code == 200 : self.log(f"{resp.status_code} [{code}] : API 손상 {resp.text}"); return False
            else : self.log(f"{resp.status_code} [{code}] : 전송 계층 실패 {resp.text}"); return False
        
        elif code in ['0000','0001','5620','5762','5766','5820','5822','00000'] :
            rows = body.get('data') or [] 
            if rows : return rows
            else :    return None
        
        else :
            self.log(f"{resp.status_code} [{code}] : {resp.text}")
            return False

        
    def get_token(self) :
        self.log(self.account+" 토큰을 발급합니다.")
        endp = '/oauth2/token'
        app_key = self.DB.store(self.appname)
        secret_key = self.DB.store(self.secname)
        params = {'grant_type':'client_credentials','client_id':app_key,'client_secret':secret_key, 'scope':'login'}
        resp = requests.post(self.host+endp, headers={'Content-Type':'application/x-www-form-urlencoded'},data=params)
        rst = resp.json()
        if  rst :
            self.DB.store(self.tkname,rst['access_token'])
            current_time = int(datetime.now().timestamp())
            self.DB.store(self.tktime,str(current_time+43200))
            return rst['access_token']
        else : 
            return False


    def revoke_token(self) :
        self.log(self.account+" 토큰을 폐기합니다.")
        endp = '/oauth2/revoke'
        app_key = self.DB.store(self.appname)
        secret_key = self.DB.store(self.secname)
        token = self.DB.store(self.tkname)
        params = {'client_id':app_key,'client_secret':secret_key, 'scope':'login','token_type_hint':'access_token','token':token}
        resp = requests.post(self.host+endp, headers={'Content-Type':'application/x-www-form-urlencoded'},data=params)
        rst = resp.json()
        if  rst  :
            self.DB.store(self.tkname,' ')
            self.DB.store(self.tktime,'0')
            return True
        else : 
            return False        


    # 현재의 실시간 가격 정보를 리턴한다 (메리츠 api의 특이점 이용)
    def get_current_price(self) :
        aa = self.account
        self.change_account('03')
        token = self.get_token()
        self.headers['authorization'] = f'Bearer {token}'
        rst = self.rst_api('get','/accounts/v1/me/overseas/holdings',{})
        if  rst  :
            rt = rst[0]
            pr = {'종목':rt['ovrs_stck_symb_iscd'],'현재가격':rt['psnt_prc'],'환율':rt['exrt']}
            self.change_account(aa)
            return pr
        else : 
            self.change_account(aa)
            return rst


    # 특정날자의 ohlc 정보를 가져온다
    def get_ohlc(self,date) :
        endp = '/market/v1/overseas/candles/days'
        params = {'mrkt_div_code':'OV','mrkt_cls_code':'AX','iscd':'SOXL','dely_rltm_cls_code':'1','mod_stpr_cls_code':'1','from':date,'to':date}
        rst = self.rst_api('get',endp,params)
        if rst :
            rt=rst[0] 
            pr = {'날자':rt['date'],'시가':rt['oprc'],'고가':rt['hprc'],'저가':rt['lprc'],'종가':rt['prpr'],'거래량':rt['acml_vol'],'증감':rt['prdy_ctrt']}
            return pr
        else : return rst


    def get_current_balance(self) :
        endp = '/accounts/v1/me/overseas/holdings'
        params = {}
        rst = self.rst_api('get',endp,params)
        rpr = []
        if rst :
            for rt in rst :
                pr = {'종목':rt['ovrs_stck_symb_iscd'],'수량':rt['rmnd_dqty'],'매도가능수량':rt['seln_able_dqty'],'현재가격':rt['psnt_prc'],'평균단가':rt['avrg_unpr'],
                    '평가손익':rt['vltn_prls_camt'],'평가수익률':rt['vltn_ert'],
                    '평가금액':rt['frcr_vltn_amt'],'매입금액':rt['byov_camt'],'환율':rt['exrt']
                    }
                rpr.append(pr)
            return rpr
        else : return rst

    def get_reserved_order(self,date,code='1') : # code 0 전체, 1 전체(취소분제외), 2(예약상태인 건만)
        endp = '/trading/v1/overseas/reserved-orders'
        params = {'iqry_sta_date':date,'iqry_fin_date':date,'seln_byov_clcd':'0','iqry_cls_code':'2','iqry_idnt_clcd':code,'tday_deal_yn':'N'}
        rst = self.rst_api('get',endp,params)
        if rst :
            pr = []
            for r in rst :
                pr.append({'종목코드':r['ovrs_stck_symb_iscd'],'접수일자':r['rsev_acpt_date'],'접수번호':r['rsev_acpt_srno'],'매매구분':r['seln_byov_clcd'],'호가유형':r['rsev_aspr_tpcd'],
                        '주문수량':r['odqt'],'주문가격':r['ovrs_stck_oder_prc'],'예약시간구분':r['oder_rsev_hour_clcd'],'주문시작':r['oder_sta_date']
                        })
            return pr
        else : return rst


    def do_reserved_buy(self,symbol,qty,price,date,check) :
        endp = '/trading/v1/overseas/reserved-orders/buy'
        params = {'ovrs_stck_symb_iscd':symbol,'ovrs_exch_vndr_idno':'0066','rsev_aspr_tpcd':'5','odqt':qty,'ovrs_stck_oder_prc':price,
                  'warn_cnfr_yn':check,'oder_rsev_cls_code':'1','oder_rsev_hour_clcd':'0',
                  'oder_sta_date':date,'oder_fin_date':date}
        rst = self.rst_api('post',endp,params)
        if rst :
            # 경고 안내 메세지가 없을 경우 예약번호를 리턴
            if rst['warn_msg'] =='' : return rst['oder_rsev_mst_no']
        else : 
            return rst

    def do_reserved_sell(self,symbol,qty,price,date,check) :
        endp = '/trading/v1/overseas/reserved-orders/sell'
        params = {'ovrs_stck_symb_iscd':symbol,'ovrs_exch_vndr_idno':'0066','rsev_aspr_tpcd':'5','odqt':qty,'ovrs_stck_oder_prc':price,
                  'warn_cnfr_yn':check,'oder_rsev_cls_code':'1','oder_rsev_hour_clcd':'0',
                  'oder_sta_date':date,'oder_fin_date':date}
        rst = self.rst_api('post',endp,params)
        if rst :
            # 경고 안내 메세지가 없을 경우 예약번호를 리턴
            if rst['warn_msg'] =='' : return rst['oder_rsev_mst_no']
        else : 
            return rst

    def do_reserved_cancel(self,date,orno) :
        # date 는 접수일자 임
        endp = '/trading/v1/overseas/reserved-orders/cancel'
        params = {'oder_rsev_mst_date':date,'oder_rsev_mst_no':orno}
        rst = self.rst_api('post',endp,params)
        if rst : return True
        else :   return rst

    # 당일 체결 현황을 보여준다
    def get_orders_today(self,done,bs) : # done(체결여부) 0 전체, 1 체결 2 미체결 / bs(매수매도) 0 전체, 1 매도, 2 매수
        endp = '/trading/v1/overseas/orders/today'
        params = {'cntg_cls_code':done,'seln_byov_clcd':bs}
        rst = self.rst_api('get',endp,params)
        if rst :
            pr = []
            for r in rst :
                pr.append({'종목코드':r['ovrs_stck_symb_iscd'],'매매구분':r['seln_byov_clcd'],'호가유형':r['aspr_type_code'],
                        '주문수량':str(r['odqt']),'주문가격':f"{float(r['ovrs_stck_oder_prc']):.2f}",'체결수량':r['cntg_qty'],'체결가격':r['cntg_crnc_prc'],
                        '주문시간':r['oder_exec_ymdh'],'주문상태':r['ovrs_stck_oder_stat_cls_code'],'주문일자':r['oder_date'],'주문번호':r['oder_no']
                        })
            return pr
        else : 
            return rst

    # 현금 잔고 현황을 가져온다
    def get_money_balance(self) : 
        pr = {}
        # get 외화($) 예수금
        rst = self.rst_api('get','/accounts/v1/me/overseas/currencies',{})
        if rst :
            for r in rst :
                if r['crcd'] == 'USD' and float(r['estm_frcr_amt']) > 0 : pr = {'달러예수금':r['estm_frcr_amt'],'평가환율':r['vltn_exrt'],'원화환산':r['excl_wncr_vltn_amt']}

        # get 원화 예수금
        rst = self.rst_api('get','/accounts/v1/me/deposit',{})
        if rst :
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
