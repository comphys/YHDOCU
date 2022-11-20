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
        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add0 == '{self.M['진행일자']}'")
        self.DB.wre = f"add0='{self.M['진행일자']}' and add1='JEPQ'"; self.M['JEPQ']    = self.DB.get_one('add3')
        self.DB.wre = f"add0='{self.M['진행일자']}' and add1='SOXL'"; 
        self.M['당일종가'] = float(self.DB.get_one('add3'))
        self.M['전일종가'] = float(self.M['LD']['add14'])

    def init_value(self) :
        LD = self.M['LD']
        # 매매전략 가져오기
        self.M['분할횟수']  = 20

        # 매수 매도 초기화
        self.M['매수금액']=0.0
        self.M['매도금액']=0.0  
        self.M['변동수량'] = 0
        self.M['매수수량'] = 0
        self.M['매도수량'] = 0

        self.M['시즌'] = int(LD['sub1'])
        self.M['평균단가'] = float(LD['sub16'])
        self.M['일매수금'] = int(LD['sub4'])
        self.M['경과일수'] = int(LD['sub16']) 
        self.M['매매현황'] = ''
        self.M['진행상황'] = '매도대기'
        self.M['보유수량'] = int(LD['add13'])
        self.M['현매수금'] = float(LD['sub17'])
        self.M['시즌자금'] = int(LD['add19'])
        self.M['시즌잔액'] = float(LD['add20'])
        self.M['진행상황'] = '매도대기'

        self.M['기초수량'] = math.ceil(self.M['일매수금']/self.M['전일종가'])

    def calculate(self)  :

        매도가격 = self.M['당일종가']
        매수가격 = self.M['당일종가']

        if  self.M['매도수량'] :
            self.M['매도금액'] = 매도가격 * self.M['매도수량']
            self.M['변동수량'] = self.M['매도수량'] 
            self.M['진행상황'] = '전량매도' 
            self.M['경과일수'] = 0
            self.M['시즌자금'] += int((self.M['매도금액'] - self.M['현매수금'])/2)

        if  self.M['매수수량'] :
            self.M['매수금액']  = 매수가격 * self.M['매수수량']
            self.M['변동수량']  = self.M['매수수량']
            self.M['시즌잔액'] -=  self.M['매수금액']
            self.M['진행상황'] = '일반매수'

      
    def normal_sell(self) :

        매수수량 = math.ceil(self.M['기초수량'] * (self.M['경과일수'] + 1))
        매도가격 = self.M['평균단가'] * 1.02

        if (매수수량 * self.M['전일종가']) > self.M['시즌잔액'] + self.M['시즌자금'] : 
            매수수량 = self.M['기초수량']
            self.M['진행상황'] = '매수제한'
            매도가격 = self.M['평균단가']*0.95

        if self.M['경과일수'] > 25 : 매도가격 = self.M['평균단가']*0.8

        self.M['전매도량'] = self.M['보유수량']
        self.M['전매도가'] = 매도가격

    def normal_buy(self)  :

        매수단가 = min(self.M['당일종가'],self.M['전매도가'])
        매수수량 = math.ceil(self.M['기초수량'] * (self.M['경과일수']+1))
        if  매수수량 * 매수단가 > self.M['시즌잔액'] + self.M['시즌자금'] : 매수수량 = self.M['기초수량'] *3
        if  매수수량 * 매수단가 > self.M['시즌잔액'] + self.M['시즌자금'] : 
            매수수량 = 0
            self.M['진행상황'] = '매수금지'  

        self.M['전매수량'] = 매수수량
        self.M['전매수가'] = 매수단가
       
                
    def check_sell(self) :

        if  self.M['당일종가'] >= float(self.M['LD']['sub20']) : 
            self.M['매도수량']  = int(self.M['LD']['sub3'])
      
    def check_buy(self) :
        if  self.M['당일종가'] <= float(self.M['LD']['sub19']) : 
            self.M['매수수량']  = int(self.M['LD']['sub3'])

    def autoinput(self)  :

        return self.return_value()

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
        ud['add7']=LD['add7']; ud['sub21']=LD['sub21']; ud['sub22']=LD['sub22']; ud['sub23']=LD['sub23'];  ud['sub24']=LD['sub24']
        # TQQQ
        ud['add14']=LD['add14']; ud['add13']=LD['add13']; ud['sub16']=LD['sub16']; ud['sub15']=LD['sub15']; ud['sub14']=LD['sub14'];  ud['sub17']=LD['sub17']
        # 투자상황
        ud['add19']=f"{round(float(LD['add19']),4):,.2f}"; ud['add18']=f"{round(float(LD['add18']),4):,.2f}"; 
        ud['sub25']=f"{int(LD['sub25']):,}"; ud['sub27']=f"{int(LD['sub27']):,}"
        ud['add20']=f"{round(float(LD['add20']),4):,.2f}"; 
        ud['sub26']=f"{int(LD['sub26']):,}"; ud['add17']=f"{int(LD['add17']):,}" 
        # 종가
        ud['add8']  = self.M['JEPQ']
        ud['add14'] = self.M['당일종가']
        # 매매결과
        ud['add11'] = self.M['매수금액']  
        ud['add12'] = self.M['매도금액']  
        ud['sub9']  = 0
        if self.M['매수금액'] : ud['sub9'] =  self.M['매수수량']
        if self.M['매수금액'] : ud['sub9'] = -self.M['매도수량']
        # 매매상황
        ud['sub11'] = self.M['진행상황']

        # update['msg']       = "데이타를 자동으로 계산하였습니다. 확인해 보시고 저장하시기 바랍니다"
        # update['replyCode'] = "SUCCESS"

        # update['add2'] = self.M['시즌'] ; update['add3'] = self.M['날수'] ; update['add4'] = self.M['진행'] 

        # update['add5']   = f"{round(self.M['당일종가'],4):,.2f}" ; update['add6'] = f"{round(self.M['매수단가'],4):,.2f}" ; update['add7'] = f"{self.M['매수수량']-self.M['매도수량']:,}"

        # update['add8']   = f"{round(self.M['매수금액']-self.M['매도금액'],4):,.4f}"; update['add9'] = f"{round(self.M['평균단가'],4):,.4f}" ; update['add10'] = f"{self.M['보유수량']:,}"

        # update['add11']  = f"{round(self.M['평가금액'],4):,.4f}"; update['add12']= f"{round(self.M['총매수금'],4):,.4f}" ; update['add14']   = f"{round(self.M['수익현황'],4):,.4f}"

        # update['add15']  = f"{round(self.M['수익률'],4):,.4f}"  ; update['add16']   = f"{round(self.M['가용잔액'],4):,.4f}" ; update['add18']   = self.M['진행상황']

        # update['add13']  = f"{round(self.M['매도수익'],4):,.2f}" if self.M['매도수익'] else self.M['매매현황']
        
        # update['sub5'] = f"{round(self.M['실현손익'],4):,.2f}"
        # update['sub6'] = self.M['일매수금'] ; update['add17']   = f"{round(self.M['추가자본'],4):,.2f}"
        
        # update['sub1']   = self.M['연속하락'] ; update['sub2'] = 'YES' if self.M['위기전략'] else 'NO'; 
        # update['sub3']   = f"{round(self.M['전략매금'],4):,.4f}";   update['sub4'] = self.M['전략가격']

        # update['buy1']   = self.M['평단매수'] ; update['buy11'] = self.M['평단수량'] ; update['buy12'] = f"{round(self.M['평단단가'],4):,.2f}"
        # update['buy2']   = self.M['큰단매수'] ; update['buy21'] = self.M['큰단수량'] ; update['buy22'] = f"{round(self.M['큰단단가'],4):,.2f}"
        # update['buy3']   = self.M['추종매수'] ; update['buy31'] = self.M['추종수량'] ; update['buy32'] = f"{round(self.M['추종단가'],4):,.2f}"
        # update['buy4']   = self.M['추가매수'] ; update['buy41'] = self.M['추가수량'] ; update['buy42'] = f"{round(self.M['추가단가'],4):,.2f}"
        # update['buy5']   = self.M['전략매수'] ; update['buy51'] = self.M['전략수량'] ; update['buy52'] = f"{round(self.M['전략단가'],4):,.2f}"

        # update['sell1']  = self.M['첫째매도'] ;  update['sell11']  = self.M['첫째수량']  ; update['sell12']  = f"{round(self.M['첫째단가'],4):,.2f}"
        # update['sell2']  = self.M['둘째매도'] ;  update['sell21']  = self.M['둘째수량']  ; update['sell22']  = f"{round(self.M['둘째단가'],4):,.2f}"
        # update['sell3']  = self.M['강제매도'] ;  update['sell31']  = self.M['강제수량']  ; update['sell32']  = f"{round(self.M['강제단가'],4):,.2f}"
        # update['sell4']  = self.M['전략매도'] ;  update['sell41']  = self.M['전매수량']  ; update['sell42']  = f"{round(self.M['전매단가'],4):,.2f}"

        # update['sub7'] = self.M['처음자본']
        # update['sub8'] = self.M['처음추가']

        return self.json(ud)
