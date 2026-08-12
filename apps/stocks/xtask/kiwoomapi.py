import requests
from datetime import datetime, timedelta
from pytz import timezone
from myutils.DB import DB
class KIWOOM :

    def __init__(self) :

        self.DB    = DB('stocks')
        self.host  = 'https://api.kiwoom.com'
        self.headers = {'Content-Type':'application/json;charset=UTF-8','cont-yn':'N'}


    def get_current_krwusa(self) :

        endp = '/api/us/exchange'
        token = self.get_token()
        self.headers['authorization'] = f'Bearer {token}'
        self.headers['api-id'] = 'ust31301'

        params = {'exch_tp' : '2'}

        response = requests.post(self.host+endp, headers=self.headers, json=params)
        rst = response.json()

        return rst

    def get_current_price(self,symbol) :

        endp = '/api/us/mrkcond'
        token = self.get_token()
        self.headers['authorization'] = f'Bearer {token}'
        self.headers['api-id'] = 'usa20100'

        params = {'stex_tp' : 'NY', 'stk_cd' : symbol}

        response = requests.post(self.host+endp, headers=self.headers, json=params)
        rst = response.json()

        return [rst['return_code'],rst['return_msg'],rst['cur_prc'],rst['flu_rt'],rst['base_close_pric'],rst['base_exrt']]

    def get_ohlc_price(self,symbol,date) :

        endp = '/api/us/mrkcond'
        token = self.get_token()
        self.headers['authorization'] = f'Bearer {token}'
        self.headers['api-id'] = 'usa20590'

        params = {'stex_tp' : 'NY', 'stk_cd' : symbol, 'base_dt':date}

        response = requests.post(self.host+endp, headers=self.headers, json=params)
        rst = response.json()

        if  rst['return_code'] == 0 :
            for aa in rst['result_list'] :
                if aa['dt'] == date :
                    a = aa
                    break
                else : return "해당 날자의 데이타가 존재하지 않습니다."
        else : return "해당 날자의 데이타가 존재하지 않습니다."

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



    # 현재 토큰 폐기 시각이 한시간 이내면 재발급 받아서 리턴하고, 그렇지 않으면 현재의 토큰을 반환한다.
    def get_token(self) :

        self.token = self.DB.store('kiwoom_token')
        self.token_valid_date = self.DB.store('kiwoom_token_date')
        app_key = self.DB.store('kiwoom_appkey')
        secret_key = self.DB.store('kiwoom_secretkey')

        kst = timezone("Asia/Seoul")
        hour_later_kst = datetime.now(kst) + timedelta(hours=1)
        hour_later_fmt = hour_later_kst.strftime("%Y%m%d%H%M%S")

        if  hour_later_fmt >= self.token_valid_date :
            
            print("토큰을 재발급합니다.")
            # 현재의 토큰을 폐기하고, 재발급 받는다.
            endp = '/oauth2/revoke'
            self.headers['api-id'] = 'au10002'

            params = {'appkey' : app_key,'secretkey' : secret_key,'token' : self.token}

            response = requests.post(self.host+endp, headers=self.headers, json=params)
            rst = response.json()

            if  rst['return_code'] == 0 : # 토큰을 재발급한다.
                endp = '/oauth2/token'
                self.headers['api-id']='au10001'
                params = {'grant_type':'client_credentials','appkey':app_key,'secretkey':secret_key}

                response = requests.post(self.host+endp, headers=self.headers, json=params)
                rst = response.json()            

                if  rst['return_code'] == 0 :
                    self.DB.store('kiwoom_token',rst['token'])
                    self.DB.store('kiwoom_token_date',rst['expires_dt'])

                else : print(rst['return_msg'])

            else : print(rst['return_msg'])


        else :
            print(f"{hour_later_fmt} < {self.token_valid_date}")
            print("현재의 토큰을 사용합니다.")
            return self.DB.store('kiwoom_token')

# 에러메세지들
# 토큰인증에러 { return_code : 3, return_msg : 증에 실패했습니다[8005:Token이 유효하지 않습니다]" }
#

AA = KIWOOM()
print('---------------------------------------------------------------------------------------------')
a = AA.get_current_price('SOXL')
print(a)
print('---------------------------------------------------------------------------------------------')
b = AA.get_ohlc_price('SOXL','20260807')
print(b)

