from system.core.load import Control
from datetime import datetime
import time
import math

class Stock_daily(Control) : 

  
    def _auto(self) :
        self.DB = self.db('stocks')
        self.M = {}

    def init_value(self) :
        self.update={}

        # 기본정보 받아오기 
        self.M['매매전략'] = self.D['post']['add20']
        self.M['체결단가'] = self.D['post']['add6'] 
        self.M['체결수량'] = self.D['post']['add7']   
        self.M['매수금액'] = self.D['post']['add8']
        self.M['가용잔액'] = self.D['post']['add16']
        self.M['추가자본'] = self.D['post']['add17']

        # 폼에 값이 없는 경우 기본적으로 ''으로 값이 전달됨, self.D['post'].get() 은 키가 정의되지 않았을 경우에 써야함
        self.M['체결단가'] = float(self.M['체결단가'].replace(',','')) if self.M['체결단가'] else 0.0
        self.M['체결수량'] = int(self.M['체결수량'].replace(',','')) if self.M['체결수량'] else 0.0
        self.M['매수금액'] = float(self.M['매수금액'].replace(',','')) if self.M['매수금액'] else 0.0
        self.M['가용잔액'] = float(self.M['가용잔액'].replace(',','')) if self.M['가용잔액'] else 0.0
        self.M['추가자본'] = float(self.M['추가자본'].replace(',','')) if self.M['추가자본'] else 0.0
        
        self.M['당일종가'] = self.M['체결단가'] = self.cur_price() 
        self.M['연속하락'] = self.old_price_trace()

        self.M['위기전략'] = 'NO'

        # 매매전략 가져오기
        self.DB.tbl, self.DB.wre = ('h_stock_strategy_board',f"add0='{self.M['매매전략']}'")
        self.S = self.DB.get_line('add1,add2,add3,add4,add5,add6,add7,add8,add9,add10,add11,add12,add14,add15,add16,add17,add18,add20,add21,add22,add23')

        self.M['수량확보']  = True if self.S['add21'] == 'on' else False  # 추가자본 투입 후 수량확보 선택
        self.M['강매허용']  = True if self.S['add16'] == 'on' else False  # 날수 초과 후 강매선택
        self.M['매수허용']  = True if self.S['add14'] == 'on' else False  # 횟수 초과 후 매수허용 선택
        self.M['과거추종']  = True if self.S['add15'] == 'on' else False  # 횟수 초과 후 과거추종 선택
        self.M['종가기준']  = True if self.S['add7']  == 'on' else False  # 횟수 초과 후 매수허용 선택
        self.M['과추일반']  = True if self.S['add6']  == 'on' else False  # 일반 매수에서 과거추종 여부
        self.M['매도대기']  = int(self.S['add11']) # 매도대기 이전에 매도되는 것을 방지(보다 큰 수익 실현을 위해)
        self.M['매수비중']  = float(self.S['add3'])/100
        self.M['평단가치']  = 1 + float(self.S['add4'])/100
        self.M['큰단가치']  = 1 + float(self.S['add5'])/100
        self.M['분할횟수']  = int(self.S['add2'])

        # 매수전략 매도전략
        self.M['평단매수'] = self.M['큰단매수'] = self.M['추종매수'] = self.M['추가매수'] = self.M['전략매수'] = 'LOC'
        self.M['평단수량'] = self.M['큰단수량'] = self.M['추종수량'] = self.M['추가수량'] = self.M['전략수량'] = 0
        self.M['평단단가'] = self.M['큰단단가'] = self.M['추종단가'] = self.M['추가단가'] = self.M['전략단가'] = 0.0

        self.M['첫째매도'] = self.M['둘째매도'] = self.M['강제매도'] = 'NOR' 
        self.M['전략매도'] = 'LOC'
        self.M['첫째수량'] = self.M['둘째수량'] = self.M['강제수량'] = self.M['전매수량'] = 0
        self.M['첫째단가'] = self.M['둘째단가'] = self.M['강제단가'] = self.M['전매단가'] = 0.0
   

    def old_price_trace(self) :
        now = int(time.mktime(datetime.strptime(self.M['기록일자'],'%Y-%m-%d').timetuple()))
        old = now-3600*24*10
        old_date = datetime.fromtimestamp(old).strftime('%Y-%m-%d')
        qry = f"SELECT add3 FROM h_stockHistory_board WHERE add0 BETWEEN '{old_date}' and '{self.M['기록일자']}' and add1='{self.M['종목코드']}' ORDER BY add0"
        aaa= self.DB.exe(qry)
        bbb= [float(x[0]) for x in aaa ]
        self.M['전일종가'] = bbb[-2]
        c_drop = 0
        for i in range(1,len(bbb)) :
            c_drop = c_drop + 1 if bbb[i] <= bbb[i-1] else 0

        return c_drop


    def cur_price(self) :
        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add0='{self.M['기록일자']}' and add1='{self.M['종목코드']}'")
        tmp =  self.DB.get_one('add3')
        return float(tmp)

    def the_first_day(self) :
        self.M['시즌'] = 1
        self.M['날수'] = 1
        self.M['회차'] = 1.0

        self.M['일매수금'] = int(self.M['가용잔액'] / self.M['분할횟수'])
        self.M['평균단가']  = self.M['당일종가']
        self.M['보유수량']  = self.M['체결수량'] = int(self.M['일매수금']/self.M['당일종가'])
        self.M['매수금액']  = self.M['당일종가'] * self.M['체결수량']
        self.M['총매수금']  = self.M['평가금액'] = self.M['매수금액']
        self.M['수익현황']  = self.M['수익률'] = 0.0
        self.M['가용잔액'] -= self.M['매수금액']
        self.M['매매현황']  = 'S'
        self.M['진행상황']  = '첫날거래'

        self.M['위기전략'] = 'NO'
        self.M['전략매금'] = '0.0'
        self.M['전략가격'] = '0.0'        

    def strategy_sell(self) :
        pass

    def force_sell(self) :
        pass

    def normal_sell(self) :
        pass
    
    def secondary_buy(self) :
        self.M['추가수량'] = math.ceil(self.M['일매수금'] / self.M['평균단가'])
        self.M['추가단가'] = self.M['평균단가']

    def acc_old(self) :
        self.M['추종단가'] = self.M['전일종가'] if self.M['종가기준'] else self.M['평균단가']
        self.M['추종수량'] = math.ceil(self.M['일매수금'] * self.M['연속하락'] / self.M['추종단가']) 

    def normal_buy(self)  :
        매수금액1  = self.M['일매수금'] * self.M['매수비중']
        매수금액2  = self.M['일매수금'] - 매수금액1
        self.info(f"{매수금액1} {매수금액2}")
        self.M['평단단가'] = self.M['평균단가'] * self.M['평단가치'] 
        self.M['큰단단가'] = self.M['평균단가'] * self.M['큰단가치']    
        self.M['평단수량'] = math.ceil(매수금액1/self.M['평단단가'])
        self.M['큰단수량'] = math.ceil(매수금액2/self.M['큰단단가'])   

    def autoinput(self) :
        self.M['기록일자'] = self.D['post']['add0']
        self.M['종목코드'] = self.D['post']['add1']
        self.DB.tbl,self.DB.wre = ('h_daily_trading_board',f"add0  < '{self.M['기록일자']}' and add1='{self.M['종목코드']}'")
        
        self.preChk = self.DB.get_one("max(no)")
        self.oldChk = self.DB.get_one("min(no)")

        self.init_value()

        if not self.preChk :

            if  self.M['가용잔액'] == 0.0 or self.M['추가자본'] == 0.0 :
                self.update['msg'] = "가용잔액과 추자자본에 대한 정보를 입력하여 주시기바랍니다"
                self.update['replyCode'] = 'NMDATA01'
                return self.json(self.update)
            else :
                self.the_first_day()
                
        
        # 매도전략
        # if self.M['수량확보'] and self.M['위기상향'] == 'YES' : self.strategy_sell()
        # if self.M['강매허용'] : self.force_sell()
        # if self.M['날수'] > self.M['매도대기'] : self.normal_sell()

        # 매수전략
        self.info(f"회차 {self.M['회차']} 분할횟수 {self.M['분할횟수']}")
        if self.M['회차'] <= self.M['분할횟수'] : 
            self.normal_buy()
            if self.M['과추일반'] : self.acc_old()
        else :
            if not self.M['위기전략'] :
                    if self.M['매수허용'] : self.secondary_buy() 
                    if self.M['과거추종'] : self.acc_old()          

        # if self.M['전략매금'] and self.M['수량확보'] : self.strategy_buy()

        return self.return_value()

    def return_value(self) :
        update = {}
        update['msg']       = "데이타를 자동으로 계산하였습니다. 확인해 보시고 저장하시기 바랍니다"
        update['replyCode'] = "SUCCESS"

        update['add2']   = self.M['시즌']
        update['add3']   = self.M['날수']
        update['add4']   = self.M['회차']
        update['add5']   = f"{round(self.M['당일종가'],4):,.2f}"
        update['add6']   = update['add5'] # 체결단가 = 당일종가

        update['add7']    = f"{self.M['체결수량']:,}"
        update['add8']    = f"{round(self.M['매수금액'],4):,.2f}"
        update['add9']    = f"{round(self.M['평균단가'],4):,.2f}"
        update['add10']   = f"{self.M['보유수량']:,}"
        update['add11']   = f"{round(self.M['평가금액'],4):,.2f}"
        update['add12']   = f"{round(self.M['총매수금'],4):,.2f}"
        update['add13']   = self.M['매매현황']
        update['add14']   = f"{round(self.M['수익현황'],4):,.2f}"
        update['add15']   = f"{round(self.M['수익률'],4):,.2f}"
        update['add16']   = f"{round(self.M['가용잔액'],4):,.2f}"
        update['add17']   = f"{round(self.M['추가자본'],4):,.2f}"
        update['add18']   = self.M['진행상황']
        update['add19']   = self.M['일매수금']

        update['sub1']   = self.M['연속하락']
        update['sub2']   = self.M['위기전략']
        update['sub3']   = self.M['전략매금']
        update['sub4']   = self.M['전략가격']

        update['buy1']   = self.M['평단매수']
        update['buy11']  = self.M['평단수량']
        update['buy12']  = f"{round(self.M['평단단가'],4):,.2f}"
        update['buy2']   = self.M['큰단매수']
        update['buy21']  = self.M['큰단수량']
        update['buy22']  = f"{round(self.M['큰단단가'],4):,.2f}"
        update['buy3']   = self.M['추종매수']
        update['buy31']  = self.M['추종수량']
        update['buy32']  = f"{round(self.M['추종단가'],4):,.2f}"
        update['buy4']   = self.M['추가매수']
        update['buy41']  = self.M['추가수량']
        update['buy42']  = f"{round(self.M['추가단가'],4):,.2f}"
        update['buy5']   = self.M['전략매수']
        update['buy51']  = self.M['전략수량']
        update['buy52']  = f"{round(self.M['전략단가'],4):,.2f}"


        update['sell1']   = self.M['첫째매도']
        update['sell2']   = self.M['둘째매도']
        update['sell3']   = self.M['강제매도']
        update['sell4']   = self.M['전략매도']

        
        return self.json(update)
