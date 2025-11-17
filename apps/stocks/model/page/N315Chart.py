from system.core.load import Model
import system.core.my_utils as my

class M_N315Chart(Model) :

    def view(self) :
        
        # 기본 값
        self.D['종목코드'] = 'SOXL'
        self.D['전략선택'] = 'N315'
        self.D['일반자금'] = f"{my.sv(self.DB.parameter('N0702')):,.2f}"
 
        self.D['수료적용'] = 'off'
        self.D['세금적용'] = 'off'

        # 기간 설정(최근 2년간)
        # self.D['end_date'] = my.timestamp_to_date(ts='now',opt=7)
        self.D['종료일자'] = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")
        # self.D['시작일자'] = my.dayofdate(self.D['종료일자'],delta=-365*2)[0]
        self.D['시작일자'] = self.DB.parameter('N0701')

    def action(self) :
        D = {}
        D['종목코드'] = self.D['post']['종목코드']
        D['일반자금'] = self.D['post']['일반자금']

        D['시작일자'] = self.D['post']['시작일자']
        D['종료일자'] = self.D['post']['종료일자']

        D['수료적용'] = self.D['post'].get('chk_fee','off')
        D['세금적용'] = self.D['post'].get('chk_tax','off')
        
        VB = self.SYS.load_app_lib('n315')
        VB.D |= D

        VB.do_viewChart()

        return self.SYS.echo(VB.D)

# ----------------------------------------------------------------------------------------------
# AJAX 
# ----------------------------------------------------------------------------------------------

class Ajax(Model) :

    def synchro_n315(self) :
        
        opt = self.D['post']['opt']
        ldate = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")
    
        if  opt == 'real' :
            sdate = self.DB.parameter('N0701')
            V_mon = my.sv(self.DB.parameter('N0702'))
        elif opt == 'test' :
            sdate = my.dayofdate(ldate,delta=-365*2)[0]
            V_mon = 60000
        
        RD = {}
        RD['sdate'] = sdate
        RD['ldate'] = ldate
        RD['V_mon'] = f"{V_mon:,.2f}"
        return self.SYS.json(RD)        