from system.core.load import Model
import system.core.my_utils as my

class M_mytestChart(Model) :

    def view(self) :
        
        # 기본 값
        self.D['종목코드'] = 'SOXL'
        self.D['일반자금'] = self.DB.parameters('05100')
 
        self.D['수료적용'] = 'on'
        self.D['세금적용'] = 'off'

        # 기간 설정(최근 2년간)
        # self.D['end_date'] = my.timestamp_to_date(ts='now',opt=7)
        self.D['종료일자'] = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")
        self.D['시작일자'] = my.dayofdate(self.D['종료일자'],delta=-365*2)[0]
        