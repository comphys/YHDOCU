from system.core.load import Control
from flask import session
import FinanceDataReader as fdr
import system.core.my_utils as ut

class Stock_update(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')

    def update(self) :

        code = self.parm[0]
        if code == 'NONE' : 
            self.set_message("종목 코드가 선택되지 않았습니다")
            return self.moveto('board/list/stockHistory')

        self.DB.tbl, self.DB.wre = ("h_user_list",f"no={session['N_NO']}")
        USER = self.DB.get("*",many=1, assoc=True)

        self.DB.tbl = 'h_stockHistory_board'
        self.DB.wre = f"add1='{code}'"

        stocks_end = self.DB.get("max(add0)",many=1,assoc=False) 

        sql = f"DELETE FROM {self.DB.tbl} WHERE add0 = '{stocks_end}'"
        self.DB.exe(sql)

        df = fdr.DataReader(code,start=stocks_end)
        df = df.astype({'Volume':'int'})
        data_field  = list(df.columns)
        data_field.insert(0,'Date')
        data_index  = [x.strftime('%Y-%m-%d') for x in df.index]
        data_db_in  = list(zip(data_index, df['Close'], df['Open'], df['High'], df['Low'], df['Volume'], df['Change']))
        
        db_keys = "add0,add3,add4,add5,add6,add7,add8,add1,add2,uid,uname,wdate,mdate"
        for row in data_db_in :
            row2 = list(row)
            row2.append(code)
            row2.append(code)
            row2.append(USER['uid'])
            row2.append(USER['uname'])
            row2.append(ut.now_timestamp())
            row2.append(ut.now_timestamp())

            values = str(row2)[1:-1]

            sql = f"INSERT INTO {self.DB.tbl} ({db_keys}) VALUES({values})"
            self.DB.exe(sql)
        
        return self.moveto('board/list/stockHistory/csh=on')


        #  df = fdr.DataReader(code,start=None, end='2010-02-26')
