from system.core.load import Control
from flask import session
from datetime import datetime
import FinanceDataReader as fdr
import system.core.my_utils as ut

class Stock_update(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')

    def update(self) :

        self.DB.tbl, self.DB.wre = ("h_user_list",f"no={session['N_NO']}")
        USER = self.DB.get("*",many=1, assoc=True)

        code = self.parm[0]
        if code == 'NONE' : 
            now = int(datetime.now().timestamp())
            old = str(now - 3600*24*7)
            self.DB.tbl, self.DB.wre = ("h_stockHistory_board",f"wdate > '{old}'")
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


    def update_stock(self,cdx,USER) :

        self.DB.tbl = 'h_stockHistory_board'
        self.DB.wre = f"add1='{cdx}'"

        stocks_end = self.DB.get("max(add0)",many=1,assoc=False) 

        sql = f"DELETE FROM {self.DB.tbl} WHERE add0 = '{stocks_end}' AND add1='{cdx}'"
        self.DB.exe(sql)

        df = fdr.DataReader(cdx,start=stocks_end)
        df = df.astype({'Volume':'int'})
        data_field  = list(df.columns)
        data_field.insert(0,'Date')
        data_index  = [x.strftime('%Y-%m-%d') for x in df.index]
        data_db_in  = list(zip(data_index, df['Close'], df['Open'], df['High'], df['Low'], df['Volume'], df['Change']))
        
        db_keys = "add0,add3,add4,add5,add6,add7,add8,add1,add2,uid,uname,wdate,mdate"
        time_now = ut.now_timestamp()
        
        for row in data_db_in :
            row2 = list(row)
            row2.append(cdx)
            row2.append(cdx)
            row2.append(USER['uid'])
            row2.append(USER['uname'])
            row2.append(time_now)
            row2.append(time_now)

            values = str(row2)[1:-1]

            sql = f"INSERT INTO {self.DB.tbl} ({db_keys}) VALUES({values})"
            self.DB.exe(sql)
        
        #  df = fdr.DataReader(code,start=None, end='2010-02-26')
