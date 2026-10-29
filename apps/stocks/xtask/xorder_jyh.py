import sys, platform
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
from zoneinfo import ZoneInfo
import time,requests

sysos = platform.system()
if    sysos == 'Windows' :  rootpath = '/YHDOCU'; macaddress = 'BCFCE7C9911F'
elif  sysos == 'Linux'   :  rootpath = '/home/comphys/YHDOCU'; macaddress = 'A475B980D0CA'
elif  sysos == 'Android' :  rootpath = '/data/data/com.termux/files/home/YHDOCU'; macaddress = 'A475B980D0CA'
else: sysos == '' 
sys.path.append(rootpath)

from apps.stocks.xtask.xload import Control
import system.core.my_utils as my

class yourClass(Control) :

    sel_type = '1'
    buy_type = '2'
    exe_type =  False # 실제 실행 / 테스트   
    ord_date = ''
    lst_date = ''
    
    def _auto(self) :
        self.DB = self.db('stocks',path=rootpath+'/')
        self.skey = self.DB.store("slack_key")

        self.API = self.load_app_lib('meritz')
        self.API.root = rootpath
        self.API.maca = macaddress

        self.my_token   = self.DB.store('api_token')
        self.my_host    = "https://comphys.pythonanywhere.com/api"
        self.my_headers = {'Content-Type':'application/json;charset=UTF-8','Authorization':self.my_token}

        self.cp  = self.API.get_current_price()['현재가격']
        self.upl = round(float(self.cp)*1.18,2)
        self.dnl = round(float(self.cp)*0.82,2)

        time.sleep(1)

    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")  
        with open(rootpath+"/logs/xtask.log","a",encoding="utf-8") as f:
            f.write(f"<span class='who-time'>{hour_now} :</span> {str}\n")

    def lprint(self,data) :
        if isinstance(data,list):
            for d in data : print(d)
        else : print(data)

    def rsn_order_data(self,board) :
        chk_last_date = self.DB.last_date(f"h_{board}_board")
        NS = self.DB.line(f"SELECT add3,r_09,r_17,r_18,r_19,r_20,s_09,s_17,s_18,s_19,s_20,n_09,n_17,n_18,n_19,n_20 FROM h_rsnLog_board WHERE add0='{chk_last_date}' LIMIT 1") 
        OD = []
        for key in ['r','s','n'] :
            if int(NS[key+'_17']) :  OD.append({'종목코드':'SOXL','주문일자':self.ord_date,'매매구분':'2','주문수량':NS[key+'_17'],'주문가격':NS[key+'_18']})
            if int(NS[key+'_19']) :  OD.append({'종목코드':'SOXL','주문일자':self.ord_date,'매매구분':'1','주문수량':NS[key+'_19'],'주문가격':NS[key+'_20']})
        return OD

    def diy_order_data(self,board) :
        ini_data   = self.DB.oneline(f"SELECT add18,add19 FROM h_{board}_board ORDER BY add0 DESC LIMIT 1")
        ini_date = ini_data[0]
        ini_capital = f"{float(ini_data[1]):,.2f}" 
        DIY= self.load_app_lib('diy')
        NS = DIY.get_nextStrategy(ini_date,self.lst_date,ini_capital)

        OD = []
        if int(NS['예정수량'])  : OD.append({'종목코드':'SOXL','주문일자':self.ord_date,'매매구분':'2','주문수량':str(NS['예정수량']),'주문가격':str(NS['예정매가'])})
        if int(NS['예정도수'])  : OD.append({'종목코드':'SOXL','주문일자':self.ord_date,'매매구분':'1','주문수량':str(NS['예정도수']),'주문가격':str(NS['예정도가'])})
        if int(NS['꼬리도수'])  : OD.append({'종목코드':'SOXL','주문일자':self.ord_date,'매매구분':'1','주문수량':str(NS['꼬리도수']),'주문가격':str(NS['꼬리도가'])})
        del NS
        return OD
    
    def send_message(self,message,ch='주식') :
        if sysos == 'Android' :
            my.send_push("주식 예약주문 보고",message)
        elif sysos=='Windows' :
            print(message)
        else :
            client = WebClient(token=self.skey)
            client.chat_postMessage(channel= ch, text= message)


    def do_my_order(self,key,orders) :

        buy_total = 0.0
        cur_total = float(self.API.get_money_balance()['통합달러'])
        buy_total = sum(float(x.get('주문가격',0))*int(x.get('주문수량'),0) for x in orders if x.get('매매구분') == self.buy_type )

        if  cur_total < buy_total : 
            short = f"{buy_total-cur_total:,.2f}"
            self.send_message(f"{key} 예수금 {short} 부족"); return         

        for o in orders :

            if  o['매매구분'] == self.sel_type :
                price = max(float(o['주문가격']),self.dnl)
                if  self.exe_type :
                    if not (rst:=self.API.do_reserved_sell('SOXL',o['주문수량'],f"{price:.2f}",self.ord_date,'Y')) : 
                        self.log(f"{key} 매도주문 오류 : {rst}")
                        return
                else : print(key,' SOXL 매도 : ',o['주문수량'],f"{price:.2f}",self.ord_date,'Y') 
  
            else : 
                price = min(float(o['주문가격']),self.upl)
                if  self.exe_type :
                    if not (rst:=self.API.do_reserved_buy('SOXL',o['주문수량'],f"{price:.2f}",self.ord_date,'Y')) : 
                        self.log(f"{key} 매수주문 오류 : {rst}")
                        return
                else : print(key,' SOXL 매수 : ',o['주문수량'],f"{price:.2f}",self.ord_date,'Y') 
            
            time.sleep(0.5)

        self.send_message(f"{self.ord_date} {key} 예약주문 완료")

