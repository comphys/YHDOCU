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

        fx = float(self.D['첫째상황'][0].replace(',','')); fy = float(self.D['첫째상황'][1].replace(',',''))
        sx = float(self.D['둘째상황'][0].replace(',','')); sy = float(self.D['둘째상황'][1].replace(',',''))
        tx = float(self.D['셋째상황'][0].replace(',','')); ty = float(self.D['셋째상황'][1].replace(',',''))
         
        self.D['평가합계'] = fy + sy + ty
        self.D['투자합계'] = fx + sx + tx
        self.D['손익현황'] = self.D['평가합계'] - self.D['투자합계']
        self.D['합수익률'] = self.D['손익현황'] / self.D['투자합계'] * 100
        self.D['total_rate'] = f"{self.D['합수익률']:.1f}"
        
        self.D['fy_w'] = int( 1470 * fy / self.D['평가합계'])
        self.D['sy_w'] = int( 1470 * sy / self.D['평가합계'])
        self.D['ty_w'] = int( 1470 * ty / self.D['평가합계'])

        ckday = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")

        self.D['오늘날자']  = ut.timestamp_to_date(opt=7) 
        self.D['오늘요일']  = ut.dayofdate(self.D['오늘날자'])
        self.D['확인날자']  = ckday
        # self.D['확인요일']  = ut.dayofdate(ckday)

        # # 전략
        tbl = ('h_daily_first_board','h_daily_second_board','h_daily_third_board')

        for i, tbl in enumerate(tbl) :
            self.DB.tbl, self.DB.wre = (tbl,f"add0='{self.D['확인날자']}' and add19='시즌진행'")
            D = self.DB.get_line("*")
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

        최종수익 = f"{최종수익:,.2f}" 
        최종수익률 = f"{최종수익률:,.1f}"

        out = [기초자금,현재자금,최종수익,최종수익률,'S'+LD['add2'],LD['add4'],LD['add10'],LD['add9'],f"{float(LD['add15']):,.1f}",f"{float(LD['add11']):,.0f}",가용잔액]
        return out

    def strategy(self,D,days=0) :
        output = ['&nbsp','&nbsp','&nbsp','&nbsp','&nbsp','&nbsp']
        if int(D['buy11']) :  output[0] = '일반매수' ; output[1] = D['buy11']; output[2] = D['buy12']
        if int(D['buy31']) :  output[0] = '추종매수' ; output[1] = D['buy31']; output[2] = D['buy32']
        if int(D['buy41']) :  output[0] = '추가매수' ; output[1] = D['buy41']; output[2] = D['buy42']
        if int(D['buy51']) :  output[0] = '전략매수' ; output[1] = D['buy51']; output[2] = D['buy52']
        if int(D['buy21']) :  output[0] = '터닝매수' ; output[1] = D['buy21']; output[2] = D['buy22']

        return output
