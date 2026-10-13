import requests
import platform
from datetime import datetime
from zoneinfo import ZoneInfo

sysos = platform.system()
if    sysos == 'Windows' :  rootpath = '/YHDOCU'
elif  sysos == 'Linux'   :  rootpath = '/home/comphys/YHDOCU'
elif  sysos == 'Android' :  rootpath = '/data/data/com.termux/files/home/YHDOCU'
else: sysos == '' 


class MERITZ :

    def __init__(self,SYS) :
        self.SYS   = SYS
        self.DB    = SYS.DB
        self.host  = 'https://openapi.imeritz.com:9443'
        self.headers = {'Content-Type':'application/json;charset=utf-8'}

        self.appname = 'meritz-app01'
        self.secname = 'meritz-sec01'
        self.tkname  = 'meritz-token01'
        self.tktime  = 'meritz-time01'
        self.account = '01'


    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")  
        with open(rootpath+"/logs/meritzapi.log","a",encoding="utf-8") as f:
            f.write(f"<span class='who-time'>{hour_now} :</span> {str}\n")

    def change_account(self,opt) :
        self.appname = 'meritz-app'+opt
        self.secname = 'meritz-sec'+opt
        self.tkname  = 'meritz-token'+opt
        self.tktime  = 'meritz-time'+opt
        self.account = opt

    def meritz_deco(func) :
        def wrapper(self,*args,**kargs) :
            token = self.get_token()
            if not token : return False
            self.headers['authorization'] = f'Bearer {token}'
            return func(self,*args,**kargs)
        return wrapper

    def get_token(self) :

        current_time = int(datetime.now().timestamp() )+3600
        token_extime = int(self.DB.store(self.tktime))

        if  token_extime < current_time :
            self.log(self.account+" 토큰을 발급합니다.")
            endp = '/oauth2/token'
            app_key = self.DB.store(self.appname)
            secret_key = self.DB.store(self.secname)
            params = {'grant_type':'client_credentials','client_id':app_key,'client_secret':secret_key, 'scope':'login'}
            response = requests.post(self.host+endp, headers={'Content-Type':'application/x-www-form-urlencoded'}, data=params)

            if  response.status_code == 200  :
                rst = response.json()  
                self.DB.store(self.tkname,rst['access_token'])
                self.DB.store(self.tktime,str(current_time+43200))
                return rst['access_token']
            
            else : 
                self.log(f"{response.status_code} : {response.text}")
                return False
        else :
            return self.DB.store(self.tkname)

    # 현재의 실시간 가격 정보를 리턴한다 (메리츠 api의 특이점 이용)
    def get_current_price(self) :
        aa = self.account
        self.change_account('03')
        token = self.get_token()
        self.headers['authorization'] = f'Bearer {token}'
        endp = '/accounts/v1/me/overseas/holdings'
        params = {}
        response = requests.get(self.host+endp, headers=self.headers, params=params)
        if response.status_code == 200 :
            rst = response.json()
            rt = rst['data'][0]
            pr = {'종목':rt['ovrs_stck_symb_iscd'],'현재가격':rt['psnt_prc'],'환율':rt['exrt']}
            self.change_account(aa)
            return pr
        else : 
            self.log(f"{response.status_code} : {response.text}")
            self.change_account(aa)
            return False


    # 특정날자의 ohlc 정보를 가져온다
    @meritz_deco
    def get_ohlc(self,date) :
        endp = '/market/v1/overseas/candles/days'
        params = {'mrkt_div_code':'OV','mrkt_cls_code':'AX','iscd':'SOXL','dely_rltm_cls_code':'1','mod_stpr_cls_code':'1','from':date,'to':date}
        response = requests.get(self.host+endp, headers=self.headers, params=params)
        if response.status_code == 200 :
            rst = response.json()
            rt = rst['data'][0]
            pr = {'날자':rt['date'],'시가':rt['oprc'],'고가':rt['hprc'],'저가':rt['lprc'],'종가':rt['prpr'],'거래량':rt['acml_vol'],'증감':rt['prdy_ctrt']}
            return pr
        else : 
            self.log(f"{response.status_code} : {response.text}")
            return False


    @meritz_deco
    def get_current_balance(self) :
        endp = '/accounts/v1/me/overseas/holdings'
        params = {}
        response = requests.get(self.host+endp, headers=self.headers, params=params)
        if response.status_code == 200 :
            rst = response.json()
            rt = rst['data'][0]
            pr = {'종목':rt['ovrs_stck_symb_iscd'],'수량':rt['rmnd_dqty'],'매도가능수량':rt['seln_able_dqty'],'현재가격':rt['psnt_prc'],'평균단가':rt['avrg_unpr'],
                  '평가손익':rt['vltn_prls_camt'],'평가수익률':rt['vltn_ert'],
                  '평가금액':rt['frcr_vltn_amt'],'매입금액':rt['byov_camt'],'환율':rt['exrt']
                  }
            return pr
        else : 
            self.log(f"{response.status_code} : {response.text}")
            return False

    @meritz_deco
    def check_reserved_order(self,date,code='1') : # code 0 전체, 1 전체(취소분제외), 2(예약상태인 건만)
        endp = '/trading/v1/overseas/reserved-orders'
        params = {'iqry_sta_date':date,'iqry_fin_date':date,'seln_byov_clcd':'0','iqry_cls_code':'2','iqry_idnt_clcd':code,'tday_deal_yn':'N'}
        response = requests.get(self.host+endp, headers=self.headers, params=params)
        if response.status_code == 200 :
            pr = []
            rst = response.json()
            rt = rst['data']
            for r in rt :
                pr.append({'종목코드':r['ovrs_stck_symb_iscd'],'접수일자':r['rsev_acpt_date'],'접수번호':r['rsev_acpt_srno'],'매매구분':r['seln_byov_clcd'],'호가유형':r['rsev_aspr_tpcd'],
                           '주문수량':r['odqt'],'주문가격':r['ovrs_stck_oder_prc'],'예약시간구분':r['oder_rsev_hour_clcd'],'주문시작':r['oder_sta_date']
                           })
            return pr
        else : 
            self.log(f"{response.status_code} : {response.text}")
            return False

    @meritz_deco
    def do_reserved_buy(self,symbol,qty,price,date,check) :
        endp = '/trading/v1/overseas/reserved-orders/buy'
        params = {'ovrs_stck_symb_iscd':symbol,'ovrs_exch_vndr_idno':'0066','rsev_aspr_tpcd':'5','odqt':qty,'ovrs_stck_oder_prc':price,'warn_cnfr_yn':check,'oder_rsev_cls_code':'1','oder_rsev_hour_clcd':'0',
                  'oder_sta_date':date,'oder_fin_date':date}
        response = requests.post(self.host+endp, headers=self.headers, json=params)
        if response.status_code == 200 :
            rst = response.json()
            if rst['data']['warn_msg'] =='' : return rst['data']['oder_rsev_mst_no']
        else : 
            self.log(f"{response.status_code} : {response.text}")
            return False

    @meritz_deco
    def do_reserved_sell(self,symbol,qty,price,date,check) :
        endp = '/trading/v1/overseas/reserved-orders/sell'
        params = {'ovrs_stck_symb_iscd':symbol,'ovrs_exch_vndr_idno':'0066','rsev_aspr_tpcd':'5','odqt':qty,'ovrs_stck_oder_prc':price,'warn_cnfr_yn':check,'oder_rsev_cls_code':'1','oder_rsev_hour_clcd':'0',
                  'oder_sta_date':date,'oder_fin_date':date}
        response = requests.post(self.host+endp, headers=self.headers, json=params)
        if response.status_code == 200 :
            rst = response.json()
            if rst['data']['warn_msg'] =='' : return rst['data']['oder_rsev_mst_no']
        else : 
            self.log(f"{response.status_code} : {response.text}")
            return False

    @meritz_deco
    def do_reserved_cancel(self,date,orno) :
        # date 는 접수일자 임
        endp = '/trading/v1/overseas/reserved-orders/cancel'
        params = {'oder_rsev_mst_date':date,'oder_rsev_mst_no':orno}
        response = requests.post(self.host+endp, headers=self.headers, json=params)
        if response.status_code == 200 :
            rst = response.json()
            if rst['rsp_cd'] == '0000' : return True
        else : 
            self.log(f"{response.status_code} : {response.text}")
            return False

    # 당일 체결 현황을 보여준다
    @meritz_deco
    def check_orders_today(self,done,bs) : # done(체결여부) 0 전체, 1 체결 2 미체결 / bs(매수매도) 0 전체, 1 매도, 2 매수
        endp = '/trading/v1/overseas/orders/today'
        params = {'cntg_cls_code':done,'seln_byov_clcd':bs}
        response = requests.get(self.host+endp, headers=self.headers, params=params)
        if response.status_code == 200 :
            pr = []
            rst = response.json()
            rt = rst['data']
            for r in rt :
                pr.append({'종목코드':r['ovrs_stck_symb_iscd'],'매매구분':r['seln_byov_clcd'],'호가유형':r['aspr_type_code'],
                           '주문수량':r['odqt'],'주문가격':r['ovrs_stck_oder_prc'],'체결수량':r['cntg_qty'],'체결가격':r['cntg_crnc_prc'],
                           '주문시간':r['oder_exec_ymdh'],'주문상태':r['ovrs_stck_oder_stat_cls_code'],'주문일자':r['oder_date'],'주문번호':r['oder_no']
                           })
            return pr
        else : 
            self.log(f"{response.status_code} : {response.text}")
            return False

    # 외화 잔고 현황을 가져온다
    @meritz_deco
    def get_money_balance(self) : 
        endp = '/accounts/v1/me/overseas/currencies'
        params = {}
        response = requests.get(self.host+endp, headers=self.headers, params=params)
        if response.status_code == 200 :
            rst = response.json()
            rt = rst['data']
            for r in rt :
                if r['crcd'] == 'USD' : return {'추정예수금':r['estm_frcr_amt'],'평가환율':r['vltn_exrt'],'원화환산':r['excl_wncr_vltn_amt']}
        else : 
            self.log(f"{response.status_code} : {response.text}")
            return False    
