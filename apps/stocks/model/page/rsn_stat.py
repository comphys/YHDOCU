from system.core.load import Model
import system.core.my_utils as my

class M_rsn_stat(Model) :

    def view(self) :
        
        # 기본 값
        self.D['종목코드'] = 'SOXL'
        
        self.D['종목코드'] = 'SOXL'
        투자자금 = self.DB.parameters('TC010')
        자금배분 = my.sf(self.DB.parameters('TC011'))
        
        self.D['기회자금'] = round(투자자금*자금배분[0]/100,2)
        self.D['안정자금'] = round(투자자금*자금배분[1]/100,2)
        self.D['생활자금'] = round(투자자금*자금배분[2]/100,2)

        self.D['기회시점'] = self.DB.parameters('TR021')
        self.D['기회회복'] = self.DB.parameters('TR022')
        self.D['안정시점'] = self.DB.parameters('TS021')
        self.D['안정회복'] = self.DB.parameters('TS022')

        self.D['수료적용'] = 'on'
        self.D['세금적용'] = 'off'
        self.D['일밸런싱'] = 'on'
        self.D['이밸런싱'] = 'on'
        self.D['일반상황'] = 'off'
        self.D['가상손실'] = 'off'

        # 기간 설정(최근 2년간)
        # self.D['end_date'] = my.timestamp_to_date(ts='now',opt=7)
        self.D['종료일자'] = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")
        self.D['통계시작'] = my.dayofdate(self.D['종료일자'],delta=-365*2)[0]
        