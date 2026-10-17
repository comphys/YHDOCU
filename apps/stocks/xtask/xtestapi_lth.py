import sys, platform
from datetime import datetime
from zoneinfo import ZoneInfo

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

    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")  
        with open(rootpath+"/logs/xtask.log","a",encoding="utf-8") as f:
            f.write(f"<span class='who-time'>{hour_now} :</span> {str}\n")

    def get_token_duetime(self) :
        ts = self.DB.store('meritz-time'+'lth')
        rst = my.timestamp_to_date(int(ts),opt=1)
        return rst

    def print_contents(self,data) :
        if data :
            for d in data : print(d)
        else : print(data)


A = yourClass()
B = A.API
today = my.kor_loc_date('US/Eastern')[0:10].replace('-','')
B.change_account('lth')

print("\033[H\033[J", end="")

while True :
    print("\033[90m----------------------------")
    print(" 1. 현재 주가 불러 오기")
    print(" 2. 특정 일 OHLC 불러 오기")
    print(" 3. 당일 체결 현황 보기")
    print(" 4. 현재 잔고 현황 보기")
    print(" 5. 현재 예약 현황 보기")
    print(" 6. 토큰 만료 시간 보기")
    print(" 7. 현재 계좌 잔액 확인")
    print("00. 나가기")
    print("----------------------------")
    ch = input("메뉴를 선택하세요 : \033[0m")
    
    if ch == '00' : break
    if ch == '1' : rst = B.get_current_price() ; print(rst)
    if ch.startswith('20') : rst = B.get_ohlc(ch) ; print(rst)
    if ch == '3' : 
        rst = B.get_orders_today('0','0') ; 
        A.print_contents(rst)
    if ch == '4' : rst = B.get_current_balance() ; print(rst)
    if ch == '5' : 
        rst = B.get_reserved_order(today,code='2')  
        A.print_contents(rst)
    if ch == '6' : rst = A.get_token_duetime(); print(rst)
    if ch == '7' : rst = B.get_money_balance() ; print(rst)
    if ch == '33': rst = B.revoke_token(); print(rst)
