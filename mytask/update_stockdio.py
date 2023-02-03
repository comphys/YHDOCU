from myutils.DB import DB
import myutils.my_utils as my

class SU :
    def __init__(self) :
        self.DB = DB('stocks')
        self.appkey = self.DB.exe("SELECT p_data_02 FROM my_keep_data WHERE no=1",many=1,assoc=False)[0]
        
    def stocks_update(self,cdx) :
        cdx = cdx.upper()
        time_now = my.now_timestamp()
        
        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add1='{cdx}'")
        b_date = self.DB.get_one("max(add0)")
        
        self.DB.wre = f"add0='{b_date}' and add1='{cdx}'"
        one = self.DB.get('add0,add4,add5,add6,add3,add7,add8,add9,add10',many=1,assoc=False)
        the_first_data = [one[0],float(one[1]),float(one[2]),float(one[3]),float(one[4]),int(one[5]),float(one[6]),int(one[7]),int(one[8])]
        
        ohlc = my.get_stock_data(self.appkey,cdx,b_date,'')
        if not ohlc : return
        
        ohlc[0] = the_first_data
        
        for i in range(1,len(ohlc)) :
            ohlc[i][6]  = round((ohlc[i][4] - ohlc[i-1][4])/ohlc[i-1][4],4)
            ohlc[i][7]  = ohlc[i-1][7]+1 if ohlc[i][4] >= ohlc[i-1][4] else 0
            ohlc[i][8]  = ohlc[i-1][8]+1 if ohlc[i][4] <  ohlc[i-1][4] else 0

        rst3 = ohlc[1:]
        
        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"

        for row in rst3 :
            row2 = list(row)
            row2 += [cdx,cdx,'comphys','정용훈',time_now,time_now]
            values = str(row2)[1:-1]
            sql = f"INSERT INTO {self.DB.tbl} ({db_keys}) VALUES({values})"
            self.DB.exe(sql)
            
        print(f"{b_date} 이후 {cdx} 주식 정보가 업데이트 되었습니다")
        
        
A = SU()
A.stocks_update('soxl')
A.stocks_update('jepq')