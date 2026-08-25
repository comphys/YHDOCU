import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class KIWOOM :

    def __init__(self,SYS) :
        self.SYS   = SYS
        self.info  = SYS.info
        self.D     = SYS.D
        self.DB    = SYS.DB
        self.token = self.get_token()
        self.host  = 'https://api.kiwoom.com'
        self.headers = {'Content-Type':'application/json;charset=UTF-8','cont-yn':'N'}

    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H%M%S")  
        with open("kiwoom.log","a",encoding="utf-8") as f:
            f.write(f"{hour_now} : {str}\n")

    def strf(self,num) :
        return round(abs(float(num)),2) 

    def kiwoom_deco(func) :
        def wrapper(self,*args) :
            if not self.token : return None
            self.headers['authorization'] = f'Bearer {self.token}'
            return func(self,*args)
        return wrapper

    # 현재 토큰 폐기 시각이 한시간 이내면 재발급 받아서 리턴하고, 그렇지 않으면 현재의 토큰을 반환한다.
    def get_token(self) :

        kst = ZoneInfo("Asia/Seoul")
        hour_later_kst = datetime.now(kst) + timedelta(hours=1)
        hour_later_fmt = hour_later_kst.strftime("%Y%m%d%H%M%S")

        if  hour_later_fmt >= self.DB.store('kiwoom_token_date') :
            
            self.log("토큰을 재발급합니다.")

            endp = '/oauth2/token'
            self.headers['api-id']='au10001'
            app_key = self.DB.store('kiwoom_appkey')
            secret_key = self.DB.store('kiwoom_secretkey')
            params = {'grant_type':'client_credentials','appkey':app_key,'secretkey':secret_key}

            response = requests.post(self.host+endp, headers=self.headers, json=params)
            rst = response.json()            

            if  rst['return_code'] == 0 :
                self.DB.store('kiwoom_token',rst['token'])
                self.DB.store('kiwoom_token_date',rst['expires_dt'])
                return rst['token']
            
            else : self.log(f"{rst['return_code']} : {rst['return_msg']}")

        else :
            return self.DB.store('kiwoom_token')
    
    @kiwoom_deco
    def get_current_price(self,symbol) :

        endp = '/api/us/mrkcond'
        self.headers['api-id'] = 'usa20100'
        params = {'stex_tp' : 'NY', 'stk_cd' : symbol}

        response = requests.post(self.host+endp, headers=self.headers, json=params)
        rst = response.json()
        return {'현재가':rst['cur_prc'],'증감':rst['flu_rt'],'전날종가':rst['base_close_pric'],'환율':rst['base_exrt']}

    @kiwoom_deco
    def get_ohlc_price(self,symbol,date) :

        endp = '/api/us/mrkcond'
        self.headers['api-id'] = 'usa20590'
        params = {'stex_tp' : 'NY', 'stk_cd' : symbol, 'base_dt':date}

        response = requests.post(self.host+endp, headers=self.headers, json=params)
        rst = response.json()

        if  rst['return_code'] == 0 :
            for aa in rst['result_list'] :
                if aa['dt'] == date :
                    a = aa
                    break
                else : return None
        else : self.log(f"코드 : {rst['return_code']}, 안내 : {rst['return_msg']}")

        ohlc = {}
        ohlc['code'] = rst['return_code']
        ohlc['rmsg'] = rst['return_msg']
        ohlc['date'] = f"{a['dt'][0:4]}-{a['dt'][4:6]}-{a['dt'][6:8]}"
        ohlc['open'] = f"{abs(float(a['open_pric'])):.2f}"
        ohlc['high'] = f"{abs(float(a['high_pric'])):.2f}"
        ohlc['lowp'] = f"{abs(float(a['low_pric'])):.2f}"
        ohlc['clsp'] = f"{abs(float(a['cur_prc'])):.2f}"
        ohlc['volm'] = a['acc_trde_qty']
        ohlc['yday'] = f"{float(a['base_pric']):.2f}"
        ohlc['diff'] = a['flu_rt']

        return ohlc