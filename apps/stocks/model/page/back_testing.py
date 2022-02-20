from system.core.load import Model
from datetime import datetime

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
        self.D['strategy'] = 'DNA 2022'
        self.D['capital'] = '20,000'
        self.D['addition'] = '2,000'
        self.D['start_date'] = '2017-01-02'
        self.D['end_date'] = '2021-12-27'
        self.D['progress'] = '60'

        