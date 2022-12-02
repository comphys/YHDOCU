from system.core.load import Control
from datetime import datetime,timedelta
import math

class Stock_victory(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')
        self.M = {}
        self.tbl = self.parm[0]
        self.M['진행일자'] = self.D['post']['add0']
        self.DB.tbl, self.DB.wre = (self.tbl, f"add0 < '{self.M['진행일자']}'")
        old_date = self.DB.get_one("max(add0)")
        self.DB.wre = f"add0='{old_date}'"
        self.M['LD'] = self.DB.get_line('*')

        # 종가구하기
        self.DB.clear()
        self.DB.tbl = 'h_stockHistory_board'
        self.DB.wre = f"add0='{self.M['진행일자']}' and add1='JEPQ'"; self.M['JEPQ']  = self.DB.get_one('add3')
        self.DB.wre = f"add0='{self.M['진행일자']}' and add1='SOXL'"; 
        self.M['당일종가'] = float(self.DB.get_one('add3'))
        self.M['전일종가'] = float(self.M['LD']['add14'])
        self.M['연속상승'] = self.DB.get_one('add9')
        self.M['연속하락'] = self.DB.get_one('add10')

    def init_value(self) :
        LD = self.M['LD']
        
        # 매매전략 가져오기
        self.M['매매전략'] = 'VICTORY'
        self.DB.tbl, self.DB.wre = ('h_stock_strategy_board',f"add0='{self.M['매매전략']}'")
        self.S = self.DB.get_line('add2,add9,add10,add17,add18,add25')
        self.M['분할횟수']  = int(self.S['add2'])
        self.M['첫매가치']  = 1 + float(self.S['add9'])/100
        self.M['둘매가치']  = 1 + float(self.S['add10'])/100
        self.M['강매시작']  = int(self.S['add17'])
        self.M['강매가치']  = 1 + float(self.S['add18']) / 100
        self.M['위매비중']  = int(self.S['add25'])

        # 매수 매도 초기화
        self.M['매수금액']=0.0
        self.M['매도금액']=0.0  
        self.M['변동수량'] = 0
        self.M['매수수량'] = 0
        self.M['매도수량'] = 0
        self.M['전매도량'] = 0
        self.M['전매도가'] = 0.0

        self.M['시즌'] = int(LD['sub1'])
        self.M['평균단가'] = float(LD['sub16'])
        self.M['일매수금'] = int(LD['sub4'])
        self.M['경과일수'] = int(LD['sub12']) 
        self.M['매매현황'] = ''
        self.M['진행상황'] = '매도대기'
        self.M['보유수량'] = int(LD['add13'])
        self.M['현매수금'] = float(LD['sub17'])
        self.M['가용잔액'] = float(LD['add19'])
        self.M['추가자금'] = float(LD['add20'])
        self.M['진행상황'] = '매도대기'
        self.M['기초수량'] = int(LD['sub18'])

    def calculate(self)  :

        매도가격 = self.M['당일종가']
        매수가격 = self.M['당일종가']
        if self.M['보유수량'] : self.M['경과일수'] +=1

        if  self.M['매도수량'] :
            self.M['매도금액'] = 매도가격 * self.M['매도수량']
            self.M['변동수량'] = -self.M['매도수량'] 
            self.M['진행상황'] = '전량매도' 
            self.M['경과일수'] = 0
            
            # 리밸런싱
            자산총액 = self.M['매도금액'] + self.M['가용잔액'] + self.M['추가자금']
            self.M['가용잔액'] = int( 자산총액 * 0.6 )
            self.M['추가자금'] = int( 자산총액 * 0.4 )
            self.M['일매수금'] = int(self.M['가용잔액'] / self.M['분할횟수'])
            self.M['시즌'] += 1
            self.M['경과일수'] = 0
            self.M['기초수량'] = 0

        if  self.M['매수수량'] :

            self.M['매수금액']  = 매수가격 * self.M['매수수량']
            self.M['변동수량']  = self.M['매수수량']
            self.M['보유수량'] += self.M['매수수량']
            self.M['평균단가']  = (self.M['현매수금'] + self.M['매수금액']) / self.M['보유수량'] 

            self.M['가용잔액'] -=  self.M['매수금액']
            if  self.M['가용잔액'] < 0 : 
                self.M['추가자금'] += self.M['가용잔액']
                self.M['가용잔액'] = 0
                
            self.M['진행상황'] = '일반매수'

        if  not self.M['경과일수'] and self.M['매수수량'] : self.M['경과일수'] = 1

    def normal_sell(self) :

        if  self.M['경과일수'] ==  0 :
            self.M['전매도량']  =  0
            self.M['전매도가']  =  self.M['당일종가']
            return

        매수수량 = math.ceil(self.M['기초수량'] * (self.M['경과일수']+1))
        매도가격 = self.M['평균단가'] * self.M['첫매가치']  if self.M['평균단가'] else self.M['당일종가']

        if (매수수량 * self.M['전일종가']) > self.M['가용잔액'] + self.M['추가자금'] : 매도가격 = self.M['평균단가']*self.M['둘매가치']

        if self.M['경과일수'] > self.M['강매시작'] : 매도가격 = self.M['평균단가']*self.M['강매가치']

        self.M['전매도량'] = self.M['보유수량']
        self.M['전매도가'] = 매도가격

    def normal_buy(self)  :

        if  self.M['경과일수'] == 0 :
            self.M['전매수량'] = math.ceil(self.M['일매수금']/self.M['당일종가'])
            self.M['전매수가'] = self.M['당일종가']
            return

        if self.M['전매도가'] : 매수단가 = min(self.M['당일종가'],self.M['전매도가'])
        else : 매수단가 = self.M['당일종가']

        매수수량 = math.ceil(self.M['기초수량'] * (self.M['경과일수']+1))
        if  매수수량 * 매수단가 > self.M['가용잔액'] + self.M['추가자금'] : 
            매수수량 = self.M['기초수량'] * self.M['위매비중']
            self.M['진행상황'] = '매수제한'
        if  매수수량 * 매수단가 > self.M['가용잔액'] + self.M['추가자금'] : 
            매수수량 = 0
            self.M['진행상황'] = '매수금지'  

        self.M['전매수량'] = 매수수량
        self.M['전매수가'] = 매수단가
        self.M['예상금액'] = f"{매수수량 * 매수단가 :,.2f}"
       
                
    def check_sell(self) :
        if  not self.M['경과일수'] : return
        if  self.M['당일종가'] >= float(self.M['LD']['sub20']) : 
            self.M['매도수량']  = int(self.M['LD']['sub3'])
      
    def check_buy(self) :
        if  not self.M['경과일수'] : 
            if  self.M['당일종가'] <= self.M['전일종가'] :
                self.M['매수수량']  = self.M['기초수량'] = math.ceil(self.M['일매수금']/self.M['전일종가'])
        else :
            if  self.M['당일종가'] <= float(self.M['LD']['sub19']) : self.M['매수수량']  = int(self.M['LD']['sub2'])


    def autoinput(self) :
        self.init_value()
        # 매도상황 검토
        self.check_sell()
        # 매수상황 검토
        self.check_buy()
        self.calculate()
       
        # 매도전략
        self.normal_sell()
        # 매수전략
        self.normal_buy()
        return self.return_value()

    def return_value(self) :
        ud = {}
        LD = self.M['LD']
        # 현금투자
        ud['add3']=LD['add3'] 
        # JEPQ
        ud['add7']=LD['add7']; ud['sub21']=LD['sub21']; ud['sub22']=LD['sub22']; ud['sub23']=LD['sub23'];  ud['sub24']=LD['sub24']; ud['sub8'] = 0
        # SOXL
        ud['add14']=LD['add14']; ud['add13']=LD['add13']; ud['sub16']=LD['sub16']; ud['sub15']=LD['sub15']; ud['sub14']=LD['sub14'];  ud['sub17']=LD['sub17']
        # 투자상황
        ud['add19']=f"{round(float(LD['add19']),4):,.2f}"; ud['add18']=f"{round(float(LD['add18']),4):,.2f}"; 
        ud['sub25']=f"{int(LD['sub25']):,}"; ud['sub27']=f"{int(LD['sub27']):,}"
        ud['add20']=f"{round(float(LD['add20']),4):,.2f}"; 
        ud['sub26']=f"{int(LD['sub26']):,}"; 
        # 종가
        ud['add8']  = self.M['JEPQ'] if self.M['JEPQ'] else 0
        ud['add14'] = self.M['당일종가']
        ud['sub5'] = self.M['연속상승']
        ud['sub6'] = self.M['연속하락']
        # 매매결과
        ud['add11'] = f"{round(self.M['매수금액'],4):,.2f}"
        ud['add12'] = f"{round(self.M['매도금액'],4):,.2f}"
        ud['sub9']  = self.M['변동수량']
        if self.M['매수금액'] : ud['sub9'] =  self.M['매수수량']
        if self.M['매도금액'] : ud['sub9'] = -self.M['매도수량']
        # 매매상황
        ud['sub11'] = self.M['진행상황']
        # 매매전략
        ud['sub1'] = self.M['시즌'];      ud['sub12'] = self.M['경과일수']
        ud['sub4'] = self.M['일매수금'];  ud['sub18'] = self.M['기초수량']
        ud['sub2'] = self.M['전매수량'];  ud['sub19'] = f"{self.M['전매수가']:,.2f}"
        ud['sub3'] = self.M['전매도량'];  ud['sub20'] = f"{self.M['전매도가']:,.2f}"
        # 자금상황
        ud['add19'] = f"{round(self.M['가용잔액'],4):,.2f}"
        ud['add20'] = f"{round(self.M['추가자금'],4):,.2f}"
        return self.json(ud)
