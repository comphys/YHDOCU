import requests
from datetime import datetime
from zoneinfo import ZoneInfo


# FY : newyork, FN : nasdaq, FA : amax
# SOXL 은 FA

class DBOPEN :

    def __init__(self,SYS) :
        self.SYS   = SYS
        self.DB    = SYS.DB
        self.host  = 'https://openapi.dbsec.co.kr:8443'
        self.headers = {'Content-Type':'application/json;charset=UTF-8','cont_yn':'N'}

    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")  
        with open("logs/dbapi.log","a",encoding="utf-8") as f:
            f.write(f"<span class='who-ip'>{hour_now} :</span> {str}\n")

    def dbapi_deco(func) :
        def wrapper(self,*args,**kargs) :
            token = self.get_token()
            if not token : return False
            self.headers['authorization'] = f'Bearer {token}'
            return func(self,*args,**kargs)
        return wrapper

    @dbapi_deco
    def get_current_price(self,symbol,mk='FA') :
        endp = '/api/v1/quote/overseas-stock/inquiry/price'
        params = { "In": { "InputIscd1": symbol,    "InputCondMrktDivCode": mk }}
        response = requests.post(self.host+endp, headers=self.headers, json=params)
        if response.status_code == 200 :
            rst = response.json()
            pr = {'종목코드':symbol,'현재가':rst['Out']['Prpr']}
            return pr
        else : 
            self.log(f"{response.status_code} : {response.text}")
            return False

    @dbapi_deco
    def get_ohlc(self,symbol,date1,date2,mk='FA') :
        endp = '/api/v1/quote/overseas-stock/chart/day'
        params = { "In": {	"InputOrgAdjPrc":"1", "InputCondMrktDivCode": mk,	"InputIscd1": symbol,	"InputDate1": date1, "InputDate2": date2}}
        response = requests.post(self.host+endp, headers=self.headers, json=params)
        rst = response.json()
        print(rst)

    def check_token_expired(self) :
        token_time = self.DB.store('dbapi_time')
        return datetime.fromtimestamp(int(token_time)).strftime("%y-%m-%d %H:%M:%S")

    def revoke_token(self) :
        self.log("토큰을 폐기합니다.")
        endp = '/oauth2/revoke'
        self.headers = {'Content-Type':'application/x-www-form-urlencoded'}
        app_key = self.DB.store('dbapi_app_key')
        secret_key = self.DB.store('dbapi_secret_key')
        token = self.DB.store('dbapi_token')
        params = {'grant_type':'client_credentials','appkey':app_key,'appsecretkey':secret_key, 'token_type_hint':'access_token','token':token}
        response = requests.post(self.host+endp, headers=self.headers, data=params)
        if response.status_code == 200 : 
            self.DB.store('dbapi_token','')
            self.DB.store('dbapi_time','000') 

    def get_token(self) :

        current_time = int(datetime.now().timestamp() )+3600
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
            self.headers = {'Content-Type':'application/json;charset=UTF-8','cont_yn':'N'}       

            if  response.status_code == 200  :
                rst = response.json()  
                self.DB.store('dbapi_token',rst['access_token'])
                self.DB.store('dbapi_time',str(current_time+86400))
                return rst['access_token']
            
            else : 
                self.log(f"{response.status_code} : {response.text}")
                return False
        else :
            return self.DB.store('dbapi_token')

    @dbapi_deco
    def check_balance(self) :
        endp = '/api/v1/trading/overseas-stock/inquiry/balance-margin'
        params = { "In":{ "WonFcurrTpCode": "2",  "TrxTpCode": "2", "CmsnTpCode": "2",  "DpntBalTpCode": "1"  }}
        response = requests.post(self.host+endp, headers=self.headers, json=params)
        rst = response.json()
        print(rst['Out3'])

    @dbapi_deco
    def get_trading_history(self,date1,date2,symbol) :
        endp = '/api/v1/trading/overseas-stock/inquiry/trading-history'
        params = { "In":{ "QrySrtDt": date1,"QryEndDt":date2, "AstkIsuNo":symbol,"AstkBnsTpCode": "0","StnlnTpCode": "0","QryTpCode": "0","WonFcurrTpCode": "2","BaseDdTpCode": "1","DpntBalTpCode": "1"}}
        response = requests.post(self.host+endp, headers=self.headers, json=params)
        rst = response.json()
        if rst['rsp_cd'] == '00000' :
            pr = []
            rst = rst['Out']
            for r in rst :
                pr.append({'주문일자':r['OrdDt'],'종목코드':r['SymCode'],'주문구분':r['BnsTpNm'],'체결수량':r['AstkExecQty'],
                           '체결가격':r['AstkExecPrc'],'매매금액':r['AstkExecAmt'],'수수료':r['AstkExecCmsn'],'결제금액':r['AstkSettAmt']})
            for p in pr : print(p)
        else :
            print(f"코드 : {rst['rsp_cd']}  메세지 : {rst['rsp_msg']}")
