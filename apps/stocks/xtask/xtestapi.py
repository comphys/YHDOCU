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
        rst = []
        for x in ['01','02','03'] : 
            ts = self.DB.store('meritz-time'+x)
            rst.append(my.timestamp_to_date(int(ts),opt=1))
        return rst
    
    def print_contents(self,data) :
        if data :
            for d in data : print(d)
        else : print(data)


    def test(self) :
        chk_last_date = self.DB.last_date('h_rsnLog_board')
        last_ohlc = self.DB.last_date('h_stockHistory_board')
        다음날자 = my.next_stock_day(last_ohlc,self.DB)[0].replace('-','')
        NS = self.DB.line(f"SELECT add3,r_09,r_17,r_18,r_19,r_20,s_09,s_17,s_18,s_19,s_20,n_09,n_17,n_18,n_19,n_20 FROM h_rsnLog_board WHERE add0='{chk_last_date}' LIMIT 1") 
        OD = []
        for key in ['r','s','n'] :
            if int(NS[key+'_17']) :  OD.append({'종목코드':'SOXL','주문일자':다음날자,'매매구분':'2','주문수량':NS[key+'_17'],'주문가격':NS[key+'_18']})
            if int(NS[key+'_19']) :  OD.append({'종목코드':'SOXL','주문일자':다음날자,'매매구분':'1','주문수량':NS[key+'_19'],'주문가격':NS[key+'_20']})
       
        return OD


A = yourClass()
B = A.API
today = my.kor_loc_date('US/Eastern')[0:10].replace('-','')

print("\033[H\033[J", end="")

while True :
    print("\033[90m----------------------------")
    print(" 1. 현재 주가 불러 오기")
    print(" 2. 특정 일 OHLC 불러 오기")
    print(" 3. 당일 체결 현황 보기(RSN)")
    print(" 4. 당일 체결 현황 보기(DIY)")
    print(" 5. 현재 잔고 현황 보기(RSN)")
    print(" 6. 현재 잔고 현황 보기(DIY)")
    print(" 7. 현재 예약 현황 보기(RSN)")
    print(" 8. 현재 예약 현황 보기(DIY)")
    print(" 9. 토큰 만료 시간 보기")
    print("10. 현재 계좌 잔액($) 확인(RSN)")
    print("11. 현재 계좌 잔액($) 확인(DIY)")
    print("00. 나가기")
    print("----------------------------")
    ch = input("메뉴를 선택하세요 : \033[0m")
    
    if ch == '00' : break
    if ch == '33' : rst = A.test(); A.print_contents(rst)
    if ch == '88' : B.renew_token(['01','02','03']) ; print("토큰을 모두 리뉴얼 했습니다")
    if ch == '1' : rst = B.get_current_price() ; print(rst)
    if ch.startswith('20') : rst = B.get_ohlc(ch) ; print(rst)
    if ch == '3' : 
        rst = B.get_orders_today('0','0') ; 
        A.print_contents(rst)
    if ch == '4' :
        B.change_account('02') 
        rst = B.get_orders_today('0','0') ; 
        A.print_contents(rst)
        B.change_account('01')
    if ch == '5' : 
        rst = B.get_current_balance()
        A.print_contents(rst)
    if ch == '6' : B.change_account('02'); rst = B.get_current_balance() ; B.change_account('01'); print(rst)
    if ch == '7' : 
        rst = B.get_reserved_order(today,code='2')  
        A.print_contents(rst)
    if ch == '8' : 
        B.change_account('02'); rst = B.get_reserved_order(today,code='2'); B.change_account('01');  
        A.print_contents(rst)
    if ch == '9' : 
        rst = A.get_token_duetime() 
        A.print_contents(rst)
    
    if ch == '10' : rst = B.get_money_balance() ; print(rst)
    if ch == '11' : B.change_account('02'); rst = B.get_money_balance() ; B.change_account('01'); print(rst)

