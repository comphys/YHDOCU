from myutils.DB import DB
import myutils.my_utils as my
import time

class SU :

    def __init__(self) :

        self.mydb = DB('stocks')
        self.skey, self.appkey = self.mydb.exe("SELECT p_data_01,p_data_02 FROM my_keep_data WHERE no=1",many=1,assoc=False)

    def stocks_update(self) :

        today = my.timestamp_to_date(opt=7)
        week_day = my.dayofdate(today)

        if week_day in ['일','월'] :
            message = f"[{today}] {week_day}요일 : Good morning !"
            my.post_slack(message)
            return

        codes = ['SOXX','SOXL','JEPQ','QQQ','TQQQ','JEPI']
        for cdx in codes :
            self.update_stock(cdx)
            time.sleep(6)

        self.mydb.close()

        message = f"[{today}] 주가 정보 업데이트를 완료하였습니다"
        my.post_slack(self.skey,message)

    def update_stock(self,cdx) :

        self.mydb.tbl, self.mydb.wre = ('h_stockHistory_board',f"add1='{cdx}'")
        b_date = self.mydb.get("max(add0)",many=1,assoc=False)
        e_date = my.timestamp_to_date(opt=7)
        if not b_date : b_date = '2015-01-01'

        the_next_day = my.dayofdate(b_date,delta=1)[0]
        self.mydb.wre = f"add0='{b_date}' and add1='{cdx}'"
        one = self.mydb.get('add0,add4,add5,add6,add3,add7,add8,add9,add10',many=1,assoc=False)
        the_first_data = [one[0],float(one[1]),float(one[2]),float(one[3]),float(one[4]),int(one[5]),float(one[6]),int(one[7]),int(one[8])]

        ohlc = my.get_stock_data(self.appkey,cdx,the_next_day,e_date)
        if not ohlc : return
        ohlc.insert(0,the_first_data)

        for i in range(1,len(ohlc)) :
            ohlc[i][6]  = round((ohlc[i][4] - ohlc[i-1][4])/ohlc[i-1][4],4)
            ohlc[i][7]  = ohlc[i-1][7]+1 if ohlc[i][4] >= ohlc[i-1][4] else 0
            ohlc[i][8]  = ohlc[i-1][8]+1 if ohlc[i][4] <  ohlc[i-1][4] else 0

        rst3 = ohlc[1:]

        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"
        time_now = my.now_timestamp()

        for row in rst3 :
            row2 = list(row)
            row2 += [cdx,cdx,'comphys','정용훈',time_now,time_now]
            values = str(row2)[1:-1]
            sql = f"INSERT INTO {self.mydb.tbl} ({db_keys}) VALUES({values})"
            self.mydb.exe(sql)

my_stocks = SU()
my_stocks.stocks_update()


