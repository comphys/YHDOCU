from system.core.load import Model
from datetime import datetime,date
import system.core.my_utils as my

class M_backtest_VOLATILITY(Model) :

# 변동성을 이용한 올타임 전략

    def calculate(self)  :
        
        if  self.M['매수수량'] : 
            self.M['가용잔액'] -=  self.M['매수금액']
            self.M['보유수량'] +=  self.M['매수수량']
            self.M['총매수금'] +=  self.M['매수금액']
            self.M['평균단가']  =  self.M['총매수금'] / self.M['보유수량'] 

            if  self.M['비용차감'] : 
                self.M['추가자금'] -=  self.commission(self.M['매수금액'],1)
                
        if  self.M['매도수량'] :
            self.M['실현수익']  = (self.M['당일종가']-self.M['평균단가'])*self.M['매도수량']  
            self.M['매수익률']  = (self.M['당일종가']/self.M['평균단가'] -1 ) * 100
            self.M['보유수량'] -= self.M['매도수량']
            self.M['가용잔액'] += self.M['매도금액']
            self.M['총매수금']  = 0.00 
            self.M['수익률']    = self.M['매수익률']; 
            self.M['평균단가']  = 0.0
            self.M['첫날기록']  = True
            self.M['매수단계']  = '일반매수'
            
            if self.M['수익률'] > 0 : self.D['일반횟수'] += 1
            if self.M['수익률'] < 0 : self.D['전략횟수'] += 1
            
            if  self.M['비용차감'] : 
                self.M['추가자금'] -=  self.commission(self.M['매도금액'],2)
                
            self.rebalance() 
            
        self.M['평가금액']  =  self.M['당일종가'] * self.M['보유수량']
        self.M['수익현황']  =  self.M['평가금액'] - self.M['총매수금']
        
        if  self.M['보유수량'] == 0 and self.M['매도수량']:
            self.M['수익률']   = self.M['매수익률']
            self.M['수익현황'] = self.M['실현수익']
        else :
            self.M['수익률']    = (self.M['당일종가']/self.M['평균단가'] -1) * 100  if self.M['평균단가'] else 0.00
        
        if self.M['날수'] > self.M['최대일수'] : self.M['최대일수'] = self.M['날수'] ; self.M['최대날자'] = self.M['day']
        if self.M['수익률'] < self.M['MDD'] : self.M['MDD'] = self.M['수익률'] ; self.M['MDD_DAY'] = self.M['day']

        self.M['진행'] = round(self.M['총매수금'] / self.M['씨드'] * 100,1)
        self.M['자산총액'] = self.M['가용잔액'] + self.M['추가자금']
        self.M['평가총액'] = self.M['자산총액'] + self.M['평가금액']


    def commission(self,mm,opt) :
        if  opt==1 :  return int(mm*0.07)/100
        if  opt==2 :  
            m1 = int(mm*0.07)/100
            m2=round(mm*0.0008)/100
            return m1+m2
        
    def rebalance(self)  :
        total = self.M['가용잔액'] + self.M['추가자금']
        self.M['평가밸류'] = total
        self.M['가용잔액'] = int(total * self.M['자본비율'])
        self.M['추가자금'] = total - self.M['가용잔액']
        self.M['일매수금'] = int(self.M['가용잔액']/self.M['분할횟수']) 
        self.M['씨드'] = self.M['가용잔액']

    def init_value(self) :
        self.M['기록시즌']  = 0
        self.M['분할횟수']  = int(self.S['add2'])
        self.M['가용잔액']  = int(self.D['init_capital'])
        self.M['일매수금']  = int(self.M['가용잔액'] / self.M['분할횟수'])
        self.M['거래코드']  = ' '
        self.M['최대날자']  = ' '
        self.M['수익누적']  = 0.0

        self.M['날수'] = 1
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

        self.M['추가자금']  = self.D['addition']

        # 리밸런싱
        self.M['자산총액'] = self.M['가용잔액'] + self.M['추가자금']
        self.M['자본비율'] = self.M['가용잔액'] / self.M['자산총액'] 

        # 챠트작성
        self.D['close_price'] = []; self.D['average_price'] = []; self.D['total_value'] = []; self.D['chart_date'] = []; self.D['eval_value'] = []
        self.D['일반횟수'] = 0
        self.D['전략횟수'] = 0
        self.M['평가밸류'] = self.M['자산총액']

    def new_day(self) :
        self.M['기록시즌'] += 1
        self.M['날수'] = 1
        self.M['수익누적']  = 0.0

        self.M['평균단가']  = self.M['당일종가']
        self.M['매수수량']  = my.ceil(self.M['일매수금']/self.M['전일종가'])
        self.M['기초수량']  = self.M['매수수량'] 

        if  self.M['당일종가'] <  round(self.M['전일종가'] * self.M['큰단가치'],2) : 
            self.M['보유수량']  = self.M['매수수량']  
            self.M['매수금액']  = self.M['당일종가'] * self.M['매수수량'] 
            self.M['총매수금']  = self.M['평가금액'] = self.M['매수금액']
            self.M['수익현황']  = self.M['수익률'] = 0.0

            if self.M['비용차감'] : self.M['추가자금'] -=  self.commission(self.M['매수금액'],1)
            self.M['가용잔액'] -= self.M['매수금액']
            self.M['자산총액'] = self.M['가용잔액'] + self.M['추가자금']
            self.M['진행상황']  = '첫날매수'
            self.M['첫날기록']  = False
            self.M['거래코드']  = 'S' 
            self.M['매수단계'] = '일반매수'
           
            self.M['진행'] = round(self.M['총매수금'] / self.M['씨드'] * 100,1)
            self.M['평가총액'] = self.M['자산총액'] + self.M['평가금액']

            return True
        else : 
            return False


    def today_sell(self) :
        
        if  self.M['당일종가'] >=  self.s_price  : 
            self.M['매도수량'] =  self.M['보유수량']
            self.M['진행상황'] = '전량매도' 
            
            if  self.M['당일종가'] < self.M['평균단가'] : 
                self.M['진행상황'] = '전략매도'
                self.M['손실회수'] = True
            else :
                self.M['손실회수'] = False

            self.M['매도금액'] = self.M['당일종가'] * self.M['매도수량']
            

    def today_buy(self) :

        if  self.M['당일종가']<= self.b_price : 
            self.M['매수수량'] = self.M['구매수량']
            거래코드 = 'L' if self.M['매수단계'] is '매수제한' else 'B'
            self.M['거래코드'] = 거래코드 + str(self.M['날수']) if self.M['구매수량'] else ' '
            self.M['매수금액'] = self.M['매수수량'] * self.M['당일종가']
            self.M['진행상황'] = self.M['매수단계']
        
    def tomorrow_step(self)   :
        # 다음 날 구매수량 및 가격 예측
        self.b_price = round(self.M['당일종가']*self.M['평단가치'],2)
        self.s_price = my.round_up(self.M['평균단가'] * self.M['첫매가치'])
        
        내일날수 = self.M['날수'] + 1
        매수수량 = my.ceil(self.M['기초수량'] * (self.M['날수']*self.M['비중조절'] + 1))
        매수금액 = 매수수량 * self.b_price
        
        if  매수금액 > self.M['자산총액']   :
            매수수량 = my.ceil(self.M['기초수량'] * self.M['위매비중'])
            매수금액 = 매수수량 * self.b_price
            self.M['매수단계'] = '매수제한' 
            
            if  매수금액 > self.M['자산총액']  :  self.M['매수단계'] =  '매수중단'; 매수수량 = 0

        if  self.M['매수단계'] in ('매수제한','매수중단') : 
            self.s_price = my.round_up(self.M['평균단가'] * self.M['둘매가치'])
        if  self.M['손실회수'] and 내일날수 <= self.M['회수기한'] : 
            self.s_price = my.round_up(self.M['평균단가'] * self.M['전화위복'])
        if  내일날수 >= self.M['강매시작'] : 
            self.s_price = my.round_up(self.M['평균단가'] * self.M['강매가치'])
        if  self.b_price >= self.s_price : self.b_price = self.s_price - 0.01 
        
       
        self.M['구매수량'] = 매수수량


    def test_it(self) :

        self.init_value()

        for idx,BD in enumerate(self.B) :
            if BD['add0'] < self.D['start_date'] : idxx = idx; continue

            self.M['day'] = BD['add0']
            self.M['당일종가'] = float(BD['add3'])
            self.M['전일종가'] = float(self.B[idx-1]['add3'])  
            self.M['거래코드'] = ' '
            self.set_value(['매도수량','매도금액','매수수량','매수금액'],0)
            
            # BD의 기록은 시작일자 보다 전의 데이타(종가기록 등)에서 시작하고, 당일종가가 전일에 비해 설정(12%)값 이상으로 상승 시 건너뛰기 위함
            if  idx == idxx + 1 or self.M['첫날기록'] : 
                if  self.new_day() : self.tomorrow_step(); self.print_backtest(); continue
                else : self.M['첫날기록'] = True; continue

            self.today_sell()
            self.today_buy()
            self.calculate()
            self.tomorrow_step()
            self.print_backtest()
        # endfor -----------------------------------------------------------------------------------------------------
        
        self.result()
        self.nextStep()

    def nextStep(self) :
        self.M['전일종가'] = self.M['당일종가']
        self.tomorrow_step()

        self.D['next_process'] = self.M['날수']
        self.D['next_base_price'] = self.M['전일종가']
        self.D['next_base_amount'] = self.M['일매수금']
        self.D['next_available_money'] = f"{self.M['자산총액']:,.0f}"
        self.D['next_status'] = self.M['매수단계']
        self.D['next_base_qty'] = self.M['기초수량']

        if  self.M['첫날기록'] :
            self.D['next_buy_qty'] = my.ceil(self.M['일매수금']/self.M['전일종가'])
            self.D['next_buy']  = round(self.M['전일종가'] * self.M['큰단가치'],2)
            self.D['next_sell'] = 0.00
            self.D['next_sell_qty']  = 0
        else :
            self.D['next_buy']  = f"{self.b_price:.2f}"
            self.D['next_buy_qty']  = self.M['구매수량']
            self.D['next_sell'] = self.s_price
            self.D['next_sell_qty']  = self.M['보유수량']
    
    def set_value(self,key,val) :
        for k in key :
            self.M[k] = val

    def test_with_progress(self) :
        self.test_it()

    def result(self) :

        self.D['max_days'] = self.M['최대일수']
        self.D['max_date'] = self.M['최대날자']
        self.D['MDD'] = f"{self.M['MDD']:.2f}"
        self.D['MDD_DAY'] = self.M['MDD_DAY']
        초기자본 = self.D['init_capital'] + self.D['addition']
        최종자본 = self.M['평가금액'] + self.M['가용잔액'] + self.M['추가자금']
        최종수익 = 최종자본 - 초기자본 
        최종수익률 = (최종수익/초기자본) * 100 
        style1 = "<span style='font-weight:bold;color:white'>"
        style2 = "<span style='font-weight:bold;color:#CEF6CE'>"
        style3 = "<span style='font-weight:bold;color:#F6CECE'>"
        self.D['output']  = f"총기간 : {style1}{self.D['days_span']:,}</span>일 "
        self.D['output'] += f"초기자본 {style1}${초기자본:,}</span> 최종자본 {style1}${최종자본:,.2f}</span> 으로 "
        self.D['output'] += f"수익은 {style2}${최종수익:,.2f}</span> 이며 수익률은 {style3}{최종수익률:,.2f}</span>% 입니다"
        
        self.D['cash_avg'] = round(sum(self.M['현금비중']) / len(self.M['현금비중']),2)
        self.D['cash_min'] = min(self.M['현금비중'])
        self.D['cash_max'] = max(self.M['현금비중'])

    
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
        self.D['s_day'] = s_day = self.D['start_date']  ; d0 = date(int(s_day[0:4]),int(s_day[5:7]),int(s_day[8:10]))
        self.D['e_day'] = e_day = self.D['end_date']    ; d1 = date(int(e_day[0:4]),int(e_day[5:7]),int(e_day[8:10]))
        delta = d1-d0
        self.D['days_span'] = delta.days

        self.D['init_capital'] = my.sv(self.D['capital'])
        self.D['addition'] = my.sv(self.D['addition']) if self.D['addition'] else 0.0

    def print_backtest(self) :
        
        tx = {}
        
        tx['날수'] = self.M['날수']
        tx['기록시즌'] = self.M['기록시즌']
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
        tx['평가금액'] = f"{round(self.M['평가금액'],4):,.2f}" if self.M['평가금액'] else f"{self.M['진행상황']}"
        tx['수익현황'] = f"{round(self.M['수익현황'],4):,.2f}"

        clr = "#F6CECE" if self.M['수익률'] > 0 else "#CED8F6"
        tx['수익률'] = f"<span style='color:{clr}'>{round(self.M['수익률'],4):,.2f}</span>"
        tx['거래코드'] = self.M['거래코드']

        tx['일매수금'] = f"{self.M['일매수금']:,}"
        if  self.M['진행상황'] in ('전량매도','전략매도') :
            자금합계 = f"{round(self.M['추가자금'] + self.M['가용잔액'],4):,.2f}"
            tx['가용잔액'] = f"<span style='font-weight:bold'>{자금합계}</span>"
            tx['수익현황'] = f"<span style='font-weight:bold;color:#F6CECE'>{tx['수익현황']}</span>"

        elif self.M['진행상황'] in ('전략매도','부분매도','손절매도') :  
            tx['가용잔액'] = self.M['진행상황'] 
        else : 
            tx['가용잔액'] = f"{self.M['자산총액']:,.2f}"
            self.M['현금비중'].append(round(self.M['자산총액'] / (self.M['총매수금']+self.M['자산총액']) *100,2))
         
        self.D['TR'].append(tx)
        
        # 챠트 기록용
        self.D['close_price'].append(self.M['당일종가'])
        if avg_price := round(self.M['평균단가'],2) : self.D['average_price'].append(avg_price)
        else : self.D['average_price'].append('None')
        self.D['chart_date'].append(self.M['day'][2:])
        self.D['total_value'].append(round(self.M['평가총액'],0))
        self.D['eval_value'].append(round(self.M['평가밸류'],0))
        
        self.M['날수'] +=1
        