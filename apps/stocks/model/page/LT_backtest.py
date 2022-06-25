from system.core.load import Model
from datetime import datetime

class M_LT_backtest(Model) :

    def view(self) :
        
        # 기본 값
        self.D['code'] = 'SOXL'
        self.D['leverage'] = '5,000'
        self.D['cash'] = '3,000'
        self.D['start_date'] = '2021-01-02'
        self.D['end_date'] = '2021-01-31'
        