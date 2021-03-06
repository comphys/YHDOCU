from system.core.load import Model
import system.core.my_utils as ut
class M_dashboard2(Model) :

    def view(self) :
        date_from = '2022-07-07'
        self.DB.tbl, self.DB.wre, self.DB.odr =('h_daily_virtual_board',f"add0 > '{date_from}'",'add0 DESC')
        self.DB.lmt = '180'
        DF = self.DB.get("add0,add5,add9")
        DFD= {x['add0']:[x['add5'],x['add9']] for x in DF}
        cnt= len(DFD)

        DSD = {}    
        DTD = {}

        start_date = DF[-1]['add0']

        self.DB.wre = f"add0 >= '{start_date}'"
        self.DB.tbl ='h_daily_first_board'
        DS = self.DB.get("add0,add9",assoc=False)
        if DS : DSD= {x[0]:x[1] for x in DS}

        self.DB.tbl ='h_daily_second_board'
        DT = self.DB.get("add0,add9",assoc=False)
        if DT : DTD= {x[0]:x[1] for x in DT}

        self.D['날자'] = []
        self.D['종가'] = []
        self.D['가상'] = []
        self.D['첫째'] = []
        self.D['둘째'] = []

        for key in DFD :
            if key in DSD : DFD[key].append(DSD[key])
            else : DFD[key].append('null')

            if key in DTD : DFD[key].append(DTD[key])
            else : DFD[key].append('null')

            self.D['날자'].append(key[2:])
            self.D['종가'].append(DFD[key][0])
            self.D['가상'].append(DFD[key][1])
            self.D['첫째'].append(DFD[key][2])
            self.D['둘째'].append(DFD[key][3])

        self.D['날자'].reverse()
        self.D['종가'].reverse()
        self.D['가상'].reverse()
        self.D['첫째'].reverse()
        self.D['둘째'].reverse() 
        
        self.D['종가최대'] = max(self.D['종가'])
        self.D['종가최소'] = min(self.D['종가'])
        MDD = (float(self.D['종가최대'])-float(self.D['종가최소']))/float(self.D['종가최대']) * 100
        self.D['MDD'] = f"{MDD:.2f}"

        self.D['가상10'] = [float(x)*0.9 for x in self.D['가상']]
        self.D['가상20'] = [float(x)*0.8 for x in self.D['가상']]
        self.D['가상30'] = [float(x)*0.7 for x in self.D['가상']]
 
        self.DB.clear()

        self.D['가상상황']  = self.outcome('h_daily_virtual_board')
        self.D['첫째상황']  = self.outcome('h_daily_first_board')
        self.D['둘째상황']  = self.outcome('h_daily_second_board')

        fx = float(self.D['가상상황']['t1'].replace(',','')); fy = float(self.D['가상상황']['t2'].replace(',',''))
        sx = float(self.D['첫째상황']['t1'].replace(',','')); sy = float(self.D['첫째상황']['t2'].replace(',',''))
        tx = float(self.D['둘째상황']['t1'].replace(',','')); ty = float(self.D['둘째상황']['t2'].replace(',',''))
         
        self.D['평가합계'] = fy + sy + ty
        self.D['투자합계'] = fx + sx + tx
        self.D['손익현황'] = self.D['평가합계'] - self.D['투자합계']
        self.D['합수익률'] = self.D['손익현황'] / self.D['투자합계'] * 100
        self.D['total_rate'] = f"{self.D['합수익률']:.1f}"
        
        self.D['fy_w'] = int( 1490 * fy / self.D['평가합계'])
        self.D['sy_w'] = int( 1490 * sy / self.D['평가합계'])
        self.D['ty_w'] = int( 1490 * ty / self.D['평가합계'])

        self.D['평가합계'] = f"{self.D['평가합계']:,.0f}" 
        self.D['투자합계'] = f"{self.D['투자합계']:,.0f}"
        self.D['손익현황'] = f"{self.D['손익현황']:,.0f}"

        ckday = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")

        self.D['오늘날자']  = ut.timestamp_to_date(opt=7) 
        self.D['오늘요일']  = ut.dayofdate(self.D['오늘날자'])
        self.D['확인날자']  = ckday
        self.D['확인요일']  = ut.dayofdate(ckday)


    def outcome(self,tbl) :

        self.DB.tbl, self.DB.wre = (tbl,"add1='SOXL'")
        start_date, last_date = self.DB.get("min(add0),max(add0)",many=1,assoc=False)

        self.DB.wre = f"add0='{start_date}'"
        기본자산, 추가자산 = self.DB.get("sub7,sub8",many=1,assoc=False) 

        self.DB.wre = f"add0='{last_date}'"
        LD = self.DB.get_line("*") 

        기초자금 = float(기본자산) + float(추가자산)
        가용잔액 = float(LD['add16']) + float(LD['add17'])
        현재자금 = float(LD['add11']) + 가용잔액
        최종수익 = 현재자금 - 기초자금 
        최종수익률 = (최종수익/기초자금) * 100 

        out = {}
        out['active'] = '#F2F5A9' if LD['add19'] == '시즌진행' else 'gray'
        out['t1'] = f"{기초자금:,.0f}"
        out['t2'] = f"{현재자금:,.0f}"
        out['t3'] = f"{최종수익:,.2f}"
        out['t4'] = f"{최종수익률:,.1f}"

        out['p1'] = 'S'+LD['add2']
        out['p2'] = LD['add4']
        out['p3'] = LD['add10']
        out['p4'] = LD['add9']
        out['p5'] = f"{float(LD['add15']):,.1f}"
        out['p6'] = f"{float(LD['add11']):,.0f}"
        out['p7'] = f"{가용잔액:,.2f}"


        strategy = ['&nbsp','&nbsp','&nbsp','&nbsp','&nbsp','&nbsp']
        
        if LD['add19'] == '시즌진행' :
            k = 0
            if int(LD['buy11']) :  strategy[k] = "<span style='color:#CEF6F5'>평단매수</span>" ; strategy[k+1] = LD['buy11'];  strategy[k+2] = LD['buy12']   ; k+=3
            if int(LD['buy21']) :  strategy[k] = "<span style='color:#CEF6F5'>큰단매수</span>" ; strategy[k+1] = LD['buy21'];  strategy[k+2] = LD['buy22']   ; k+=3
            if int(LD['buy31']) :  strategy[k] = "<span style='color:#CEF6F5'>추종매수</span>" ; strategy[k+1] = LD['buy31'];  strategy[k+2] = LD['buy32']   ; k+=3
            if int(LD['buy41']) :  strategy[k] = "<span style='color:#CEF6F5'>추가매수</span>" ; strategy[k+1] = LD['buy41'];  strategy[k+2] = LD['buy42']   ; k+=3
            if int(LD['buy51']) :  strategy[k] = "<span style='color:#CEF6F5'>전략매수</span>" ; strategy[k+1] = LD['buy51'];  strategy[k+2] = LD['buy52']   ; k+=3
            
            if int(LD['sell11']) : strategy[k] = "<span style='color:#F8E6E0'>첫째매도</span>" ; strategy[k+1] = LD['sell11']; strategy[k+2] = LD['sell12']  ; k+=3
            if int(LD['sell21']) : strategy[k] = "<span style='color:#F8E6E0'>둘째매도</span>" ; strategy[k+1] = LD['sell21']; strategy[k+2] = LD['sell22']  ; k+=3
            if int(LD['sell31']) : strategy[k] = "<span style='color:#F8E6E0'>강제매도</span>" ; strategy[k+1] = LD['sell31']; strategy[k+2] = LD['sell32']  ; k+=3
            if int(LD['sell41']) : strategy[k] = "<span style='color:#F8E6E0'>전략매도</span>" ; strategy[k+1] = LD['sell41']; strategy[k+2] = LD['sell42']
        
        out['s1'] = strategy[0] 
        out['s2'] = strategy[1] 
        out['s3'] = strategy[2] 
        out['s4'] = strategy[3] 
        out['s5'] = strategy[4] 
        out['s6'] = strategy[5] 
        return out
