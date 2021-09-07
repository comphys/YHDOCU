from system.core.load import Control
import FinanceDataReader as fdr
import system.core.my_utils as ut

class Stockupdate(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')

    def update(self) :

        code = "SOXL"
        self.DB.tbl = 'h_stockHistory_board'
        self.DB.wre = f"add1='{code}'"

        stocks_bgn = self.DB.get("min(add0)",many=1,assoc=False)
        stocks_end = self.DB.get("max(add0)",many=1,assoc=False) 

        if stocks_bgn == None :

            df = fdr.DataReader(code)
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
                row2.append('comphys')
                row2.append('정용훈')
                row2.append(ut.now_timestamp())
                row2.append(ut.now_timestamp())

                values = str(row2)[1:-1]

                sql = f"INSERT INTO {self.DB.tbl} ({db_keys}) VALUES({values})"
                self.DB.exe(sql)
        
        return self.moveto('board/list/stockHistory')


        #  df = fdr.DataReader(code,start=None, end='2010-02-26')
