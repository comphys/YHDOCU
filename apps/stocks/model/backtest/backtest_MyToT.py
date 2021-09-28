from system.core.load import Model
from datetime import datetime,date
import math

class M_backtest_MyToT(Model) :

# 무한매수법의 개인 변형 적용

    def print_backtest(self) :
        tx = {}
        # 날수 계산
        self.M['날수'] += 1
        if self.M['진행상황'] in ('전량매도','강제매도','부분매도') : self.M['날수'] = 0 
        if self.M['진행상황'] == '첫날거래' : self.M['날수'] = 1

        if self.M['날수'] > self.M['최대일수'] : self.M['최대일수'] = self.M['날수']

        tx['코드'] = self.D['code']
        tx['시즌'] = self.M['날수']
        tx['회차'] = self.M['회차']
        tx['기록일자'] = self.M['day']
        tx['당일종가'] = f"{round(self.M['당일종가'],4):,.2f}"
        tx['체결단가'] = tx['당일종가']
        tx['체결수량'] = self.M['체결수량']
        tx['매수금액'] = f"{round(self.M['매수금액'],4):,.3f}"
        tx['평균단가'] = f"{round(self.M['평균단가'],4):,.4f}"
        tx['보유수량'] = self.M['보유수량']
        tx['평가금액'] = f"{round(self.M['평가금액'],4):,.2f}"
        tx['총매수금'] = f"{round(self.M['총매수금'],4):,.2f}"
        tx['수익현황'] = f"{round(self.M['수익현황'],4):,.2f}"
        clr = "#F6CECE" if self.M['수익률'] > 0 else "#CED8F6"
        tx['수익률'] = f"<span style='color:{clr}'>{round(self.M['수익률'],4):,.2f}"
        tx['매도금액'] = f"{round(self.M['매도금액'],4):,.2f}" if self.M['매도금액'] else self.M['구매코드']
        tx['가용잔액'] = f"{round(self.M['가용잔액'],4):,.2f}"
        tx['진행상황'] = self.M['진행상황']
        tx['일매수금'] = self.M['일매수금']
        self.D['TR'].append(tx)

    def calculate(self)  :

        max_buy_cnt = math.ceil((self.M['가용잔액'] + self.M['추가자본']) / self.M['평균단가'])    
        self.M['체결수량'] = min(self.M['체결수량'], max_buy_cnt)

        self.M['연속하락']  =  self.M['연속하락'] + 1 if  self.M['당일종가'] <= self.M['전일종가'] else 0 
        self.M['매수금액']  =  self.M['체결수량'] * self.M['당일종가']
        self.M['가용잔액'] -=  self.M['매수금액']
        self.M['보유수량'] +=  self.M['체결수량']
        self.M['총매수금'] +=  self.M['매수금액']
        self.M['평가금액']  =  self.M['당일종가'] * self.M['보유수량']
        self.M['평균단가']  =  self.M['총매수금'] / self.M['보유수량'] if self.M['보유수량'] != 0 else 0
        self.M['수익현황']  =  self.M['평가금액'] - self.M['총매수금']
        self.M['수익률']    = (self.M['수익현황'] / self.M['총매수금']) * 100 if self.M['총매수금'] else 0
        
        if  self.M['진행상황'] in ('강제매도','전량매도','부분매도') :
            self.M['수익현황'] = self.M['매도수익']
            self.M['수익률']   = self.M['매수익률']
            self.M['일매수금'] = int(self.M['가용잔액']/self.M['분할횟수']) 
            self.rebalance()      
        
        if  self.M['보유수량'] == 0 : 
            self.M['첫날기록'] = True

        # self.info(f"{self.M['day']} : {self.M['가용잔액'] + self.M['추가자본']}")
    
    def rebalance(self)  :
        total = self.M['가용잔액'] + self.M['추가자본']
        self.M['가용잔액'] = round(total * self.M['자본비율'], 2)
        self.M['추가자본'] = round(total - self.M['가용잔액'], 2)
        self.info(f"{self.M['day']} : 자본 {self.M['가용잔액']} / 추가 {self.M['추가자본']}" )

    def rebalance2(self)  :
        total = self.M['가용잔액'] + self.M['추가자본']
        self.M['가용잔액'] = int(self.D['init_capital'])
        self.M['추가자본'] = total - self.M['가용잔액']
        self.info(f"{self.M['day']} : 자본 {self.M['가용잔액']} / 추가 {self.M['추가자본']}" )

    def init_value(self) :
        self.M['분할횟수']  = int(self.S['add3'])
        self.M['가용잔액']  = int(self.D['init_capital'])
        self.M['일매수금']  = int(self.M['가용잔액'] / self.M['분할횟수'])
        self.M['매수비중']  = float(self.S['add4'])/100
        self.M['평단가치']  = 1 + float(self.S['add5'])/100
        self.M['큰단가치']  = 1 + float(self.S['add6'])/100
        self.M['매도비중']  = float(self.S['add7'])/100
        self.M['첫매가치']  = 1 + float(self.S['add8'])/100
        self.M['둘매가치']  = 1 + float(self.S['add9'])/100
        self.M['채결단가']  = 0.0
        self.M['구매코드']  = ''
        self.M['대기횟수']  = int(self.S['add19']) # 대기횟수 이전에 매도되는 것을 방지(보다 큰 수익 실현을 위해)

        self.M['날수'] = 0
        self.M['최대일수']  = 0 # 최고 오래 지속된 시즌의 일수
        self.M['첫날기록']  = False
        self.M['전일종가']  = 0.0
        self.M['강매가치']  = 1 + float(self.S['add12']) / 100
        self.D['TR'] = []
        tmp = self.S['add15'].split('/')
        tmp.pop()
        self.M['추종종가']  = [int(x) for x in tmp]
        self.M['연속하락']  = 0
        self.M['추종방식']  = self.S['add14']

        # 위기극복
        self.M['횟수제한']  = int(self.S['add10'])  # 매수를 수행 할 날자의 최대치
        self.M['추가자본']  = int(self.D['addition'])
        self.M['매수허용']  = True if self.S['add16'] == 'on' else False  # 횟수 초과 후 매수허용 선택
        self.M['현재추종']  = True if self.S['add17'] == 'on' else False  # 횟수 초과 후 현재추종 선택
        self.M['과거추종']  = True if self.S['add18'] == 'on' else False  # 횟수 초과 후 과거추종 선택

        # 리밸런싱
        total = self.M['가용잔액'] + self.M['추가자본'] 
        self.M['자본비율'] = self.M['가용잔액'] / total
        self.M['추가비율'] = self.M['추가자본'] / total

        # self.info(f"초기구성 : 자본 {self.M['가용잔액']} / 추가 {self.M['추가자본']}" )

    def new_day(self) :
        self.M['회차'] = 1.0
        self.M['평균단가']  = self.M['당일종가']
        self.M['보유수량']  = self.M['체결수량'] = int(self.M['일매수금']/self.M['당일종가'])
        self.M['매수금액']  = self.M['당일종가'] * self.M['체결수량']
        self.M['총매수금']  = self.M['평가금액'] = self.M['매수금액']
        self.M['수익현황']  = self.M['수익률'] = 0.0
        self.M['가용잔액'] -= self.M['매수금액']
        self.M['진행상황']  = '첫날거래'
        self.M['첫날기록']  = False

    def force_sell(self,강제매도가) :
        self.M['진행상황']  = '강제매도'
        self.M['매도금액']  =  self.M['보유수량'] * 강제매도가
        self.M['매도수익']  =  self.M['매도금액'] - self.M['총매수금'] 
        self.M['매수익률']  =  self.M['매도수익'] / self.M['총매수금'] * 100  
        self.M['가용잔액'] +=  self.M['매도금액']
        self.M['보유수량']  = 0 ; self.M['회차']  = 0.0 
        self.M['총매수금']  = 0.0
        
    def normal_sell(self) :
        if self.M['날수'] < self.M['대기횟수'] : return 
        매도수량 = 0
        매도가격1 = self.M['평균단가'] * self.M['첫매가치']
        매도가격2 = self.M['평균단가'] * self.M['둘매가치']
        매도수량1 = math.ceil(self.M['보유수량'] * self.M['매도비중'])
        매도수량2 = self.M['보유수량'] - 매도수량1

        if self.M['당일고가'] >= 매도가격1 : self.M['매도금액'] += 매도가격1 * 매도수량1  ; 매도수량 += 매도수량1  
        if self.M['당일고가'] >= 매도가격2 : self.M['매도금액'] += 매도가격2 * 매도수량2  ; 매도수량 += 매도수량2  
            
        if 매도수량 : 
            ratio = 매도수량 / self.M['보유수량']
            self.M['매도수익']  = self.M['매도금액'] - self.M['총매수금'] * ratio  
            self.M['매수익률']  = self.M['매도수익'] / (self.M['총매수금'] * ratio) * 100
            self.M['보유수량'] -= 매도수량  
            self.M['가용잔액'] += self.M['매도금액']
            self.M['총매수금']  =  self.M['보유수량'] * self.M['평균단가']
            self.M['회차'] = 0.0
            self.M['진행상황']  = '전량매도' if self.M['보유수량'] == 0 else '부분매도'
                

    def normal_buy(self) :
        매수금액1  = self.M['일매수금'] * self.M['매수비중']
        매수금액2  = self.M['일매수금'] - 매수금액1
        평단가매수 = self.M['평균단가'] * self.M['평단가치'] 
        큰단가매수 = self.M['평균단가'] * self.M['큰단가치']
        
        if  self.M['당일종가'] <= 평단가매수 : 
            self.M['체결수량'] += math.ceil(매수금액1 / 평단가매수) ; self.M['회차'] += 0.5 ; self.M['구매코드'] += 'N'
        if  self.M['당일종가'] <= 큰단가매수 : 
            self.M['체결수량'] += math.ceil(매수금액2 / 큰단가매수) ; self.M['회차'] += 0.5 ; self.M['구매코드'] += 'N'  

    def secondary_buy(self) :
        
        if  self.M['당일종가'] <= self.M['평균단가'] : 
            self.M['체결수량'] += math.ceil(self.M['일매수금'] / self.M['평균단가']) 
            self.M['회차'] += 1.0 ; self.M['구매코드'] += 'S'
        
    def acc_cur(self) :
        rate = [0.95,0.94,0.93,0.92,0.91,0.90,0.89]
        for idx, val in enumerate(rate) :
            if self.M['당일종가'] <= min(self.M['평균단가'], self.M['전일종가']) * rate[idx] and self.M['추종종가'][idx] : 
                self.M['체결수량'] += math.ceil(self.M['일매수금'] * self.M['추종종가'][idx] / self.M['평균단가'] * val )  
                self.M['회차'] += self.M['추종종가'][idx]
                self.M['구매코드'] += 'C'

    def acc_old(self) :
        # 기준점을 평균단가와 전일종가로 비교했을 경우 평균단가를 기준으로 할 경우 수익성이 더 좋게 나옴
        # sell_price = min(self.M['전일종가'], self.M['평균단가'])
        sell_price = self.M['평균단가']
        if  self.M['연속하락'] > 0 and self.M['당일종가'] <= sell_price : 
            self.M['체결수량'] += math.ceil(self.M['일매수금'] * self.M['연속하락'] / sell_price)  
            self.M['회차'] += self.M['연속하락'] 
            self.M['구매코드'] += str(self.M['연속하락'])

    def test_it(self) :

        self.init_value()

        for idx,BD in enumerate(self.B) :
            self.M['day'] = BD['add0']
            self.M['당일종가'] = float(BD['add3'])
            if idx !=0 : self.M['전일종가'] = float(self.B[idx-1]['add3'])     

            self.M['당일고가'] = float(BD['add5'])
            self.M['체결수량'] = 0
            self.M['매도금액'] = 0.0
            self.M['진행상황'] = '정상진행' 
            self.M['구매코드'] = ''       

            if  idx == 0 or self.M['첫날기록'] : 
                self.new_day()
                self.print_backtest()
                continue
            
        #   매도부분 --------------------------------------------------------------------------------------------------
            # step1 : 강제매도
            강제매도가 = self.M['평균단가'] * self.M['강매가치']
            if self.M['회차'] > self.M['분할횟수'] and self.M['당일고가'] >= 강제매도가 :  self.force_sell(강제매도가)
            # step2 : 일반매도
            else : self.normal_sell()
        
        #   매수부분 --------------------------------------------------------------------------------------------------
            # step3 : 정상매수
            
            if self.M['가용잔액'] > 0 and self.M['회차'] <= self.M['분할횟수'] : 
                self.normal_buy()
                # step3-1 : 종가하락 가중 매수
                if self.M['추종방식'] == '현재추종' : self.acc_cur()
                if self.M['추종방식'] == '과거추종' : self.acc_old()
                if self.M['추종방식'] == '복합추종' : self.acc_cur() ; self.acc_old()
            
            elif self.M['회차'] <= self.M['횟수제한'] and self.M['가용잔액'] + self.M['추가자본'] > 0 :

                if self.M['매수허용'] : self.secondary_buy() 
                if self.M['현재추종'] : self.acc_cur() 
                if self.M['과거추종'] : self.acc_old() 

        #   결과정리 --------------------------------------------------------------------------------------------------
            # step4 : 기타항목 계산
            self.calculate()
            # step5 : 결과 기록
            self.result()
            self.print_backtest()
        # endfor -----------------------------------------------------------------------------------------------------


    def result(self) :

        self.D['max_days'] = self.M['최대일수']
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
        self.S = self.DB.get_line('add1,add2,add3,add4,add5,add6,add7,add8,add9,add10,add11,add12,add14,add15,add16,add17,add18,add19')

        # 종가 및 최고가 가져오기
        self.DB.tbl, self.DB.wre, self.DB.odr = ('h_stockHistory_board',f"add1='{self.D['code']}' AND add0 BETWEEN '{self.D['start_date']}' AND '{self.D['end_date']}'",'add0')
        self.B = self.DB.get('add0,add3,add5') # 날자, 종가, 고가 

        # 기간 계산하기
        self.D['s_day'] = s_day = self.B[0]['add0']  ; d0 = date(int(s_day[0:4]),int(s_day[5:7]),int(s_day[8:10]))
        self.D['e_day'] = e_day = self.B[-1]['add0'] ; d1 = date(int(e_day[0:4]),int(e_day[5:7]),int(e_day[8:10]))
        delta = d1-d0
        self.D['days_span'] = delta.days

        self.D['init_capital'] = int(self.D['capital'].replace(',',''))
        self.D['addition'] = int(self.D['addition'].replace(',','')) if self.D['addition'] else 0
        self.test_it()