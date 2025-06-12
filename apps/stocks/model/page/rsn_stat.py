from system.core.load import Model
import system.core.my_utils as my

class M_rsn_stat(Model) :

    def view(self) :
        
        # 기본 값
        self.D['종목코드'] = 'SOXL'
        
        self.D['종목코드'] = 'SOXL'
        self.D['투자자금'] = self.DB.parameter('TC010')

        self.D['기회시점'] = self.DB.parameter('TR021')
        self.D['기회회복'] = self.DB.parameter('TR022')
        self.D['안정시점'] = self.DB.parameter('TS021')
        self.D['안정회복'] = self.DB.parameter('TS022')

        self.D['수료적용'] = 'on'
        self.D['세금적용'] = 'off'
        self.D['일밸런싱'] = 'on'
        self.D['이밸런싱'] = 'on'
        self.D['일반상황'] = 'off'
        self.D['가상손실'] = 'off'
        self.D['일년단위'] = 'off'

        # 기간 설정(최근 2년간)
        # self.D['end_date'] = my.timestamp_to_date(ts='now',opt=7)
        self.D['종료일자'] = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")
        self.D['통계시작'] = my.dayofdate(self.D['종료일자'],delta=-365*2)[0]
        