import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from myutils.DB import DB
import time

class MERITZ :

    def __init__(self) :
        self.DB    = DB('stocks')
        self.host  = 'https://openapi.imeritz.com:9443'
        self.mac = 'BCFCE7C9911F' # wondows
        # self.mac = 'A475B980D0CA' # mobile
        self.headers = {'Content-Type':'application/json;charset=UTF-8','mac_address':self.mac}
        
    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")  
        with open("logs/meritzapi.log","a",encoding="utf-8") as f:
            f.write(f"<span class='who-time'>{hour_now} :</span> {str}\n")

    def meritz_deco(func) :
        def wrapper(self,*args,**kargs) :
            token = self.get_token()
            if not token : return False
            self.headers['authorization'] = f'Bearer {token}'
            return func(self,*args,**kargs)
        return wrapper

    def get_token(self) :

        current_time = int(datetime.now().timestamp() )+3600
        token_extime = int(self.DB.store('meritz-time'))

        if  token_extime < current_time :
            self.log("토큰을 재발급합니다.")
            self.headers = {'Content-Type':'application/x-www-form-urlencoded'}
            endp = '/oauth2/token'
            app_key = self.DB.store('meritz-app01')
            secret_key = self.DB.store('meritz-sec01')
            params = {'grant_type':'client_credentials','client_id':app_key,'client_secret':secret_key, 'scope':'login'}
            response = requests.post(self.host+endp, headers=self.headers, data=params)
            self.headers = {'Content-Type':'application/json;charset=UTF-8','mac_address':self.mac}       

            if  response.status_code == 200  :
                rst = response.json()  
                self.DB.store('meritz-token',rst['access_token'])
                self.DB.store('meritz-time',str(current_time+43200))
                return rst['access_token']
                return '--------------------------------------------------'
            
            else : 
                self.log(f"{response.status_code} : {response.text}")
                return False
        else :
            return self.DB.store('meritz-token')

    @meritz_deco
    def get_current_price(self,symbol,mk='AX') :
        endp = '/market/v1/overseas/prices'
        params = { "mrkt_div_code": 'OV', "mrkt_cls_code": mk, "iscd":symbol,"dely_rltm_cls_code":"1" }
        response = requests.get(self.host+endp, headers=self.headers, params=params)
        if response.status_code == 200 :
            rst = response.json()
            return rst
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
            pr = {'종목':rt['ovrs_stck_symb_iscd'],'수량':rt['rmnd_dqty'],'매도가능수량':rt['seln_able_dqty'],'평균단가':rt['avrg_unpr'],'현재가격':rt['psnt_prc'],'전일대비':rt['prdy_vrss_rsfl_crnc_prc'],
                  '평가손익':rt['vltn_prls_camt'],'평가수익률':rt['vltn_ert'],
                  '매수금액':rt['byov_camt'],'평가금액':rt['frcr_vltn_amt'],'환율':rt['exrt']
                  }
            return pr
        else : 
            self.log(f"{response.status_code} : {response.text}")
            return False

    @meritz_deco
    def check_reserved_order(self,date) :
        endp = '/trading/v1/overseas/reserved-orders'
        params = {'iqry_sta_date':date,'iqry_fin_date':date,'seln_byov_clcd':'0','iqry_cls_code':'2','iqry_idnt_clcd':'0','tday_deal_yn':'N'}
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


API = MERITZ()
# rst = API.do_reserved_buy('SOXL','1','135.12','20261014','Y')
# print(rst)
# rst = API.do_reserved_sell('SOXL','1','148.00','20261014','Y')
# print(rst)
rst = API.do_reserved_cancel('20261012','115822')
print(rst)
time.sleep(1)
rst = API.check_reserved_order('20261012')
for r in rst :
    print(r)


