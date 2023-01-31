from myutils.DB import DB
import myutils.my_utils as my
import time,FinanceDataReader as fdr

class SU :

    def __init__(self) :
        self.DB = DB('stocks')
        self.skey, self.appkey = self.DB.exe("SELECT p_data_01,p_data_02 FROM my_keep_data WHERE no=1",many=1,assoc=False)

    def stocks_update(self) :

        today = my.timestamp_to_date(opt=7)
        week_day = my.dayofdate(today)

        if week_day in ['일','월'] :
            message = f"[{today}] {week_day}요일 : Good morning !"
            my.post_slack(self.skey,message)
            return

        self.update_fdr('soxl')
        self.update_fdr('jepq')

        self.DB.close()

        message = f"[{today}] 주가 정보 업데이트를 완료하였습니다"
        my.post_slack(self.skey,message)

    def update_fdr(self,cdx) :

        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add1='{cdx}'")
        b_date = self.DB.get("max(add0)",many=1,assoc=False)
        e_date = my.timestamp_to_date(opt=7)

        df = fdr.DataReader(cdx,start=b_date, end=e_date)
        df['Str_Date'] = df.index.strftime('%Y-%m-%d')

        df['Up']     = 0
        df['Dn']     = 0

        df['Open']  = round(df['Open'],2)
        df['High']  = round(df['High'],2)
        df['Low']   = round(df['Low'],2)
        df['Close'] = round(df['Close'],2)
        df['Change']= round(df['Close'].diff(periods=1)/df['Close'].shift(1),4)

        df = df[['Str_Date','Open','High','Low','Close','Volume','Change','Up','Dn']]
        dflist = df.values.tolist()

        self.DB.wre = f"add0='{b_date}' and add1='{cdx}'"
        one = self.DB.get('add9,add10',many=1,assoc=False)

        dflist[0][7] = int(one[0])
        dflist[0][8] = int(one[1])

        for i in range(1,len(dflist)) :
            dflist[i][7]  = dflist[i-1][7]+1 if dflist[i][4] >= dflist[i-1][4] else 0
            dflist[i][8]  = dflist[i-1][8]+1 if dflist[i][4] <  dflist[i-1][4] else 0

        ohlc = dflist[1:]

        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"
        time_now = my.now_timestamp()
        cdx = cdx.upper()

        for row in ohlc :
            row2 = list(row)
            row2 += [cdx,cdx,'comphys','정용훈',time_now,time_now]
            values = str(row2)[1:-1]
            sql = f"INSERT INTO {self.DB.tbl} ({db_keys}) VALUES({values})"
            self.DB.exe(sql)


my_stocks = SU()
my_stocks.stocks_update()
