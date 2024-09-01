from myutils.DB import DB
import myutils.my_utils as my

class SU :
    def __init__(self) :
        self.DB = DB('stocks')
        self.skey = self.DB.store("slack_key")

    def send_message(self,message) :
        if self.DB.system == "Linux" : my.post_slack(self.skey,message)
        else : print(message)

    def stocks_update(self,cdx,today) :
        cdx = cdx.upper()
        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add1='{cdx}'")
        b_date = self.DB.get_one("max(add0)")
        
        self.DB.wre = f"add0='{b_date}' and add1='{cdx}'"
        # add0 = date / add1 = code / add2 = alias / add4 = open / add5 = high / add6 = low / add7 = volume / add8 = change / add9 = up / add10 = dn
        one = self.DB.get('add0,add4,add5,add6,add3,add7,add8,add9,add10',many=1,assoc=False)
        the_first_data = [one[0],float(one[1]),float(one[2]),float(one[3]),float(one[4]),int(one[5]),float(one[6]),int(one[7]),int(one[8])]
        app_key = self.DB.store("tiingo")
  
        ohlc = my.get_tiingo_price(app_key,cdx,b_date,today)

        if  not ohlc : 
            self.send_message("No data updated")
            return
        
        ohlc[0] = the_first_data
            
        for i in range(1,len(ohlc)) :
            ohlc[i][6]  = round((ohlc[i][4] - ohlc[i-1][4])/ohlc[i-1][4]*100,2)
            ohlc[i][7]  = ohlc[i-1][7]+1 if ohlc[i][4] >= ohlc[i-1][4] else 0
            ohlc[i][8]  = ohlc[i-1][8]+1 if ohlc[i][4] <  ohlc[i-1][4] else 0
            
        rst3 = ohlc[1:]

        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"
        time_now = my.now_timestamp()

        for row in rst3 :
            row2 = list(row)
            row2 += [cdx,cdx,'comphys','정용훈',time_now,time_now]
            values = str(row2)[1:-1]
            sql = f"INSERT INTO {self.DB.tbl} ({db_keys}) VALUES({values})"
            self.DB.exe(sql)

        lday = rst3[-1][0]
        self.send_message(f"{lday} 주가 업데이트 완료")


    def forex_update(self) :
        getdate, usdkrw = my.get_usd_krw()
        w_time = my.timestamp_to_date()
        qry = f"INSERT INTO usd_krw (date,usd_krw,wtime) VALUES('{getdate}','{usdkrw}','{w_time}')"
        self.DB.exe(qry)


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
    A.stocks_update('soxl',today)
    A.forex_update()








