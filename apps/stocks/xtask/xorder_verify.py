import sys, platform
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
from zoneinfo import ZoneInfo
import time

sysos = platform.system()
if    sysos == 'Windows' :  rootpath = '/YHDOCU'; macaddress = 'BCFCE7C9911F'
elif  sysos == 'Linux'   :  rootpath = '/home/comphys/YHDOCU'; macaddress = 'A475B980D0CA'
elif  sysos == 'Android' :  rootpath = '/data/data/com.termux/files/home/YHDOCU'; macaddress = 'A475B980D0CA'
else: sysos == '' 
sys.path.append(rootpath)

from apps.stocks.xtask.xload import Control
import system.core.my_utils as my

class yourClass(Control) :

    def _auto(self) :
        self.DB = self.db('stocks',path=rootpath+'/')
        self.skey = self.DB.store("slack_key")

        self.API = self.load_app_lib('meritz')
        self.API.root = rootpath
        self.API.maca = macaddress  

        self.today = my.kor_loc_date('US/Eastern')[0:10]
        self.weekd = my.dayofdate(self.today)


    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")  
        with open(rootpath+"/logs/xtask.log","a",encoding="utf-8") as f:
            f.write(f"<span class='who-time'>{hour_now} :</span> {str}\n")

    def lprint(self,data) :
        if isinstance(data,list) :
            for d in data : print(d)
        else : print(data)
    
    def rsn_order_data(self) :
        last_ohlc = self.DB.last_date('h_stockHistory_board')
        next_date = my.next_stock_day(last_ohlc,self.DB)[0].replace('-','')
        NS = self.DB.line(f"SELECT add3,r_09,r_17,r_18,r_19,r_20,s_09,s_17,s_18,s_19,s_20,n_09,n_17,n_18,n_19,n_20 FROM h_rsnLog_board WHERE add0='{last_ohlc}' LIMIT 1") 
        OD = []
        for key in ['r','s','n'] :
            if int(NS[key+'_17']) :  OD.append({'종목코드':'SOXL','주문일자':next_date,'매매구분':'2','주문수량':NS[key+'_17'],'주문가격':NS[key+'_18']})
            if int(NS[key+'_19']) :  OD.append({'종목코드':'SOXL','주문일자':next_date,'매매구분':'1','주문수량':NS[key+'_19'],'주문가격':NS[key+'_20']})
        return OD

    def diy_order_data(self,b='logDIY') :
        ini_data   = self.DB.oneline(f"SELECT add18,add19 FROM h_{b}_board ORDER BY add0 DESC LIMIT 1")
        ini_date = ini_data[0]
        ini_capital = f"{float(ini_data[1]):,.2f}"
        last_date = self.DB.last_date('h_rsnLog_board')
        next_date = my.next_stock_day(last_date,self.DB)[0].replace('-','')

        DIY = self.load_app_lib('diy')
        NS  = DIY.get_nextStrategy(ini_date,last_date,ini_capital)
        OD = []
        if int(NS['예정수량']) : OD.append({'종목코드':'SOXL','주문일자':next_date,'매매구분':'2','주문수량':str(NS['예정수량']),'주문가격':str(NS['예정매가'])})
        if int(NS['예정도수']) : OD.append({'종목코드':'SOXL','주문일자':next_date,'매매구분':'1','주문수량':str(NS['예정도수']),'주문가격':str(NS['예정도가'])})
        if int(NS['꼬리도수']) : OD.append({'종목코드':'SOXL','주문일자':next_date,'매매구분':'1','주문수량':str(NS['꼬리도수']),'주문가격':str(NS['꼬리도가'])})
        
        return OD
    
    def send_message(self,message,ch='주식') :
        
        if sysos == 'Android' :
            my.send_push("주식 주문 검증 보고",message)
        elif sysos == 'Windows' :
            print("주식 주문 검증 보고",message)
        else :  
            client = WebClient(token=self.skey)
            try:
                client.chat_postMessage(channel= ch, text= message)
                return True
            except SlackApiError as e:
                assert e.response["ok"] is False
                assert e.response["error"]
                self.log(f"slack error : {e.response['error']}")

    def verify_rsn_order(self) :
        order = self.rsn_order_data()
        acted = self.API.get_orders_today('2','0')  
        if len(order) != len(acted) : return (False,"RSN 주문 건수 오류")
        cnt = 0
        for o in order :
            for a in acted :
                if a['주문상태'] != '0' : return (False,"RSN 주문상태 오류") 
                if a['호가유형'] != '5' : return (False,"RSN 호가유형 오류")
                if o.items() <= a.items() :  cnt += 1
        if cnt != len(order) : return (False,"RSN 주문내용 상이")
        
        return (True,"RSN 주문상태 정상")

    def verify_diy_order(self,t='DIY',b='logDIY') :
        order = self.diy_order_data(b)
        acted = self.API.get_orders_today('2','0') 

        if len(order) != len(acted) : return (False,f"{t} 주문건수 오류")
        cnt = 0
        for o in order :
            for a in acted :
                if a['주문상태'] != '0' : return (False,f"{t} 주문상태 오류") 
                if a['호가유형'] != '5' : return (False,f"{t} 호가유형 오류")
                if o.items() <= a.items() :  cnt += 1
        if cnt != len(order) : return (False,f"{t} 주문내용 상이")
        
        return (True,f"{t} 주문상태 정상")       


# ------------------------------------------------------------------------------------------------------------------
A = yourClass()

# # 증시 휴장일 체크하기
ck_holiday = A.DB.exe(f"SELECT description FROM parameters WHERE val='{A.today}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday[0][0] if ck_holiday else ''

skip = ''
if A.weekd in ['토','일'] : skip = f"{A.weekd}요일 입니다"
if is_holiday : skip = is_holiday
if A.today > '2027-09-30' : skip = 'API 키 갱신이 필요합니다'

if  not skip :
    # 작업코드 시작-------------------------------------------------------------------------------------------------------------------
    A.API.change_account('01')
    rst1 = A.verify_rsn_order()
    A.send_message(rst1[1]) 
    time.sleep(1)

    A.API.change_account('02')
    rst2 = A.verify_diy_order('DIY','logDIY')
    A.send_message(rst2[1])
    time.sleep(1)

    A.API.change_account('03')
    rst3 = A.verify_diy_order('Pocket','logDIY2')
    A.send_message(rst3[1])
    time.sleep(1)

    A.API.change_account('lth')
    rst4 = A.verify_diy_order('LTH','logLTH')
    A.send_message(rst4[1])
    time.sleep(1)

    # 작업코드 종료-------------------------------------------------------------------------------------------------------------------