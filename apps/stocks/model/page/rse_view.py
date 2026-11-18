from system.core.load import Model
import system.core.my_utils as my

#
# RSE ( Revolution, Stable, New Trust ) Strategy 
#
class M_rse_view(Model) :

    def view(self) :
        
        # 기본 값
        self.D['종목코드'] = 'SOXL'
        self.D['투자자금'] = self.DB.parameter('EC010')

        self.D['기회시점'] = self.DB.parameter('ER021')
        self.D['기회회복'] = self.DB.parameter('ER022')
        self.D['안정시점'] = self.DB.parameter('ES021')
        self.D['안정회복'] = self.DB.parameter('ES022')

        self.D['수료적용'] = 'off'
        self.D['세금적용'] = 'off'
        self.D['일반상황'] = 'on'
        self.D['가상손실'] = 'off'

        # 기간 설정(최근 2년간)
        # self.D['end_date'] = my.timestamp_to_date(ts='now',opt=7)
        self.D['종료일자'] = self.DB.last_date("h_stockHistory_board")
        self.D['시작일자'] = my.dayofdate(self.D['종료일자'],delta=-365*2)[0]


    def action(self) :
        D = {}

        D['투자자금'] = self.D['post']['투자자금']
        D['시작일자'] = self.D['post']['시작일자']
        D['종료일자'] = self.D['post']['종료일자']

        if  D['시작일자'] > D['종료일자'] : 
            return self.SYS.moveto('page/view/rse_view')

        # -------------------
        D['기회시점'] = self.D['post']['기회시점']
        D['기회회복'] = self.D['post']['기회회복']
        D['안정시점'] = self.D['post']['안정시점']
        D['안정회복'] = self.D['post']['안정회복']

        D['수료적용'] = self.D['post'].get('chk_fee','off')
        D['세금적용'] = self.D['post'].get('chk_tax','off')
        D['일반상황'] = self.D['post'].get('chk_von','off')
        D['가상손실'] = self.D['post'].get('chk_chx','off')
        
        RSE = self.SYS.load_app_lib('rse')
        RSE.D |= D

        RSE.do_viewChart()
        D |= RSE.D

# ----------------------------------------------------------------------------------------------
# AJAX 
# ----------------------------------------------------------------------------------------------

class Ajax(Model) :

    def get_ohlc(self) :
        code = self.gets['code']
        date = self.gets['date']

        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add1='{code}' and add0='{date}'")
        ohlc = self.DB.get_line("add4,add5,add6,add3,add8,add9,add10")
        # day_change = (float(ohlc['add5']) - float(ohlc['add4'])) / float(ohlc['add4']) * 100
        change = float(ohlc['add8'])
        output  = "<div id='stock_prices' style='width:430px;height:80px;padding:10px;background-color:#1d1f24;color:#e1e1e1;border:2px solid slategray;' ondblclick=\"h_dialog.close('OHLC_DAY')\">"
        output += "<table class='table' style='text-align:center'><tr><th>시가</th><th>고가</th><th>저가</th><th>종가</th><th>변동</th><th>상승</th><th>하락</th></tr><tr>"
        output += f"<td>{ohlc['add4']}</td>"
        output += f"<td style='color:#F6CECE'>{ohlc['add5']}</td>"
        # output += f"<td>{day_change:.1f}</td>"
        output += f"<td style='color:#CED8F6'>{ohlc['add6']}</td>"
        output += f"<td style='color:#F5F6CE'>{ohlc['add3']}</td>"
        output += f"<td>{change:.1f}%</td>"
        output += f"<td>{ohlc['add9']}</td>"
        output += f"<td>{ohlc['add10']}</td>"
        output += "</tr></table></div>"

        return output


    def log_rse(self) :
        
        RSE = self.SYS.load_app_lib('rse')
        
        PD = {} # post data

        PD['투자자금'] = self.D['post']['투자자금']

        PD['시작일자'] = self.D['post']['시작일자']
        PD['종료일자'] = self.D['post']['종료일자']
        PD['기회시점'] = self.D['post']['기회시점']
        PD['기회회복'] = self.D['post']['기회회복']
        PD['안정시점'] = self.D['post']['안정시점']
        PD['안정회복'] = self.D['post']['안정회복']        
        
        PD['수료적용'] = 'on' if self.D['post']['수료적용'] == 'true' else 'off'
        PD['세금적용'] = 'on' if self.D['post']['세금적용'] == 'true' else 'off'
        PD['가상손실'] = 'on' if self.D['post']['가상손실'] == 'true' else 'off'

       
        key = self.D['post']['적용전략']
            
        RSE.D |= PD
        RSE.get_simResult(PD['시작일자'],PD['종료일자'])
        DC = RSE.get_simulLog(key)
        return self.SYS.json(DC)
    
    def synchro(self) :
        
        opt = self.D['post']['opt']
        ldate = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")
    
        if  opt == 'real' :
            sdate = self.DB.parameter('EX050')
            T_mon = my.sv(self.DB.parameter('EX051'))
            mode_ = self.DB.parameter('EX052')
        elif opt == 'test' :
            sdate = my.dayofdate(ldate,delta=-365*2)[0]
            T_mon = my.sv(self.DB.parameter('EC010'))
            mode_ = '기본진행'
        
        RD = {}
        RD['sdate'] = sdate
        RD['ldate'] = ldate
        RD['T_mon'] = f"{T_mon:,.2f}"
        RD['mode_'] = mode_
        
        return self.SYS.json(RD)