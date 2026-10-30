from datetime import datetime
from zoneinfo import ZoneInfo
import time

from xload import Control
import system.core.my_utils as my
class myClass(Control) :

    def _auto(self) :
        self.DB = self.db('stocks',path=self._root+'/')
        self.skey = self.DB.store("slack_key")
        self.title= '주식주문 검증 보고'

        self.API = self.load_app_lib('meritz')
        self.API.maca = self._macA  

    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")  
        with open(self._root+"/logs/xtask.log","a",encoding="utf-8") as f:
            f.write(f"<span class='who-time'>{hour_now} :</span> {str}\n")

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
A = myClass()

today = my.kor_loc_date('US/Eastern')
weekd = my.dayofdate(today[0:10])
chk_date = today[0:10]
chk_time = today[11:16]
# A.today 는 미국 현지 시간을 기준으로 한다. 
# 이 파일의 실행은 한국시간으로 22:30 또는 23:30분 이후여야 한다.  

# # 증시 휴장일 체크하기
ck_holiday = A.DB.exe(f"SELECT description FROM parameters WHERE val='{chk_date}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday[0][0] if ck_holiday else ''

skip = ''
if weekd in ['토','일'] : skip = f"{weekd}요일 입니다"
if is_holiday : skip = is_holiday
if chk_time <  '09:30' or chk_time > '16:00' : skip = '정규장 시간이 아닙니다.'
if chk_date > '2027-09-30' : skip = 'API 키 갱신이 필요합니다'

if  skip :
    A.send_message(skip)

else :

    A.API.change_account('01')
    rst1 = A.verify_rsn_order()
    A.send_message(rst1[1]) 
    time.sleep(1)

    A.API.change_account('02')
    rst2 = A.verify_diy_order('DIY','logDIY')
    A.send_message(rst2[1])
    time.sleep(1)

    A.API.change_account('03')
    rst3 = A.verify_diy_order('POC','logDIY2')
    A.send_message(rst3[1])
    time.sleep(1)

    A.API.change_account('lth')
    rst4 = A.verify_diy_order('LTH','logLTH')
    A.send_message(rst4[1])
    time.sleep(1)