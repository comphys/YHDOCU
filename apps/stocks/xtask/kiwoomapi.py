import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from myutils.DB import DB
import sys

def log(*args, **kwargs) :

    with open("kiwoom.txt","a",encoding="utf-8") as f:
        print(*args, **kwargs, file=f)


class KIWOOM :

    def __init__(self) :

        self.DB    = DB('stocks')
        self.host  = 'https://api.kiwoom.com'
        self.headers = {'Content-Type':'application/json;charset=UTF-8','cont-yn':'N'}
        self.token = self.get_token()

    def get_current_price(self,symbol) :

        endp = '/api/us/mrkcond'
        self.headers['authorization'] = f'Bearer {self.token}'
        self.headers['api-id'] = 'usa20100'

        params = {'stex_tp' : 'NY', 'stk_cd' : symbol}

        response = requests.post(self.host+endp, headers=self.headers, json=params)
        rst = response.json()

        return {'코드':rst['return_code'],'안내':rst['return_msg'],'현재가':rst['cur_prc'],'증감':rst['flu_rt'],'전날종가':rst['base_close_pric'],'환율':rst['base_exrt']}

    def get_ohlc_price(self,symbol,date) :

        endp = '/api/us/mrkcond'
        self.headers['authorization'] = f'Bearer {self.token}'
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
        ohlc['코드'] = rst['return_code']
        ohlc['안내'] = rst['return_msg']
        ohlc['날자'] = f"{a['dt'][0:4]}-{a['dt'][4:6]}-{a['dt'][6:8]}"
        ohlc['시가'] = f"{abs(float(a['open_pric'])):.2f}"
        ohlc['고가'] = f"{abs(float(a['high_pric'])):.2f}"
        ohlc['저가'] = f"{abs(float(a['low_pric'])):.2f}"
        ohlc['종가'] = f"{abs(float(a['cur_prc'])):.2f}"
        ohlc['볼륨'] = a['acc_trde_qty']
        ohlc['전날'] = f"{float(a['base_pric']):.2f}"
        ohlc['증감'] = a['flu_rt']

        return ohlc

    # 미국주식 원장 잔고 확인
    def check_the_balance(self) :

        endp = '/api/us/acnt'
        self.headers['authorization'] = f'Bearer {self.token}'
        self.headers['api-id'] = 'ust21070'

        params = {}

        response = requests.post(self.host+endp, headers=self.headers, json=params)
        rst = response.json()

        r = rst['result_list'][0]
        
        rst_pretty = {'코드':rst['return_code'],'안내':rst['return_msg'],
                      '종목명':r['stk_cd'],'보유수량':int(r['poss_qty']),'매입단가':r['frgn_stk_book_uv'],'현재가':r['now_pric'],
                      '매입금액':r['frgn_stk_book_amt'],'평가금액':r['evlt_amt'],'손익금액':r['pl_amt'],'손익율':r['pl_rt']}
        return rst_pretty 


    # 현재 토큰 폐기 시각이 한시간 이내면 재발급 받아서 리턴하고, 그렇지 않으면 현재의 토큰을 반환한다.
    def get_token(self) :

        self.token = self.DB.store('kiwoom_token')
        self.token_valid_date = self.DB.store('kiwoom_token_date')
        app_key = self.DB.store('kiwoom_appkey')
        secret_key = self.DB.store('kiwoom_secretkey')

        kst = ZoneInfo("Asia/Seoul")
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
                    print("새로운 토큰을 발급받았습니다.")
                    return self.DB.store('kiwoom_token')

                else : print(rst['return_msg'])

            else : print(rst['return_msg'])


        else :
            print(f"{hour_later_fmt} < {self.token_valid_date}")
            nyse_tz = ZoneInfo("America/New_York")
            nyse_time = datetime.now(nyse_tz)
            nyse_time = nyse_time.strftime("%Y-%m-%d %H:%M %Z")
            print(f"현지시각 : {nyse_time}")
            log(f"현지시각 : {nyse_time}")
            return self.DB.store('kiwoom_token')

# 에러메세지들
# 토큰인증에러 { return_code : 3, return_msg : 증에 실패했습니다[8005:Token이 유효하지 않습니다]" }
#

AA = KIWOOM()
print('---------------------------------------------------------------------------------------------')
a = AA.get_current_price('SOXL')
print(a)
print('---------------------------------------------------------------------------------------------')
b = AA.get_ohlc_price('SOXL','20260813')
print(b)
log(f"실시간 : {a['현재가']} : OHLC :{b['종가']}")
log('-----------------------------------------')
print('---------------------------------------------------------------------------------------------')
# d = AA.check_the_balance()
# print(d)
