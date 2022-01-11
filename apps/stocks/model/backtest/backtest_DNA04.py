from system.core.load import Model
from datetime import datetime,date
import math,time

class M_backtest_DNA04(Model) :

# 무한매수법의 개인 변형 적용으로 평균가 다운 전략

    def print_backtest(self) :
        tx = {}
        # 날수 계산
        self.M['날수'] += 1
        if self.M['진행상황'] in ('전량매도','전략매도') : self.M['날수'] = 0 
        if self.M['진행상황'] == '첫날거래' : self.M['날수'] = 1

        tx['코드'] = self.D['code']
        tx['시즌'] = self.M['날수']
        tx['회차'] = self.M['진행']
        tx['기록일자'] = self.M['day']
        tx['당일종가'] = f"<span class='clsv{self.M['기록시즌']}'>{round(self.M['당일종가'],4):,.2f}</span>"
        tx['체결단가'] = tx['당일종가']
        tx['체결수량'] = self.M['체결수량']
        tx['매수금액'] = f"{round(self.M['매수금액'],4):,.3f}"
        tx['평균단가'] = f"<span class='avgv{self.M['기록시즌']}'>{round(self.M['평균단가'],4):,.4f}</span>"
        tx['보유수량'] = self.M['보유수량']
        tx['평가금액'] = f"{round(self.M['평가금액'],4):,.2f}"
        tx['총매수금'] = f"{round(self.M['총매수금'],4):,.2f}"
        tx['수익현황'] = f"{round(self.M['수익현황'],4):,.2f}"
        clr = "#F6CECE" if self.M['수익률'] > 0 else "#CED8F6"
        tx['수익률'] = f"<span style='color:{clr}'>{round(self.M['수익률'],4):,.2f}"
        tx['매도금액'] = f"{round(self.M['매도금액'],4):,.2f}" if self.M['매도금액'] else self.M['구매코드']
        if self.M['가용잔액'] < 0 :
            tx['가용잔액'] = 0
            tx['추가잔액'] = self.M['추가자본'] + self.M['가용잔액']
        else :
            tx['가용잔액'] = self.M['가용잔액']
            tx['추가잔액'] = self.M['추가자본'] 

        tx['가용잔액'] = f"{round(tx['가용잔액'],4):,.2f}"
        tx['추가잔액'] = f"{round(tx['추가잔액'],4):,.2f}"
        tx['진행상황'] = self.M['진행상황'] if self.M['진행상황'] != '전량매도' else f"<span onclick='show_chart({self.M['기록시즌']})' style='cursor:pointer'>전량매도</span>"
        tx['일매수금'] = self.M['일매수금']
        self.D['TR'].append(tx)

    def calculate(self)  :
        # 모든 매수는 당일종가로 거래된 것으로 가정 LOC 거래 원칙
        self.M['연속하락']  =  self.M['연속하락'] + 1 if  self.M['당일종가'] <  self.M['전일종가'] else 0 
        self.M['연속상승']  =  self.M['연속상승'] + 1 if  self.M['당일종가'] >= self.M['전일종가'] else 0 
        self.M['매수금액']  =  self.M['체결수량'] * self.M['당일종가']
        self.M['가용잔액'] -=  self.M['매수금액']
        self.M['보유수량'] +=  self.M['체결수량']
        self.M['총매수금'] +=  self.M['매수금액']
        self.M['평가금액']  =  self.M['당일종가'] * self.M['보유수량']
        self.M['평균단가']  =  self.M['총매수금'] / self.M['보유수량'] if self.M['보유수량'] != 0 else 0
        self.M['수익현황']  =  self.M['평가금액'] - self.M['총매수금']
        self.M['수익률']    = (self.M['수익현황'] / self.M['총매수금']) * 100 if self.M['총매수금'] else 0
        
        if  self.M['보유수량'] == 0 : 
            self.M['수익현황'] = self.M['매도수익']
            self.M['수익률']   = self.M['매수익률']
            self.M['전략매금'] = 0
            self.M['위기전략'] = False
            self.M['첫날기록'] = True

            if self.M['리밸런싱'] : self.rebalance()  

        if self.M['진행상황'] in ('전량매도','전략매도') :
            if self.M['날수'] > self.M['최대일수'] : self.M['최대일수'] = self.M['날수'] ; self.M['최대날자'] = self.M['day']
        
        self.M['진행'] = round(self.M['총매수금'] / self.M['씨드'] * 100,1)

    def rebalance(self)  :
        total = self.M['가용잔액'] + self.M['추가자본']
        self.M['가용잔액'] = round(total * self.M['자본비율'], 2)
        self.M['추가자본'] = round(total - self.M['가용잔액'], 2)
        self.M['일매수금'] = int(self.M['가용잔액']/self.M['분할횟수']) 
        self.M['씨드'] = self.M['가용잔액']

    def init_value(self) :
        self.M['기록시즌']  = 0
        self.M['분할횟수']  = int(self.S['add2'])
        self.M['가용잔액']  = int(self.D['init_capital'])
        self.M['일매수금']  = int(self.M['가용잔액'] / self.M['분할횟수'])
        self.M['매수비중']  = float(self.S['add3'])/100
        self.M['평단가치']  = 1 + float(self.S['add4'])/100
        self.M['큰단가치']  = 1 + float(self.S['add5'])/100
        self.M['첫매가치']  = 1 + float(self.S['add9'])/100
        self.M['둘매가치']  = 1 + float(self.S['add10'])/100
        self.M['채결단가']  = 0.0
        self.M['구매코드']  = ''
        self.M['매도대기']  = int(self.S['add11']) # 매도대기 이전에 매도되는 것을 방지(보다 큰 수익 실현을 위해)
        self.M['리밸런싱']  = True if self.S['add12'] == 'on' else False  # 리밸런싱 수행 여부
        self.M['최대날자']  = ' '
        self.M['매도체결']  = False

        self.M['날수'] = 0
        self.M['진행'] = 0
        self.M['씨드'] = self.D['init_capital']
        self.M['최대일수']  = 0 # 최고 오래 지속된 시즌의 일수
        self.M['첫날기록']  = False
        self.M['전일종가']  = 0.0
        
        self.D['TR'] = []

        self.M['연속하락']  = 0
        self.M['연속상승']  = 0

        self.M['추가자본']  = int(self.D['addition'])
        self.M['전략가격']  = 0

        # 수량확보
        self.M['수량확보']  = True if self.S['add21'] == 'on' else False  # 추가자본 투입 후 수량확보 선택
        self.M['매도시점']  = float(self.S['add22'])/100
        self.M['매수시점']  = float(self.S['add23'])/100
        self.M['전략매금']  = 0
        self.M['위기전략']  = False
        self.M['위매비중']  = float(self.S['add25'])/100
        self.M['위매횟수']  = int(self.S['add24'])
        self.M['매도횟수']  = 0



        # 리밸런싱
        total = self.M['가용잔액'] + self.M['추가자본'] 
        self.M['자본비율'] = self.M['가용잔액'] / total
        self.M['추가비율'] = self.M['추가자본'] / total


    def new_day(self) :
        self.M['기록시즌'] += 1
        self.M['연속하락']  = int(self.old_price_trace('DN'))
        self.M['연속상승']  = int(self.old_price_trace('UP'))
        self.M['회차'] = 1.0 
        # 첫날 지나친 회차 증가는 지양함 
        if self.M['연속하락'] : self.M['회차'] += 1
        self.M['평균단가']  = self.M['당일종가']
        self.M['체결수량']  = math.ceil(self.M['일매수금']/self.old_price_trace('YD'))
        if  self.M['연속하락'] : 
            self.M['체결수량'] += self.M['체결수량'] * self.M['연속하락']

        self.M['보유수량']  = self.M['체결수량'] 
        self.M['매수금액']  = self.M['당일종가'] * self.M['체결수량']
        self.M['총매수금']  = self.M['평가금액'] = self.M['매수금액']
        self.M['수익현황']  = self.M['수익률'] = 0.0
        self.M['가용잔액'] -= self.M['매수금액']
        self.M['진행상황']  = '첫날거래'
        self.M['첫날기록']  = False
        self.M['구매코드']  = 'S' 
        if self.M['연속하락'] : self.M['구매코드']  += str(self.M['연속하락'])
        self.M['진행'] = round(self.M['총매수금'] / self.M['씨드'] * 100,1)


    def base_buy(self)  :

        매수금액1  = self.M['일매수금'] * self.M['매수비중']
        매수금액2  = self.M['일매수금'] - 매수금액1
        평단가금액 = self.M['평균단가'] * self.M['평단가치'] 
        큰단가금액 = self.M['평균단가'] * self.M['큰단가치']

        if  self.M['당일종가'] <= 큰단가금액 : 
            self.M['체결수량'] += math.ceil(매수금액2 / 큰단가금액)*2 ; self.M['구매코드'] = 'B'        
        if  self.M['당일종가'] <= self.M['전일종가'] : 
            self.M['체결수량'] += math.ceil(매수금액1 / 평단가금액)*4 ; self.M['구매코드'] = 'A'
        self.M['진행상황'] = '기초매수'
        

    def normal_buy(self) :

        if self.M['위기전략'] : return 

        구매금액  = self.M['전일종가']
        한도금액  = self.M['추가자본'] + self.M['가용잔액']
        기본수량  = math.ceil(self.M['일매수금'] / 구매금액)

        if self.M['연속상승'] >= 1 :
            if 한도금액 < self.M['일매수금'] * 2 :
                self.M['체결수량']  = math.ceil(한도금액 / 구매금액)
                self.M['위기전략'] = True
            else :
                self.M['체결수량']  = 기본수량 * 2

            if  self.M['당일종가'] <= 구매금액 : self.M['구매코드'] = 'T'
            else : self.M['체결수량'] = 0

        if self.M['연속하락'] >= 1 :
            if 한도금액 < self.M['일매수금'] * (1+self.M['연속하락']) :
                self.M['체결수량']  = math.ceil(한도금액 / 구매금액)
                self.M['위기전략'] = True 
            else :
                self.M['체결수량']  = 기본수량 * (1+self.M['연속하락'])
                
            if  self.M['당일종가'] <= 구매금액 : self.M['구매코드'] = 'D' + str(self.M['연속하락'])
            else : self.M['체결수량'] = 0
                
        
        self.M['진행상황'] = '일반매수'

    def normal_sell(self) :
        
        if self.M['매도체결'] : return 
         
        매도가격 = self.M['평균단가'] * self.M['첫매가치']
        if self.M['전략매금'] : 매도가격 = self.M['평균단가'] * 1.05
        매도수량 = self.M['보유수량']
        
        self.M['진행상황'] = '매도대기' 
        if self.M['당일종가'] >= 매도가격 : 
            self.M['매도금액'] = self.M['당일종가'] * 매도수량    
            self.M['매도수익'] = self.M['매도금액'] - self.M['총매수금']  
            self.M['매수익률'] = self.M['매도수익'] / (self.M['총매수금']) * 100
            self.M['보유수량'] = 0  
            self.M['가용잔액'] += self.M['매도금액']
            self.M['총매수금'] = 0 
            self.M['회차'] = 0.0
            self.M['진행상황']  = '전량매도' 
            self.M['매도체결']  = True
            
                
    def strategy_sell(self) : # LOC 매도

        if self.M['매도체결'] or self.M['수익률'] > 0 : return 

        # 매도수량 = int(self.M['보유수량'] * self.M['위매비중']) 
        # 매도가격 = self.M['전략가격'] * (1-self.M['매수시점']) if self.M['전략매금'] > 0 else self.M['평균단가'] * (1+self.M['매도시점']) 

        매도가격 = self.M['평균단가'] * (1+self.M['매도시점']) 
        매도수량 = int(self.M['보유수량'] * self.M['위매비중'])

        if self.M['당일종가'] >= 매도가격  : 

            ratio = 매도수량 / self.M['보유수량']
            self.M['매도금액'] = self.M['당일종가'] * 매도수량  
            self.M['매도수익']  = self.M['매도금액'] - self.M['총매수금'] * ratio  
            self.M['매수익률']  = self.M['매도수익'] / (self.M['총매수금'] * ratio) * 100
            self.M['보유수량'] -= 매도수량  
            self.M['가용잔액'] += self.M['매도금액']
            self.M['총매수금']  =  self.M['보유수량'] * self.M['평균단가']
            self.M['진행상황']  = '전략매도' 
            self.M['전략매금'] += self.M['매도금액']
            self.M['전략가격']  = self.M['당일종가']
            self.M['매도체결']  = True
            self.M['매도횟수'] += 1
            self.M['위기전략'] = False
        else :
            매수단가 = self.M['전략가격'] * (1+self.M['매수시점'])
            self.M['진행상황'] = f"{매도가격:.2f}-{매수단가:.2f}" if self.M['전략가격'] else f"매도:{매도가격:.2f}"

    def test_it(self) :

        self.init_value()

        for idx,BD in enumerate(self.B) :
            self.M['day'] = BD['add0']
            self.M['당일종가'] = float(BD['add3'])
            self.M['전일종가'] = float(self.B[idx-1]['add3'])     

            self.M['당일고가'] = float(BD['add5'])
            self.M['체결수량'] = 0
            self.M['매도금액'] = 0.0
            self.M['진행상황'] = ' ' 
            self.M['구매코드'] = ' '       

            if  idx == 0 or self.M['첫날기록'] : 
                self.new_day()
                self.print_backtest()
                continue
            
        #   ----------------------------------------------------------------------------------------------------------
            if self.M['날수'] > self.M['매도대기'] : self.normal_sell()
            if self.M['위기전략'] : self.strategy_sell()
        #   ----------------------------------------------------------------------------------------------------------
            if  not self.M['매도체결'] and self.M['추가자본'] + self.M['가용잔액'] > 0 :  
                if self.M['진행'] < 24 : self.base_buy()
                else : self.normal_buy()

            self.M['매도체결']  = False

        #   결과정리 --------------------------------------------------------------------------------------------------
            self.calculate()
            self.print_backtest()
        # endfor -----------------------------------------------------------------------------------------------------
        self.result()

    def result(self) :

        self.D['max_days'] = self.M['최대일수']
        self.D['max_date'] = self.M['최대날자']
        초기자본 = self.D['init_capital'] 
        최종자본 = self.M['평가금액'] + self.M['가용잔액'] + self.M['추가자본'] - self.D['addition']
        최종수익 = 최종자본 - self.D['init_capital'] 
        최종수익률 = (최종수익/self.D['init_capital']) * 100 
        style1 = "<span style='font-weight:bold;color:white'>"
        style2 = "<span style='font-weight:bold;color:#CEF6CE'>"
        style3 = "<span style='font-weight:bold;color:#F6CECE'>"
        self.D['output']  = f"총기간 : {style1}{self.D['days_span']:,}</span>일 "
        self.D['output']  = f"초기자본 {style1}${초기자본:,}</span> 최종자본 {style1}${최종자본:,.2f}</span> 으로 "
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
        self.DB.tbl, self.DB.wre, self.DB.odr = ('h_stockHistory_board',f"add1='{self.D['code']}' AND add0 BETWEEN '{self.D['start_date']}' AND '{self.D['end_date']}'",'add0')
        self.B = self.DB.get('add0,add3,add5') # 날자, 종가, 고가 

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
        self.test_it()

    def old_price_trace(self,opt) : # opt True for C_drop, False for C_up
        now = int(time.mktime(datetime.strptime(self.M['day'],'%Y-%m-%d').timetuple()))
        old_date = datetime.fromtimestamp(now-3600*24*14).strftime('%Y-%m-%d')
        qry = f"SELECT add3 FROM h_stockHistory_board WHERE add0 BETWEEN '{old_date}' and '{self.M['day']}' and add1='{self.D['code']}' ORDER BY add0"
        aaa= self.DB.exe(qry)
        aaa= [float(x[0]) for x in aaa ]

        bbb = aaa[:-1] 
        c_drop = 0
        c_goup   = 0

        for i in range(1,len(bbb)) :
            c_drop = c_drop + 1 if bbb[i] <= bbb[i-1] else 0
            c_goup = c_goup + 1 if bbb[i] >  bbb[i-1] else 0
        
        if opt == 'DN' : 
            return c_drop
        elif opt == 'UP' :
            return c_goup
        elif opt == 'YD' :
            return aaa[-2]