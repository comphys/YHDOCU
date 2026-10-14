import sys, platform
from datetime import datetime
from zoneinfo import ZoneInfo
import requests

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
        self.API.headers = {'Content-Type':'application/json;charset=UTF-8','mac_address':macaddress}     

    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")  
        with open(rootpath+"/logs/xtask.log","a",encoding="utf-8") as f:
            f.write(f"<span class='who-time'>{hour_now} :</span> {str}\n")

    def get_token_duetime(self) :
        rst = []
        for x in ['01','02','03'] : 
            ts = self.DB.store('meritz-time'+x)
            rst.append(my.timestamp_to_date(int(ts),opt=1))
        return rst



A = yourClass()
B = A.API
today = my.kor_loc_date('US/Eastern')[0:10].replace('-','')

print("\033[H\033[J", end="")

while True :
    print("----------------------------")
    print("1. 현재 주가 불러 오기")
    print("2. 특정 일 OHLC 불러 오기")
    print("3. 당일 체결 현황 보기(RSN)")
    print("4. 당일 체결 현황 보기(DIY)")
    print("5. 현재 잔고 현황 보기(RSN)")
    print("6. 현재 잔고 현황 보기(DIY)")
    print("7. 현재 예약 현황 보기(RSN)")
    print("8. 현재 예약 현황 보기(DIY)")
    print("9. 토큰 만료 시간 보기")
    print("0. 나가기")
    print("----------------------------")
    ch = input("메뉴를 선택하세요 : ")
    
    if ch == '0' : break
    if ch == '10' : B.renew_token() ; print("토큰을 모두 리뉴얼 했습니다")
    if ch == '1' : rst = B.get_current_price() ; print(rst)
    if ch.startswith('20') : rst = B.get_ohlc(ch) ; print(rst)
    if ch == '3' : 
        rst = B.check_orders_today('0','0') ; 
        for r in rst : print(r)
    if ch == '4' :
        B.change_account('02') 
        rst = B.check_orders_today('0','0') ; 
        for r in rst : print(r)
        B.change_account('01')
    if ch == '5' : rst = B.get_current_balance() ; print(rst)
    if ch == '6' : B.change_account('02'); rst = B.get_current_balance() ; B.change_account('01'); print(rst)
    if ch == '7' : 
        rst = B.check_reserved_order(today,code='2')  
        for r in rst : print(r)
    if ch == '8' : 
        B.change_account('02'); rst = B.check_reserved_order(today,code='2'); B.change_account('01');  
        for r in rst : print(r)
    if ch == '9' : 
        rst = A.get_token_duetime() 
        for r in rst : print(r)

