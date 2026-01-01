from myutils.DB import DB
import myutils.my_utils as my

class SU :
    def __init__(self) :
        self.DB = DB('stocks')
        self.skey = self.DB.store("slack_key")
        self.tkey = self.DB.store("tiingo")

    def send_message(self,message) :
        if self.DB.system == "Linux" : my.post_slack(self.skey,message)
        else : print(message)

    def stocks_update(self,cdx,today) :
        cdx = cdx.upper()
        b_date = self.DB.one(f"SELECT max(add0) FROM h_stockHistory_board WHERE add1='{cdx}'")
        
        # # add0 = date / add1 = code / add2 = alias / add4 = open / add5 = high / add6 = low / add7 = volume / add8 = change / add9 = up / add10 = dn
        one = self.DB.oneline(f"SELECT add0,add4,add5,add6,add3,add7,add8,add9,add10 FROM h_stockHistory_board WHERE add0='{b_date}' and add1='{cdx}'")
        the_first_data = [one[0],float(one[1]),float(one[2]),float(one[3]),float(one[4]),int(one[5]),float(one[6]),int(one[7]),int(one[8])]
 
        ohlc = my.get_tiingo_price(self.tkey,cdx,b_date,today)

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
        
        # 환율 업데이트
        krw = my.get_usd_krw()

        if rst3 :
            for row in rst3 :
                row2 = list(row)
                row2 += [cdx,'','comphys','정용훈',time_now,time_now]
                values = str(row2)[1:-1]
                sql = f"INSERT INTO h_stockHistory_board ({db_keys}) VALUES({values})"
                self.DB.exe(sql)

            lday = rst3[-1][0]
            self.DB.exe(f"UPDATE h_stockHistory_board SET add2={krw[1]} WHERE add0='{lday}'")
            self.send_message(f"{lday}일 주가&환율 업데이트")
        else :
            self.send_message(f"No data to update...")

    def stock_holiday(self,today) :
        
        weekd = my.dayofdate(today)

        if weekd in ['토','일'] : return f"{weekd}요일 : Good morning !"
        chk = self.DB.one(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")

        return "Today is a holiday !" if chk else None

# --------------------------------------------------------------------------------------------------
A = SU()
today = my.kor_loc_date('US/Eastern')[0:10]
skip = A.stock_holiday(today)

if  skip : 
    A.send_message(skip)

else :
    A.stocks_update('soxl',today)

