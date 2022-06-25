from system.core.load import Model
from datetime import datetime,date
import system.core.my_utils as my
import math,time

class M_backtest_LT_backtest(Model) :


# 분할 매수를 통한 수익 극대화 전략

    def print_backtest(self) :
        tx = {}
        #--------------------------------------------------------
        self.M['날수'] += 1; 
        tx['날수']  = self.M['날수']
        tx['기록일자']  = self.M['기록일자']
        tx['당일종가']  = f"{round(self.M['당일종가'],4):,.2f}</span>"
        tx['당일매수']  = 0
        tx['거래금액']  = 0
        tx['보유수량']  = self.M['보유수량']
        tx['최소가치']  = self.M['최소가치']
        tx['현재가치']  = self.M['현재가치']
        tx['최대가치']  = self.M['최대가치']
        tx['가용잔액']  = 0

        self.D['TR'].append(tx)


    def calculate(self)  :

        pass
        

    def rebalance(self)  :
        total = self.M['가용잔액'] + self.M['추가자본']
        self.M['가용잔액'] = round(total * self.M['자본비율'])
        self.M['추가자본'] = round(total - self.M['가용잔액'])
        self.M['일매수금'] = int(self.M['가용잔액']/self.M['분할횟수']) 
        self.M['씨드'] = self.M['가용잔액']

    def init_value(self) :
        self.D['TR'] = []

        self.M['날수']  = 0
        self.M['기록일자']  = 0
        self.M['당일종가']  = 0.0
        self.M['매수']  = 0
        self.M['거래금액']  = 0
        self.M['보유수량']  = 0
        self.M['최소가치']  = 0
        self.M['현재가치']  = 0
        self.M['최대가차']  = 0
        self.M['가용잔액']  = 0


    def new_day(self) :
        self.M['보유수량'] = int(self.D['init_leverage'] / self.M['당일종가'])
        self.M['현재가치'] = self.M['보유수량'] * self.M['당일종가']
        self.M['최소가치'] = self.M['현재가치'] * 0.88
        self.M['최대가치'] = self.M['현재가치'] * 1.12


    def test_it(self) :
        self.init_value()
        for idx,LD in enumerate(self.L) :
            if LD['add0'] < self.D['start_date'] : idxx = idx; continue
            
            self.M['기록일자'] = LD['add0']
            self.M['당일종가'] = float(LD['add3'])

            if  idx == idxx + 1 : self.new_day(); self.print_backtest(); continue

        #   결과정리 --------------------------------------------------------------------------------------------------
            # self.calculate()
            self.print_backtest()
        # endfor -----------------------------------------------------------------------------------------------------
        self.result()

    def result(self) :

        pass
    
    def view(self) :
        
        pass

    def get_start(self) :


        # 종가 및 최고가 가져오기
        base_code = 'SOXX' if self.D['code'] == 'SOXL' else 'QQQ'

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

