from myutils.DB import DB
import myutils.my_utils as my

class SU :
    def __init__(self) :
        self.DB = DB('stocks')
        self.skey = self.DB.store("slack_key")

    def send_message(self,message) :
        if self.DB.system == "Linux" : my.post_slack(self.skey,message)
        else : print(message)


    def forex_update(self) :
        krw = my.get_usd_krw()
        self.DB.exe(f"UPDATE h_stockHistory_board SET add2={krw[1]} WHERE add0='{krw[0]}'")
        self.send_message(f"{krw[0]}일 환율 업데이트 완료")
        
    
# --------------------------------------------------------------------------------------------------
today = my.kor_loc_date('US/Eastern')[0:10]
weekd = my.dayofdate(today)
A = SU()
chk_holiday = A.DB.exe(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
chk_off = chk_holiday[0][0] if chk_holiday else ''

skip = (weekd in ['토','일']) or chk_off

if  skip :
    pass
else :
    krw = A.forex_update()
    