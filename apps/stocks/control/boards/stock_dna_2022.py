from system.core.load import Control
from datetime import datetime,timedelta
import math

class Stock_dna_2022(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')
        self.M = {}

    def init_value(self) :
        self.auto = True
        # POST 데이타, 사용자 입력으로 부터 데이타를 받아서 초기화 
        self.M['매매전략'] = self.D['post']['add20']
        
        self.M['체결단가'] = self.D['post']['add6']   ; self.M['체결단가'] = float(self.M['체결단가'].replace(',','')) if self.M['체결단가'] else 0.0
        self.M['체결수량'] = self.D['post']['add7']   ; self.M['체결수량'] =   int(self.M['체결수량'].replace(',','')) if self.M['체결수량'] else 0
        self.M['매수금액'] = self.D['post']['add8']   ; self.M['매수금액'] = float(self.M['매수금액'].replace(',','')) if self.M['매수금액'] else 0.0
        
        # 임의입력 시 체결단가, 체결수량, 매수금액 중 2개는 입력되어야 함
        if  self.M['체결단가'] or self.M['체결수량'] or self.M['매수금액'] :
            self.auto = False 
            if   self.M['체결단가'] and self.M['체결수량'] : self.M['매수금액'] = self.M['체결단가'] * self.M['체결수량']
            elif self.M['체결단가'] and self.M['매수금액'] : self.M['체결수량'] = int(self.M['매수금액'] / self.M['체결단가'])
            elif self.M['체결수량'] and self.M['매수금액'] : self.M['체결단가'] = self.M['매수금액'] / self.M['체결수량']
        
        self.M['가용잔액'] = self.D['post']['add16']  ; self.M['가용잔액'] = float(self.M['가용잔액'].replace(',','')) if self.M['가용잔액'] else 0.0
        self.M['추가자본'] = self.D['post']['add17']  ; self.M['추가자본'] = float(self.M['추가자본'].replace(',','')) if self.M['추가자본'] else 0.0
        
        self.M['연속하락'] = self.old_price_trace('DN')  
        self.M['연속상승'] = self.old_price_trace('UP') 
        self.M['체결단가'] = self.M['체결단가'] if self.M['체결단가'] else self.M['당일종가']

        # 매매전략 가져오기
        self.DB.tbl, self.DB.wre = ('h_stock_strategy_board',f"add0='{self.M['매매전략']}'")
        self.S = self.DB.get_line('add1,add2,add3,add4,add5,add6,add7,add8,add9,add10,add11,add12,add14,add15,add16,add17,add18,add20,add21,add22,add23,add24,add25')
        self.M['분할횟수']  = int(self.S['add2'])

        # 매수 매도 초기화
        
        self.M['평단매수']='LOC';  self.M['평단수량'] = 0 ; self.M['평단단가'] = 0.0 ; self.M['매수비중']=float(self.S['add3'])/100 ; self.M['평단가치']=1+float(self.S['add4'])/100
        self.M['큰단매수']='LOC';  self.M['큰단수량'] = 0 ; self.M['큰단단가'] = 0.0 ; self.M['큰단가치']=1+float(self.S['add5'])/100
        self.M['추종매수']='LOC';  self.M['추종수량'] = 0 ; self.M['추종단가'] = 0.0 
        self.M['추가매수']='LOC';  self.M['추가수량'] = 0 ; self.M['추가단가'] = 0.0         
        self.M['전략매수']='LOC';  self.M['전략수량'] = 0 ; self.M['전략단가'] = 0.0
        self.M['첫째매도']='LOC';  self.M['첫째수량'] = 0 ; self.M['첫째단가'] = 0.0 ; self.M['매도비중']=float(self.S['add8'])/100 ; self.M['첫매가치']=1+float(self.S['add9'])/100
        self.M['둘째매도']='LOC';  self.M['둘째수량'] = 0 ; self.M['둘째단가'] = 0.0 ; self.M['둘매가치']=1+float(self.S['add10'])/100
        self.M['강제매도']='NOR';  self.M['강제수량'] = 0 ; self.M['강제단가'] = 0.0 ; self.M['강매시작']=int(self.S['add17']) ; self.M['강매가치']=1+float(self.S['add18'])/100
        self.M['전략매도']='LOC';  self.M['전매수량'] = 0 ; self.M['전매단가'] = 0.0 
        self.M['매도금액']=0.0  
        
        # 조건 트리거
        self.M['수량확보']  = True if self.S['add21'] == 'on' else False  # 추가자본 투입 후 수량확보 선택
        self.M['강매허용']  = True if self.S['add16'] == 'on' else False  # 날수 초과 후 강매선택
        self.M['매수허용']  = True if self.S['add14'] == 'on' else False  # 횟수 초과 후 매수허용 선택
        self.M['과거추종']  = True if self.S['add15'] == 'on' else False  # 횟수 초과 후 과거추종 선택
        self.M['종가기준']  = True if self.S['add7']  == 'on' else False  # 횟수 초과 후 매수허용 선택
        self.M['과추일반']  = True if self.S['add6']  == 'on' else False  # 일반 매수에서 과거추종 여부
        self.M['매도대기']  = int(self.S['add11']) # 매도대기 이전에 매도되는 것을 방지(보다 큰 수익 실현을 위해)
        self.M['리밸런싱']  = True if self.S['add12'] == 'on' else False  # 리밸런싱 수행 여부


        # 전략 매수 매도 가격 설정
        self.M['매도시점']  = float(self.S['add22'])/100 ; self.M['매수시점'] = float(self.S['add23'])/100 
        self.M['전매횟수']  = int(self.S['add24'])
        self.M['전매비중']  = float(self.S['add25'])/100
        # 매도 체크
        self.M['매도수량'] = 0

        # 첫날이 아닌 경우 기본변수 초기화
        self.M['첫날기록']  = False
        if self.preChk :

            self.DB.tbl, self.DB.wre = (self.parm[0],f"no={self.preChk}")
            self.B = self.DB.get_line('*')

            self.M['시즌'] = int(self.B['add2'])

            self.M['평균단가'] = float(self.B['add9'])

            self.M['일매수금'] = int(self.B['sub6'])
            self.M['날수'] = int(self.B['add3']) + 1
            self.M['회차'] = float(self.B['add4'])            
            self.M['매매현황'] = ''
            self.M['진행상황'] = '매도대기'
            self.M['보유수량'] = int(self.B['add10'])
            self.M['가용잔액'] = float(self.B['add16'])
            self.M['추가자본'] = float(self.B['add17'])
            self.M['총매수금'] = float(self.B['add12'])
            self.M['위기전략'] = True if self.B['sub2'] == 'YES' else False  
            self.M['전략매금'] = float(self.B['sub3']) ; self.M['전략가격'] = float(self.B['sub4'])

            self.M['처음자본'] = float(self.B['sub7']) 
            self.M['처음추가'] = float(self.B['sub8']) 
            self.M['연속하락'] = int(self.B['sub1'])

            self.M['진행'] = round(self.M['총매수금'] / self.M['처음자본'] * 100,1)

    def rebalance(self)  :
        total = self.M['처음자본'] + self.M['처음추가']
        self.M['자본비율'] = self.M['처음자본'] / total
        total1 =self.M['가용잔액'] + self.M['추가자본']
        self.M['가용잔액'] = round(total1 * self.M['자본비율'], 2)
        self.M['추가자본'] = total1 - self.M['가용잔액']
        self.M['일매수금'] = int(self.M['가용잔액']/self.M['분할횟수'])

    def calculate(self)  :
        
        if  self.M['매도수량'] :
            ratio = self.M['매도수량'] / self.M['보유수량']
            self.M['매도금액']  = self.M['당일종가'] * self.M['매도수량']
            self.M['매도수익']  = self.M['매도금액'] - self.M['총매수금'] * ratio  
            self.M['매수익률']  = self.M['매도수익'] / (self.M['총매수금'] * ratio) * 100
            self.M['보유수량'] -= self.M['매도수량']  
            self.M['가용잔액'] += self.M['매도금액']
            self.M['총매수금']  = self.M['보유수량'] * self.M['평균단가']
            if  self.M['보유수량'] == 0 :
                self.M['진행상황']  = '전량매도' 
                self.M['전략매금']  = 0
                self.M['전략가격']  = 0
            else :
                self.M['진행상황']  = '전략매도' 
                self.M['전략매금']  = self.M['매도금액']
                self.M['전략가격']  = self.M['당일종가']
                self.M['전매수량']  = 0
                self.M['전매단가']  = 0.0
            
            self.M['위기전략']  = False
            self.M['날수'] = 0

        if self.M['체결수량'] :
            if self.auto : self.M['매수금액']  =  self.M['체결수량'] * self.M['체결단가']
            self.M['가용잔액'] -=  self.M['매수금액']
            self.M['보유수량'] +=  self.M['체결수량']
            self.M['총매수금'] +=  self.M['매수금액']


        self.M['평가금액']  =  self.M['당일종가'] * self.M['보유수량']
        self.M['평균단가']  =  self.M['총매수금'] / self.M['보유수량'] if self.M['보유수량'] != 0 else 0
        self.M['수익현황']  =  self.M['평가금액'] - self.M['총매수금']
        self.M['수익률']    = (self.M['수익현황'] / self.M['총매수금']) * 100 if self.M['총매수금'] else 0
        self.M['진행'] = round(self.M['총매수금'] / self.M['처음자본'] * 100,1)

        if  self.M['진행상황'] == '전량매도' :
            self.M['수익현황'] = self.M['매도수익']
            self.M['수익률']   = self.M['매수익률']
            self.M['평균단가'] = float(self.B['add9'])
            if self.M['리밸런싱'] : self.rebalance()      
      
        self.M['연속하락'] = self.old_price_trace('DN')

    # 당일종가 전일종가 와 연속하락 일수 구하기  
    def old_price_trace(self,opt) :
        datetime_now = datetime.strptime(self.M['기록일자'],'%Y-%m-%d')
        old_date = datetime_now - timedelta(days=14)
        qry = f"SELECT add3 FROM h_stockHistory_board WHERE add0 BETWEEN '{old_date}' and '{self.M['기록일자']}' and add1='{self.M['종목코드']}' ORDER BY add0"
        aaa= self.DB.exe(qry)
        bbb= [float(x[0]) for x in aaa ]
        if opt == 'CDN' or opt == 'CUP' : bbb = bbb[:-1]
        self.M['전일종가'] = bbb[-2]
        self.cur_price()
        c_drop = 0
        c_goup = 0
        for i in range(1,len(bbb)) :
            c_drop = c_drop + 1 if bbb[i] <  bbb[i-1] else 0
            c_goup = c_goup + 1 if bbb[i] >= bbb[i-1] else 0
        if opt == 'DN' or opt == 'CDN' :
            return c_drop
        elif opt == 'UP' or opt == 'CUP' :
            return c_goup
        elif opt == 'YD' :
            return bbb[-2]

    def cur_price(self) :
        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add0='{self.M['기록일자']}' and add1='{self.M['종목코드']}'")
        tmp = self.DB.get('add3,add5',many=1,assoc=False)
        if tmp : self.M['당일종가'], self.M['당일고가'] = (float(tmp[0]),float(tmp[1]))
        else : 
            self.M['당일종가'] = 0.0
            self.M['당일고가'] = 0.0

    def the_first_day(self) :
        cnt = 0
        self.M['시즌'] = int(self.M['시즌체크']) if self.M['시즌체크'] else 1  ; 
        self.M['날수'] = 1 
        #리밸런싱
        self.M['처음자본'] = self.M['가용잔액']
        self.M['처음추가'] = self.M['추가자본'] 

        self.M['일매수금'] = int(self.M['가용잔액'] / self.M['분할횟수'])
        self.M['체결단가'] = self.M['당일종가']
        
        if self.auto : 
            self.M['체결수량'] = math.ceil(self.M['일매수금']/self.old_price_trace('YD')) 
            if cnt:=self.old_price_trace("CDN") : 
                self.M['체결수량'] += self.M['체결수량'] * cnt 

        self.M['매수금액']  = self.M['당일종가'] * self.M['체결수량']
        self.M['평균단가']  = self.M['당일종가']
        self.M['보유수량']  = self.M['체결수량']
        self.M['평가금액']  = self.M['당일종가'] * self.M['보유수량']
        self.M['총매수금']  = self.M['매수금액']
        self.M['수익현황']  =  self.M['평가금액'] - self.M['총매수금']
        self.M['수익률']    = (self.M['수익현황'] / self.M['총매수금']) * 100 if self.M['총매수금'] else 0
        self.M['가용잔액'] -= self.M['매수금액']
        self.M['매매현황']  = 'S'
        if cnt : self.M['매매현황']  += str(cnt)
        self.M['진행상황']  = '첫날거래'
        self.M['위기전략']  = False ; self.M['전략매금'] = 0 ; self.M['전략가격'] = 0
        self.M['첫날기록']  = False
        self.M['연속하락']  = self.old_price_trace('DN')
        self.M['진행'] = round(self.M['총매수금'] / self.M['처음자본'] * 100,1)

    def strategy_sell(self) :
        if  self.M['수익률'] > 0 : 
            self.M['진행상황'] = '일매대기'
            return
        self.M['전매수량'] = int(self.M['보유수량']*self.M['전매비중']) 
        self.M['전매단가'] = self.M['평균단가'] * (1+self.M['매도시점'])
        self.M['진행상황'] = '전매대기'

    def normal_sell(self) :

        self.M['첫째단가'] = self.M['평균단가'] * self.M['첫매가치'] if not self.M['전략매금'] else self.M['평균단가'] * self.M['둘매가치']
        if (self.M['첫째단가']-self.M['당일종가']) / self.M['당일종가'] > 0.35 : return

        self.M['첫째수량'] = self.M['보유수량'] 


    def base_buy(self) :
        
        매수금액1  = self.M['일매수금'] * self.M['매수비중']
        매수금액2  = self.M['일매수금'] - 매수금액1
        self.M['평단단가'] = self.M['당일종가'] 
        self.M['큰단단가'] = self.M['당일종가'] * 1.15
  
        self.M['평단수량'] = math.ceil(매수금액1 / self.M['평단단가']) *4  
        self.M['큰단수량'] = math.ceil(매수금액2 / (self.M['평균단가']*self.M['큰단가치'])) *2  

    def normal_buy(self)  :

        매수단가 = self.M['당일종가']
        한도금액 = self.M['추가자본'] + self.M['가용잔액']
       
        기본수량 = math.ceil(self.M['일매수금'] / 매수단가)
        
        if self.M['연속상승'] >=1 :
            if 한도금액 < self.M['일매수금'] * 2 :
                self.M['큰단수량'] = int(한도금액 / 매수단가)
                self.M['큰단단가'] = 매수단가
            else :
                self.M['큰단수량'] = 기본수량 * 2
                self.M['큰단단가'] = 매수단가

        if self.M['연속하락'] >= 1 :
            
            if 한도금액 < self.M['일매수금'] * (1+self.M['연속하락']) :
                self.M['평단수량']  = int(한도금액 / 매수단가)
                self.M['평단단가']  = 매수단가
            else :
                self.M['평단수량']  = 기본수량 * (1+self.M['연속하락'])
                self.M['평단단가'] = 매수단가
                
    def check_sell(self) :

        # 변수 불러오기
        self.M['전매수량'] = int(self.B['sell41']) ; self.M['전매단가'] = float(self.B['sell42'])
        self.M['강매수량'] = int(self.B['sell31']) ; self.M['강매단가'] = float(self.B['sell32'])
        self.M['첫매수량'] = int(self.B['sell11']) ; self.M['첫매단가'] = float(self.B['sell12'])
        self.M['둘매수량'] = int(self.B['sell21']) ; self.M['둘매단가'] = float(self.B['sell22'])


        # 일반매도
        if self.M['첫매수량'] and self.M['당일종가'] >= self.M['첫매단가'] : self.M['매도금액'] += self.M['당일종가'] * self.M['첫매수량']  ; self.M['매도수량'] += self.M['첫매수량']  
        if self.M['둘매수량'] and self.M['당일종가'] >= self.M['둘매단가'] : self.M['매도금액'] += self.M['당일종가'] * self.M['둘매수량']  ; self.M['매도수량'] += self.M['둘매수량']  
        # 전략매도
        if self.M['전매수량'] and self.M['당일종가'] >= self.M['전매단가'] : self.M['매도수량'] += self.M['전매수량'] 

    
    def check_buy(self) :

        if self.auto :
            CP = 21
            # 큰단매수 검토
            if many := int(self.B['buy21'])  : 
                if  self.M['당일종가'] <= float(self.B['buy22']):  
                    if self.M['진행'] < CP : # 기초매수
                        self.M['체결수량'] += many ; self.M['매매현황'] = 'B'  
                        self.M['진행상황']  = '기초매수'
                    else : # 연속상승
                        if (self.M['추가자본'] + self.M['가용잔액']) < self.M['일매수금'] * 2 : self.M['위기전략'] = True
                        self.M['체결수량'] += many ; self.M['매매현황'] += 'T'
                        self.M['진행상황']  = '터닝매수'

            # 평단매수 검토
            if many := int(self.B['buy11'])  : 
                if  self.M['당일종가'] <= float(self.B['buy12']):  
                    if self.M['진행'] < CP : # 기초매수
                        self.M['체결수량'] += many ; self.M['매매현황'] = 'A' 
                        self.M['진행상황']  = '기초매수'                      
                    else : # 연속하락
                        if (self.M['추가자본'] + self.M['가용잔액']) < self.M['일매수금'] * (1+self.M['연속하락']) : self.M['위기전략'] = True
                        self.M['체결수량'] += many ; self.M['매매현황'] += 'D' + str(self.M['연속하락'])
                        self.M['진행상황']  = '추종매수'

        else :
            self.M['매매현황'] += 'M'    


    def autoinput(self) :
        self.update={}
        self.M['기록일자'] = self.D['post']['add0']
        self.M['종목코드'] = self.D['post']['add1']
        self.M['시즌체크'] = self.D['post'].get('add2',0)
        self.DB.tbl,self.DB.wre = (self.parm[0],f"add0  < '{self.M['기록일자']}' and add1='{self.M['종목코드']}' and add19='시즌진행'")
        if self.M['시즌체크'] : self.DB.wre += f" and add2='{self.M['시즌체크']}'"
        self.preChk = self.DB.get_one("max(no)")
        self.oldChk = self.DB.get_one("min(no)")

        self.DB.tbl, self.DB.wre = (self.parm[0],f"add0='{self.M['기록일자']}' and add1='{self.M['종목코드']}'")
        if self.M['시즌체크'] : self.DB.wre += f" and add2='{self.M['시즌체크']}'"
        if self.DB.get_one('add0') and self.parm[0] != 'modify': 
            self.update['msg'] = "같은 날자에 입력된 데이타가 존재합니다" 
            self.update['replyCode'] = 'NOTICE'
            return self.json(self.update)
        self.init_value()

        if not self.M['당일종가'] : self.update['msg'] = "해당일 기록된 주가를 찾을 수 없습니다" ;self.update['replyCode'] = 'NOTICE'; return self.json(self.update)
        if not self.preChk :
            if  self.M['가용잔액'] == 0.0 or self.M['추가자본'] == 0.0 :
                self.update['msg'] = "가용잔액과 추자자본에 대한 정보를 입력하여 주시기바랍니다"
                self.update['replyCode'] = 'NMDATA01'
                return self.json(self.update)
            else :
                self.the_first_day()

        else :
            # 매도상황 검토
            self.check_sell()
            # 매수상황 검토
            self.check_buy()
            self.calculate()
            if self.M['첫날기록'] : self.the_first_day()
            
       
        # 매도전략
        CP = 21
        if self.M['진행'] >= CP : self.normal_sell()
        if self.M['위기전략'] : self.strategy_sell()

        # 매수전략
        if not  self.M['위기전략'] :
            if  self.M['진행'] < CP : 
                self.base_buy()
            else : 
                self.normal_buy()

   
        return self.return_value()

    def return_value(self) :
        update = {}
        update['msg']       = "데이타를 자동으로 계산하였습니다. 확인해 보시고 저장하시기 바랍니다"
        update['replyCode'] = "SUCCESS"

        update['add2'] = self.M['시즌'] ; update['add3'] = self.M['날수'] ; update['add4'] = self.M['진행'] 

        update['add5']   = f"{round(self.M['당일종가'],4):,.2f}" ; update['add6'] = f"{round(self.M['체결단가'],4):,.2f}" ; update['add7'] = f"{self.M['체결수량']:,}"

        update['add8']   = f"{round(self.M['매수금액'],4):,.4f}"; update['add9'] = f"{round(self.M['평균단가'],4):,.4f}" ; update['add10'] = f"{self.M['보유수량']:,}"

        update['add11']  = f"{round(self.M['평가금액'],4):,.4f}"; update['add12']= f"{round(self.M['총매수금'],4):,.4f}" ; update['add14']   = f"{round(self.M['수익현황'],4):,.4f}"

        update['add15']  = f"{round(self.M['수익률'],4):,.4f}"  ; update['add16']   = f"{round(self.M['가용잔액'],4):,.4f}" ; update['add18']   = self.M['진행상황']

        update['add13']  = f"{round(self.M['매도금액'],4):,.2f}" if self.M['매도금액'] else self.M['매매현황']
          
        update['sub6'] = self.M['일매수금'] ; update['add17']   = f"{round(self.M['추가자본'],4):,.2f}"
        
        update['sub1']   = self.M['연속하락'] ; update['sub2'] = 'YES' if self.M['위기전략'] else 'NO'; 
        update['sub3'] = self.M['전략매금'] ;   update['sub4'] = self.M['전략가격']

        update['buy1']   = self.M['평단매수'] ; update['buy11'] = self.M['평단수량'] ; update['buy12'] = f"{round(self.M['평단단가'],4):,.2f}"
        update['buy2']   = self.M['큰단매수'] ; update['buy21'] = self.M['큰단수량'] ; update['buy22'] = f"{round(self.M['큰단단가'],4):,.2f}"
        update['buy3']   = self.M['추종매수'] ; update['buy31'] = self.M['추종수량'] ; update['buy32'] = f"{round(self.M['추종단가'],4):,.2f}"
        update['buy4']   = self.M['추가매수'] ; update['buy41'] = self.M['추가수량'] ; update['buy42'] = f"{round(self.M['추가단가'],4):,.2f}"
        update['buy5']   = self.M['전략매수'] ; update['buy51'] = self.M['전략수량'] ; update['buy52'] = f"{round(self.M['전략단가'],4):,.2f}"

        update['sell1']  = self.M['첫째매도'] ;  update['sell11']  = self.M['첫째수량']  ; update['sell12']  = f"{round(self.M['첫째단가'],4):,.2f}"
        update['sell2']  = self.M['둘째매도'] ;  update['sell21']  = self.M['둘째수량']  ; update['sell22']  = f"{round(self.M['둘째단가'],4):,.2f}"
        update['sell3']  = self.M['강제매도'] ;  update['sell31']  = self.M['강제수량']  ; update['sell32']  = f"{round(self.M['강제단가'],4):,.2f}"
        update['sell4']  = self.M['전략매도'] ;  update['sell41']  = self.M['전매수량']  ; update['sell42']  = f"{round(self.M['전매단가'],4):,.2f}"

        update['sub7'] = self.M['처음자본']
        update['sub8'] = self.M['처음추가']

        return self.json(update)