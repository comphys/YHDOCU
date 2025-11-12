from system.core.load import Model
import system.core.my_utils as my

class M_mytestChart(Model) :

    def view(self) :
        
        # 기본 값
        self.D['종목코드'] = 'SOXL'
        self.D['전략선택'] = 'T3DAYS'
        self.D['일반자금'] = self.DB.parameter('05100')
 
        self.D['수료적용'] = 'on'
        self.D['세금적용'] = 'off'

        # 기간 설정(최근 2년간)
        # self.D['end_date'] = my.timestamp_to_date(ts='now',opt=7)
        self.D['종료일자'] = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")
        self.D['시작일자'] = my.dayofdate(self.D['종료일자'],delta=-365*2)[0]

    def action(self) :
        
        D = {}
        D['종목코드'] = self.D['post']['종목코드']
        D['일반자금'] = self.D['post']['일반자금']

        D['시작일자'] = self.D['post']['시작일자']
        D['종료일자'] = self.D['post']['종료일자']

        D['수료적용'] = self.D['post'].get('chk_fee','off')
        D['세금적용'] = self.D['post'].get('chk_tax','off')
        
        VB = self.SYS.load_app_lib('t3days')
        VB.D |= D

        VB.do_viewChart()

        VB.D['skin'] = f"{self.skin}/{self.D['bid']}.html"
        return self.SYS.echo(VB.D)
        