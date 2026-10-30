from datetime import datetime
from zoneinfo import ZoneInfo
import time

from xload import Control
import system.core.my_utils as my
class myClass(Control) :

    def _auto(self) :
        self.DB = self.db('stocks',path=self._root+'/')
        self.skey = self.DB.store("slack_key")
        self.title= '주식 로그기록 보고'

    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")  
        with open(self._root+"/logs/xtask.log","a",encoding="utf-8") as f:
            f.write(f"<span class='who-time'>{hour_now} :</span> {str}\n")

    def log_update(self,day) :

        OHLC = self.load_app_lib('ohlc')
        OHLC.stocks_update('soxl',day)
        time.sleep(1)
        for log in ['rsnLog','logDIY','logDIY2','logLTH','log315_ljk'] :
            log = self.load_bajax(log,'update_log')
            log()
        self.send_message(day+" Updated")
        


# today 는 증권거래소의 시각(미국 뉴욕)을 기준으로 하고 있다. 날자가 변경되기 전에 실행시켜야 한다. 국내시간기준 오후1시(섬머타임 기간), 오후2시 이전에 실행되어야 함
LOG = myClass()

last_date = LOG.DB.last_date('h_stockHistory_board')
today_time = my.kor_loc_date('US/Eastern')
today = today_time[0:10]
hour  = int(today_time[11:13])
weekd = my.dayofdate(today)

# 증시 휴장일 체크하기
ck_holiday = LOG.DB.one(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday if ck_holiday else ''

skip = ''
if weekd in ['토','일'] : skip = f"쉬는날 입니다."
if is_holiday : skip = is_holiday
if today <= last_date : skip = "이전 날자입니다."
if int(hour) < 18 : skip = "시간을 확인해 주세요"

if  skip :
    LOG.send_message(skip)

else :
    LOG.log_update(today)
