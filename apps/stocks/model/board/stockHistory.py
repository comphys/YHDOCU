from system.core.load import Model
import system.core.my_utils as my
import time

class Ajax(Model) :

    def update_stock(self) :

        last_date = self.DB.last_date('h_stockHistory_board')
        next_date = my.next_stock_day(last_date,self.DB)

        OHLC = self.load_app_lib('ohlc')
        OHLC.stocks_update('soxl',next_date)
        time.sleep(1)
        for log in ['rsnLog','logDIY','logDIY2','logLTH','log315_ljk'] :
            log = self.load_bajax(log,'update_log')
            log()
        return self.SYS.json("OK")

        # ----------------------------------------------------------------------    


    def update_simple(self) :

        sd = self.D['post']['s_d']
        sc = self.D['post']['s_c']
        sk = self.D['post']['s_k'].replace(',','')

        ld = self.DB.oneline(f"SELECT add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2 FROM h_stockHistory_board ORDER BY rowid desc LIMIT 1")
        ld = list(ld)
        
        ld[6] = round(( float(sc)-float(ld[4]) ) / float(ld[4]) *100,2)
        ld[7] = int(ld[7]) + 1 if float(sc) >= float(ld[4]) else 0
        ld[8] = int(ld[8]) + 1 if float(sc) <  float(ld[4]) else 0

        ld[1]  = ld[2] = ld[3] = '0.0'
        ld[4]  = sc
        ld[0]  = sd
        ld[10] = sk

        time_now = my.now_timestamp()
        ld += ['comphys','정용훈',time_now,time_now]
        values = str(ld)[1:-1]
        sql = f"INSERT INTO h_stockHistory_board (add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate) VALUES({values})"
        self.DB.exe(sql)

        return self.SYS.json("OK")

