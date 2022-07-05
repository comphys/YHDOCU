from system.core.load import Model
from datetime import datetime

class M_LT_backtest(Model) :

    def view(self) :
        
        # 기본 값
        self.D['code'] = 'SOXL'
        self.D['leverage'] = '6,000'
        self.D['cash'] = '4,000'
        self.D['start_date'] = '2017-01-03'
        self.D['end_date'] = '2021-12-27'
        self.D['strategy'] = '변동리밸런싱_기본'