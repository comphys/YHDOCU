import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from myutils.DB import DB

# FY : newyork, FN : nasdaq, FA : amax
# SOXL 은 FA

class DBAPI :

    def __init__(self) :
        self.DB = DB('stocks')
        self.host  = 'https://openapi.dbsec.co.kr:8443'
        self.headers = {'Content-Type':'application/json;charset=UTF-8','cont_yn':'N'}

    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H%M%S")  
        with open("logs/dbapi.log","a",encoding="utf-8") as f:
            f.write(f"{hour_now} : {str}\n")

    def dbapi_deco(func) :
        def wrapper(self,*args) :
            token = self.get_token()
            if not token : return False
            self.headers['authorization'] = f'Bearer {token}'
            return func(self,*args)
        return wrapper

    @dbapi_deco
    def get_current_price(self,symbol) :
        endp = '/api/v1/quote/overseas-stock/inquiry/price'
        params = { "In": { "InputIscd1": symbol,    "InputCondMrktDivCode": "FA" }}
        response = requests.post(self.host+endp, headers=self.headers, json=params)
        rst = response.json()
        print(rst)

    @dbapi_deco
    def get_ohlc(self,symbol,date1,date2) :
        endp = '/api/v1/quote/overseas-stock/chart/day'
        params = { "In": {	"InputOrgAdjPrc":"1", "InputCondMrktDivCode": "FY",	"InputIscd1": symbol,	"InputDate1": date1, "InputDate2": date2}}
        response = requests.post(self.host+endp, headers=self.headers, json=params)
        rst = response.json()
        print(rst)


    def revoke_token(self) :

        self.log("토큰을 폐기합니다.")
        endp = '/oauth2/revoke'
        self.headers = {'Content-Type':'application/x-www-form-urlencoded'}
        app_key = self.DB.store('dbapi_app_key')
        secret_key = self.DB.store('dbapi_secret_key')
        token = self.DB.store('dbapi_token')
        params = {'grant_type':'client_credentials','appkey':app_key,'appsecretkey':secret_key, 'token_type_hint':'access_token','token':token}
        response = requests.post(self.host+endp, headers=self.headers, data=params)
        rst = response.json()
        self.DB.store('dbapi_token','')
        self.DB.store('dbapi_time','000') 

    def get_token(self) :

        current_time = int(datetime.now().timestamp() )
        token_extime = int(self.DB.store('dbapi_time'))

        if  token_extime < current_time :
            self.revoke_token()
            self.log("토큰을 재발급합니다.")
            self.headers = {'Content-Type':'application/x-www-form-urlencoded'}
            endp = '/oauth2/token'
            app_key = self.DB.store('dbapi_app_key')
            secret_key = self.DB.store('dbapi_secret_key')
            params = {'grant_type':'client_credentials','appkey':app_key,'appsecretkey':secret_key, 'scope':'oob'}
            response = requests.post(self.host+endp, headers=self.headers, data=params)
            rst = response.json()            

            if  rst['access_token']  :
                self.DB.store('dbapi_token',rst['access_token'])
                self.DB.store('dbapi_time',str(current_time+82800))
                return rst['access_token']
            
            else : 
                self.log(f"{rst['rsp_cd']} : {rst['rsp_msg']}")
                return False
        else :
            return self.DB.store('dbapi_token')
            

api = DBAPI()
# api.get_current_price('SGOV')
print('----------------------------------------------------------------------------------------------------')
api.get_ohlc('SGOV','20260904','20260904')
# api.revoke_token()
# api.temp()
# token = api.get_token()
# print(token)


