from system.core.load import Model
import system.core.my_utils as my


class M_backtest_LT_backtest(Model) :


# 분할 매수를 통한 수익 극대화 전략

    def print_backtest(self) :
        tx = {}
        #--------------------------------------------------------
        self.D['chart_date'].append(self.M['기록일자'][2:])
        self.D['chart_min'].append( self.M['최소가치'])
        self.D['chart_target'].append( self.M['목표가치'])
        self.D['chart_cur'].append( self.M['현재가치'])
        self.D['chart_max'].append( self.M['최대가치'])
        #---------------------------------------------------------

        self.M['날수'] += 1; 
        tx['날수']  = self.M['날수']
        tx['기록일자']  = self.M['기록일자']
        tx['당일종가']  = f"{self.M['당일종가']:,.2f}"
        tx['기본종가']  = f"{self.M['기본종가']:,.2f}"
        tx['당일매수']  = self.M['매수']
        tx['당일매도']  = self.M['매도']
        tx['거래금액']  = f"{self.M['거래금액']:,.2f}"
        tx['보유수량']  = self.M['보유수량']
        tx['최소가치']  = f"{self.M['최소가치']:,.2f}"
        tx['목표가치']  = f"{self.M['목표가치']:,.2f}"
        tx['현재가치']  = f"{self.M['현재가치']:,.2f}"
        tx['최대가치']  = f"{self.M['최대가치']:,.2f}"
        tx['가용잔액']  = f"{self.M['가용잔액']:,.2f}"
        tx['주식비중']  = f"{self.M['주식비중']:,.1f}%"
        tx['현금비중']  = f"{self.M['현금비중']:,.1f}%"
        tx['수익률']    = f"{self.M['수익률']:,.2f}%"

        self.D['TR'].append(tx)
        
    def calculate(self)  :

        pass
        

    def init_value(self) :
        self.D['TR'] = []
        self.D['chart_date'] = []
        self.D['chart_min']  = []
        self.D['chart_target'] = []
        self.D['chart_cur'] = []
        self.D['chart_max'] = []

        self.M['날수']  = 0
        self.M['기록일자']  = 0
        self.M['당일종가']  = 0.0
        self.M['매수']  = 0
        self.M['거래금액']  = 0
        self.M['보유수량']  = 0
        self.M['최소가치']  = 0
        self.M['현재가치']  = 0
        self.M['최대가차']  = 0
        self.M['가용잔액']  = self.D['init_cash']

        self.M['상승밴드']  = 1.1
        self.M['하강밴드']  = 0.9
        self.M['가치증가']  = 1.0


    def buy(self) :
        
        if  self.M['당일종가'] <= self.M['전일종가'] :
            # self.M['매수'] = int((self.M['최대가치'] - self.M['현재가치']) / self.M['당일종가']) 
            self.M['매수'] = int((self.M['가용잔액'] * 0.1)  / self.M['당일종가']) 
            self.M['거래금액'] = self.M['매수'] * self.M['당일종가']
            if  self.M['가용잔액'] - self.M['거래금액'] < 0 : 
                self.M['매수'] = 0
                self.M['거래금액'] = 0
                return
            self.M['가치증가'] = (self.M['보유수량']+ self.M['매수'])/self.M['보유수량']
            self.M['보유수량'] += self.M['매수']
            self.M['가용잔액'] -= self.M['거래금액']
            self.M['가용잔액'] = round(self.M['가용잔액'],2)

    def sell(self) :
        if self.M['당일종가'] >= self.M['전일종가'] :
            # self.M['매도'] = int((self.M['현재가치'] - self.M['최소가치']) / self.M['당일종가'])
            self.M['매도'] = int(self.M['보유수량'] * 0.05) 
            self.M['보유수량'] -= self.M['매도']
            self.M['거래금액'] = self.M['매도'] * self.M['당일종가']
            self.M['가용잔액'] += self.M['거래금액']
            self.M['가용잔액'] = round(self.M['가용잔액'],2)

    
    def new_day(self) :
        self.M['보유수량'] = int(self.D['init_leverage'] / self.M['당일종가'])
        self.M['현재가치'] = self.M['보유수량'] * self.M['당일종가']
        self.M['기본배수'] = self.M['현재가치'] / self.M['기본종가']
        self.M['목표가치'] = self.M['기본종가'] * self.M['기본배수']
        self.M['최소가치'] = self.M['목표가치'] * self.M['하강밴드']
        self.M['최대가치'] = self.M['목표가치'] * self.M['상승밴드']
        self.M['가용잔액'] = self.M['가용잔액'] + self.D['init_leverage'] - self.M['현재가치']
        self.M['기종가'] = self.M['기본종가']
        self.M['당종가'] = self.M['당일종가']
        self.proportion()

    def proportion(self) :
        init_total = self.D['init_leverage'] + self.D['init_cash']
        total = self.M['현재가치'] + self.M['가용잔액']
        self.M['주식비중'] = round(self.M['현재가치'] / total * 100,2)
        self.M['현금비중'] = round(self.M['가용잔액'] / total * 100,2)
        self.M['수익률'] = (total-init_total)/init_total * 100
       

    def test_it(self) :
        self.init_value()
        for idx,LD in enumerate(self.L) :
            if LD['add0'] < self.D['start_date'] : idxx = idx; continue
            self.M['매수'] = 0
            self.M['매도'] = 0
            self.M['거래금액'] = 0
            self.M['기록일자'] = LD['add0']
            self.M['당일종가'] = float(LD['add3'])
            self.M['전일종가'] = float(self.L[idx-1]['add3'])  
            self.M['기본종가'] = float(self.B[idx]['add3'])
            
            if idx == idxx + 1 : self.new_day(); self.print_backtest(); continue

            if self.M['현재가치'] < self.M['최소가치'] : self.buy()
            if self.M['현재가치'] > self.M['최대가치'] : self.sell()

            self.M['현재가치'] = self.M['당일종가'] * self.M['보유수량']

        #   결과정리 --------------------------------------------------------------------------------------------------
            # self.calculate()
            self.proportion()
            self.rebalance()
            self.print_backtest()
        # endfor -----------------------------------------------------------------------------------------------------
        self.result()

    def rebalance(self) :

        if self.D['strategy'] == '변동리밸런싱_기본'  :
            if self.M['매도'] :  self.M['기본배수'] = (self.M['당일종가'] * self.M['보유수량'])/self.M['기본종가']
            self.M['목표가치'] = self.M['기본종가'] * self.M['기본배수']
        
        elif self.D['strategy'] == '변동리밸런싱_매수' :
            if self.M['매수'] : self.M['기본배수'] = self.M['기본배수'] * self.M['가치증가']
            self.M['목표가치'] = self.M['기본종가'] * self.M['기본배수']
        
        elif self.D['strategy'] == '고정리밸런싱_증가' :
            self.M['목표가치'] = self.M['목표가치'] * 1.002
        
        self.M['최소가치'] = self.M['목표가치'] * self.M['하강밴드']
        self.M['최대가치'] = self.M['목표가치'] * self.M['상승밴드']

         

    def result(self) :
        code_price_change = (self.M['당일종가'] - self.M['당종가']) / self.M['당종가'] * 100
        base_price_change = (self.M['기본종가'] - self.M['기종가']) / self.M['기종가'] * 100 
       
        초기자본 = self.D['init_leverage'] + self.D['init_cash']
        최종자본 = self.M['현재가치'] + self.M['가용잔액'] 
        최종수익 = 최종자본 - 초기자본 
        최종수익률 = (최종수익/초기자본) * 100 
        style1 = "<span style='font-weight:bold;color:white'>"
        style2 = "<span style='font-weight:bold;color:#CEF6CE'>"
        style3 = "<span style='font-weight:bold;color:#F6CECE'>"
        self.D['output_l']  = f"{style2}{self.D['기본코드']}</span>({style3}{base_price_change:,.2f}</span>%)&nbsp; {style1}{self.D['code']}</span>({style3}{code_price_change:,.2f}</span>%)"
        self.D['output_r']  = f"초기자본 {style1}${초기자본:,}</span> 최종자본 {style1}${최종자본:,.2f}</span> 으로 "
        self.D['output_r'] += f"수익은 {style2}${최종수익:,.2f}</span> 이며 수익률은 {style3}{최종수익률:,.2f}</span>% 입니다"
    
    def view(self) :
        
        pass

    def get_start(self) :

        # 매매전략 가져오기

        # 종가 및 최고가 가져오기
        base_code = 'SOXX' if self.D['code'] == 'SOXL' else 'QQQ'
        self.D['기본코드'] = base_code

        old_date = my.dayofdate(self.D['start_date'],-7)[0]
        self.DB.tbl, self.DB.wre, self.DB.odr = ('h_stockHistory_board',f"add1='{self.D['code']}' AND add0 BETWEEN '{old_date}' AND '{self.D['end_date']}'",'add0')
        self.L = self.DB.get('add0,add3') # 날자, 종가 
        self.DB.wre = f"add1='{base_code}' AND add0 BETWEEN '{old_date}' AND '{self.D['end_date']}'" 
        self.B = self.DB.get('add0,add3') # 날자, 종가 

        # 데이타 존재 여부 확인
        self.DB.tbl, self.DB.wre = ("h_stockHistory_board",f"add1='{self.D['code']}'")
        chk_data = self.DB.get_one("min(add0)")
        if chk_data > self.D['start_date'] : 
            self.D['NOTICE'] = f" {self.D['start_date']} 에서 {self.D['end_date']} 까지 분석을 위한 데이타가 부족합니다. 시작 날자를 {chk_data} 이후 3일 뒤로 조정하시기 바랍니다."
            return

        self.D['init_leverage'] = int(self.D['leverage'].replace(',',''))
        self.D['init_cash'] = int(self.D['cash'].replace(',','')) if self.D['cash'] else 0

