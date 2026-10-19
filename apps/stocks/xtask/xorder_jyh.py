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
    
    def _auto(self) :
        self.DB = self.db('stocks',path=rootpath+'/')
        self.skey = self.DB.store("slack_key")

        self.API = self.load_app_lib('meritz')
        self.API.root = rootpath
        self.API.maca = macaddress

        self.today = my.kor_loc_date('US/Eastern')[0:10]
        self.weekd = my.dayofdate(self.today)
        self.my_token   = self.DB.store('api_token')
        self.my_host    = "https://comphys.pythonanywhere.com/api"
        self.my_headers = {'Content-Type':'application/json;charset=UTF-8','Authorization':self.my_token}

        
        self.cp = self.API.get_current_price()
        time.sleep(1)

    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")  
        with open(rootpath+"/logs/xtask.log","a",encoding="utf-8") as f:
            f.write(f"<span class='who-time'>{hour_now} :</span> {str}\n")

    def rsn_order_data(self) :
        chk_last_date = self.DB.last_date('h_rsnLog_board')
        last_ohlc = self.DB.last_date('h_stockHistory_board')
        다음날자 = my.next_stock_day(last_ohlc,self.DB)[0].replace('-','')
        NS = self.DB.line(f"SELECT add3,r_09,r_17,r_18,r_19,r_20,s_09,s_17,s_18,s_19,s_20,n_09,n_17,n_18,n_19,n_20 FROM h_rsnLog_board WHERE add0='{chk_last_date}' LIMIT 1") 
        OD = []
        for key in ['r','s','n'] :
            if int(NS[key+'_17']) :  OD.append({'종목코드':'SOXL','주문일자':다음날자,'매매구분':'2','주문수량':NS[key+'_17'],'주문가격':NS[key+'_18']})
            if int(NS[key+'_19']) :  OD.append({'종목코드':'SOXL','주문일자':다음날자,'매매구분':'1','주문수량':NS[key+'_19'],'주문가격':NS[key+'_20']})
       
        return OD

    def diy_order_data(self) :
        ini_data   = self.DB.oneline(f"SELECT add18,add19 FROM h_logDIY_board ORDER BY add0 DESC LIMIT 1")
        ini_date = ini_data[0]
        ini_capital = f"{float(ini_data[1]):,.2f}"
        last_date = self.DB.last_date('h_rsnLog_board')
        다음날자 = my.next_stock_day(last_date,self.DB)[0].replace('-','')

        DIY = self.load_app_lib('diy')
        NS  = DIY.get_nextStrategy(ini_date,last_date,ini_capital)
        OD = []
        if int(NS['예정수량']) : OD.append({'종목코드':'SOXL','주문일자':다음날자,'매매구분':'2','주문수량':str(NS['예정수량']),'주문가격':str(NS['예정매가'])})
        if int(NS['예정도수']) : OD.append({'종목코드':'SOXL','주문일자':다음날자,'매매구분':'1','주문수량':str(NS['예정도수']),'주문가격':str(NS['예정도가'])})
        
        return OD
    
    def send_message(self,message,ch='주식') :
        client = WebClient(token=self.skey)
        try:
            client.chat_postMessage(channel= ch, text= message)
            return True
        except SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]
            self.log(f"slack error : {e.response['error']}")

    def do_rsn_order(self) :
        odday = self.today.replace('-','') 
        c_upl = round(float(self.cp['현재가격'])*1.18,2)
        c_dnl = round(float(self.cp['현재가격'])*0.78,2)

        rsn = self.rsn_order_data()
        buy_total_rsn = 0.0
        total_rsn = self.API.get_money_balance()

        for r in rsn :
            if    r['매매구분'] == self.sel_type and float(r['주문가격']) < c_dnl : r['주문가격'] = f"{c_dnl:.2f}" # for sell
            elif  r['매매구분'] == self.buy_type and float(r['주문가격']) > c_upl : r['주문가격'] = f"{c_upl:.2f}" # for buy
            if    r['매매구분'] == self.buy_type : buy_total_rsn += float(r['주문가격']) * int(r['주문수량'])

        for r in rsn :
            if r['매매구분'] == self.sel_type : 
                rst = self.API.do_reserved_sell('SOXL',r['주문수량'],'110.00',odday,'Y')
                if not rst : self.log(f"RSN 매도주문 오류 : {rst}"); return
                time.sleep(0.5)
                
        self.send_message(f"{self.today} RSN 매도주문 완료")

        if float(total_rsn['통합달러']) >= buy_total_rsn :
            for r in rsn :
                if r['매매구분'] == self.buy_type : 
                    rst = self.API.do_reserved_buy('SOXL',r['주문수량'],r['주문가격'],odday,'Y')
                    if not rst : self.log(f"RSN 매수주문 오류 : {rst}"); return
                    time.sleep(0.5)
            self.send_message(f"{self.today} RSN 매수주문 완료")
            # 확인 날자 업데이트 
            self.DB.parameter_update('TX070',self.today)
            requests.post(self.my_host+'/check/check_rsn',headers=self.my_headers,json={'rsn_check':self.today})
        else :
            self.send_message("RSN 계좌 예수금 부족")

    def do_diy_order(self) :
        odday = self.today.replace('-','') 
        c_upl = round(float(self.cp['현재가격'])*1.18,2)
        c_dnl = round(float(self.cp['현재가격'])*0.78,2)
        
        diy = self.diy_order_data() 
        buy_total_diy = 0.0
        total_diy = self.API.get_money_balance()

        for d in diy :
            if    d['매매구분'] == self.sel_type and float(d['주문가격']) < c_dnl : d['주문가격'] = f"{c_dnl:.2f}" # for sell
            elif  d['매매구분'] == self.buy_type and float(d['주문가격']) > c_upl : d['주문가격'] = f"{c_upl:.2f}" 
            if    d['매매구분'] == self.buy_type : buy_total_diy += float(d['주문가격']) * int(d['주문수량'])

        for d in diy :
            if d['매매구분'] == self.sel_type : 
                rst  = self.API.do_reserved_sell('SOXL',d['주문수량'],d['주문가격'],odday,'Y')
                if not rst : self.log(f"DIY 매도주문 오류 : {rst}"); return
                time.sleep(0.5)

        if float(total_diy['통합달러']) >= buy_total_diy :
            for d in diy :
                if d['매매구분'] == self.buy_type : 
                    rst  = self.API.do_reserved_buy('SOXL',d['주문수량'],d['주문가격'],odday,'Y')
                    if not rst : self.log(f"DIY 매수주문 오류 : {rst}"); return
                    time.sleep(0.5)
            
            self.send_message(f"{self.today} DIY 주문을 완료")
            # 확인 날자 업데이트 
            self.DB.parameter_update('A0710',self.today)
            requests.post(self.my_host+'/check/check_diy',headers=self.my_headers,json={'diy_check':self.today})
        else :
            self.send_message("DIY 계좌 예수금 부족")



# ------------------------------------------------------------------------------------------------------------------
A = yourClass()

# # 증시 휴장일 체크하기
ck_holiday = A.DB.exe(f"SELECT description FROM parameters WHERE val='{A.today}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday[0][0] if ck_holiday else ''

skip = ''
if A.weekd in ['토','일'] : skip = f"{A.weekd}요일 입니다"
if is_holiday : skip = is_holiday
if A.today > '2027-09-30' : skip = 'API 키 갱신이 필요합니다'

if  skip :
    A.send_message(skip)

else :
    # 작업코드 시작-------------------------------------------------------------------------------------------------------------------
    A.do_rsn_order()
    A.API.change_account('02');    A.do_diy_order();    A.API.change_account('01')

    # 작업코드 종료-------------------------------------------------------------------------------------------------------------------