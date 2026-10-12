import sys, platform

sysos = platform.system()
if    sysos == 'Windows' :  rootpath = '/YHDOCU'; macaddress = 'BCFCE7C9911F'
elif  sysos == 'Linux'   :  rootpath = '/home/comphys/YHDOCU'
elif  sysos == 'Android' :  rootpath = '/data/data/com.termux/files/home/YHDOCU'; macaddress = 'A475B980D0CA'
else: sysos == '' 
sys.path.append(rootpath)

from apps.stocks.xtask.xload import Control
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
from zoneinfo import ZoneInfo
import system.core.my_utils as my
import time

class yourClass(Control) :

    def _auto(self) :
        self.DB = self.db('stocks',path=rootpath+'/')
        self.skey = self.DB.store("slack_key")

        self.API = self.load_app_lib('meritz')
        self.API.headers = {'Content-Type':'application/json;charset=UTF-8','mac_address':macaddress}     

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
        # 다음 날 주문정보 갖고오기
        ini_data   = self.DB.oneline(f"SELECT add18,add19 FROM h_logDIY_board ORDER BY add0 DESC LIMIT 1")
        ini_date = ini_data[0]
        ini_capital = f"{float(ini_data[1]):,.2f}"
        last_date = self.DB.last_date('h_rsnLog_board')
        다음날자 = my.next_stock_day(last_date,self.DB)[0].replace('-','')

        DIY = self.load_app_lib('diy')
        NS  = DIY.get_nextStrategy(ini_date,last_date,ini_capital)
        OD = []
        if int(NS['예정수량']) : OD.append({'종목코드':'SOXL','주문일자':다음날자,'매매구분':'2','주문수량':NS['예정수량'],'주문가격':NS['예정매가']})
        if int(NS['예정도수']) : OD.append({'종목코드':'SOXL','주문일자':다음날자,'매매구분':'1','주문수량':NS['예정도수'],'주문가격':NS['예정도가']})
        
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


# ------------------------------------------------------------------------------------------------------------------
today = my.kor_loc_date('US/Eastern')[0:10]
weekd = my.dayofdate(today)
A = yourClass()
B = A.API

# # 증시 휴장일 체크하기
ck_holiday = A.DB.exe(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday[0][0] if ck_holiday else ''

skip = ''
if weekd in ['토','일'] : skip = f"{weekd}요일 입니다"
if is_holiday : skip = is_holiday
if today > '2027-09-30' : skip = 'API 키 갱신이 필요합니다'

if  skip :
    A.send_message(skip)

else :
    # 작업코드 시작-------------------------------------------------------------------------------------------------------------------

    odday = today.replace('-','') 
    # 현재 주가 정보를 가져온다
    cp = B.get_current_price()
    c_upl = round(float(cp['현재가격'])*1.18,2)
    c_dnl = round(float(cp['현재가격'])*0.78,2)

    # RSN 의 주문 정보를 가져온다
    rsn = A.rsn_order_data() 
    buy_total_rsn = 0.0
    total_rsn = B.get_money_balance()

    for r in rsn :
        if  r['매매구분'] == '1' and float(r['주문가격']) < c_dnl : r['주문가격'] = f"{c_dnl:.2f}" # for sell
        if  r['매매구분'] == '2' and float(r['주문가격']) > c_upl : 
            r['주문가격'] = f"{c_upl:.2f}" 
            buy_total_rsn += float(r['주문가격']) * int(r['주문수량'])
    
    if float(total_rsn['추정예수금']) >= buy_total_rsn :
        for r in rsn :
            if r['매매구분'] == '1' : 
                B.do_reserved_sell('SOXL',r['주문수량'],r['주문가격'],odday,'Y')
                time.sleep(0.5)
            
            if r['매매구분'] == '2' : 
                B.do_reserved_buy('SOXL',r['주문수량'],r['주문가격'],odday,'Y')
                time.sleep(0.5)

        A.send_message("RSN 주문을 완료하였습니다")
    else :
        A.send_message("RSN 계좌 예수금 부족")

    # DIY 의 주문 정보를 가져온다
    B.change_account('02')
    diy = A.diy_order_data() 
    buy_total_diy = 0.0
    total_diy = B.get_money_balance()
    
    for d in diy :
        if  d['매매구분'] == '1' and float(d['주문가격']) < c_dnl : d['주문가격'] = f"{c_dnl:.2f}" # for sell
        if  d['매매구분'] == '2' and float(d['주문가격']) > c_upl : 
            d['주문가격'] = f"{c_upl:.2f}" 
            buy_total_diy += float(d['주문가격']) * int(d['주문수량'])

    if float(total_diy['추정예수금']) >= buy_total_diy :
        for d in diy :
            if d['매매구분'] == '1' : 
                B.do_reserved_sell('SOXL',r['주문수량'],r['주문가격'],odday,'Y')
                time.sleep(0.5)
            
            if d['매매구분'] == '2' : 
                B.do_reserved_buy('SOXL',r['주문수량'],r['주문가격'],odday,'Y')
                time.sleep(0.5)
        
        A.send_message("DIY 주문을 완료하였습니다")
    else :
        A.send_message("DIY 계좌 예수금 부족")

    # 작업코드 종료-------------------------------------------------------------------------------------------------------------------