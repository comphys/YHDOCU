from system.core.load import Model
from datetime import datetime
import system.core.my_utils as my

class M_back_testing(Model) :

    def view(self) :
        
        now = int(datetime.now().timestamp())
        old = str(now - 3600*24*7)
        self.DB.tbl, self.DB.wre = ("h_stockHistory_board",f"wdate > '{old}'")
        self.D['sel_codes'] = self.DB.get("distinct add1",assoc=False)

        self.DB.tbl, self.DB.wre = ("h_stock_strategy_board",None)
        self.D['sel_strategy'] = self.DB.get("add0",assoc=False)

        # 기본 값
        self.D['code'] = 'SOXL'
        self.D['strategy'] = 'VICTORY'
        self.D['capital'] = '24,000'
        self.D['addition'] = '12,000'
        self.D['chanceCapital'] = '7,200'
        # 기간 설정(최근 2년간)
        # self.D['end_date'] = my.timestamp_to_date(ts='now',opt=7)
        self.D['end_date'] = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")
        self.D['start_date'] = my.dayofdate(self.D['end_date'],delta=-365*2)[0]
        self.D['progress'] =  '0.0'


        