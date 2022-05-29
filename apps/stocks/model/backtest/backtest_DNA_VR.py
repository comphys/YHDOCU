from system.core.load import Model
from datetime import datetime,date
import system.core.my_utils as my
import math,time

class M_backtest_DNA_VR(Model) :

# 분할 매수를 통한 수익 극대화 전략

    def print_backtest(self) :
        tx = {}
        #--------------------------------------------------------
        self.M['날수'] += 1; self.M['완료일수'] += 1 ; 
        if self.M['진행상황'] == '첫날거래' : self.M['날수'] = 1
        tx['날수'] = self.M['날수']

        if self.M['매도수량'] : self.M['날수'] = 0
        if self.M['진행상황'] == '전량매도' : tx['날수'] = self.M['완료일수']; self.M['완료일수'] = 0

        tx['진행'] = self.M['진행']; tx['기록일자'] = self.M['day']
        tx['당일종가'] = f"<span class='clsv{self.M['기록시즌']}'>{round(self.M['당일종가'],4):,.2f}</span>"
        #-----------------------------------------------------------
        tx['매수수량'] = self.M['매수수량'] if self.M['매수수량'] else ' '
        tx['매수금액'] = f"{round(self.M['매수금액'],4):,.3f}" if self.M['매수금액'] else ' '
        tx['평균단가'] = f"<span class='avgv{self.M['기록시즌']}'>{round(self.M['평균단가'],4):,.4f}</span>"
        #-----------------------------------------------------------
        tx['매도수량'] = f"{self.M['매도수량']:,}" if self.M['매도수량'] else ' '
        tx['매도금액'] = f"{round(self.M['매도금액'],4):,.2f}" if self.M['매도금액'] else self.M['거래코드']
        
        if  self.M['매도금액'] : 
            clr = "#F6CECE" if self.M['실현수익'] > 0 else "#CED8F6"
            tx['실현수익'] = f"<span style='color:{clr}'>{round(self.M['실현수익'],4):,.2f}</span>"
        else : tx['실현수익'] = self.M['진행상황']

        tx['보유수량'] = self.M['보유수량']
        tx['총매수금'] = f"{round(self.M['총매수금'],4):,.2f}"
        자금합계 = f"{round(self.M['추가자본'] + self.M['가용잔액'],4):,.2f}"
        tx['평가금액'] = f"{round(self.M['평가금액'],4):,.2f}" if self.M['평가금액'] else f"<span style='font-weight:bold;color:#CEF6CE'>{자금합계}</span>" 
        tx['수익현황'] = f"{round(self.M['수익현황'],4):,.2f}"

        clr = "#F6CECE" if self.M['수익률'] > 0 else "#CED8F6"
        tx['수익률'] = f"<span style='color:{clr}'>{round(self.M['수익률'],4):,.2f}</span>"
        tx['거래코드'] = self.M['거래코드']

        tx['일매수금'] = f"{self.M['일매수금']:,}"
        if  self.M['진행상황'] == '전량매도' :
            tx['가용잔액'] =  f"<span onclick='show_chart({self.M['기록시즌']})' style='cursor:pointer'>전량매도</span>"
            tx['수익현황'] = f"<span style='font-weight:bold;color:#F6CECE'>{tx['수익현황']}</span>"

        elif self.M['진행상황'] in ('전략매도','부분매도') :  
            tx['가용잔액'] = self.M['진행상황'] 
        else : 
            tx['가용잔액'] = 자금합계

        self.D['TR'].append(tx)

    def calculate(self)  :

        if  self.M['매수수량'] : 
            self.M['가용잔액'] -=  self.M['매수금액']
            self.M['보유수량'] +=  self.M['매수수량']
            self.M['총매수금'] +=  self.M['매수금액']
            self.M['평균단가']  =  self.M['총매수금'] / self.M['보유수량'] 

        if  self.M['매도수량'] :
            self.M['실현수익']  = (self.M['당일종가']-self.M['평균단가'])*self.M['매도수량']   
            self.M['수익누적'] += self.M['실현수익'] 
            self.M['매수익률']  = (self.M['당일종가']/self.M['평균단가'] -1 ) * 100
            self.M['보유수량'] -= self.M['매도수량'] 
            self.M['가용잔액'] += self.M['매도금액']
            self.M['총매수금']  = self.M['보유수량'] * self.M['평균단가']
            

        self.M['평가금액']  =  self.M['당일종가'] * self.M['보유수량']
        self.M['수익현황']  =  self.M['평가금액'] - self.M['총매수금']
        self.M['수익률']    = (self.M['당일종가']/self.M['평균단가'] -1) * 100 

        if  self.M['보유수량'] == 0 : 
            self.M['수익률']   = self.M['매수익률']
            self.M['수익현황'] = self.M['수익누적']
            self.M['평균단가'] = 0.0
            self.M['전략가격'] = 0.0
            self.M['위기전략'] = False
            self.M['첫날기록'] = True   
            if self.M['리밸런싱'] : self.rebalance()   

        if self.M['날수'] > self.M['최대일수'] : self.M['최대일수'] = self.M['날수'] ; self.M['최대날자'] = self.M['day']
        if self.M['수익률'] < self.M['MDD'] : self.M['MDD'] = self.M['수익률'] ; self.M['MDD_DAY'] = self.M['day']

        self.M['진행'] = round(self.M['총매수금'] / self.M['씨드'] * 100,1)
        

    def rebalance(self)  :
        total = self.M['가용잔액'] + self.M['추가자본']
        self.M['가용잔액'] = round(total * self.M['자본비율'])
        self.M['추가자본'] = round(total - self.M['가용잔액'])
        self.M['일매수금'] = int(self.M['가용잔액']/self.M['분할횟수']) 
        self.M['씨드'] = self.M['가용잔액']

    def init_value(self) :
        self.M['기록시즌']  = 0
        self.M['분할횟수']  = int(self.S['add2'])
        self.M['가용잔액']  = int(self.D['init_capital'])
        self.M['일매수금']  = int(self.M['가용잔액'] / self.M['분할횟수'])
        self.M['매수비중']  = float(self.S['add3'])/100
        self.M['평단가치']  = float(self.S['add4'])
        self.M['큰단가치']  = 1 + float(self.S['add5'])/100
        self.M['첫매가치']  = 1 + float(self.S['add9'])/100
        self.M['둘매가치']  = 1 + float(self.S['add10'])/100
        self.M['거래코드']  = ' '
        self.M['매도대기']  = int(self.S['add11']) # 매도대기 이전에 매도되는 것을 방지(보다 큰 수익 실현을 위해)
        self.M['리밸런싱']  = True if self.S['add12'] == 'on' else False  # 리밸런싱 수행 여부
        self.M['최대날자']  = ' '
        self.M['완료일수']  = 0
        self.M['수익누적']  = 0.0

        self.M['날수'] = 0
        self.M['진행'] = 0
        self.M['씨드'] = self.D['init_capital']
        self.M['최대일수']  = 0   # 최고 오래 지속된 시즌의 일수
        self.M['MDD']  = -5      # 최고 MDD
        self.M['MDD_DAY']  = ' ' # 최고 오래 지속된 시즌의 일수
        self.M['첫날기록']  = False
        self.M['전일종가']  = 0.0
        self.M['매수수량']  = 0
        self.M['매도수량']  = 0
        self.M['매도금액']  = 0.0
        self.M['실현수익']  = 0.0

        self.D['TR'] = []

        self.M['연속하락']  = 0
        self.M['연속상승']  = 0

        self.M['추가자본']  = int(self.D['addition'])
        self.M['전략가격']  = 0

        # 수량확보
        self.M['수량확보']  = True if self.S['add21'] == 'on' else False  # 추가자본 투입 후 수량확보 선택
        self.M['매도시점']  = float(self.S['add22'])/100
        self.M['매수시점']  = float(self.S['add23'])/100
        self.M['위기전략']  = False
        self.M['위매비중']  = float(self.S['add25'])/100
        self.M['위매횟수']  = int(self.S['add24'])
        self.M['매도횟수']  = 0

        # 리밸런싱
        total = self.M['가용잔액'] + self.M['추가자본'] 
        self.M['자본비율'] = self.M['가용잔액'] / total

    def new_day(self) :
        self.M['기록시즌'] += 1
        self.M['연속하락']  = self.M['전속하락']
        self.M['연속상승']  = self.M['전속상승']
        self.M['수익누적']  = 0.0

        매수금액 = self.M['가용잔액'] * self.M['매도대기'] / 100
   
        self.M['평균단가']  = self.M['당일종가']
        self.M['매수수량']  = math.ceil(매수금액/self.M['전일종가'])

        self.M['보유수량']  = self.M['매수수량'] 
        self.M['매수금액']  = self.M['당일종가'] * self.M['매수수량']
        self.M['총매수금']  = self.M['평가금액'] = self.M['매수금액']
        self.M['수익현황']  = self.M['수익률'] = 0.0
        self.M['가용잔액'] -= self.M['매수금액']
        self.M['진행상황']  = '첫날거래'
        self.M['첫날기록']  = False
        self.M['거래코드']  = 'S' 
         
        self.M['진행'] = round(self.M['총매수금'] / self.M['씨드'] * 100,1)

    # 매수시 최종 리턴 값은 [매수수량], 체결가격은 종가를 따름 
     

    def normal_buy(self) :

        if self.M['진행'] > 80 : return 
        if self.M['수익률'] > self.M['평단가치'] : return
        if self.M['당일종가'] > self.M['전일종가'] : return

        매수금액 = self.M['총매수금'] - self.M['평가금액']

        self.M['매수수량'] = int(매수금액/self.M['전일종가']) * 2
        self.M['매수금액'] = self.M['매수수량'] * self.M['당일종가']

        self.M['거래코드'] = 'V'
        self.M['진행상황'] = '저가매수'


    def normal_sell(self) :

        
        매도가격 = self.M['평균단가'] * self.M['둘매가치'] if self.M['진행'] > 80  else self.M['평균단가'] * self.M['첫매가치']

        self.M['진행상황'] = '매도대기'

        if  self.M['당일종가'] >= 매도가격 : 
            self.M['매도수량'] = self.M['보유수량']
            self.M['진행상황'] = '전량매도' 
            
            self.M['매도금액'] = self.M['당일종가'] * self.M['매도수량']
                
    def test_it(self) :

        self.init_value()

        for idx,BD in enumerate(self.B) :
            if BD['add0'] < self.D['start_date'] : idxx = idx; continue

            self.M['day'] = BD['add0']
            self.M['당일종가'] = float(BD['add3'])
            self.M['당일고가'] = float(BD['add5'])
            self.M['전일종가'] = float(self.B[idx-1]['add3'])  
            self.M['전속상승'] = int(self.B[idx-1]['add9'])
            self.M['전속하락'] = int(self.B[idx-1]['add10']) 
            self.M['매도금액'] = self.M['매수수량'] = self.M['매도수량'] = self.M['매수금액']=0
            self.M['거래코드'] = ' '

            if  idx == idxx + 1 or self.M['첫날기록'] : self.new_day(); self.print_backtest(); continue
            
            self.normal_sell()
            
            if self.M['진행'] < 80 : self.normal_buy()

        #   결과정리 --------------------------------------------------------------------------------------------------
            self.M['연속상승'] = int(BD['add9'])
            self.M['연속하락'] = int(BD['add10'])
            self.calculate()
            self.print_backtest()
        # endfor -----------------------------------------------------------------------------------------------------
        self.result()

    def result(self) :

        self.D['max_days'] = self.M['최대일수']
        self.D['max_date'] = self.M['최대날자']
        self.D['MDD'] = f"{self.M['MDD']:.2f}"
        self.D['MDD_DAY'] = self.M['MDD_DAY']
        초기자본 = self.D['init_capital'] + self.D['addition']
        최종자본 = self.M['평가금액'] + self.M['가용잔액'] + self.M['추가자본']
        최종수익 = 최종자본 - 초기자본 
        최종수익률 = (최종수익/초기자본) * 100 
        style1 = "<span style='font-weight:bold;color:white'>"
        style2 = "<span style='font-weight:bold;color:#CEF6CE'>"
        style3 = "<span style='font-weight:bold;color:#F6CECE'>"
        self.D['output']  = f"총기간 : {style1}{self.D['days_span']:,}</span>일 "
        self.D['output'] += f"초기자본 {style1}${초기자본:,}</span> 최종자본 {style1}${최종자본:,.2f}</span> 으로 "
        self.D['output'] += f"수익은 {style2}${최종수익:,.2f}</span> 이며 수익률은 {style3}{최종수익률:,.2f}</span>% 입니다"
    
    def view(self) :
        
        now = int(datetime.now().timestamp())
        old = str(now - 3600*24*7)
        self.DB.tbl, self.DB.wre = ("h_stockHistory_board",f"wdate > '{old}'")
        self.D['sel_codes'] = self.DB.get("distinct add1",assoc=False)

        self.DB.tbl, self.DB.wre = ("h_stock_strategy_board",None)
        self.D['sel_strategy'] = self.DB.get("add0",assoc=False)

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
        self.D['s_day'] = s_day = self.B[0]['add0']  ; d0 = date(int(s_day[0:4]),int(s_day[5:7]),int(s_day[8:10]))
        self.D['e_day'] = e_day = self.B[-1]['add0'] ; d1 = date(int(e_day[0:4]),int(e_day[5:7]),int(e_day[8:10]))
        delta = d1-d0
        self.D['days_span'] = delta.days

        self.D['init_capital'] = int(self.D['capital'].replace(',',''))
        self.D['addition'] = int(self.D['addition'].replace(',','')) if self.D['addition'] else 0


    # [IF THIS DAY] ----------------------------------------------------------------------------

    def this_day(self) :
        
        self.M['기록시즌'] += 1

        self.M['연속하락']  = self.M['전속하락']
        self.M['연속상승']  = self.M['전속상승']

        self.M['progress'] = float(self.D['progress'])
 
        총매수금 = int(self.D['init_capital'] * self.M['progress']/100)
        self.M['평균단가']  = self.M['당일종가']
        self.M['매수수량']  = math.ceil(총매수금/self.M['전일종가'])

        self.M['보유수량']  = self.M['매수수량'] 
        self.M['매수금액']  = self.M['당일종가'] * self.M['매수수량']
        self.M['총매수금']  = self.M['평가금액'] = self.M['매수금액']
        self.M['수익현황']  = self.M['수익률'] = 0.0
        self.M['가용잔액'] -= self.M['매수금액']
        self.M['체결수량']  = self.M['매수수량']
        self.M['진행상황']  = '첫날거래'
        self.M['첫날기록']  = False
        self.M['구매코드']  = 'ST' 
        
        self.M['매수수량'] = 0
        self.M['진행'] = round(self.M['총매수금'] / self.M['씨드'] * 100,1)  

    def test_this_day(self) :

        self.init_value()

        for idx,BD in enumerate(self.B) :
            if BD['add0'] < self.D['start_date'] : idxx = idx; continue
            self.M['day'] = BD['add0']
            self.M['당일종가'] = float(BD['add3'])
            self.M['당일고가'] = float(BD['add5'])
            self.M['전일종가'] = float(self.B[idx-1]['add3'])
            self.M['전속상승'] = int(self.B[idx-1]['add9'])
            self.M['전속하락'] = int(self.B[idx-1]['add10']) 
            self.M['매도금액'] = self.M['매수수량'] = self.M['매도수량'] = self.M['매수금액']=0
            self.M['거래코드'] = ' '

            if  idx == idxx+1 : self.this_day(); continue
            if  self.M['첫날기록'] : self.D['sell_date'] = self.M['day']; break
            
            if self.M['진행'] >= self.M['매도대기']: self.normal_sell()
            
            if self.M['위기전략'] and self.M['수량확보'] : self.strategy_sell()
            else : self.base_buy() if self.M['진행'] < self.M['매도대기'] else self.normal_buy()
            
            self.M['연속상승'] = int(BD['add9'])
            self.M['연속하락'] = int(BD['add10'])
            self.calculate()
        self.result_the_day()    

    # [IF THIS DAY] ----------------------------------------------------------------------------

    def test_the_day(self) :

        self.init_value()

        for idx,BD in enumerate(self.B) :
            if BD['add0'] < self.D['start_date'] : idxx = idx; continue
            self.M['day'] = BD['add0']
            self.M['당일종가'] = float(BD['add3'])
            self.M['당일고가'] = float(BD['add5'])
            self.M['전일종가'] = float(self.B[idx-1]['add3'])   
            self.M['전속상승'] = int(self.B[idx-1]['add9'])
            self.M['전속하락'] = int(self.B[idx-1]['add10']) 
            self.M['매도금액'] = self.M['매수수량'] = self.M['매도수량'] = self.M['매수금액']=0
            self.M['거래코드'] = ' '

            if  idx == idxx+1 : self.new_day(); continue
            if  self.M['첫날기록'] : self.D['sell_date'] = self.M['day']; break
            
            if self.M['진행'] >= self.M['매도대기'] : self.normal_sell()
            
            if self.M['위기전략'] and self.M['수량확보'] : self.strategy_sell()
            else : self.base_buy() if self.M['진행'] < self.M['매도대기'] else self.normal_buy()

            self.M['연속상승'] = int(BD['add9'])
            self.M['연속하락'] = int(BD['add10'])
            self.calculate()
        # endfor -----------------------------------------------------------------------------------------------------
        self.result_the_day()

    def result_the_day(self) :

        # 기간 계산하기
        self.D['s_day'] = s_day = self.D['start_date']  ; d0 = date(int(s_day[0:4]),int(s_day[5:7]),int(s_day[8:10]))
        self.D['e_day'] = e_day = self.M['day'];      d1 = date(int(e_day[0:4]),int(e_day[5:7]),int(e_day[8:10]))
        delta = d1-d0
        self.D['days_span'] = delta.days        

        self.D['s_capital'] = self.D['init_capital'] + self.D['addition']
        self.D['e_capital'] = self.M['평가금액'] + self.M['가용잔액'] + self.M['추가자본']
        self.D['ca_profit'] = self.D['e_capital'] - self.D['s_capital'] 
        self.D['profit_rate'] = (self.D['ca_profit']/self.D['s_capital']) * 100

    
    def test_with_progress(self) :

        self.init_value()

        for idx,BD in enumerate(self.B) :
            if BD['add0'] < self.D['start_date'] : idxx = idx; continue
            self.M['day'] = BD['add0']
            self.M['당일종가'] = float(BD['add3'])
            self.M['당일고가'] = float(BD['add5'])
            self.M['전일종가'] = float(self.B[idx-1]['add3'])  
            self.M['전속상승'] = int(self.B[idx-1]['add9'])
            self.M['전속하락'] = int(self.B[idx-1]['add10']) 
            self.M['매도금액'] = self.M['매수수량'] = self.M['매도수량'] = self.M['매수금액']=0
            self.M['거래코드'] = ' '

            if  idx == idxx+1 : self.this_day(); continue
            if  self.M['첫날기록'] : self.D['sell_date'] = self.M['day']; break
            
            if self.M['진행'] >= self.M['매도대기'] : self.normal_sell()
            
            if self.M['위기전략'] and self.M['수량확보'] : self.strategy_sell()
            else : self.base_buy() if self.M['진행'] < self.M['매도대기'] else self.normal_buy()

        #   결과정리 --------------------------------------------------------------------------------------------------
            self.M['연속상승'] = int(BD['add9'])
            self.M['연속하락'] = int(BD['add10'])
            self.calculate()
            self.print_backtest()
        # endfor -----------------------------------------------------------------------------------------------------
        self.result()
