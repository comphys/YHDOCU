from datetime import date
import system.core.my_utils as my

class RST :

    def __init__(self,SYS) :
        self.SYS  = SYS
        self.info = SYS.info
        self.D    = SYS.D
        self.DB   = SYS.DB

        self.B = {}
        self.V = {}
        self.R = {}
        self.S = {}
        self.T = {}
        self.M = {}
  

    def calculate_sub(self,tac,key) :
        
        if  tac['매수수량'] : 
            tac['현재잔액'] -= tac['매수금액']
            tac['보유수량'] += tac['매수수량']
            tac['총매수금'] += tac['매수금액']
            tac['평균단가'] =  tac['총매수금'] / tac['보유수량'] 
            if self.D['수료적용'] == 'on' : tac['현재잔액'] -=  self.commission(tac['매수금액'],1)
        
        if  tac['매도수량'] :
            tac['실현수익']  = (self.M['당일종가'] - tac['평균단가']) * tac['매도수량']
            tac['보유수량'] -=  tac['매도수량'];  tac['현재잔액'] += tac['매도금액']; tac['총매수금'] = 0.00
            tac['수익현황']  =  tac['실현수익']
            
            if self.D['수료적용'] == 'on' : tac['현재잔액'] -=  self.commission(tac['매도금액'],2)
            if self.D['세금적용'] == 'on' : tac['현재잔액'] -=  self.tax(tac['실현수익'])
            
            self.rstCount(tac['실현수익'],key)

        tac['평가금액'] =  self.M['당일종가'] * tac['보유수량'] 
        tac['현수익률'] = (self.M['당일종가'] / tac['평균단가'] -1) * 100  if tac['평균단가'] else 0.00

    def calculate(self)  :
        
        self.calculate_sub(self.T,'생')
        self.calculate_sub(self.S,'안')
        self.calculate_sub(self.R,'기')
        self.calculate_sub(self.V,'일')
        
        if  self.V['매도수량'] :
            self.M['첫날기록'] = True
            self.M['매수단계'] = '일반매수'
            self.M['회복전략'] = self.M['손실회수']
            self.set_value(['평균단가'],0.0)
            self.rebalance() 
            
        else  : 
            for tac in [self.V,self.R,self.S,self.T] : tac['수익현황'] = tac['평가금액'] - tac['총매수금']

        self.realMDD()


    def realMDD(self) :

        for tac in (self.V,self.R,self.S,self.T) :
            tac['실최하락'] = (tac['평가금액']-tac['총매수금']) / (tac['현재잔액'] + tac['총매수금']) * 100
            if  tac['실최하락'] < tac['진최하락'] : 
                tac['진최하락'] = tac['실최하락']; tac['최하일자'] = self.M['현재일자']

        if  self.M['현재날수'] > self.M['최대일수'] : 
            self.M['최대일수'] = self.M['현재날수'] 
            self.M['최대날자'] = self.M['현재일자']
        
    def rstCount(self,profit,key) :

        if  profit >= 0 : 
            if self.M['회복전략'] : self.D[key+'회익절'] += 1
            else : self.D[key+'정익절'] += 1  
        else : 
            if self.M['회복전략'] : self.D[key+'회손절'] += 1
            else : self.D[key+'정손절'] += 1   

    def commission(self,mm,opt) :

        fee = int(mm*0.07)/100
        if opt==2 : fee += round(mm*0.0008)/100
        return fee
        
    def tax(self,mm) :

        return int(mm*0.22) 
        
        
    def rebalance(self)  :

        total = self.R['현재잔액'] + self.S['현재잔액'] + self.T['현재잔액']
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
    
        if  self.D['일밸런싱'] == 'on' :
            self.R['현재잔액'] = self.S['현재잔액'] = self.T['현재잔액'] = round( total /3,2)

        for tac in (self.V,self.R,self.S,self.T) :   
            tac['일매수금'] = int(tac['현재잔액']/self.M['분할횟수']) 

        color = "#F6CECE" if difft >= 0 else "#CED8F6"
        self.D['손익통계'].append([self.M['현재일자'],f"{total:,.2f}",f"{difft:,.2f}",f"{diffp:.2f}",color,self.M['기록시즌'],f"{diff0:.2f}"])


    def today_sell(self) :
        
        if  self.M['당일종가'] >= self.M['매도가격'] : 
            for tac in (self.V,self.R,self.S,self.T) : 
                tac['매도수량'] = tac['보유수량']
                tac['매도금액'] = tac['매도수량'] * self.M['당일종가']

            self.M['진행상황']  = '익절매도' 
            self.M['회복전략']  = self.M['손실회수']
            
            if  self.M['당일종가'] < self.V['평균단가'] : 
                self.M['진행상황'] = '손절매도'
                self.M['손실회수'] = True
            else :
                self.M['손실회수'] = False


    def today_buy_RST(self,tac,key) :

        if  self.M['현재날수'] == 2 and key == 'R':
            self.R['매수수량'] = my.ceil(self.R['기초수량'] * (self.M['비중조절'] + 1))
            self.R['거래코드'] = f"R{self.R['매수수량']}"
            self.R['매수금액'] = self.R['매수수량'] * self.M['당일종가'] 

        if  tac['진행시작'] :
            tac['매수수량'] = tac['구매수량'] 
            tac['매수금액'] = tac['매수수량'] * self.M['당일종가']
            tac['거래코드'] = f"{key}{tac['매수수량']}" if tac['매수수량'] else ' '

        else :
            if  self.M['현재날수'] > 2 and self.M['당일종가'] <= tac['매수가격'] :
                tac['매수수량'] = self.chance_qty(tac['기초수량'],key)
                # 2024.07.15
                if tac['매수수량'] * tac['매수가격'] > tac['현재잔액'] : tac['매수수량'] = int(tac['현재잔액']/tac['매수가격'])
                tac['거래코드'] = f"{key}{tac['매수수량']}/{tac['기초수량']}" 
                tac['매수금액'] = tac['매수수량'] * self.M['당일종가']
                tac['진행시작'] = True


    def today_buy(self) :

        if  self.M['당일종가'] <= self.M['매수가격'] : 
            self.V['매수수량']  = self.V['구매수량']
            거래코드 = 'L' if self.M['매수단계'] == '매수제한' else 'B'
            self.V['거래코드']  = 거래코드 + str(self.V['매수수량']) if self.V['구매수량'] else ' '
            self.V['매수금액']  = self.V['매수수량'] * self.M['당일종가']
            self.M['진행상황']  = self.M['매수단계']

            # R 전략, S 전략의 매수가격은 V전략 매수가격 보다 같거나 작다.
            self.today_buy_RST(self.R,'R')
            self.today_buy_RST(self.S,'S')
            self.today_buy_RST(self.T,'T')
            
    def chance_qty(self,basic_qty,key) :
            
            찬스수량 = 0   
            day_limit = 6 if key == 'R' else 7 
            day_count = min(self.M['현재날수']+self.M['찬스일가'],day_limit)
            for i in range(0,day_count) : 
                찬스수량 += my.ceil( basic_qty *(i*1.25 + 1))
            return 찬스수량   
    
    def tomorrow_step_RST(self,tac,key)  :
        
        if  not tac['현재잔액'] : tac['구매수량'] = 0; return

        if  tac['진행시작'] :
            tac['구매수량'] = my.ceil(tac['기초수량'] * (self.M['현재날수']*self.M['비중조절'] + 1))

            if  tac['현재잔액'] < tac['구매수량'] * self.M['매수가격'] : 
                tac['구매수량'] = my.ceil(tac['기초수량'] * self.M['위매비중']) 
                if  tac['현재잔액'] < tac['구매수량'] * self.M['매수가격'] : 
                    tac['구매수량'] = 0
                    if  self.D['이밸런싱'] == 'on' and key in ('R','S') :
                        self.T['현재잔액'] += tac['현재잔액']
                        tac['현재잔액'] = 0.0
        
        else :  tac['매수가격'] = self.take_chance(tac)

    def tomorrow_buy(self) :

        self.M['매수가격'] = round(self.M['당일종가']*self.M['평단가치'],2)
        self.V['구매수량'] = my.ceil(self.V['기초수량'] * (self.M['현재날수']*self.M['비중조절'] + 1))
        
        if  self.V['현재잔액'] < self.V['구매수량'] * self.M['매수가격'] :
            self.V['구매수량'] = my.ceil(self.V['기초수량'] * self.M['위매비중'])
            self.M['매수단계'] = '매수제한' 

            if  self.V['현재잔액'] < self.V['구매수량'] * self.M['매수가격'] : 
                self.V['구매수량'] = 0
                self.M['매수단계'] = '매수중단'


    def tomorrow_sell(self) :

        # [일반진행]---------------------------------------------------------------------------------------------
        if  not self.M['손실회수'] :
            
            if  self.M['매수단계'] not in ('매수제한','매수중단') :  
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
                self.M['매도가격'] = min(my.round_up(self.V['평균단가'] * self.M['전화위복']),my.round_up(self.R['평균단가'] * self.R['위기탈출']))
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
        CPRICE = my.round_up(self.M['당일종가'] * self.M['종가상승'])
        
        if  CPRICE > LPRICE : 
            self.M['매도가격'] = min(self.M['매도가격'],CPRICE)     

        if self.M['매수가격']>= self.M['매도가격'] : self.M['매수가격'] = self.M['매도가격'] - 0.01
            

    def tomorrow_step(self)   :
        
        self.tomorrow_buy()
        self.tomorrow_sell()

        self.tomorrow_step_RST(self.R,'R')
        self.tomorrow_step_RST(self.S,'S')
        self.tomorrow_step_RST(self.T,'T')

        if  self.M['매수가격']>= self.M['매도가격'] : self.M['매수가격'] = self.M['매도가격'] - 0.01

        
    def take_chance(self,tac) :
        H = self.V['보유수량']
        n = self.V['구매수량']
        A = self.V['총매수금']
        if H == 0 : return 0
        p = tac['회복시점'] if self.M['손실회수'] else tac['진입시점']

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
            self.M['현재날수'] = 1
            
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
                if self.D['수료적용'] == 'on'  : tac['현재잔액'] -=  self.commission(tac['매수금액'],1)

            self.M['진행상황'] = '첫날매수'    
            self.M['매수단계'] = '일반매수'
            self.M['첫날기록'] = False
 
            return True

        else : 
            return False
        

    def result(self) :

        self.D['최대일수'] = self.M['최대일수']
        self.D['최대날자'] = self.M['최대날자']
        self.D['MDD1'] = f"{self.V['진최하락']:.2f}"; self.D['MDD_DAY1'] = self.V['최하일자'][2:]
        self.D['MDD2'] = f"{self.R['진최하락']:.2f}"; self.D['MDD_DAY2'] = self.R['최하일자'][2:]
        self.D['MDD3'] = f"{self.S['진최하락']:.2f}"; self.D['MDD_DAY3'] = self.S['최하일자'][2:]
        self.D['MDD4'] = f"{self.T['진최하락']:.2f}"; self.D['MDD_DAY4'] = self.T['최하일자'][2:]
        
        초기자본1 = float(self.D['일반자금'].replace(',','')) 
        최종자본1 = self.V['평가금액'] + self.V['현재잔액'] 
        최종수익1 = 최종자본1 - 초기자본1 
        self.D['v_profit'] = round((최종수익1/초기자본1) * 100,2)      
        
        초기자본2 = float(self.D['기회자금'].replace(',',''))
        최종자본2 = self.R['평가금액'] + self.R['현재잔액'] 
        최종수익2 = 최종자본2 - 초기자본2 
        self.D['r_profit'] = round((최종수익2/초기자본2) * 100,2)

        초기자본3 = float(self.D['안정자금'].replace(',',''))
        최종자본3 = self.S['평가금액'] + self.S['현재잔액'] 
        최종수익3 = 최종자본3 - 초기자본3 
        self.D['s_profit'] = round((최종수익3/초기자본3) * 100,2)

        초기자본4 = float(self.D['생활자금'].replace(',',''))
        최종자본4 = self.T['평가금액'] + self.T['현재잔액'] 
        최종수익4 = 최종자본4 - 초기자본4 
        self.D['t_profit'] = round((최종수익4/초기자본4) * 100,2)
        
        초기자본 = 초기자본2 + 초기자본3 + 초기자본4
        최종자본 = 최종자본2 + 최종자본3 + 최종자본4
        최종수익 = 최종자본 - 초기자본 
        self.D['profit_t'] = round((최종수익/초기자본) * 100,2)
        
        self.D['R_총경과일'] = self.D['days_span']
        self.D['R_초기자본'] = f"{초기자본:,.0f}"
        self.D['R_최종자본'] = f"{최종자본:,.2f}"
        self.D['R_최종수익'] = f"{최종수익:,.2f}"
        self.D['R_종수익률'] = f"{self.D['profit_t']:,.2f}"
        self.D['RV종수익률'] = f"{self.D['v_profit']:,.2f}"
        self.D['RR종수익률'] = f"{self.D['r_profit']:,.2f}"
        self.D['RS종수익률'] = f"{self.D['s_profit']:,.2f}"
        self.D['RT종수익률'] = f"{self.D['t_profit']:,.2f}"

    
    def new_day(self) :

        self.R['매수가격'] = 0.0;  self.R['진행시작'] = False; self.R['매수금액'] = 0.0; self.R['매수수량'] = 0
        self.S['매수가격'] = 0.0;  self.S['진행시작'] = False; self.S['매수금액'] = 0.0; self.S['매수수량'] = 0
        self.T['매수가격'] = 0.0;  self.T['진행시작'] = False; self.T['매수금액'] = 0.0; self.T['매수수량'] = 0

        self.set_value(['매도수량','매도금액','매수수량','매수금액','수익현황','현수익률','평균단가'],0)
            
        if  self.M['당일종가'] <  round(self.M['전일종가'] * self.M['큰단가치'],2) :
            
            self.M['기록시즌'] += 1
            self.M['현재날수'] = 1
            
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
                if self.D['수료적용'] == 'on'  : tac['현재잔액'] -=  self.commission(tac['매수금액'],1)

            self.M['진행상황'] = '첫날매수'    
            self.M['매수단계'] = '일반매수'
            self.M['첫날기록'] = False
 
            return True

        else : 
            return False


    def simulate(self) :

        for idx,BD in enumerate(self.B) : 
            if BD['add0'] < self.D['시작일자'] : idxx = idx; continue

            self.M['현재일자'] = BD['add0']
            self.M['당일종가'] = float(BD['add3'])
            self.M['종가변동'] = float(BD['add8']) 
            self.M['전일종가'] = float(self.B[idx-1]['add3'])  
            self.V['거래코드'] = ' ' 
            self.R['거래코드'] = ' '
            self.S['거래코드'] = ' '
            self.T['거래코드'] = ' '
            self.set_value(['매도수량','매도금액','매수수량','매수금액','수익현황','현수익률'],0)
            
            # BD의 기록은 시작일자 보다 전의 데이타(종가기록 등)에서 시작하고, 당일종가가 전일에 비해 설정(12%)값 이상으로 상승 시 건너뛰기 위함
            if  idx == idxx + 1 or self.M['첫날기록'] : 
                if  self.new_day() : self.tomorrow_step(); self.add_day(); continue
                else : self.M['첫날기록'] = True; continue

            self.today_sell()
            self.today_buy()
            self.calculate()
            self.tomorrow_step()
            self.add_day()

    def add_day(self) :
        if not self.V['보유수량'] and not self.V['매도수량']: return
        self.M['현재날수'] +=1    
            


    def get_start(self,start_date,end_date) :

        old_date = my.dayofdate(start_date,-7)[0]
        self.DB.tbl, self.DB.wre, self.DB.odr = ('h_stockHistory_board',f"add1='SOXL' AND add0 BETWEEN '{old_date}' AND '{end_date}'",'add0')
        self.B = self.DB.get('add0,add3,add8') # 날자, 종가, 증감        

        # 데이타 존재 여부 확인
        self.DB.tbl, self.DB.wre = ("h_stockHistory_board",f"add1='SOXL'")
        chk_data = self.DB.get_one("min(add0)")
        if chk_data > start_date : 
            self.D['NOTICE'] = f" {start_date} 에서 {end_date} 까지 분석을 위한 데이타가 부족합니다. 시작 날자를 {chk_data} 이후 3일 뒤로 조정하시기 바랍니다."
            return "NOTICE"
        
        self.D['시작일자'] = start_date

        # 기간 계산하기
        self.D['s_day'] = s_day = start_date  ; d0 = date(int(s_day[0:4]),int(s_day[5:7]),int(s_day[8:10]))
        self.D['e_day'] = e_day = end_date    ; d1 = date(int(e_day[0:4]),int(e_day[5:7]),int(e_day[8:10]))
        delta = d1-d0
        self.D['days_span'] = delta.days

    def get_date_serial(self,start_date,end_date) :
        qry = f"SELECT add0 FROM h_stockHistory_board WHERE add1='SOXL' AND add0 BETWEEN '{start_date}' AND '{end_date}' ORDER BY add0"
        return self.DB.col(qry)


    def init_capital(self,V,R,S,T) :
        
        self.V['현재잔액']  = V; self.V['일매수금']  = int(self.V['현재잔액'] / self.M['분할횟수'])
        self.R['현재잔액']  = R; self.R['일매수금']  = int(self.R['현재잔액'] / self.M['분할횟수'])
        self.S['현재잔액']  = S; self.S['일매수금']  = int(self.S['현재잔액'] / self.M['분할횟수'])
        self.T['현재잔액']  = T; self.T['일매수금']  = int(self.T['현재잔액'] / self.M['분할횟수'])

        
    def init_value(self) :

        ST = self.DB.parameters_dict('매매전략/VRS')
        
        self.M['비중조절']  = ST['01001']  # 매매일수 에 따른 구매수량 가중치(1.25)
        self.M['평단가치']  = ST['00300']  # 매수시 가중치(1.022)
        self.M['큰단가치']  = ST['00200']  # 첫날매수 시 가중치(1.12)
        self.M['첫매가치']  = ST['00400']  # 일반매도 시 이율(1.022) 
        self.M['둘매가치']  = ST['00500']  # 매수제한 시 이율(0.939) 
        self.M['강매시작']  = ST['00800']  # 강매시작 일(24) 
        self.M['강매가치']  = ST['00700']  # 손절가 범위(0.7)
        self.M['위매비중']  = ST['01000']  # 매수제한 시 매수범위 기본수량의 (3)
        self.R['매도보정']  = ST['01100']
        self.S['매도보정']  = ST['01200']
        self.T['매도보정']  = ST['01400']
        self.R['위기탈출']  = ST['01500']
        self.M['종가상승']  = ST['01600']  # 종가상승 폭이 설정 수치 이상일 경우 전체 매도 가격
        self.M['매도대기']  = ST['00600']  # 매도대기(18)
        self.M['전화위복']  = ST['00900']  # 손절 이후 매도 이율(1.12)
        self.M['회복탈출']  = ST['00901']  # 손절 이후 S, T 평균값의 10% 이상시 매도
        self.M['분할횟수']  = ST['00100']  # 분할 횟수
        self.M['찬스일가']  = ST['01002']  # V,R 전략 시 찬스 수량 계산 가중일

        self.M['손실회수']  = False  
        self.M['회복전략']  = False      # 현재 진행 중인 상황이 손실회수 상태인지 아닌지를 구분( for 통계정보 )
        self.M['매수단계']  = '일반매수'
        self.M['기록시즌']  = 0

        self.D['일반자금']  = ST['05100']
        self.D['기회자금']  = ST['05200']
        self.D['안정자금']  = ST['05300']
        self.D['생활자금']  = ST['05400']        

        self.V['현재잔액']  = my.sv(self.D['일반자금'])
        self.R['현재잔액']  = my.sv(self.D['기회자금'])
        self.S['현재잔액']  = my.sv(self.D['안정자금'])
        self.T['현재잔액']  = my.sv(self.D['생활자금'])

        self.V['일매수금']  = int(self.V['현재잔액'] / self.M['분할횟수'])
        self.R['일매수금']  = int(self.R['현재잔액'] / self.M['분할횟수'])
        self.S['일매수금']  = int(self.S['현재잔액'] / self.M['분할횟수'])
        self.T['일매수금']  = int(self.T['현재잔액'] / self.M['분할횟수'])
        
        self.M['거래코드']  = ' '
        self.M['최대날자']  = ' '

        self.M['현재날수']  = 1
        self.M['최대일수']  = 0   # 최고 오래 지속된 시즌의 일수
        
        self.M['첫날기록']  = False
        self.R['진행시작']  = False 
        self.S['진행시작']  = False 
        self.T['진행시작']  = False
        
        self.R['진입시점']  = float(ST['02100']) 
        self.R['회복시점']  = float(ST['02200']) 
        self.S['진입시점']  = float(ST['02300']) 
        self.S['회복시점']  = float(ST['02400']) 
        self.T['진입시점']  = float(ST['02401'])
        self.T['회복시점']  = float(ST['02402'])

        self.D['수료적용']  = 'on'
        self.D['세금적용']  = 'off'
        self.D['일밸런싱']  = 'on'
        self.D['이밸런싱']  = 'on'

        self.M['전일종가']  = 0.0
        
        self.set_value(['매수수량','매도수량','구매수량','보유수량'],0)
        self.set_value(['매수금액','매도금액','실현수익','총매수금','평균단가','수익현황','현수익률','평가금액','매수가격'],0.0)

        self.set_value(['진최하락'],0)
        self.set_value(['최하일자'],'')

        self.D['TR'] = []

        # 챠트작성
        self.D['c_date'] = []
        self.D['clse_p'] = []
        self.D['avge_r'] = []; self.D['avge_s'] = []; self.D['avge_t'] = []
        # self.D['eval_r'] = []; self.D['eval_s'] = []; self.D['eval_t'] = []
        self.D['totalV'] = []
        self.D['일반횟수'] = 0
        self.D['전략횟수'] = 0
        self.D['기회전량'] = 0
        self.D['기회전략'] = 0
        # 결과작성
        self.D['일정익절'] = 0; self.D['기정익절'] = 0; self.D['안정익절'] = 0; self.D['생정익절'] = 0
        self.D['일정손절'] = 0; self.D['기정손절'] = 0; self.D['안정손절'] = 0; self.D['생정손절'] = 0
        self.D['일회익절'] = 0; self.D['기회익절'] = 0; self.D['안회익절'] = 0; self.D['생회익절'] = 0
        self.D['일회손절'] = 0; self.D['기회손절'] = 0; self.D['안회손절'] = 0; self.D['생회손절'] = 0
        # 통계자료
        self.D['손익통계'] = [[self.D['시작일자'],f"{self.R['현재잔액']+self.S['현재잔액']+self.T['현재잔액']:,.2f}",'0.00','0.00',"#F6CECE",'','0.00']]
        self.D['월익통계'] = [[self.D['시작일자'][:7],0.00]]
        self.D['손익저점'] = 100.0
        self.D['저점날자'] = ''

    def set_value(self,key,val) :
        for k in key :
            self.V[k] = val
            self.R[k] = val
            self.S[k] = val
            self.T[k] = val

    

