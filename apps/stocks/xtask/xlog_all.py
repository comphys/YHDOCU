import sys, platform

sysos = platform.system()
if    sysos == 'Windows' :  rootpath = '/YHDOCU'  
elif  sysos == 'Linux'   :  rootpath = '/home/comphys/YHDOCU'
elif  sysos == 'Android' :  rootpath = '/data/data/com.termux/files/home/YHDOCU'
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

    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")  
        with open(rootpath+"/logs/xtask.log","a",encoding="utf-8") as f:
            f.write(f"<span class='who-time'>{hour_now} :</span> {str}\n")

    def send_message(self,message,ch='주식') :
        client = WebClient(token=self.skey)
        try:
            client.chat_postMessage(channel= ch, text= message)
            return True
        except SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]
            self.log(f"slack error : {e.response['error']}")

    def log_update(self) :

        self.D['lst_sday'] = my.last_stock_day(self.DB)
        self.D['lst_ohlc'] = self.DB.last_date('h_stockHistory_board')
        if  self.D['lst_sday'] != self.D['lst_ohlc'] : 
            OHLC = self.load_app_lib('ohlc')
            the_next_day = my.next_stock_day(self.D['lst_ohlc'],self.DB)[0]
            if OHLC.stocks_update('soxl',the_next_day) : self.D['lst_ohlc'] = self.DB.last_date('h_stockHistory_board')
            # time.sleep(10)
            RSN  =  self.load_bajax('rsnLog','update_log'); RSN()
            time.sleep(2)
            DIY  =  self.load_bajax('logDIY','update_log'); DIY()
            time.sleep(2)
            N315 =  self.load_bajax('log315_ljk','update_log'); N315()
            self.send_message(the_next_day+" Updated")
        else :
            self.send_message("nothing to update")


today = my.kor_loc_date('US/Eastern')[0:10]
weekd = my.dayofdate(today)
LOG = yourClass()

# 증시 휴장일 체크하기
ck_holiday = LOG.DB.exe(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday[0][0] if ck_holiday else ''

skip = ''
if weekd in ['토','일'] : skip = f"{weekd}요일 입니다"
elif is_holiday : skip = is_holiday

if  skip :
    LOG.send_message(skip)
    pass

else :
    LOG.log_update()