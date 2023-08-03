from system.core.load import Model
from datetime import datetime,date
import system.core.my_utils as my

class M_backtest_DEVELOPE(Model) :

# 변동성을 이용한 올타임 전략

    def calculate(self)  :

        if  self.M['매수수량'] or self.R['매수수량'] : 
            self.M['가용잔액'] -=  self.M['매수금액'];  self.R['기회자금'] -= self.R['매수금액']
            self.M['보유수량'] +=  self.M['매수수량'];  self.R['보유수량'] += self.R['매수수량']
            self.M['총매수금'] +=  self.M['매수금액'];  self.R['총매수금'] += self.R['매수금액']
            self.M['평균단가']  =  self.M['총매수금'] / self.M['보유수량'] 
            self.R['평균단가']  =  self.R['총매수금'] / self.R['보유수량'] if self.R['보유수량'] else 0.0
            self.T['평균단가']  =  (self.M['총매수금'] + self.R['총매수금']) / (self.M['보유수량'] + self.R['보유수량'])

            if  self.M['비용차감'] : 
                self.M['추가자금'] -=  self.commission(self.M['매수금액'],1)
                self.R['기회자금'] -=  self.commission(self.R['매수금액'],1)
                
 
        if  self.M['매도수량'] :
            self.M['실현수익']  = (self.M['당일종가']-self.M['평균단가'])*self.M['매도수량']  
            self.R['실현수익']  = (self.M['당일종가']-self.R['평균단가'])*self.R['매도수량'] 
            self.M['수익누적'] += self.M['실현수익']; self.R['수익누적'] += self.R['실현수익'] 
            self.M['매수익률']  = (self.M['당일종가']/self.M['평균단가'] -1 ) * 100
            self.R['매수익률']  = (self.M['당일종가']/self.R['평균단가'] -1 ) * 100 if self.R['평균단가'] else 0.00
            self.M['보유수량'] -= self.M['매도수량']; self.R['보유수량'] -= self.R['매도수량']
            self.M['가용잔액'] += self.M['매도금액']; self.R['기회자금'] += self.R['매도금액']
            self.M['총매수금']  = 0.00; self.R['총매수금']  = 0.00 
            
            if  self.M['비용차감'] : 
                self.M['추가자금'] -=  self.commission(self.M['매도금액'],2)
                self.R['기회자금'] -=  self.commission(self.R['매도금액'],2)
            

        self.M['평가금액']  =  self.M['당일종가'] * self.M['보유수량'] 
        self.R['평가금액']  =  self.M['당일종가'] * self.R['보유수량']
        
        self.M['수익현황']  =  self.M['평가금액'] - self.M['총매수금']; self.R['수익현황']  =  self.R['평가금액'] - self.R['총매수금']
        self.M['수익률']    = (self.M['당일종가']/self.M['평균단가'] -1) * 100 
        self.R['수익률']    = (self.M['당일종가']/self.R['평균단가'] -1) * 100  if self.R['평균단가'] else 0.00
        self.T['수익률']    = (self.M['당일종가']/self.T['평균단가'] -1) * 100  if self.T['평균단가'] else 0.00
        

        if  self.M['보유수량'] == 0 : 
            self.M['수익률']   = self.M['매수익률']
            self.R['수익률']   = self.R['매수익률']
            self.M['수익현황'] = self.M['수익누적']; self.R['수익현황'] = self.R['수익누적']
            self.M['평균단가'] = 0.0; self.R['평균단가'] = 0.0; self.T['평균단가'] = 0.0
            self.M['첫날기록'] = True
            self.M['매수단계'] = '일반매수'
            
            if self.R['수익률'] > 0 : self.D['기회전량'] += 1
            if self.R['수익률'] < 0 : self.D['기회전략'] += 1
            
            self.rebalance()   

        if self.M['날수'] > self.M['최대일수'] : self.M['최대일수'] = self.M['날수'] ; self.M['최대날자'] = self.M['day']
        if self.M['수익률'] < self.M['MDD1'] : self.M['MDD1'] = self.M['수익률'] ; self.M['MDD_DAY1'] = self.M['day']
        if self.R['수익률'] < self.M['MDD2'] : self.M['MDD2'] = self.R['수익률'] ; self.M['MDD_DAY2'] = self.M['day']

        self.M['자산총액'] = self.M['가용잔액'] + self.M['추가자금']

    def commission(self,mm,opt) :
        if  opt==1 :  return int(mm*0.07)/100
        if  opt==2 :  
            m1 = int(mm*0.07)/100
            m2=round(mm*0.0008)/100
            return m1+m2
        
    def rebalance(self)  :
        total = self.M['가용잔액'] + self.M['추가자금'] 
        self.T['평가밸류'] = total + self.R['기회자금']
        self.M['가용잔액'] = int(total * self.M['자본비율'])
        self.M['추가자금'] = total - self.M['가용잔액']
        self.M['일매수금'] = int(self.M['가용잔액']/self.M['분할횟수']) 
        self.M['씨드'] = self.M['가용잔액']


    def set_price(self) :
        self.days = self.M['날수'] + 1
        self.buy_price = round(self.M['전일종가']*self.M['평단가치'],2)
        
        self.sell_price = my.round_up(self.M['평균단가'] * self.M['첫매가치'])

        if  self.M['매수단계'] in ('매수제한','매수중단') : self.sell_price = my.round_up(self.M['평균단가'] * self.M['둘매가치'])
        if  self.M['손실회수'] and self.days <= self.M['회수기한'] : self.sell_price = my.round_up(self.M['평균단가'] * self.M['전화위복'])
        if  self.days >= self.M['강매시작'] : self.sell_price = my.round_up(self.M['평균단가'] * self.M['강매가치'])

        if self.buy_price >= self.sell_price : self.buy_price = self.sell_price - 0.01 
        # self.buy_price = max(self.M['평균단가'],self.sell_price)

    def normal_sell(self) :
        
        if  self.M['당일종가'] >=  self.sell_price  : 
            self.M['매도수량'] =  self.M['보유수량']; self.R['매도수량'] = self.R['보유수량']
            self.M['진행상황'] = '전량매도' 
            self.D['전량횟수'] += 1
            if  self.M['당일종가'] < self.M['평균단가'] : 
                self.M['진행상황'] = '전략매도'
                self.D['전략횟수'] += 1
                self.M['손실회수'] = True
            else :
                self.M['손실회수'] = False

            self.M['매도금액'] = self.M['당일종가'] * self.M['매도수량']
            self.R['매도금액'] = self.M['당일종가'] * self.R['매도수량']
            #
            self.R['기회가격'] = 0.0
            self.R['기회진행'] = False
            self.R['매수금액'] = 0.0
            self.R['매수수량'] = 0
            

    def normal_buy(self) :

        if  self.M['당일종가']<= self.buy_price : 
            self.M['매수수량'] = self.M['구매수량']
            거래코드 = 'L' if self.M['매수단계'] is '매수제한' else 'B'
            self.M['거래코드'] = 거래코드 + str(self.M['매수수량']) if self.M['구매수량'] else ' '
            self.M['매수금액'] = self.M['매수수량'] * self.M['당일종가']
            self.M['진행상황'] = self.M['매수단계']
            
            if  self.R['기회진행'] :
                self.R['매수수량'] = self.R['구매수량'] 
                self.R['매수금액'] = self.R['매수수량'] * self.M['당일종가']   
                self.M['거래코드']+= f"/R{self.R['매수수량']}" if self.M['매수수량'] and self.R['매수수량'] else ' '  
     
            
        if  not self.R['기회진행'] and self.R['기회가격'] and self.M['날수'] >= 2 and self.M['당일종가']<= self.R['기회가격'] :
            self.R['기회진행'] = True
            self.chance_init()
            매수수량R = self.R['찬스수량']
            매수금액R = 매수수량R * self.M['당일종가']
            
            if 매수금액R > self.R['기회자금'] :
                매수수량R = int(self.R['기회자금']/self.M['당일종가'])
            
            self.M['거래코드'] += f"/R{매수수량R}" 
            self.R['매수수량'] = 매수수량R
            self.R['매수금액'] = self.R['매수수량'] * self.M['당일종가']
            
    
    def chance_init(self) :
            가용잔액 = int(self.R['기회자금'] * 2/3)
            일매수금 = int(가용잔액/22)
            매수비율 = 일매수금 / self.M['일매수금'] 
            기초수량 = my.ceil(매수비율 * self.M['기초수량'])

            찬스수량 = 0    
            for i in range(0,self.M['날수']+1) : 
                찬스수량 += my.ceil(기초수량 *(i*1.25 + 1))
            
            self.R['기초수량'] = 기초수량
            self.R['찬스수량'] = 찬스수량
            
            
        
    def buy_step(self)   :

        self.M['날수'] += 1
        매수수량 = my.ceil(self.M['기초수량'] * (self.M['날수']*self.M['비중조절'] + 1))
        매수금액 = 매수수량 * self.M['당일종가'] 

        if  매수금액 > self.M['자산총액']   :
            매수수량 = my.ceil(self.M['기초수량'] * self.M['위매비중'])
            매수금액 = 매수수량 * self.M['당일종가']
            self.M['매수단계'] = '매수제한' 
            
            if  매수금액 > self.M['자산총액']  :  
                self.M['매수단계'] =  '매수중단'; 
                매수수량 = 0
       
        self.M['구매수량'] = 매수수량
        
        if  self.R['기회진행'] :
            매수수량R = my.ceil(self.R['기초수량'] * (self.M['날수']*self.M['비중조절'] + 1))
            매수금액R = 매수수량R * self.M['당일종가'] 

            if  매수금액R > self.R['기회자금']   :
                매수수량R = my.ceil(self.R['기초수량'] * self.M['위매비중'])
                매수금액R = 매수수량R * self.M['당일종가']
                
                if  매수금액R > self.R['기회자금']  :  매수수량R = 0        
                
            self.R['구매수량'] = 매수수량R
        
        else : 
            self.R['기회가격'] = self.take_chance(self.M['보유수량'],매수수량,self.M['총매수금'])
        
        
    # ---------------------------------------------------------------------------------------------------------------------
    #
    #
    #
    # ---------------------------------------------------------------------------------------------------------------------
    def take_chance(self,H,n,A) :
        if H == 0 : return 0
        p = self.R['기회시점']
        N = H + n
        k = N / (1+p/100)
        return round(A/(k-n),2)
    
    def test_it(self) :

        self.init_value()

        for idx,BD in enumerate(self.B) :
            if BD['add0'] < self.D['start_date'] : idxx = idx; continue

            self.M['day'] = BD['add0']
            self.M['당일종가'] = float(BD['add3'])
            self.M['전일종가'] = float(self.B[idx-1]['add3'])  
            self.M['거래코드'] = ' '
            self.set_value(['매도수량','매도금액','매수수량','매수금액'],0)
            
            if  idx == idxx + 1 or self.M['첫날기록'] : 
                if  self.new_day() : 
                    self.buy_step()
                    self.print_backtest(); 
                    continue
                else : 
                    self.M['첫날기록'] = True
                    continue
            
            self.set_price()
            self.normal_sell()
            self.normal_buy()

        #   결과정리 --------------------------------------------------------------------------------------------------
            self.calculate()
            self.buy_step()
            self.print_backtest()
        # endfor -----------------------------------------------------------------------------------------------------
        self.result()
    
    def set_value(self,key,val) :
        for k in key :
            self.M[k] = val
            self.R[k] = val

    def test_with_progress(self) :
        self.test_it()

    def result(self) :

        self.D['max_days'] = self.M['최대일수']
        self.D['max_date'] = self.M['최대날자']
        self.D['MDD1'] = f"{self.M['MDD1']:.2f}"
        self.D['MDD_DAY1'] = self.M['MDD_DAY1']
        self.D['MDD2'] = f"{self.M['MDD2']:.2f}"
        self.D['MDD_DAY2'] = self.M['MDD_DAY2']
        
        초기자본1 = self.D['init_capital'] + self.D['addition'] 
        최종자본1 = self.M['평가금액'] + self.M['가용잔액'] + self.M['추가자금'] 
        최종수익1 = 최종자본1 - 초기자본1 
        최종수익률1 = (최종수익1/초기자본1) * 100      
        
        초기자본2 = float(self.D['chanceCapital'].replace(',',''))
        최종자본2 = self.R['평가금액'] + self.R['기회자금'] 
        최종수익2 = 최종자본2 - 초기자본2 
        최종수익률2 = (최종수익2/초기자본2) * 100  
        
        초기자본 = 초기자본1 + 초기자본2 
        최종자본 = 최종자본1 + 최종자본2 
        최종수익 = 최종자본 - 초기자본 
        최종수익률 = (최종수익/초기자본) * 100
        
        style1 = "<span style='font-weight:bold;color:white'>"
        style2 = "<span style='font-weight:bold;color:#CEF6CE'>"
        style3 = "<span style='font-weight:bold;color:#F6CECE'>"
        self.D['output']  = f"총 {style1}{self.D['days_span']:,}</span>일 "
        self.D['output'] += f"초기 {style1}${초기자본:,.0f}</span> 최종 {style1}${최종자본:,.2f}</span> "
        self.D['output'] += f"수익은 {style2}${최종수익:,.2f}</span> 수익률은 {style3}{최종수익률:,.2f}( {최종수익률1:,.2f} / {최종수익률2:,.2f} ) %</span>"
        
        self.D['cash_avg'] = round(sum(self.M['현금비중']) / len(self.M['현금비중']),2)
        self.D['cash_min'] = min(self.M['현금비중'])
        self.D['cash_max'] = max(self.M['현금비중'])

    


    def get_start(self) :

        # 매매전략 가져오기
        self.DB.tbl, self.DB.wre = ('h_stock_strategy_board',f"add0='{self.D['strategy']}'")
        self.S = self.DB.get_line('add1,add2,add3,add4,add5,add6,add7,add8,add9,add10,add11,add12,add14,add15,add16,add17,add18,add20,add21,add22,add23,add24,add25')

        # 종가 및 최고가 가져오기
        old_date = my.dayofdate(self.D['start_date'],-7)[0]
        self.DB.tbl, self.DB.wre, self.DB.odr = ('h_stockHistory_board',f"add1='{self.D['code']}' AND add0 BETWEEN '{old_date}' AND '{self.D['end_date']}'",'add0')
        self.B = self.DB.get('add0,add3,add5,add9,add10') # 날자, 종가, 고가, 상승, 하락 

        # 데이타 존재 여부 확인
        self.DB.tbl, self.DB.wre = ("h_stockHistory_board",f"add1='{self.D['code']}'")
        chk_data = self.DB.get_one("min(add0)")
        if chk_data > self.D['start_date'] : 
            self.D['NOTICE'] = f" {self.D['start_date']} 에서 {self.D['end_date']} 까지 분석을 위한 데이타가 부족합니다. 시작 날자를 {chk_data} 이후 3일 뒤로 조정하시기 바랍니다."
            return

        # 기간 계산하기
        self.D['s_day'] = s_day = self.D['start_date']  ; d0 = date(int(s_day[0:4]),int(s_day[5:7]),int(s_day[8:10]))
        self.D['e_day'] = e_day = self.D['end_date']    ; d1 = date(int(e_day[0:4]),int(e_day[5:7]),int(e_day[8:10]))
        delta = d1-d0
        self.D['days_span'] = delta.days

        self.D['init_capital'] = int(self.D['capital'].replace(',',''))
        self.D['addition'] = int(self.D['addition'].replace(',','')) if self.D['addition'] else 0

    def print_backtest(self) :
        tx = {}
        #--------------------------------------------------------
        if self.M['거래코드'] == 'S' : self.M['날수'] = 1; 
        tx['날수'] = self.M['날수']; 
        if self.M['매도수량'] : self.M['날수'] = 0
        tx['기록시즌'] = self.M['기록시즌']
        tx['기록일자'] = self.M['day']
        tx['당일종가'] = f"<span class='clsv{self.M['기록시즌']}'>{round(self.M['당일종가'],4):,.2f}</span>"
        #-----------------------------------------------------------
        tx['매수수량'] = self.M['매수수량'] + self.R['매수수량'] if self.M['매수수량'] else ' '
        tx['매수금액'] = f"{round(self.M['매수금액']+self.R['매수금액'],4):,.3f}" if self.M['매수금액'] else ' '
        tx['종합평균'] = f"{round(self.T['평균단가'],4):,.4f}"
        tx['일반평균'] = f"<span class='avgn{self.M['기록시즌']}'>{round(self.M['평균단가'],4):,.4f}</span>"
        tx['기회평균'] = f"<span class='avgc{self.M['기록시즌']}'>{round(self.R['평균단가'],4):,.4f}</span>" if self.R['평균단가'] else f"<span class='avgc{self.M['기록시즌']}'> </span>"
        #-----------------------------------------------------------
        tx['매도수량'] = f"{self.M['매도수량']+self.R['매도수량']:,}" if self.M['매도수량'] else ' '
        tx['진행현황'] = f"{round(self.M['매도금액']+self.R['매도금액'],4):,.2f}" if self.M['매도금액'] else self.M['거래코드']
        
        if  self.M['매도금액'] : 
            clr = "#F6CECE" if self.M['실현수익'] > 0 else "#CED8F6"
            tx['실현수익'] = f"<span style='color:{clr}'>{round(self.M['실현수익']+self.R['실현수익'],4):,.2f}</span>"
        else : tx['실현수익'] = self.M['진행상황']

        tx['보유수량'] = self.M['보유수량'] + self.R['보유수량']
        tx['총매수금'] = f"{round(self.M['총매수금']+self.R['총매수금'],4):,.2f}"
        
        
        tx['평가금액'] = f"{round(self.M['평가금액']+self.R['평가금액'],4):,.2f}" if self.M['평가금액'] else f"{self.M['진행상황']}"
        tx['일반수익'] = f"{round(self.M['수익현황'],4):,.2f}"
        tx['기회수익'] = f"{round(self.R['수익현황'],4):,.2f}" 
        
        clr = "#F6CECE" if self.M['수익률'] > 0 else "#CED8F6"
        tx['수익률1'] = f"<span style='color:{clr}'>{round(self.M['수익률'],4):,.2f}</span>"
        
        clr = "#F6CECE" if self.R['수익률'] > 0 else "#CED8F6"
        tx['수익률2'] = f"<span style='color:{clr}'>{round(self.R['수익률'],4):,.2f}</span>" if self.R['수익률'] else '0.00'
        
        tx['거래코드'] = self.M['거래코드']

        tx['일매수금'] = f"{self.M['일매수금']:,}"
        
        if  self.M['진행상황'] in ('전량매도','전략매도') :
            자금합계 = f"{round(self.M['추가자금'] + self.M['가용잔액'],4):,.2f}"
            tx['가용잔액'] = f"<span style='font-weight:bold'>{자금합계}</span>"
            tx['일반수익'] = f"<span style='font-weight:bold;color:#F6CECE'>{tx['일반수익']}</span>"
            tx['기회수익'] = f"<span style='font-weight:bold;color:#F6CECE'>{tx['기회수익']}</span>"

        else : 
            tx['가용잔액'] = f"{self.M['자산총액']:,.2f}"
            self.M['현금비중'].append(round(self.M['자산총액'] / (self.M['총매수금']+self.M['자산총액']) *100,2))
            
            
        tx['기회자금'] = f"{self.R['기회자금']:,.2f}"
         
        self.D['TR'].append(tx)
        
        # 챠트 기록용
        self.D['close_price'].append(self.M['당일종가'])
        if avg_price := round(self.T['평균단가'],2) : self.D['average_price'].append(avg_price)
        else : self.D['average_price'].append('None')
        self.D['chart_date'].append(self.M['day'][2:])
        self.D['eval_value'].append(round(self.T['평가밸류'],0))


    def init_value(self) :
        self.R = {}
        self.T = {}
        self.M['기록시즌']  = 0
        self.M['분할횟수']  = int(self.S['add2'])
        self.M['가용잔액']  = int(self.D['init_capital'])
        self.M['일매수금']  = int(self.M['가용잔액'] / self.M['분할횟수'])
        self.M['거래코드']  = ' '
        self.M['최대날자']  = ' '
        self.M['수익누적']  = 0.0

        self.M['날수'] = 0
        self.M['씨드'] = self.D['init_capital']
        self.M['최대일수']  = 0   # 최고 오래 지속된 시즌의 일수
        self.M['MDD1']  = 0      # 최고 MDD
        self.M['MDD_DAY1']  = ' ' # 최고 오래 지속된 시즌의 일수
        self.M['MDD2']  = 0      # 최고 MDD
        self.M['MDD_DAY2']  = ' ' # 최고 오래 지속된 시즌의 일수
        self.M['첫날기록']  = False
        self.M['전일종가']  = 0.0
        self.M['매수수량']  = 0
        self.M['매도수량']  = 0
        self.M['매도금액']  = 0.0
        self.M['실현수익']  = 0.0
        self.M['현금비중']  = []

        self.M['비중조절']  = 1 + float(self.S['add3'])/100   # 매매일수 에 따른 구매수량 가중치
        self.M['평단가치']  = 1 + float(self.S['add4'])/100   # 매수시 가중치
        self.M['큰단가치']  = 1 + float(self.S['add5'])/100   # 첫날매수 시 가중치
        self.M['첫매가치']  = 1 + float(self.S['add9'])/100   # 일반매도 시 이율 
        self.M['둘매가치']  = 1 + float(self.S['add10'])/100  # 매수제한 시 이율 
        self.M['강매시작']  = int(self.S['add17'])            # 손절경과일 
        self.M['강매가치']  = 1 + float(self.S['add18'])/100  # 손절가 범위
        self.M['위매비중']  = int(self.S['add25'])
        self.M['회수기한']  = int(self.S['add11'])
        self.M['전화위복']  = 1 + float(self.S['add22'])/100
        self.M['손실회수']  = False
        self.M['매수단계']  = '일반매수'
        self.M['비용차감']  = True if self.S['add7'] == 'on' else False  # 수수료 계산날수 초과 후 강매선택

        self.D['TR'] = []

        self.M['추가자금']  = int(self.D['addition'])

        # 리밸런싱
        self.M['자산총액'] = self.M['가용잔액'] + self.M['추가자금']
        self.M['자본비율'] = self.M['가용잔액'] / self.M['자산총액'] 
        
        # 리밸런싱 2차 전략
        self.R['기회자금'] = float(self.D['chanceCapital'].replace(',',''))
        self.R['기회시점'] = float(self.D['chancePoint'])
        self.R['기회가격'] = 0.0
        self.R['기회진행'] = False
        self.R['매수수량'] = 0
        self.R['매수금액'] = 0.0
        self.R['보유수량'] = 0
        self.R['매도수량'] = 0
        self.R['총매수금'] = 0.0
        self.R['평가금액'] = 0.0
        self.R['수익현황'] = 0.0
        self.R['실현수익'] = 0.0
        self.R['평균단가'] = 0.0; self.T['평균단가'] = 0.0
        self.R['수익누적'] = 0.0

        # 챠트작성
        self.D['close_price'] = []; self.D['average_price'] = []; self.D['total_value'] = []; self.D['chart_date'] = []; self.D['eval_value'] = []
        self.D['전량횟수'] = 0
        self.D['전략횟수'] = 0
        self.D['기회전량'] = 0
        self.D['기회전략'] = 0
        self.T['평가밸류'] = self.M['자산총액'] + self.R['기회자금']

    def new_day(self) :
        self.M['기록시즌'] += 1
        self.M['수익누적']  = 0.0; self.R['수익누적']  = 0.0

        self.M['평균단가']  = self.M['당일종가']; self.T['평균단가']  = self.M['당일종가']
        self.M['매수수량']  = my.ceil(self.M['일매수금']/self.M['전일종가'])
        self.M['기초수량']  = self.M['매수수량'] 

        if  self.M['당일종가'] <  round(self.M['전일종가'] * self.M['큰단가치'],2) : 
            self.M['보유수량']  = self.M['매수수량']  
            self.M['매수금액']  = self.M['당일종가'] * self.M['매수수량'] 
            self.M['총매수금']  = self.M['평가금액'] = self.M['매수금액']
            self.M['수익현황']  = self.M['수익률'] = 0.0; self.R['수익현황']  = self.R['수익률'] = 0.0

            if self.M['비용차감'] : self.M['추가자금'] -=  self.commission(self.M['매수금액'],1)
            self.M['가용잔액'] -= self.M['매수금액']
            self.M['자산총액'] = self.M['가용잔액'] + self.M['추가자금']
            self.M['진행상황']  = '첫날매수'
            self.M['첫날기록']  = False
            self.M['거래코드']  = f"S{self.M['매수수량']}" 
            self.M['매수단계'] = '일반매수'
           

            return True
        else : 
            return False


    def view(self) :
        
        now = int(datetime.now().timestamp())
        old = str(now - 3600*24*7)
        self.DB.tbl, self.DB.wre = ("h_stockHistory_board",f"wdate > '{old}'")
        self.D['sel_codes'] = self.DB.get("distinct add1",assoc=False)

        self.DB.tbl, self.DB.wre = ("h_stock_strategy_board",None)
        self.D['sel_strategy'] = self.DB.get("add0",assoc=False) 