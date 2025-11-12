from system.core.load import Model
import system.core.my_utils as my

class M_rst_view(Model) :

    def view(self) :
        
        # 기본 값
        self.D['종목코드'] = 'SOXL'
        self.D['일반자금'] = self.DB.parameter('05100')
        self.D['기회자금'] = self.DB.parameter('05200')
        self.D['안정자금'] = self.DB.parameter('05300')
        self.D['생활자금'] = self.DB.parameter('05400')

        self.D['기회시점'] = self.DB.parameter('02100')
        self.D['기회회복'] = self.DB.parameter('02200')
        self.D['안정시점'] = self.DB.parameter('02300')
        self.D['안정회복'] = self.DB.parameter('02400')
        self.D['생활시점'] = self.DB.parameter('02401')
        self.D['생활회복'] = self.DB.parameter('02402')

        self.D['수료적용'] = 'on'
        self.D['세금적용'] = 'off'
        self.D['일밸런싱'] = 'on'
        self.D['이밸런싱'] = 'on'
        self.D['일반상황'] = 'off'
        self.D['가상손실'] = 'off'
        self.D['랜덤종가'] = 'off'

        # 기간 설정(최근 2년간)
        # self.D['end_date'] = my.timestamp_to_date(ts='now',opt=7)
        self.D['종료일자'] = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")
        self.D['시작일자'] = my.dayofdate(self.D['종료일자'],delta=-365*2)[0]
        
    def action(self) :

        D = {}
        D['종목코드'] = self.D['post']['종목코드']
        D['일반자금'] = self.D['post']['일반자금']
        D['기회자금'] = self.D['post']['기회자금']
        D['안정자금'] = self.D['post']['안정자금']
        D['생활자금'] = self.D['post']['생활자금']

        D['시작일자'] = self.D['post']['시작일자']
        D['종료일자'] = self.D['post']['종료일자']
        # -------------------
        D['기회시점'] = self.D['post']['기회시점']
        D['기회회복'] = self.D['post']['기회회복']
        D['안정시점'] = self.D['post']['안정시점']
        D['안정회복'] = self.D['post']['안정회복']
        D['생활시점'] = self.D['post']['생활시점']
        D['생활회복'] = self.D['post']['생활회복']

        D['수료적용'] = self.D['post'].get('chk_fee','off')
        D['세금적용'] = self.D['post'].get('chk_tax','off')
        D['일밸런싱'] = self.D['post'].get('chk_brs','off')
        D['이밸런싱'] = self.D['post'].get('chk_rs_','off')
        D['일반상황'] = self.D['post'].get('chk_von','off')
        D['가상손실'] = self.D['post'].get('chk_chx','off')
        D['랜덤종가'] = self.D['post'].get('chk_rnd','off')
        
        RST = self.SYS.load_app_lib('rst')
        RST.D |= D

        RST.do_viewChart()
    
        D['skin'] = f"{self.skin}/{self.D['bid']}.html"
        return self.SYS.echo(RST.D)