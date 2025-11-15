from system.core.load import Control
from flask import session
import system.core.my_utils as my

class Stock_update(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')
        self.stock = self.load_app_lib('stock')

    def send_message(self,message) :
        if self.DB.system == "Linux" : my.post_slack(self.skey,message)
        else : print(message)

    def update_stock(self) :

        usdkrw = self.stock.get_usd_krw()[1]

        self.DB.tbl, self.DB.wre = ("h_user_list",f"no={session['N_NO']}")
        USER = self.DB.get("*",many=1, assoc=True)

        cdx = 'SOXL'
        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add1='{cdx}'")
        b_date = self.DB.get_one("max(add0)") 
        today = my.kor_loc_date('US/Eastern')[0:10]
        if not b_date : b_date = '2015-01-01'
        
        self.DB.wre = f"add0='{b_date}' and add1='{cdx}'"
        # add4 : Open, add5 : High, add6 : Low, add3 : Close, add7 : Vol, add8 : Change, add9 : Up, add10 : Dn
        one = self.DB.get('add0,add4,add5,add6,add3,add7,add8,add9,add10',many=1,assoc=False) 
        the_first_data = [one[0],float(one[1]),float(one[2]),float(one[3]),float(one[4]),int(one[5]),float(one[6]),int(one[7]),int(one[8])]
        app_key = self.DB.store("tiingo")
        
        new_data = self.stock.get_tiingo_price(app_key,cdx,b_date,today)
        
        if  not new_data : 
            self.send_message("No data updated")
            return

        ohlc = self.stock.get_tiingo_price(app_key,cdx,b_date,today)
        if not ohlc : return

        ohlc[0]= the_first_data

        for i in range(1,len(ohlc)) :
            ohlc[i][6]  = round((ohlc[i][4] - ohlc[i-1][4])/ohlc[i-1][4]*100,2)
            ohlc[i][7]  = ohlc[i-1][7]+1 if ohlc[i][4] >= ohlc[i-1][4] else 0
            ohlc[i][8]  = ohlc[i-1][8]+1 if ohlc[i][4] <  ohlc[i-1][4] else 0

        rst3 = ohlc[1:]

        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"
        time_now = my.now_timestamp()

        for row in rst3 :
            row2 = list(row)
            row2 += [cdx,usdkrw,USER['uid'],USER['uname'],time_now,time_now]
            values = str(row2)[1:-1]
            sql = f"INSERT INTO {self.DB.tbl} ({db_keys}) VALUES({values})"
            self.DB.exe(sql)
        
        self.set_message("종목 업데이트를 완료하였습니다")
        return self.moveto('board/list/stockHistory/csh=on')

    def update_krw(self) :
        pass

    def delete(self) :

        code = self.parm[0]
        if not code : return
        self.DB.exe(f"DELETE FROM h_stockHistory_board WHERE add1='{code}'")
        self.set_message("종목 삭제를 완료하였습니다")
        return self.moveto('board/list/stockHistory')
        