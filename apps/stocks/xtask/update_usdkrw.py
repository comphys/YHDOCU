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
        usdkrw = my.get_usd_krw()
        # w_time = my.timestamp_to_date()
        # qry = f"INSERT INTO usd_krw (date,usd_krw,wtime) VALUES('{getdate}','{usdkrw}','{w_time}')"
        # self.DB.exe(qry)
        return usdkrw


# --------------------------------------------------------------------------------------------------
today = my.kor_loc_date('US/Eastern')[0:10]
weekd = my.dayofdate(today)
A = SU()
chk_holiday = A.DB.exe(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
chk_off = chk_holiday[0][0] if chk_holiday else ''

skip = (weekd in ['토','일']) or chk_off

if  skip :
    message = f"Today is a holiday !" if chk_off else f"[{today}] {weekd}요일 : Good morning !"
    A.send_message(message)

else :
    krw = A.forex_update()
    A.DB.exe(f"UPDATE h_stockHistory_board SET add2={krw[1]} WHERE add0='{krw[0]}'")
    A.send_message(f"{krw[0]}일 환율 업데이트 완료")

