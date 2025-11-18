from myutils.DB import DB
import myutils.my_utils as my

class SU :
    def __init__(self) :
        self.DB = DB('stocks')
        self.skey = self.DB.store("slack_key")

    def send_message(self,message) :
        if self.DB.system == "Linux" : my.post_slack(self.skey,message)
        else : print(message)


    
# --------------------------------------------------------------------------------------------------
today = my.kor_loc_date('US/Eastern')[0:10]
weekd = my.dayofdate(today)
A = SU()
chk_holiday = A.DB.one(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
skip = (weekd in ['토','일']) or chk_holiday

if  skip :
    pass
else :
    krw = my.get_usd_krw()
    A.DB.exe(f"UPDATE h_stockHistory_board SET add2={krw[1]} WHERE add0='{today}'")
    A.send_message("환율 업데이트 완료")
    