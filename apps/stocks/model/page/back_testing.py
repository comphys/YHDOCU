from system.core.load import Model
from datetime import datetime
import math
class M_back_testing(Model) :

    def view(self) :
        
        now = int(datetime.now().timestamp())
        old = str(now - 3600*24*7)
        self.DB.tbl, self.DB.wre = ("h_stockHistory_board",f"wdate > '{old}'")
        self.D['sel_codes'] = self.DB.get("distinct add1",assoc=False)

        self.DB.tbl, self.DB.wre = ("h_stock_strategy_board",None)
        self.D['sel_strategy'] = self.DB.get("add0",assoc=False)

    def get_start(self) :
        self.M = {}

        # 매매전략 가져오기
        self.DB.tbl, self.DB.wre = ('h_stock_strategy_board',f"add0='{self.D['strategy']}'")
        self.S = self.DB.get_line('add1,add2,add3,add4,add5,add6,add7,add8,add9,add10')

        # 종가 및 최고가 가져오기
        self.DB.tbl, self.DB.wre, self.DB.odr = ('h_stockHistory_board',f"add1='{self.D['code']}' AND add0 BETWEEN '{self.D['start_date']}' AND '{self.D['end_date']}'",'add0')
        self.B = self.DB.get('add0,add3,add5')

        self.M['capital'] = int(self.D['capital'].replace(',',''))

        if   self.S['add10'] == 'IT_V1'  :    self.test_IT_V1()
        elif self.S['add10'] == 'IT_V2'  :    self.test_IT_V1()
        elif self.S['add10'] == 'TLP_V1' :    self.test_TLP_V1()

    def test_IT_V1(self) :
        분할횟수 = int(self.S['add1'])
        일매수금 = int(self.M['capital'] / 분할횟수)

        tx = {}
        TR = []

        for idx,BD in enumerate(self.B) : 
            if idx == 0 : #첫날 기록
                기록일자 = BD['add0']
                시즌 = 1
                회차 = 1.0
                당일종가 = float(BD['add3'])
                체결단가 = 당일종가
                체결수량 = int(일매수금/당일종가)
                매수금액 = 당일종가 * 체결수량
                평균단가 = 당일종가
                보유수량 = 체결수량
                평가금액 = 매수금액
                총매수금 = 매수금액
                수익현황 = 0.00
                수익률   = 0.00
                가용잔액 = self.M['capital'] - 매수금액
                진행상황 = '첫날거래'

            else : 
                기록일자 = BD['add0']
                체결수량1 = 0; 체결수량2 = 0 
                당일종가  = float(BD['add3'])
                매수금액1 = 일매수금 * float(self.S['add2']) / 100
                매수금액2 = 일매수금 - 매수금액1
                전일평단가 = 평균단가
                평단가매수 = 전일평단가 * (1+float(self.S['add4'])/100)
                큰단가매수 = 전일평단가 * (1+float(self.S['add5'])/100)
                
                if 당일종가 <= 평단가매수 :  
                    체결수량1 = math.ceil(매수금액1 / 평단가매수)
                    회차 += 0.5
                if 당일종가 <= 큰단가매수 :  
                    체결수량2 = math.ceil(매수금액2 / 큰단가매수)
                    회차 += 0.5

                체결수량 = 체결수량1 + 체결수량2
                체결단가 = 당일종가
                매수금액 = 체결수량 * 당일종가

                가용잔액 -= 매수금액
                보유수량 += 체결수량
                총매수금 += 매수금액
                평균단가 =  총매수금/보유수량
                평가금액 =  당일종가 * 보유수량
                수익현황 =  평가금액 - 총매수금
                수익률   =  (수익현황 / 총매수금) * 100
                시즌 = 1
                진행상황 = '정상진행'
                

            # 포맷
            tx['코드'] = self.D['code']
            tx['시즌'] = 시즌
            tx['회차'] = 회차
            tx['기록일자'] = 기록일자
            tx['당일종가'] = f"{round(당일종가,4):,.2f}"
            tx['체결단가'] = 체결단가
            tx['체결수량'] = 체결수량
            tx['매수금액'] = f"{round(매수금액,4):,.3f}"
            tx['평균단가'] = f"{round(평균단가,4):,.4f}"
            tx['보유수량'] = 보유수량
            tx['평가금액'] = f"{round(평가금액,4):,.2f}"
            tx['총매수금'] = f"{round(총매수금,4):,.2f}"
            tx['수익현황'] = f"{round(수익현황,4):,.2f}"
            clr = "#F6CECE;" if 수익률 > 0 else "#CED8F6"
            tx['수익률'] = f"<span style='color:{clr}'>{round(수익률,4):,.2f}"
            tx['가용잔액'] = f"{round(가용잔액,4):,.2f}"
            tx['진행상황'] = 진행상황
            TR.append(tx)
            tx = {}

            self.D['TR'] = TR



    def test_IT_V2(self) :
        pass

    def test_TLP_V1(self) :
        pass

