from system.core.load import Control
from flask import session
from datetime import datetime
import FinanceDataReader as fdr
import system.core.my_utils as ut

class Stock_update(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')
        self.app_key = self.DB.one('SELECT p_data_02 FROM my_keep_data WHERE no=1')

    def update(self) :

        self.DB.tbl, self.DB.wre = ("h_user_list",f"no={session['N_NO']}")
        USER = self.DB.get("*",many=1, assoc=True)

        code = self.parm[0]
        if code == 'NONE' : 
            today = ut.timestamp_to_date(opt=7)
            old_day = ut.dayofdate(today,delta=-7)[0]

            self.DB.tbl, self.DB.wre = ("h_stockHistory_board",f"add1 > '{old_day}'")
            codes = self.DB.get("distinct add1",assoc=False)

            for cdx in codes :
                self.update_stock(cdx,USER)

        else :  self.update_stock(code,USER)
            
        self.set_message("종목 업데이트를 완료하였습니다")
        return self.moveto('board/list/stockHistory/csh=on')

    def delete(self) :

        code = self.parm[0]
        if not code : return
        self.DB.exe(f"DELETE FROM h_stockHistory_board WHERE add1='{code}'")
        self.set_message("종목 삭제를 완료하였습니다")
        return self.moveto('board/list/stockHistory')

    def update_stock2(self,cdx,USER) :

        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add1='{cdx}'")
        start_b = self.DB.get("max(add0)",many=1,assoc=False) 
        start_e = ut.timestamp_to_date(opt=7)

        if not start_b : start_b = '2015-01-01'

        self.DB.exe(f"DELETE FROM {self.DB.tbl} WHERE add0 >= '{start_b}' AND add1='{cdx}'")

        data = ut.get_stock_data(cdx,start_b,start_e)

        ohlc = data['data']

        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"
        time_now = ut.now_timestamp()
        cdx = cdx.upper()
        for row in ohlc :
            row2 = list(row)
            row2 += [cdx,cdx,USER['uid'],USER['uname'],time_now,time_now]
            values = str(row2)[1:-1]
            sql = f"INSERT INTO {self.DB.tbl} ({db_keys}) VALUES({values})"
            self.DB.exe(sql)

    def update_stock(self,cdx,USER) :

        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add1='{cdx}'")
        b_date = self.DB.get("max(add0)",many=1,assoc=False)
        e_date = ut.timestamp_to_date(opt=7)

        df = fdr.DataReader(cdx,start=b_date, end=e_date)
        df = df.astype({'Volume':'int'})

        Date    = [x.strftime('%Y-%m-%d') for x in df.index]
        Change  = [round(x,3) for x in df['Change']]

        cnt = len(Date)
        Up  = [0]*cnt
        Dn  = [0]*cnt

        for i in range(1,cnt) :
            if df['Close'][i] <  df['Close'][i-1] : Dn[i] = Dn[i-1] + 1 
            if df['Close'][i] >= df['Close'][i-1] : Up[i] = Up[i-1] + 1 

        ohlc = list(zip(Date,df['Open'],df['High'],df['Low'],df['Close'],df['Volume'],Change,Up,Dn))

        self.DB.exe(f"DELETE FROM {self.DB.tbl} WHERE add0 >= '{b_date}' AND add1='{cdx}'")

        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"
        time_now = ut.now_timestamp()
        cdx = cdx.upper()
        
        for row in ohlc :
            row2 = list(row)    
            row2 += [cdx,cdx,'comphys','정용훈',time_now,time_now]
            values = str(row2)[1:-1]
            sql = f"INSERT INTO {self.DB.tbl} ({db_keys}) VALUES({values})"
            self.DB.exe(sql)        
