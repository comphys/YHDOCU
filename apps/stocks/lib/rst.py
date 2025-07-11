import system.core.my_utils as my
from random import sample

class RST :

    def __init__(self,SYS) :
        self.SYS   = SYS
        self.info  = SYS.info
        self.D     = SYS.D
        self.DB    = SYS.DB
        self.chart = False
        self.stat  = False
        self.op    = 'jrst'

        self.B = {}
        self.V = {}
        self.R = {}
        self.S = {}
        self.T = {}
        self.M = {}
  
    # ------------------------------------------------------------------------------------------------------------------------------------------
    # same with xtask BEGIN, last modified 2024.10.18.
    # ------------------------------------------------------------------------------------------------------------------------------------------ 
    # 매수수량 : 실제 매수한 수량, 매도수량 : 실제 매도한 수량
    # 예정수량 : 매수 예정 수량

    
    def calculate_sub(self,tac,key) :
        
        if  tac['매수수량'] : 
            tac['현재잔액'] -= tac['매수금액']
            tac['보유수량'] += tac['매수수량']
            tac['총매수금'] += tac['매수금액']
            tac['평균단가'] =  tac['총매수금'] / tac['보유수량'] 
            
            if self.D['수료적용'] == 'on' :  tac['수수료등']  = self.commission(tac['매수금액'],1); tac['현재잔액'] -= tac['수수료등']
        
        tac['현수익률'] = (self.M['당일종가'] / tac['평균단가'] -1) * 100  if tac['평균단가'] else 0.00
        
        if  tac['매도수량'] :
            tac['실현수익']  =  tac['매도금액'] - tac['총매수금']
            tac['보유수량'] -=  tac['매도수량'];  tac['현재잔액'] += tac['매도금액']; tac['총매수금'] = 0.00
            tac['수익현황']  =  tac['실현수익']
            
            if self.D['수료적용'] == 'on' : tac['수수료등']  = self.commission(tac['매도금액'],2); tac['현재잔액'] -= tac['수수료등'] 
            if self.D['세금적용'] == 'on' : tac['현재잔액'] -= self.tax(tac['실현수익'])
            
            tac['현수익률'] = (tac['현재잔액'] / tac['시초금액'] -1) * 100
            
            self.rstCount(tac['실현수익'],key)

        tac['평가금액'] =  self.M['당일종가'] * tac['보유수량'] 
        

    def calculate(self)  :
        
        self.calculate_sub(self.T,'생')
        self.calculate_sub(self.S,'안')
        self.calculate_sub(self.R,'기')
        self.calculate_sub(self.V,'일')
        
        if  self.V['매도수량'] :

            if  self.M['당일종가']>= self.V['평균단가'] : 
                self.M['기본진행'] = True
                self.set_value(['진행상황'],'익절매도')
            else :
                self.M['기본진행'] = False
                self.set_value(['진행상황'],'손절매도')
            
            self.M['첫날기록'] = True
            self.set_value(['매수단계'],'일반매수')
            self.set_value(['평균단가'],0.0)
            self.rebalance()

        else  : 
            for tac in [self.V,self.R,self.S,self.T] : tac['수익현황'] = tac['평가금액'] - tac['총매수금']

        self.realMDD()


    def realMDD(self) :
        
        if not self.stat : return
        for tac in (self.V,self.R,self.S,self.T) :
            tac['실최하락'] = (tac['평가금액']-tac['총매수금']) / (tac['현재잔액'] + tac['총매수금']) * 100
            if  tac['실최하락'] < tac['진최하락'] : 
                tac['진최하락'] = tac['실최하락']; tac['최하일자'] = self.M['현재일자']

        if  self.M['현재날수'] > self.M['최장일수'] : 
            self.M['최장일수'] = self.M['현재날수'] 
            self.M['최장일자'] = self.M['현재일자']
        
    def rstCount(self,profit,key) :
        
        if not self.stat : return
        if  profit >= 0 : 
            if self.M['기본진행'] : self.D[key+'정익절'] += 1
            else : self.D[key+'회익절'] += 1  
        else : 
            if self.M['기본진행'] : self.D[key+'정손절'] += 1
            else : self.D[key+'회손절'] += 1   

    def commission(self,mm,opt) :

        fee = int(mm*0.07)/100
        if opt==2 : fee += round(mm*0.0008)/100
        self.D['총수수료'] += fee
        return fee
        
    def tax(self,mm) :

        return int(mm*0.22) 
        
    def rebalance(self)  :

        total = self.R['현재잔액'] + self.S['현재잔액'] + self.T['현재잔액']
        if  self.D['일밸런싱'] == 'on' :
            self.R['현재잔액'] = self.S['현재잔액'] = self.T['현재잔액'] = round( total /3,2)

        for tac in (self.V,self.R,self.S,self.T) :   
            tac['일매수금'] = int(tac['현재잔액']/self.M['분할횟수'])

        self.V['시초금액']  = self.V['현재잔액']
        self.R['시초금액']  = self.R['현재잔액']
        self.S['시초금액']  = self.S['현재잔액']
        self.T['시초금액']  = self.T['현재잔액'] 

        if  self.stat :
            pzero = my.sv(self.D['손익통계'][0][1])
            pbase = my.sv(self.D['손익통계'][-1][1])
            difft = total - pbase
            diffz = total - pzero
            diffp = difft/pbase * 100
            diff0 = diffz/pzero * 100

            if diffp <= self.D['손익저점'] : self.D['손익저점'] = diffp; self.D['저점날자'] = self.M['현재일자']

            diffd = self.D['월익통계'][-1][0][:7] 
            if   self.M['현재일자'][0:7] == diffd : self.D['월익통계'][-1][1] += difft 
            else : self.D['월익통계'].append([self.M['현재일자'][0:7],difft])
            color = "#F6CECE" if difft >= 0 else "#CED8F6"
            self.D['손익통계'].append([self.M['현재일자'],f"{total:,.2f}",f"{difft:,.2f}",f"{diffp:.2f}",color,self.M['기록시즌'],f"{diff0:.2f}"])
    
    def today_sell(self) :
        
        if  self.M['당일종가'] >= self.M['매도가격'] : 

            for tac in (self.V,self.R,self.S,self.T) : 
                tac['매도수량'] = tac['보유수량']
                tac['매도금액'] = tac['매도수량'] * self.M['당일종가']

    def today_buy_RST(self,tac,key) :
        
        days = 2 if key == 'R' else self.M['대기전략']

        if  self.M['현재날수'] == days and key == 'R':
            self.R['매수수량'] = my.ceil(self.R['기초수량'] * (self.M['비중조절'] + 1))
            self.R['거래코드'] = f"R{self.R['매수수량']}"
            self.R['매수금액'] = self.R['매수수량'] * self.M['당일종가'] 
            self.R['진행상황'] = '일반매수'

        if  tac['진행시작'] :
            tac['매수수량'] = tac['예정수량'] 
            tac['매수금액'] = tac['매수수량'] * self.M['당일종가']
            tac['거래코드'] = f"{key}{tac['매수수량']}" if tac['매수수량'] else ' '
            tac['진행상황'] = '일반매수'

        else :
            
            if  self.M['현재날수'] > days and self.M['당일종가'] <= tac['매수가격'] :
                tac['매수수량'] = self.chance_qty(tac['기초수량'],key)
                # 2024.07.15
                if tac['매수수량'] * tac['매수가격'] > tac['현재잔액'] : tac['매수수량'] = int(tac['현재잔액']/tac['매수가격'])
                tac['거래코드'] = f"{key}{tac['매수수량']}/{tac['기초수량']}" 
                tac['매수금액'] = tac['매수수량'] * self.M['당일종가']
                tac['진행시작'] = True
                tac['진행상황'] = '전략매수'

    def today_buy(self) :

        if  self.M['당일종가'] <= self.M['매수가격'] : 
            self.V['매수수량']  = self.V['예정수량']
            거래코드 = 'L' if self.V['매수단계'] == '매수제한' else 'B'
            self.V['거래코드']  = 거래코드 + str(self.V['매수수량']) if self.V['매수수량'] else ' '
            self.V['매수금액']  = self.V['매수수량'] * self.M['당일종가']
            self.V['진행상황']  = '일반매수'

            # R 전략, S 전략의 매수가격은 V전략 매수가격 보다 같거나 작다.
            self.today_buy_RST(self.R,'R')
            self.today_buy_RST(self.S,'S')
            self.today_buy_RST(self.T,'T')
            
    def chance_qty(self,basic_qty,key) :
            
            찬스수량 = 0   
            day_limit = 6 if key == 'R' else 7 
            day_count = min(self.M['현재날수']+self.M['찬스일가'],day_limit)
            for i in range(0,day_count) : 
                찬스수량 += my.ceil( basic_qty *(i*self.M['비중조절'] + 1))
            return 찬스수량   
    
    def tomorrow_buy_RST(self,tac,key)  :
        
        if  not tac['현재잔액'] : tac['예정수량'] = 0; return

        if  tac['진행시작'] :
            tac['예정수량'] = my.ceil(tac['기초수량'] * (self.M['현재날수']*self.M['비중조절'] + 1))

            if  tac['현재잔액'] < tac['예정수량'] * self.M['매수가격'] : 
                tac['예정수량'] = my.ceil(tac['기초수량'] * self.M['위매비중']) 
                tac['매수단계'] = '매수제한'
                
                if  tac['현재잔액'] < tac['예정수량'] * self.M['매수가격'] : 
                    tac['예정수량'] = 0
                    tac['매수단계'] = '매수중단'
                    
                    if  self.D['이밸런싱'] == 'on' and key in ('R','S') :
                        self.T['현재잔액'] += tac['현재잔액']
                        tac['현재잔액'] = 0.0
        
        else :  
            tac['매수가격'] = self.take_chance(tac)


    def tomorrow_buy(self) :

        self.M['매수가격'] = round(self.M['당일종가']*self.M['평단가치'],2)
        self.V['예정수량'] = my.ceil(self.V['기초수량'] * (self.M['현재날수']*self.M['비중조절'] + 1))
        
        if  self.V['현재잔액'] < self.V['예정수량'] * self.M['매수가격'] :
            self.V['예정수량'] = my.ceil(self.V['기초수량'] * self.M['위매비중'])
            self.V['매수단계'] = '매수제한' 

            if  self.V['현재잔액'] < self.V['예정수량'] * self.M['매수가격'] : 
                self.V['예정수량'] = 0
                self.V['매수단계'] = '매수중단'

    def tomorrow_sell(self) :

        # [기본진행]---------------------------------------------------------------------------------------------
        if  self.M['기본진행'] :
            
            if  self.V['매수단계'] not in ('매수제한','매수중단') :  
                self.M['매도가격'] = my.round_up(self.V['평균단가'] * self.M['첫매가치'])
                
                # R,S 보정 2024.03.18. / T 보정 2019.05.02. 2019.05.06. 
                for tac in (self.R,self.S,self.T) : 
                    if  tac['진행시작'] : 
                        self.M['매도가격'] = min(self.M['매도가격'],my.round_up(tac['평균단가'] * tac['매도보정']))
            else :
                self.M['매도가격'] = my.round_up(self.V['평균단가'] * self.M['둘매가치'])  
        
        # [전략진행]---------------------------------------------------------------------------------------------
        else :
           
            if  self.M['현재날수'] < self.M['매도대기'] :
                
                # R 보정 2024.06.18 -> 2024.07.10
                self.M['매도가격'] = min(my.round_up(self.V['평균단가'] * self.M['전략가치']),my.round_up(self.R['평균단가'] * self.R['위기탈출']))
                # S(=T) 보정 2021.08.30 -> 2021.10.12
                if  self.S['진행시작']  : 
                    self.M['매도가격'] = min(self.M['매도가격'],my.round_up(self.S['평균단가'] * self.M['회복탈출']))
            else :
                self.M['매도가격'] = my.round_up(self.V['평균단가'] * self.M['둘매가치'])
        
        # [최종결정]---------------------------------------------------------------------------------------------
        LPRICE = my.round_up(self.V['평균단가'] * self.M['강매가치'])
        
        if  self.M['현재날수'] >= self.M['강매시작'] : 
            self.M['매도가격']  = LPRICE

        # 2024.06.18 이후 폭락장 보정
        CPRICE = my.round_up(self.M['당일종가'] * self.M['종가상승']) if self.M['현재날수'] <= 10 else my.round_up(self.M['당일종가'] * self.M['종가탈출'])

        if  CPRICE >= LPRICE : 
            self.M['매도가격'] = min(self.M['매도가격'],CPRICE)    

    def tomorrow_step(self)   :
        
        self.tomorrow_buy()
        self.tomorrow_sell()
        self.tomorrow_buy_RST(self.R,'R')
        self.tomorrow_buy_RST(self.S,'S')
        self.tomorrow_buy_RST(self.T,'T')

        if  self.M['매수가격']>= self.M['매도가격'] : self.M['매수가격'] = self.M['매도가격'] - 0.01
        
    def take_chance(self,tac) :

        H = self.V['보유수량']
        n = self.V['예정수량']
        A = self.V['총매수금']
        if H == 0 : return 0
        p = tac['진입시점'] if self.M['기본진행'] else tac['회복시점']

        N = H + n
        k = N / (1+p/100)
        return round(A/(k-n),2)
    
    def new_day(self) :

        self.R['매수가격'] = 0.0;  self.R['진행시작'] = False; self.R['매수금액'] = 0.0; self.R['매수수량'] = 0
        self.S['매수가격'] = 0.0;  self.S['진행시작'] = False; self.S['매수금액'] = 0.0; self.S['매수수량'] = 0
        self.T['매수가격'] = 0.0;  self.T['진행시작'] = False; self.T['매수금액'] = 0.0; self.T['매수수량'] = 0

        self.set_value(['매도수량','매도금액','매수수량','매수금액','수익현황','현수익률','평균단가'],0)
            
        if  self.M['당일종가'] <  round(self.M['전일종가'] * self.M['큰단가치'],2) :
            
            self.M['기록시즌'] += 1
            self.M['현재날수']  = 1
            
            for tac in (self.V,self.R,self.S,self.T) : tac['기초수량']  = my.ceil(tac['일매수금']/self.M['전일종가'])
            
            for tac in (self.V,self.R) :
                tac['매수수량']  = tac['기초수량']
                tac['수익현황']  = tac['현수익률'] = 0.0
                tac['보유수량']  = tac['매수수량']
                tac['평균단가']  = self.M['당일종가'] 
                tac['매수금액']  = self.M['당일종가'] * tac['매수수량']
                tac['총매수금']  = tac['평가금액'] = tac['매수금액']
                tac['현재잔액'] -= tac['매수금액']
                tac['거래코드']  = f"{tac['매수수량']}" 
                if self.D['수료적용'] == 'on' : tac['수수료등'] = self.commission(tac['매수금액'],1); tac['현재잔액'] -= tac['수수료등']

            self.V['매수단계'] = '일반매수'
            self.V['진행상황'] = '첫날매수'
            self.M['첫날기록'] = False
 
            return True

        else : 
            return False
    
    
    def simulate(self,printOut=False) :

        for idx,BD in enumerate(self.B) : 
            if BD['add0'] < self.D['시작일자'] : idxx = idx; continue

            self.M['현재일자'] = BD['add0']
            self.M['당일종가'] = float(BD['add3'])
            self.M['종가변동'] = float(BD['add8']) 
            self.M['전일종가'] = float(self.B[idx-1]['add3'])  
            self.V['거래코드'] = self.R['거래코드'] = self.S['거래코드'] = self.T['거래코드'] = ' '
            self.set_value(['매도수량','매도금액','매수수량','매수금액','수익현황','현수익률'],0)
            
            # BD의 기록은 시작일자 보다 전의 데이타(종가기록 등)에서 시작하고, 당일종가가 전일에 비해 설정값 이상으로 상승 시 건너뛰기 위함
            if  idx == idxx + 1 or self.M['첫날기록'] : 
                if  self.new_day() : self.tomorrow_step(); self.increase_count(printOut); continue
                else : self.M['첫날기록'] = True; continue

            self.today_sell()
            self.today_buy()
            self.calculate()
            self.tomorrow_step()
            self.increase_count(printOut)
    
    def set_value(self,key,val) :

        for k in key :
            self.V[k] = val
            self.R[k] = val
            self.S[k] = val
            self.T[k] = val

    def result(self) :

        self.D['최장일수'] = self.M['최장일수']
        self.D['최장일자'] = self.M['최장일자']
        self.D['현재일자'] = self.M['현재일자']
        self.D['MDD1'] = f"{self.V['진최하락']:.2f}"; self.D['MDD_DAY1'] = self.V['최하일자'][2:]
        self.D['MDD2'] = f"{self.R['진최하락']:.2f}"; self.D['MDD_DAY2'] = self.R['최하일자'][2:]
        self.D['MDD3'] = f"{self.S['진최하락']:.2f}"; self.D['MDD_DAY3'] = self.S['최하일자'][2:]
        self.D['MDD4'] = f"{self.T['진최하락']:.2f}"; self.D['MDD_DAY4'] = self.T['최하일자'][2:]

        총매입금  = self.R['총매수금'] + self.S['총매수금'] + self.T['총매수금']
        총보유량  = self.R['보유수량'] + self.S['보유수량'] + self.T['보유수량']
        총평가금  = self.M['당일종가'] * 총보유량
        평가손익  = 총평가금 - 총매입금
        
        초기자본1 = float(self.D['일반자금'].replace(',','')); 최종자본1=self.V['평가금액']+self.V['현재잔액']; 최종수익1=최종자본1-초기자본1; self.D['v_profit']=round((최종수익1/초기자본1)*100,2)
        초기자본2 = float(self.D['기회자금'].replace(',','')); 최종자본2=self.R['평가금액']+self.R['현재잔액']; 최종수익2=최종자본2-초기자본2; self.D['r_profit']=round((최종수익2/초기자본2)*100,2)
        초기자본3 = float(self.D['안정자금'].replace(',','')); 최종자본3=self.S['평가금액']+self.S['현재잔액']; 최종수익3=최종자본3-초기자본3; self.D['s_profit']=round((최종수익3/초기자본3)*100,2)
        초기자본4 = float(self.D['생활자금'].replace(',','')); 최종자본4=self.T['평가금액']+self.T['현재잔액']; 최종수익4=최종자본4-초기자본4; self.D['t_profit']=round((최종수익4/초기자본4)*100,2)
        
        초기자본 = 초기자본2 + 초기자본3 + 초기자본4; 최종자본 = 최종자본2 + 최종자본3 + 최종자본4; 최종수익 = 최종자본 - 초기자본 
        self.D['profit_t'] = round((최종수익/초기자본) * 100,2)
        
        self.D['R_총매입금'] = f"{총매입금:,.2f}"
        self.D['R_총평가금'] = f"{총평가금:,.2f}"
        self.D['R_총보유량'] = f"{총보유량:,}"
        self.D['R_평가손익'] = f"{평가손익:,.2f}"
        self.D['R_평가익률'] = self.next_percent(총매입금,총평가금)

        self.D['R_초기자본'] = f"{초기자본:,.0f}"
        self.D['R_최종자본'] = f"{최종자본:,.2f}"
        self.D['R_최종수익'] = f"{최종수익:,.2f}"
        self.D['R_최종익률'] = f"{self.D['profit_t']:,.2f}"
        self.D['R_일반익률'] = f"{self.D['v_profit']:,.2f}"
        self.D['R_기회익률'] = f"{self.D['r_profit']:,.2f}"
        self.D['R_안정익률'] = f"{self.D['s_profit']:,.2f}"
        self.D['R_생활익률'] = f"{self.D['t_profit']:,.2f}"
        self.D['R_총경과일'] = f"{my.diff_day(self.D['시작일자'],self.D['종료일자']):,}"

        if self.chart and self.D['c_date'] : self.D['s_date'] = self.D['c_date'][0]; self.D['e_date'] = self.D['c_date'][-1]

        if  self.stat :
            self.D['월별구분'] = [ x[0] for x in self.D['월익통계']][-28:]
            self.D['월별이익'] = [ round(x[1]) for x in self.D['월익통계']][-28:]

            if  self.D['월별이익'][0] == 0 :
                self.D['월별구분'].pop(0)
                self.D['월별이익'].pop(0)

            monthly_total = sum(self.D['월별이익'])
            monthly_lenth = len(self.D['월별이익'])
            
            if monthly_lenth : 
                self.D['월별구분'].append('AVG')
                self.D['월별이익'].append(round(monthly_total/monthly_lenth))

            self.D['손익저점'] = f"{self.D['손익저점']:.2f}"

            # 손익통계 분석
            asis = [float(x[3]) for x in self.D['손익통계']]
            asis = asis[1:]
    
            asis_c = len(asis)
            asis_p = [x for x in asis if x >= 0.0 ]
            asis_u = [x for x in asis if x < 0.0]
            asispc = len(asis_p)
            asisuc = len(asis_u)
            asispm = sum(asis_p) / asispc if asispc else 0.0
            asisum = sum(asis_u) / asisuc if asisuc else 0.0

            win_p = asispc / asis_c * 100 if asis_c else 0.0

            self.D['R_총매도수'] = asis_c; self.D['R_총익절수'] = asispc; self.D['R_총손절수'] = asisuc
            self.D['R_총익승률'] = f"{win_p:.2f}" ; self.D['R_익절평균'] = f"{asispm:.2f}"; self.D['R_손절평균'] = f"{asisum:.2f}"        

    def get_start(self,s='',e='') :

        self.D['종목코드']  = 'SOXL'

        if not s : s = self.D['시작일자']
        if not e : e = self.D['종료일자']
        
        old_date = my.dayofdate(s,-7)[0]  
        lst_date = self.DB.one("SELECT max(add0) FROM h_stockHistory_board") 
        
        if old_date < '2010-03-15' : old_date = '2010-03-15'; s = '2010-03-22'
        
        if e > lst_date : e = lst_date
        if s > e : s = '2020-01-02'; e = lst_date
        
        self.D['시작일자'] = s
        self.D['종료일자'] = e
          
        self.DB.tbl,self.DB.wre,self.DB.odr = ("h_stockHistory_board",f"add1='{self.D['종목코드']}' AND add0 BETWEEN '{old_date}' AND '{e}'","add0")
        self.B = self.DB.get('add0,add3,add8,add9,add10') # 날자, 종가, 증감, 연상,연하 

    def increase_count(self,printOut=False) :
        
        if not self.V['보유수량'] and not self.V['매도수량']: return
        if printOut : self.print_backtest()
        self.M['현재날수'] +=1
        
    def init_value(self) :

        if '비중조절' not in self.M :
            
            ST = self.DB.parameters_dict('매매전략/VRS')
            
            self.M['비중조절']  = ST['01001']  
            self.M['평단가치']  = ST['00300']  
            self.M['큰단가치']  = ST['00200']  
            self.M['첫매가치']  = ST['00400']  
            self.M['둘매가치']  = ST['00500']  
            self.M['강매시작']  = ST['00800']  
            self.M['강매가치']  = ST['00700']  
            self.M['위매비중']  = ST['01000']  
            self.M['대기전략']  = ST['01003']
            self.R['매도보정']  = ST['01100']
            self.S['매도보정']  = ST['01200']
            self.T['매도보정']  = ST['01400']
            self.R['위기탈출']  = ST['01500']
            self.M['종가상승']  = ST['01600'] 
            self.M['종가탈출']  = ST['01601']
             
            self.M['매도대기']  = ST['00600']  
            self.M['전략가치']  = ST['00900']  
            self.M['회복탈출']  = ST['00901']  
            self.M['분할횟수']  = ST['00100']  
            self.M['찬스일가']  = ST['01002']  
            self.M['일반보드']  = ST['03500']
            self.M['기회보드']  = ST['03501'] if self.op=='rst' else ST['03701']
            self.M['안정보드']  = ST['03502'] if self.op=='rst' else ST['03702']
            self.M['생활보드']  = ST['03503'] if self.op=='rst' else ST['03703']

        self.M['기본진행']  = True  
        self.V['매수단계']  = self.R['매수단계'] = self.S['매수단계'] = self.T['매수단계'] = '일반매수'
        self.V['진행상황']  = self.R['진행상황'] = self.S['진행상황'] = self.T['진행상황'] = '매수대기'
        self.M['기록시즌']  = 0
        self.D['총수수료'] = 0.0
        
        self.R['진입시점']  = float(self.D['기회시점']) if '기회시점' in self.D else ST['02100']
        self.R['회복시점']  = float(self.D['기회회복']) if '기회회복' in self.D else ST['02200']
        self.S['진입시점']  = float(self.D['안정시점']) if '안정시점' in self.D else ST['02300']
        self.S['회복시점']  = float(self.D['안정회복']) if '안정회복' in self.D else ST['02400']
        self.T['진입시점']  = float(self.D['생활시점']) if '생활시점' in self.D else ST['02401']
        self.T['회복시점']  = float(self.D['생활회복']) if '생활회복' in self.D else ST['02402']

        if '가상손실' in self.D  and  self.D['가상손실'] == 'on' : self.M['기본진행']  = False     
        if '수료적용' not in self.D : self.D['수료적용']  = 'on' 
        if '세금적용' not in self.D : self.D['세금적용']  = 'off'
        if '일밸런싱' not in self.D : self.D['일밸런싱']  = 'on'
        if '이밸런싱' not in self.D : self.D['이밸런싱']  = 'on'
        if '랜덤종가' not in self.D : self.D['랜덤종가']  = 'off'
            
        if '일반자금' not in self.D : self.D['일반자금']  = ST['05100']
        if '기회자금' not in self.D : self.D['기회자금']  = ST['05200']
        if '안정자금' not in self.D : self.D['안정자금']  = ST['05300']
        if '생활자금' not in self.D : self.D['생활자금']  = ST['05400']

        self.V['현재잔액']  = self.V['시초금액'] = my.sv(self.D['일반자금'])
        self.R['현재잔액']  = self.R['시초금액'] = my.sv(self.D['기회자금'])
        self.S['현재잔액']  = self.S['시초금액'] = my.sv(self.D['안정자금'])
        self.T['현재잔액']  = self.T['시초금액'] = my.sv(self.D['생활자금'])
        
        self.V['일매수금']  = int(self.V['현재잔액'] / self.M['분할횟수'])
        self.R['일매수금']  = int(self.R['현재잔액'] / self.M['분할횟수'])
        self.S['일매수금']  = int(self.S['현재잔액'] / self.M['분할횟수'])
        self.T['일매수금']  = int(self.T['현재잔액'] / self.M['분할횟수'])    
        
        self.M['거래코드']  = ' '
        self.M['최장일자']  = ' '
        self.M['현재날수']  = 1
        self.M['최장일수']  = 0   # 최고 오래 지속된 시즌의 일수
        
        self.M['첫날기록']  = False
        self.R['진행시작']  = self.S['진행시작'] = self.T['진행시작']  = False

        self.M['전일종가']  = 0.0
        
        self.set_value(['매수수량','매도수량','예정수량','보유수량'],0)
        self.set_value(['매수금액','매도금액','실현수익','총매수금','평균단가','수익현황','현수익률','평가금액','매수가격','수수료등'],0.0)

        self.set_value(['진최하락'],0)
        self.set_value(['최하일자'],'')

        if  self.chart : # 챠트작성
            
            self.D['TR'] = []
            self.D['c_date'] = []
            self.D['clse_p'] = []
            self.D['avge_r'] = []; self.D['avge_s'] = []; self.D['avge_t'] = []

        # 통계자료
        if  self.stat :

            self.D['totalV'] = []
            self.D['일정익절'] = 0; self.D['기정익절'] = 0; self.D['안정익절'] = 0; self.D['생정익절'] = 0
            self.D['일정손절'] = 0; self.D['기정손절'] = 0; self.D['안정손절'] = 0; self.D['생정손절'] = 0
            self.D['일회익절'] = 0; self.D['기회익절'] = 0; self.D['안회익절'] = 0; self.D['생회익절'] = 0
            self.D['일회손절'] = 0; self.D['기회손절'] = 0; self.D['안회손절'] = 0; self.D['생회손절'] = 0

            self.D['손익통계'] = [[self.D['시작일자'],f"{self.R['현재잔액']+self.S['현재잔액']+self.T['현재잔액']:,.2f}",'0.00','0.00',"#F6CECE",'','0.00']]
            self.D['월익통계'] = [[self.D['시작일자'][:7],0.00]]
            self.D['손익저점'] = 100.0
            self.D['저점날자'] = ''
            

    def nextStep(self) :

        self.D['N_일자'] = self.M['현재날수'] 
        self.D['N_종가'] = self.M['당일종가']
        self.D['N_변동'] = round(self.M['종가변동'],2)
        self.D['N_단계'] = self.V['매수단계']

        if  self.R['보유수량'] :
            self.D['NT-AVG'] = round((self.R['총매수금']+self.S['총매수금']+self.T['총매수금'])/(self.R['보유수량']+self.S['보유수량']+self.T['보유수량']),2)
        else :
            self.D['NT-AVG'] = '0.00'
        self.D['LPRICE'] = my.round_up(self.V['평균단가'] * self.M['강매가치'])
        self.D['CPRICE'] = my.round_up(self.M['당일종가'] * self.M['종가상승']) if self.D['N_일자']-1  <= 10 else my.round_up(self.M['당일종가'] * self.M['종가탈출'])

        # 변수초기화
        self.D['N_기회도종비'] = self.D['N_안정도종비'] = self.D['N_생활도종비'] = ''

        if  self.M['첫날기록'] : 

            self.D['N_일자'] = 1 
            self.D['N_일반기초'] = my.ceil(self.V['일매수금']/self.M['당일종가'])
            self.D['N_기회기초'] = my.ceil(self.R['일매수금']/self.M['당일종가'])
            self.D['N_안정기초'] = my.ceil(self.S['일매수금']/self.M['당일종가'])
            self.D['N_생활기초'] = my.ceil(self.T['일매수금']/self.M['당일종가'])
            
            self.D['N_일반매수가'] = self.D['N_기회매수가'] = round(self.M['당일종가'] * self.M['큰단가치'],2)
            self.D['N_안정매수가'] = self.D['N_생활매수가'] = 0.0
            
            self.D['N_일반매수량'] = self.D['N_일반기초']
            self.D['N_기회매수량'] = self.D['N_기회기초']
            self.D['N_안정매수량'] = self.D['N_생활매수량'] = 0

            self.D['N_일반매도량'] = self.D['N_기회매도량'] = self.D['N_안정매도량'] = self.D['N_생활매도량'] = 0

            self.D['N_일반매도가'] = self.D['N_기회매도가'] = self.D['N_안정매도가'] = self.D['N_생활매도가'] = 0.0
            self.D['N_일반종대비'] = self.D['N_기회종대비'] = self.next_percent(self.M['당일종가'],self.D['N_기회매수가'])
            self.D['N_안정종대비'] = self.D['N_생활종대비'] = self.D['N_공통종대비'] = ''
            
        else : 
            self.next_buy_RST()

            self.D['N_일반기초'] = self.V['기초수량']
            self.D['N_기회기초'] = self.R['기초수량']
            self.D['N_안정기초'] = self.S['기초수량']
            self.D['N_생활기초'] = self.T['기초수량']

            self.V['진행시작'] = True
            
            for (tac,key) in [(self.V,'일반'),(self.R,'기회'),(self.S,'안정'),(self.T,'생활')] : 
                self.D['N_'+key+'매수량'] = tac['매수수량']
                self.D['N_'+key+'매수가'] = self.M['매수가격'] if tac['진행시작'] else tac['매수가격']
                self.D['N_'+key+'평대비'] = self.next_percent(tac['평균단가'],self.D['N_'+key+'매수가'])
                self.D['N_'+key+'종대비'] = self.next_percent(self.M['당일종가'],self.D['N_'+key+'매수가'])
                self.D['N_'+key+'매수가'] = f"{self.D['N_'+key+'매수가']:,.2f}"

                self.D['N_'+key+'매도량'] = tac['보유수량']
                self.D['N_'+key+'매도가'] = f"{self.M['매도가격']:.2f}"
                self.D['N_'+key+'도평비'] = self.next_percent(tac['평균단가'],self.M['매도가격'])
                self.D['N_'+key+'도종비'] = self.next_percent(self.M['당일종가'],self.M['매도가격'])


    def next_percent(self,a,b) :
        
        if not a : return ''
        return f"{(b/a-1)*100:.2f}"
    
    def next_buy_RST(self) :

        self.V['매수수량']  = my.ceil(self.V['기초수량'] * ((self.M['현재날수']-1)*self.M['비중조절'] + 1))

        if  self.V['현재잔액'] < self.V['매수수량'] * self.M['매수가격'] : 
            self.V['매수수량'] = my.ceil(self.V['기초수량'] * self.M['위매비중'])
            if  self.V['현재잔액'] < self.V['매수수량'] * self.M['매수가격'] : self.V['예정수량'] = 0
            
        for (tac,key) in [(self.R,'R'),(self.S,'S'),(self.T,'T')] :
            # 이틀 째까지는 전략 V 와 같은 패턴
            days = 2 if key == 'R' else self.M['대기전략']
            if  self.M['현재날수'] == days and key == 'R' : self.R['매수수량'] = my.ceil(self.R['기초수량'] * (self.M['비중조절'] + 1))

            if  tac['진행시작'] : tac['매수수량'] = tac['예정수량'] 

            else :
                if  self.M['현재날수'] > days  :
                    
                    tac['매수가격'] = self.take_chance(tac)
                    if tac['매수가격'] > self.M['매수가격'] : tac['매수가격'] = self.M['매수가격']
                    
                    tac['매수수량'] = self.chance_qty(tac['기초수량'],key)
                    if tac['매수수량'] * tac['매수가격'] > tac['현재잔액'] : tac['매수수량'] = int(tac['현재잔액']/tac['매수가격'])
                else :
                    tac['매수가격'] = self.M['매수가격']
    # ------------------------------------------------------------------------------------------------------------------------------------------
    # same with xtask END
    # ------------------------------------------------------------------------------------------------------------------------------------------

    def print_backtest(self) :

        tx = {}
        #--------------------------------------------------------
        tx['현재날수'] = self.M['현재날수'] 
        tx['기록시즌'] = self.M['기록시즌']
        tx['기록일자'] = self.M['현재일자'][2:]
        tx['당일종가'] = f"<span class='clsp{self.M['기록시즌']}'>{round(self.M['당일종가'],4):,.2f}</span>"
        clr = "#F6CECE" if self.M['종가변동'] >= 0 else "#CED8F6"
        tx['종가변동'] = f"<span style='color:{clr}'>{self.M['종가변동']:,.2f}</span>"
        #--------------------------------------------------------
        tx['일반진행'] = f"{round(self.V['매도금액'],4):,.2f}" if self.V['매도금액'] else self.V['거래코드']
        tx['일반평균'] = f"{round(self.V['평균단가'],4):,.4f}" if self.V['평균단가'] else ""
        clr = "#F6CECE" if self.V['현수익률'] > 0 else "#CED8F6"
        tx['일반수익'] = f"<span style='color:{clr}'>{round(self.V['수익현황'],4):,.2f}</span>"
        tx['일반익률'] = f"<span style='color:{clr}'>{round(self.V['현수익률'],4):,.2f}</span>"
        tx['일반잔액'] = f"{self.V['현재잔액']:,.2f}"
        #--------------------------------------------------------
        for tac,key,key2 in [(self.R,'기회','r'),(self.S,'안정','s'),(self.T,'생활','t')] :
            tx[key+'진행'] = f"{round(tac['매도금액'],4):,.2f}" if tac['매도금액'] else tac['거래코드']
            tx[key+'평균'] = f"<span class='avg{key2}{self.M['기록시즌']}'>{round(tac['평균단가'],4):,.4f}</span>" if tac['평균단가'] else f"<span class='avg{key2}{self.M['기록시즌']}'></span>"
            clr = "#F6CECE" if tac['현수익률'] > 0 else "#CED8F6"
            tx[key+'수익'] = f"<span style='color:{clr}'>{round(tac['수익현황'],4):,.2f}</span>" 
            tx[key+'익률'] = f"<span style='color:{clr}'>{round(tac['현수익률'],4):,.2f}</span>" 
            tx[key+'잔액'] = f"{tac['현재잔액']:,.2f}"
        #--------------------------------------------------------
        tx['진행상황'] = self.V['진행상황']
            
        self.D['TR'].append(tx)
        
        self.D['clse_p'].append(self.M['당일종가'])

        if avg_r := round(self.R['평균단가'],2) : self.D['avge_r'].append(avg_r)
        else : self.D['avge_r'].append('null')
        if avg_s := round(self.S['평균단가'],2) : self.D['avge_s'].append(avg_s)
        else : self.D['avge_s'].append('null') 
        if avg_t := round(self.T['평균단가'],2) : self.D['avge_t'].append(avg_t)
        else : self.D['avge_t'].append('null')     
        
        self.D['c_date'].append(self.M['현재일자'][2:])
        self.D['totalV'].append(round(self.R['현재잔액']+self.R['평가금액']+self.S['현재잔액']+self.S['평가금액']+self.T['현재잔액']+self.T['평가금액'],0))
        

    def get_simResult(self,start='',end='',result=False) :
        
        self.D['종료일자'] = self.DB.one("SELECT max(add0) FROM h_stockHistory_board") if not end else end
        self.D['시작일자'] = my.dayofdate(self.D['종료일자'],delta=-365*2)[0] if not start else start 
        
        self.get_start()
        self.init_value()
        self.simulate()
        if result : self.result()
    
    def get_thisYearResult(self) :

        end   = my.timestamp_to_date(opt=7)
        start = end[:4]+'-01-01'
        self.get_simResult(start,end,result=True) 
        return self.D['R_최종익률']
    
    def do_viewChart(self) :

        self.chart = True
        self.stat  = True
        self.get_start_virtual() if self.D['랜덤종가'] == 'on' else self.get_start()
        self.init_value()
        self.simulate(printOut=True)
        self.result()
        self.nextStep()

    def put_initCapital(self,V,R,S,T) :
        
        self.D['일반자금'] = f"{V:,.2f}" 
        self.D['기회자금'] = f"{R:,.2f}" 
        self.D['안정자금'] = f"{S:,.2f}" 
        self.D['생활자금'] = f"{T:,.2f}" 
        
    def get_dateList(self,start_date,end_date) :
        
        qry = f"SELECT add0 FROM h_stockHistory_board WHERE add1='SOXL' AND add0 BETWEEN '{start_date}' AND '{end_date}' ORDER BY add0"
        return self.DB.col(qry)

    
    def get_syncData(self,backto='',origin=False) :
        
        s_date = my.timestamp_to_date(opt=7) if not backto else backto

        order = 'add0 ASC' if origin else 'add0 DESC' 
        V_board = self.DB.parameter('03500')
        R_board = self.DB.parameter('03501') if self.op=='rst' else self.DB.parameter('03701')
        V_date  = self.DB.one(f"SELECT add0 FROM {V_board} WHERE add0 < '{s_date}' and sub12='1' ORDER BY {order} LIMIT 1")
        V_money = self.DB.one(f"SELECT add3 FROM {V_board} WHERE add0 < '{V_date}' and sub12='0' ORDER BY {order} LIMIT 1")
        R_money = self.DB.one(f"SELECT add3 FROM {R_board} WHERE add0 < '{V_date}' and sub12='0' ORDER BY {order} LIMIT 1")
        V_mode  = self.DB.one(f"SELECT sub7 FROM {V_board} WHERE add0 = '{V_date}'")
        
        return (V_date,float(V_money),float(R_money),float(V_mode))
    
    def get_nextStrategy(self,tac) :
        
        (V_date,V_money,R_money,V_mode) = self.get_syncData()
        self.put_initCapital(V_money,R_money,R_money,R_money)
        if V_mode : self.D['가상손실'] = 'on'
        self.get_simResult(V_date)
 
        self.nextStep()
        tN = {'V':'일반','R':'기회','S':'안정','T':'생활'}
        return {'buy_p':self.D['N_'+tN[tac]+'매수가'],'buy_q':self.D['N_'+tN[tac]+'매수량'],'yx_b': self.D['N_'+tN[tac]+'종대비'],
                'sel_p':self.D['N_'+tN[tac]+'매도가'],'sel_q':self.D['N_'+tN[tac]+'매도량'],'yx_s': self.D['N_'+tN[tac]+'도종비']}
      

    def do_tacticsLog(self,theDate) :
        
        (V_date,V_money,R_money,V_mode) = self.get_syncData(theDate)
        if V_mode : self.D['가상손실'] = 'on'
        self.put_initCapital(V_money,R_money,R_money,R_money)
        self.get_simResult(V_date,theDate)
        

    def get_tacticLog(self,theDate,tactic) :
        
        if   tactic == 'V' : tac = self.V ; RST_board = self.M['일반보드']
        elif tactic == 'R' : tac = self.R ; RST_board = self.M['기회보드']
        elif tactic == 'S' : tac = self.S ; RST_board = self.M['안정보드']
        elif tactic == 'T' : tac = self.T ; RST_board = self.M['생활보드']

        preDate = self.DB.one(f"SELECT max(add0) FROM {RST_board} WHERE add0 < '{theDate}'")
        if not preDate : return 
        LD = self.DB.line(f"SELECT * FROM {RST_board} WHERE add0='{preDate}'")
        LD['Update'] = float(LD['add1'])==0 and float(LD['add2'])==0 and float(LD['add11'])==0 and float(LD['add12'])==0 and int(LD['add9'])==0
        
        LD['add0'] = theDate
        LD['wdate']= LD['mdate']= my.now_timestamp()
   
        LD['add3'] = f"{tac['현재잔액']:.2f}"
        LD['add4'] = f"{tac['현재잔액']/(tac['현재잔액'] + tac['평가금액']) * 100:.2f}"
        
        LD['add11'] = f"{tac['매수금액']:.2f}"
        LD['add12'] = f"{tac['매도금액']:.2f}"
        LD['add5']  = tac['매수수량'] 
        if tac['매도금액'] : LD['add5'] = -tac['매도수량']
        LD['add8']  = f"{tac['현수익률']:.2f}"
        
        LD['add14'] = self.M['당일종가']
        LD['add15'] = f"{tac['평가금액']:.2f}"
        LD['add9']  = tac['보유수량']
        LD['add16'] = f"{tac['평가금액']/(tac['현재잔액'] + tac['평가금액']) * 100:.2f}"
        
        LD['add7']  = f"{tac['평균단가']:.4f}"
        LD['sub15'] = f"{float(LD['sub15'])+tac['매도금액']:.2f}"
        LD['sub14'] = f"{float(LD['sub14'])+tac['매수금액']:.2f}"
        LD['add6']  = f"{tac['총매수금']:.2f}"
        
        LD['sub5'], LD['sub6'] = self.DB.oneline(f"SELECT add9,add10 FROM h_stockHistory_board WHERE add0='{theDate}'")
        LD['add20'] = self.M['종가변동']
        LD['add18'] = f"{tac['수익현황']:.2f}"
        
        LD['sub1']  = int(LD['sub1']) + 1 if tac['매도금액'] else LD['sub1'] 
        LD['sub4']  = tac['일매수금']
        
        LD['sub12']  = 0 if self.M['첫날기록'] else self.M['현재날수'] - 1 
        
        LD['add17']  = f"{tac['현재잔액'] +tac['평가금액']:.2f}"
        LD['sub7']   = LD['sub7']
        if  tactic == 'V' and self.V['매도금액'] : 
            LD['sub7'] = '0.00' if self.V['실현수익'] > 0 else self.M['전략가치']
        
        LD['sub29']  = '전량매도' if self.M['첫날기록'] else tac['진행상황'] 
        LD['sub30']  = f"{tac['수수료등']:.2f}" if LD['add5'] else '0.00'
        LD['sub31']  = f"{tac['수수료등'] + float(LD['sub31']):.2f}" if LD['add5'] else LD['sub31']
        if  self.M['현재날수'] -1 == 1 : 
            LD['sub29'] = '첫날매수'
            LD['sub31'] = LD['sub30']
        if  not tac['보유수량'] and not tac['매도금액'] : LD['sub31'] = '0.00'
        if  not tac['매수금액'] and not tac['매도금액'] and LD['sub12'] : LD['sub29'] = '매도대기'
        
        LD['content'] ="<div><p>Written by Auto</p></div>"
        del LD['no']
        return LD
    
    def get_nextStrategyLog(self,tac) :

        nX = {'V':'일반','R':'기회','S':'안정','T':'생활'}
        nS = {'sub18':self.D['N_'+nX[tac]+'기초'],'sub2' :self.D['N_'+nX[tac]+'매수량'],'sub3':self.D['N_'+nX[tac]+'매도량'],
              'sub19':self.D['N_'+nX[tac]+'매수가'],'sub20':self.D['N_'+nX[tac]+'매도가']}
        return nS
    
    def get_backDateStat(self) :

        sx = {}

        sx['시작일자'] = self.D['시작일자']
        sx['경과일자'] = self.D['R_총경과일']

        sx['최종수익'] = self.D['R_최종수익']
        sx['종수익률'] = self.D['R_최종익률']
        sx['최장기록'] = f"{self.D['최장일수']}<span style='color:gray'>({self.D['최장일자'][2:]})</span>"

        sx['기회최락'] = f"{self.D['MDD2']}<span style='color:gray'>({self.D['MDD_DAY2']})</span>"    if self.D['MDD_DAY2'] else ''
        sx['안정최락'] = f"{self.D['MDD3']}<span style='color:gray'>({self.D['MDD_DAY3']})</span>"    if self.D['MDD_DAY3'] else ''
        sx['생활최락'] = f"{self.D['MDD4']}<span style='color:gray'>({self.D['MDD_DAY4']})</span>"    if self.D['MDD_DAY4'] else ''
        sx['저점기록'] = f"<b>{self.D['손익저점']}</b><span style='color:gray'>({self.D['저점날자'][2:]})</span>" if self.D['저점날자'] else ''
        
        if float(self.D['MaxDP']) >= float(self.D['손익저점']) : self.D['MaxDP'] = self.D['손익저점']; self.D['MaxDD'] = self.D['시작일자']

        sx['게임횟수'] = f"{self.D['R_총매도수']}<span style='color:gray'>({self.D['R_총익절수']}/{self.D['R_총손절수']})</span>"
        sx['게임승률'] = self.D['R_총익승률']
        sx['게임익평'] = self.D['R_익절평균']
        sx['게임손평'] = self.D['R_손절평균']

        sx['기회갯수'] = f"{self.D['기정익절']}-{self.D['기정손절']} : {self.D['기회익절']}-{self.D['기회손절']}"
        sx['안정갯수'] = f"{self.D['안정익절']}-{self.D['안정손절']} : {self.D['안회익절']}-{self.D['안회손절']}"
        sx['생활갯수'] = f"{self.D['생정익절']}-{self.D['생정손절']} : {self.D['생회익절']}-{self.D['생회손절']}"

        return sx

    def do_viewStat(self,opt) :

        self.chart = False
        self.stat  = True
        B = self.get_dateList(self.D['시작일자'],self.D['종료일자'])
        
        self.D['MaxDP'] = 100.0
        self.D['MaxDD'] = ''
        self.D['SR'] = []
        
        last_day = self.DB.one("SELECT add0 FROM h_stockHistory_board ORDER BY add0 DESC LIMIT 1")
        end = ''
        
        for b in B :
            if opt == '1year' : 
                year1 = my.dayofdate(b,365)[0]
                if  year1 < last_day : 
                    end = year1
                else :
                    end = '' 
                    break
            self.get_start(b,end)
            self.init_value()
            self.simulate()
            self.result()
            self.D['SR'].append(self.get_backDateStat())
            
        if  self.D['SR'] : 
            self.D['SR'].pop()
        
            self.D['chart_dte'] = [x['시작일자'] for x in self.D['SR']]
            self.D['chart_val'] = [my.sv(x['종수익률']) for x in self.D['SR']]
            self.D['chart_dte'].reverse()
            self.D['chart_val'].reverse()
            
            if  opt == '1year' :
                self.D['over_100p'] = [x for x in self.D['chart_val'] if x > 100] 
                totcnt = len(self.D['chart_val'])
                cnt100 = len(self.D['over_100p'])
                over_p = cnt100/totcnt*100
                self.D['over100st'] = f"{cnt100} / {totcnt} ( {over_p:.1f}% )"

# ------------------------------------------------------------------------------------
    def get_start_virtual(self) :

        old_date = my.dayofdate(self.D['시작일자'],-7)[0]
        qry = f"SELECT add0 FROM h_stockHistory_board WHERE add1='SOXL' AND add0 BETWEEN '{old_date}' AND '{self.D['종료일자']}'"
        B = self.DB.col(qry) 
        cnt = len(B)
        qry = f"SELECT add8 FROM h_stockHistory_board WHERE add0 >='2010-05-01' ORDER BY add0 DESC"
        R = self.DB.col(qry)

        C = [10.0]*cnt; P=[0.0]*cnt; self.B = []
        P = sample(R,cnt)

        for i in range(1,cnt) :
            r = float(P[i])/100
            C[i] = round(C[i-1]*(1+r),2)
            self.B.append({'add0':B[i],'add3':C[i],'add8':P[i]})
        
