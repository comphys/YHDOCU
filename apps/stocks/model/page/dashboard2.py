from system.core.load import Model
import system.core.my_utils as ut
class M_dashboard2(Model) :

    def view(self) :
        
        self.DB.tbl, self.DB.wre, self.DB.odr =('h_daily_first_board',"add19='시즌진행'",'add0 DESC')
        self.DB.lmt = '60'
        DF = self.DB.get("add0,add5,add9",assoc=False)
        DFD= {x[0]:[x[1],x[2]] for x in DF}
        start_date = DF[-1][0]

        self.DB.wre = f"add0 >= '{start_date}'"
        self.DB.tbl ='h_daily_second_board'
        DS = self.DB.get("add0,add9",assoc=False)
        DSD= {x[0]:x[1] for x in DS}

        self.DB.tbl ='h_daily_third_board'
        DT = self.DB.get("add0,add9",assoc=False)
        DTD= {x[0]:x[1] for x in DT}

        self.D['날자'] = []
        self.D['종가'] = []
        self.D['첫째'] = []
        self.D['둘째'] = []
        self.D['셋째'] = []

        for key in DFD :
            if key in DSD : DFD[key].append(DSD[key])
            else : DFD[key].append('null')

            if key in DTD : DFD[key].append(DTD[key])
            else : DFD[key].append('null')

            self.D['날자'].append(key[2:])
            self.D['종가'].append(DFD[key][0])
            self.D['첫째'].append(DFD[key][1])
            self.D['둘째'].append(DFD[key][2])
            self.D['셋째'].append(DFD[key][3])

        self.D['날자'].reverse()
        self.D['종가'].reverse()
        self.D['첫째'].reverse()
        self.D['둘째'].reverse()
        self.D['셋째'].reverse()    

        self.DB.clear()

        # 상황
        self.D['첫째상황']  = self.outcome('h_daily_first_board')
        self.D['둘째상황'] = self.outcome('h_daily_second_board')
        self.D['셋째상황']  = self.outcome('h_daily_third_board')

        self.D['평가합계'] = float(self.D['첫째상황'][1].replace(',','')) + float(self.D['둘째상황'][1].replace(',','')) + float(self.D['셋째상황'][1].replace(',',''))
        self.D['투자합계'] = float(self.D['첫째상황'][0].replace(',','')) + float(self.D['둘째상황'][0].replace(',','')) + float(self.D['셋째상황'][0].replace(',',''))
        self.D['손익현황'] = self.D['평가합계'] - self.D['투자합계']
        self.D['합수익률'] = self.D['손익현황'] / self.D['투자합계'] * 100
        self.D['total_rate'] = f"{self.D['합수익률']:.1f}"
        
        # self.D['평가합계'] = f"{self.D['평가합계']:,.0f}"
        # self.D['투자합계'] = f"{self.D['투자합계']:,.0f}"
        # self.D['손익현황'] = f"<span style='color:#ced8f6'>{self.D['손익현황']:,.2f}</span>"  if self.D['손익현황'] < 0 else f"<span style='color:#f6cece'>{self.D['손익현황']:,.2f}</span>"
        # self.D['합수익률'] = f"<span style='color:#ced8f6'>{self.D['합수익률']:,.1f}%</span>" if self.D['합수익률'] < 0 else f"<span style='color:#f6cece'>{self.D['합수익률']:,.1f}%</span>"

        ckday = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")

        self.D['오늘날자']  = ut.timestamp_to_date(opt=7) 
        self.D['오늘요일']  = ut.dayofdate(self.D['오늘날자'])
        self.D['확인날자']  = ckday
        # self.D['확인요일']  = ut.dayofdate(ckday)

        # # 전략
        # tbl = ('h_daily_first_board','h_daily_second_board','h_daily_third_board')
        # tle = ('첫째계좌','둘째계좌','셋째계좌')
        # ttt = ('첫째전략','둘째전략','셋째전략')

        # for i, tbl in enumerate(tbl) :
        #     self.DB.tbl, self.DB.wre = (tbl,f"add0='{self.D['확인날자']}' and add19='시즌진행'")
        #     D = self.DB.get_line("*")
        #     days = self.DB.one(f"SELECT count(no) FROM {tbl} WHERE add19='시즌진행'")
        #     if D : self.D[ttt[i]] = self.print_out(D,title=tle[i],days=days)
        #     else : self.D[ttt[i]] = f"<div style='text-align:center'>{self.D['확인날자']}({self.D['확인요일']}) 일에 대한 {tle[i]} 정보가 없습니다</div>"            

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

        기초자금 = f"{기초자금:,.0f}"
        현재자금 = f"{현재자금:,.0f}"
        가용잔액 = f"{가용잔액:,.2f}"
        profit_rate = f"{최종수익률:.1f}" 
        최종수익 = f"<span style='color:#ced8f6'>{최종수익:,.2f}</span>" if 최종수익 < 0 else f"<span style='color:#f6cece'>{최종수익:,.2f}</span>"
        최종수익률 = f"<span style='color:#ced8f6'>{최종수익률:,.1f}%</span>" if 최종수익률 < 0 else f"<span style='color:#f6cece'>{최종수익률:,.1f}%</span>"

        out = [기초자금,현재자금,최종수익,최종수익률,'S'+LD['add2'],LD['add4'],LD['add10'],LD['add9'],f"{float(LD['add15']):,.1f}",f"{float(LD['add11']):,.0f}",가용잔액]
        return out
