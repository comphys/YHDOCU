from system.core.load import Control
from flask import session
import FinanceDataReader as fdr
import time,system.core.my_utils as ut

class Stock_update(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')
        self.app_key = self.DB.one('SELECT p_data_02 FROM my_keep_data WHERE no=1')

    def update(self) :

        self.DB.tbl, self.DB.wre = ("h_user_list",f"no={session['N_NO']}")
        USER = self.DB.get("*",many=1, assoc=True)

        opt = self.parm[0]
        codes = ['SOXL','JEPQ']
        
        for cdx in codes :
            if opt == 'stockdio' :
                self.update_stockdio(cdx,USER)
                time.sleep(5)
            else :
                self.update_fdr(cdx,USER)
                time.sleep(2)
            
        self.set_message("종목 업데이트를 완료하였습니다")
        return self.moveto('board/list/stockHistory/csh=on')

    def delete(self) :

        code = self.parm[0]
        if not code : return
        self.DB.exe(f"DELETE FROM h_stockHistory_board WHERE add1='{code}'")
        self.set_message("종목 삭제를 완료하였습니다")
        return self.moveto('board/list/stockHistory')
        

    def update_stockdio(self,cdx,USER) :
        
        app_key = self.DB.one("SELECT p_data_02 FROM my_keep_data WHERE no=1")
        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add1='{cdx}'")
        b_date = self.DB.get("max(add0)",many=1,assoc=False) 
        e_date = ut.timestamp_to_date(opt=7)
        if not b_date : b_date = '2015-01-01'

        the_next_day = ut.dayofdate(b_date,delta=1)[0]
        self.DB.wre = f"add0='{b_date}' and add1='{cdx}'"
        one = self.DB.get('add0,add4,add5,add6,add3,add7,add8,add9,add10',many=1,assoc=False)
        the_first_data = [one[0],float(one[1]),float(one[2]),float(one[3]),float(one[4]),int(one[5]),float(one[6]),int(one[7]),int(one[8])]

        ohlc = ut.get_stock_data(app_key,cdx,the_next_day,e_date)
        if not ohlc : return
        ohlc.insert(0,the_first_data)

        for i in range(1,len(ohlc)) :
            ohlc[i][6]  = round((ohlc[i][4] - ohlc[i-1][4])/ohlc[i-1][4],4)
            ohlc[i][7]  = ohlc[i-1][7]+1 if ohlc[i][4] >= ohlc[i-1][4] else 0
            ohlc[i][8]  = ohlc[i-1][8]+1 if ohlc[i][4] <  ohlc[i-1][4] else 0

        rst3 = ohlc[1:]

        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"
        time_now = ut.now_timestamp()

        for row in rst3 :
            row2 = list(row)
            row2 += [cdx,cdx,USER['uid'],USER['uname'],time_now,time_now]
            values = str(row2)[1:-1]
            sql = f"INSERT INTO {self.DB.tbl} ({db_keys}) VALUES({values})"
            self.DB.exe(sql)

    def update_fdr(self,cdx,USER) :

        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add1='{cdx}'")
        b_date = self.DB.get("max(add0)",many=1,assoc=False)
        e_date = ut.timestamp_to_date(opt=7)

        df = fdr.DataReader(cdx,start=b_date, end=e_date)
        Str_Date    = [x.strftime('%Y-%m-%d') for x in df.index]

        df['Str_Date'] = Str_Date

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
        time_now = ut.now_timestamp()
        
        for row in ohlc :
            row2 = list(row)    
            row2 += [cdx,cdx,USER['uid'],USER['uname'],time_now,time_now]
            values = str(row2)[1:-1]
            sql = f"INSERT INTO {self.DB.tbl} ({db_keys}) VALUES({values})"
            self.DB.exe(sql)        


    def update_stock(self) :
        cdx = self.parm[0]
        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add1='{cdx}'")
        b_date = '2016-01-01'
        e_date = ut.timestamp_to_date(opt=7)

        df = fdr.DataReader(cdx,start=b_date, end=e_date)
        Str_Date    = [x.strftime('%Y-%m-%d') for x in df.index]

        df['Str_Date'] = Str_Date

        df['Up']     = 0
        df['Dn']     = 0

        df['Open']  = round(df['Open'],2)
        df['High']  = round(df['High'],2)
        df['Low']   = round(df['Low'],2)
        df['Close'] = round(df['Close'],2)
        df['Change']= round(df['Close'].diff(periods=1)/df['Close'].shift(1),4)

        df = df[['Str_Date','Open','High','Low','Close','Volume','Change','Up','Dn']]
        dflist = df.values.tolist()

        dflist[0][7] = 0
        dflist[0][8] = 0

        for i in range(1,len(dflist)) :
            dflist[i][7]  = dflist[i-1][7]+1 if dflist[i][4] >= dflist[i-1][4] else 0
            dflist[i][8]  = dflist[i-1][8]+1 if dflist[i][4] <  dflist[i-1][4] else 0

        ohlc = dflist[1:]

        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"
        time_now = ut.now_timestamp()
        
        for row in ohlc :
            row2 = list(row)    
            row2 += [cdx,cdx,'comphys','정용훈',time_now,time_now]
            values = str(row2)[1:-1]
            sql = f"INSERT INTO {self.DB.tbl} ({db_keys}) VALUES({values})"
            self.DB.exe(sql) 
        
        return self.moveto('board/list/stockHistory/csh=on')