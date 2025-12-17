from system.core.load import Model
import system.core.my_utils as my

class Ajax(Model) :


    def update_stock(self) :

        stockLIB = self.SYS.load_app_lib('stock')
        usdkrw = stockLIB.get_usd_krw()[1]

        cdx = 'SOXL'
        
        app_key = self.DB.store("tiingo")
        today = my.kor_loc_date('US/Eastern')[0:10]
        b_date = self.DB.last_date("h_stockHistory_board") 
        if not b_date : b_date = '2015-01-01'
        
        # add4 : Open, add5 : High, add6 : Low, add3 : Close, add7 : Vol, add8 : Change, add9 : Up, add10 : Dn
        one = self.DB.oneline(f"SELECT add0,add4,add5,add6,add3,add7,add8,add9,add10 FROM h_stockHistory_board WHERE add0='{b_date}' and add1='{cdx}'") 

        the_first_data = [one[0],float(one[1]),float(one[2]),float(one[3]),float(one[4]),int(one[5]),float(one[6]),int(one[7]),int(one[8])]
        
        ohlc = stockLIB.get_tiingo_price(app_key,cdx,b_date,today)

        if not ohlc : return self.SYS.json("tiingo server error")

        ohlc[0]= the_first_data

        for i in range(1,len(ohlc)) :
            ohlc[i][6]  = round((ohlc[i][4] - ohlc[i-1][4])/ohlc[i-1][4]*100,2)
            ohlc[i][7]  = ohlc[i-1][7]+1 if ohlc[i][4] >= ohlc[i-1][4] else 0
            ohlc[i][8]  = ohlc[i-1][8]+1 if ohlc[i][4] <  ohlc[i-1][4] else 0

        rst3 = ohlc[1:]

        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"
        time_now = my.now_timestamp()

        for row in rst3 :
            row2 = list(row)
            row2 += [cdx,usdkrw,'comphys','정용훈',time_now,time_now]
            values = str(row2)[1:-1]
            sql = f"INSERT INTO h_stockHistory_board ({db_keys}) VALUES({values})"
            self.DB.exe(sql)
            return self.SYS.json("OK")
        
    def delete(self) :

        code = self.parm[0]
        if not code : return
        self.DB.exe(f"DELETE FROM h_stockHistory_board WHERE add1='{code}'")
