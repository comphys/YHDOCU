from myutils.DB import DB
import myutils.my_utils as my
import FinanceDataReader as fdr

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

        old = my.dayofdate(today,delta=-10)[0]
        qry = f"SELECT distinct add1 FROM h_stockHistory_board WHERE add1 > '{old}'"
        codes = self.mydb.exe(qry)
        codes = [x[0] for x in codes]
        for cdx in codes : self.update_stock(cdx)

        self.mydb.close()

        message = f"[{today}] 주가 정보 업데이트를 완료하였습니다"
        # my.post_slack(self.skey,message)

    def update_stock(self,cdx) :

        self.mydb.tbl, self.mydb.wre = ('h_stockHistory_board',f"add1='{cdx}'")
        b_date = self.mydb.get("max(add0)",many=1,assoc=False)
        e_date = my.timestamp_to_date(opt=7)
        
        self.mydb.wre = f"add0 ='{b_date}' and add1='{cdx}'"
        old_data = self.mydb.get('add9,add10',many=1,assoc=False)

        df = fdr.DataReader(cdx,start=b_date, end=e_date)
        df = df.astype({'Volume':'int'})

        Date    = [x.strftime('%Y-%m-%d') for x in df.index]
        Change  = [round(x,3) for x in df['Change']]

        cnt = len(Date)
        Up  = [0]*cnt ; Up[0] = int(old_data[0])
        Dn  = [0]*cnt ; Dn[0] = int(old_data[1])

        for i in range(1,cnt) :
            if df['Close'][i] <  df['Close'][i-1] : Dn[i] = Dn[i-1] + 1 
            if df['Close'][i] >= df['Close'][i-1] : Up[i] = Up[i-1] + 1 

        ohlc = list(zip(Date,df['Open'],df['High'],df['Low'],df['Close'],df['Volume'],Change,Up,Dn))

        self.mydb.exe(f"DELETE FROM {self.mydb.tbl} WHERE add0 >= '{b_date}' AND add1='{cdx}'")

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


