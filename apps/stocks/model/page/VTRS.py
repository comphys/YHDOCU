from system.core.load import Model
import system.core.my_utils as my

class M_VTRS(Model) :

    def view(self) :
        
        # 기본 값
        self.D['종목코드'] = 'SOXL'
        self.D['시작자금'] = '36,000'
        
        self.D['타임지연'] = 1
        self.D['타임시점'] = -2.0
        self.D['기회시점'] = -2.0
        self.D['기회회복'] = 0.0
        self.D['안정시점'] = -2.0
        self.D['안정회복'] = 0.0

        # 기간 설정(최근 2년간)
        # self.D['end_date'] = my.timestamp_to_date(ts='now',opt=7)
        self.D['종료일자'] = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")
        self.D['시작일자'] = my.dayofdate(self.D['종료일자'],delta=-365*2)[0]
        