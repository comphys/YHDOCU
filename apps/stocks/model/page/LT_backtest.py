from system.core.load import Model
from datetime import datetime

class M_LT_backtest(Model) :

    def view(self) :
        
        # 기본 값
        self.D['code'] = 'SOXL'
        self.D['leverage'] = '5,000'
        self.D['cash'] = '3,000'
        self.D['start_date'] = '2022-01-03'
        self.D['end_date'] = '2022-01-31'
        self.D['strategy'] = '변동리밸런싱_기본'