# ------------------------------------------------------------------------------------------------------------------
# 예약을 위한 코드임으로 이페이지의 현재 시간(A.today) 기준은 한국시간 기준이다. 
# 이 페이지의 실행은 한국시간 09:00 ~ 22:00 사이에 실행된다고 가정한다. 
# ------------------------------------------------------------------------------------------------------------------
A = yourClass()
A.exe_type = True

last_date = A.DB.last_date('h_stockHistory_board')
nextStock = my.next_stock_day(last_date,A.DB)
today_kor = my.kor_loc_date('Asia/Seoul')
todayWeek = my.dayofdate(today_kor[0:10])
todayTime = int(today_kor[11:13])

Action = True

if Action :

    # # 증시 휴장일 체크하기
    skip = ''
    if todayWeek in ['토','일'] : skip = f"{todayWeek}요일 입니다"
    elif today_kor[0:10] != nextStock[0] : skip = "예약 가능 날자가 아닙니다."
    elif today_kor[0:10] > '2027-09-30' : skip = 'API 키 갱신이 필요합니다'
    elif todayTime < 9 or todayTime > 22 : skip = '예약 가능 시간이 아닙니다.' 
    else :
        A.lst_date = last_date
        A.ord_date = nextStock[0]

    if  skip :
        A.send_message(skip)

    else :
        # RSN
        A.API.change_account('01')
        orders = A.rsn_order_data('rsnLog')
        A.do_my_order('RSN',orders)
        if A.exe_type :
            A.DB.parameter_update('TX070',A.ord_date)
            requests.post(A.my_host+'/check/check_rsn',headers=A.my_headers,json={'rsn_check':A.ord_date})

        # DIY
        A.API.change_account('02')
        orders = A.diy_order_data('logDIY')
        A.do_my_order('DIY',orders)
        if A.exe_type :
            A.DB.parameter_update('A0710',A.ord_date)
            requests.post(A.my_host+'/check/check_diy',headers=A.my_headers,json={'diy_check':A.ord_date})

        # DIY2
        A.API.change_account('03')
        orders = A.diy_order_data('logDIY2')
        A.do_my_order('DIY2',orders)

        # LTH
        A.API.change_account('lth')
        orders = A.diy_order_data('logLTH')
        A.do_my_order('LTH',orders)
       
else :
    print("Action 스위치가 꺼져 있습니다.")