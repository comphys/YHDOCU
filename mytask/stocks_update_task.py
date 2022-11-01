from myutils.DB import DB
import myutils.my_utils as my
import time,FinanceDataReader as fdr

class SU :

    def __init__(self) :

        self.mydb = DB('stocks')
        self.skey = self.mydb.one("SELECT p_data_01 FROM my_keep_data WHERE no=1")


    def stocks_update(self) :

        today = my.timestamp_to_date(opt=7)
        week_day = my.dayofdate(today)

        if week_day in ['일','월'] :
            message = f"[{today}] {week_day}요일 : Good morning !"
            my.post_slack(message)
            return

        codes = ['SOXX','SOXL','JEPQ','QQQ','TQQQ','JEPI']
        for cdx in codes :
            self.update_fdr(cdx)
            time.sleep(3)

        self.mydb.close()

        message = f"[{today}] 주가 정보 업데이트를 완료하였습니다"
        my.post_slack(self.skey,message)

    def update_fdr(self,cdx) :

        self.mydb.tbl, self.mydb.wre = ('h_stockHistory_board',f"add1='{cdx}'")
        b_date = self.mydb.get("max(add0)",many=1,assoc=False)
        e_date = my.timestamp_to_date(opt=7)

        df = fdr.DataReader(cdx,start=b_date, end=e_date)
        Str_Date    = [x.strftime('%Y-%m-%d') for x in df.index]
        cnt = len(Str_Date)
        df['Str_Date'] = Str_Date
    
        df['Change'] = [0.0]*cnt
        df['Up']     = [0]*cnt
        df['Dn']     = [0]*cnt

        df['Open']  = round(df['Open'],2)
        df['High']  = round(df['High'],2)
        df['Low']   = round(df['Low'],2)
        df['Close'] = round(df['Close'],2)
    
        df.drop('Adj Close',axis=1,inplace=True)
        df = df[['Str_Date','Open','High','Low','Close','Volume','Change','Up','Dn']]
        dflist = df.values.tolist()

        self.mydb.wre = f"add0='{b_date}' and add1='{cdx}'"
        one = self.mydb.get('add9,add10',many=1,assoc=False)

        dflist[0][7] = int(one[0])
        dflist[0][8] = int(one[1])

        for i in range(1,cnt) :
            dflist[i][6]  = round((dflist[i][4] - dflist[i-1][4])/dflist[i-1][4],4)
            dflist[i][7]  = dflist[i-1][7]+1 if dflist[i][4] >= dflist[i-1][4] else 0
            dflist[i][8]  = dflist[i-1][8]+1 if dflist[i][4] <  dflist[i-1][4] else 0

        ohlc = dflist[1:]       

        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"
        time_now = ut.now_timestamp()
        cdx = cdx.upper()

        for row in ohlc :
            row2 = list(row)
            row2 += [cdx,cdx,'comphys','정용훈',time_now,time_now]
            values = str(row2)[1:-1]
            sql = f"INSERT INTO {self.mydb.tbl} ({db_keys}) VALUES({values})"
            self.mydb.exe(sql)


my_stocks = SU()
my_stocks.stocks_update()
