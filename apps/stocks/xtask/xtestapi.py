import sys, platform, time
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
        rst = []
        for x in ['01','02','03','lth'] : 
            ts = self.DB.store('meritz-time'+x)
            rst.append(my.timestamp_to_date(int(ts),opt=1))
        return rst
    
    def print_contents(self,data) :
        if isinstance(data,list):
            for d in data : print(d)
        else : print(data)


    def test(self) :
        return self.API.get_market_date()    


A = yourClass()
B = A.API
today = B.get_market_date()

print("\033[H\033[J", end="")

while True :
    print("\033[90m----------------------------")
    print(" 1. 현재 주가 불러 오기")
    print(" 2. 특정 일 OHLC 불러 오기")
    print(" 3. 당일 체결 현황 보기(300,310,320)")
    print(" 4. 현재 잔고 현황 보기")
    print(" 5. 현재 예약 현황 보기")
    print(" 6. 토큰 만료 시간 보기")
    print(" 7. 현재 계좌 잔액 확인")
    print(" 8. 실시간 매도 주문(기본:지정가)")
    print(" 9. 실시간 매수 주문(기본:지정가)")
    print("10. 예약 매수 주문(기본:LOC)")
    print(" 0. 나가기")
    print("----------------------------")
    ch = input(f"{today} 계좌[{B.account}] 메뉴를 선택하세요 : \033[0m")
    if ch == '0' : break
    elif ch in ['01','02','03','lth'] : B.change_account(ch)
    elif ch == '1'  : rst = B.get_current_price() ; A.print_contents(rst)
    elif ch.startswith('20') : rst = B.get_ohlc(ch) ; print(rst)
    elif ch in ['300','310','320'] : 
        rst = B.get_orders_today(ch[1],ch[2])
        A.print_contents(rst)
    elif ch == '4' : 
        rst = B.get_account_balance()
        A.print_contents(rst)
    elif ch == '5' : 
        rst = B.get_reserved_order(today,code='2')  
        A.print_contents(rst)
    elif ch == '6' : 
        rst = A.get_token_duetime() 
        A.print_contents(rst)
    elif ch == '7' : rst = B.get_money_balance() ; print(rst)
    elif ch == '8' : 
        order = input("실시간 매도 : 수량/가격/[01/0|32/7] : ") 
        if order != '0' : 
            order = order.split('/')
            B.do_real_sell(order[0],order[1],order[2],order[3]) 
            time.sleep(1)
            rst = B.get_orders_today('2','0')
            A.print_contents(rst)
    elif ch == '9' : 
        order = input("실시간 매수 : 수량/가격/[01/0|32/7] : ")
        if order != '0' : 
            order = order.split('/')
            B.do_real_buy(order[0],order[1],order[2],order[3]) 
            time.sleep(1)
            rst = B.get_orders_today('2','0')
            A.print_contents(rst)
    elif ch == '10' : 
        order = input("예약 매수 : 수량/가격 : ")
        if order != '0' : 
            order = order.split('/')
            B.do_reserved_buy('SOXL',order[0],order[1],today,'Y')
            time.sleep(1)
            rst = B.get_reserved_order(today,code='2') 
            A.print_contents(rst)
    elif ch == 'X' : 
        cancel = input("주문을 취소 : 날자/주문번호/수량 : ")
        if cancel != '0' : 
            cancel = cancel.split('/')
            B.do_real_cancel(cancel[0],cancel[1],cancel[2]) 
            time.sleep(1)
            rst = B.get_orders_today('2','0')
            A.print_contents(rst)


