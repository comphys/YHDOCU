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

        message = f"[{today}] 주가 정보 업데이트를 완료하였습니다"
        my.post_slack(self.skey,message)

    def update_stock(self,cdx) :

        self.mydb.tbl, self.mydb.wre = ('h_stockHistory_board',f"add1='{cdx}'")
        b_date = self.mydb.get("max(add0)",many=1,assoc=False)
        e_date = my.timestamp_to_date(opt=7)

        if not b_date : b_date = '2015-01-01'
        b_date = my.dayofdate(b_date,delta=1)[0]
        if e_date < b_date : return

        data = my.get_stock_data(self.appkey,cdx,b_date,e_date)
        ohlc = data['data']
        if not ohlc : return

        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"
        time_now = my.now_timestamp()
        cdx = cdx.upper()
        for row in ohlc :
            row2 = list(row)
            row2 += [cdx,cdx,'comphys','정용훈',time_now,time_now]
            values = str(row2)[1:-1]
            sql = f"INSERT INTO {self.mydb.tbl} ({db_keys}) VALUES({values})"
            self.mydb.exe(sql)


my_stocks = SU()
my_stocks.stocks_update()