from myutils.DB import DB
import myutils.my_utils as my

class update_Log :

    def __init__(self) :

        self.DB    = DB('stocks')
        self.chart = False
        self.stat  = False
        self.skey = self.DB.store("slack_key")

        self.B = {}
        self.V = {}
        self.R = {}
        self.S = {}
        self.N = {}
        self.M = {}
        self.D = {}

    def send_message(self,message) :
        if self.DB.system == "Linux" : my.post_slack(self.skey,message)
        else : print(message)  

# ------------------------------------------------------------------------------------------------------------------------------------------
# From rsn.py in sytem lib
# ------------------------------------------------------------------------------------------------------------------------------------------

    def calculate_A(self,tac) :
        
        if  tac['매수수량'] : 
            tac['매수금액'] =  tac['매수수량'] * self.M['당일종가']
            tac['보유수량'] += tac['매수수량']
            tac['현재잔액'] -= tac['매수금액']
            tac['총매수금'] += tac['매수금액']
            tac['평균단가'] =  tac['총매수금'] / tac['보유수량'] 
            self.commission(tac,1)
            
            if  tac['잔액이동'] :
                self.N['현재잔액'] += tac['현재잔액']
                tac['현재잔액'] = 0
                tac['진행상황'] = '매수중단'
                tac['잔액이동'] = False
                self.rebalance_N()
        
        tac['평가금액'] =  tac['보유수량'] * self.M['당일종가']  
        tac['수익현황'] =  tac['평가금액'] - tac['총매수금']
        tac['현수익률'] =  tac['수익현황'] / tac['총매수금'] *  100  if tac['총매수금'] else 0.00    
        
        if  tac['매도수량'] : # VRS 의 매도는 같이 이루어진다.
            tac['매도금액']  = tac['매도수량'] * self.M['당일종가']
            tac['보유수량'] -= tac['매도수량']
            tac['현재잔액'] += tac['매도금액']
            tac['중도합계'] += tac['매도금액']
            tac['수익현황']  = tac['매도금액'] - tac['총매수금']
            tac['현수익률']  = tac['수익현황'] / tac['총매수금'] * 100  if tac['총매수금'] else 0.00 # for N tactic 중간 실현수익률
            tac['중익합계'] += tac['수익현황']  
            tac['실현익률']  = round( tac['중익합계']/(tac['중도합계']-tac['중익합계']) * 100,2 )
            tac['평가금액']  = 0.0 # 그래프에서 토탈가치 표시를 위해 매도일 평가금액도 표시해 주어야 한다.
            tac['평균단가']  = 0.0
            tac['총매수금']  = 0.0

            self.commission(tac,2)
            self.tax(tac)
            if  tac == self.N : 
                self.N['매수차수'] = 0 
                self.N['매도예가'] = 0
                if not self.V['매도수량'] : self.rebalance_N() # just for N tactic 

    def calculate(self)  :
        
        self.calculate_A(self.V) # 계산순서 ( V-N-R-S ) V는 기준, N은 RS의 잔액이동의 영향을 피하기 위해 RS보다 우선 계산함
        self.calculate_A(self.N) 
        self.calculate_A(self.R)
        self.calculate_A(self.S)

        if  self.V['매도수량'] :
            self.rstCount() # self.M['기본진행] 값을 재설정하기 전에 수행되어야 함        
            self.N['매도금액'] = self.N['중도합계']
            self.N['수익현황'] = self.N['중익합계']
            self.N['현수익률'] = self.N['실현익률']
            
            if  self.V['수익현황'] >= 0 : # 현수익률은 RS>N 에 의해 수익이라도 손실로 계산될 수 있어, 수익현황으로 판단하여야 함 
                self.M['기본진행'] = True
                self.set_value(['진행상황'],'익절매도')
            else :
                self.M['기본진행'] = False
                self.set_value(['진행상황'],'손절매도')
            
            self.M['첫날기록'] = True

            self.rebalance()
        
        self.realMDD()

    def realMDD(self) :
        
        # 현수익률을 실최하략으로 적용 ( RSN 전략 특성상, 현재잔액+총매수금이 0일 경우도 발생함)
        if not self.stat : return
        for tac in (self.V,self.R,self.S,self.N) :
            if  tac['현수익률'] < tac['진최하락'] : 
                tac['진최하락'] = tac['현수익률']; tac['최하일자'] = self.M['현재일자']

        if  self.M['현재날수'] > self.M['최장일수'] : 
            self.M['최장일수'] = self.M['현재날수'] 
            self.M['최장일자'] = self.M['현재일자']
        
    def rstCount(self) :
        
        if not self.stat : return
        for profit,key in [(self.V['중익합계'],'일'),(self.R['중익합계'],'기'),(self.S['중익합계'],'안'),(self.N['중익합계'],'생')] :
            if  profit > 0  : 
                if self.M['기본진행'] : self.D[key+'정익절'] += 1
                else : self.D[key+'회익절'] += 1  
            elif profit < 0 : 
                if self.M['기본진행'] : self.D[key+'정손절'] += 1
                else : self.D[key+'회손절'] += 1   

    def commission(self,tac,opt) :
       
        if self.D['수료적용'] == 'on' :
            mm = tac['매수금액'] if opt==1 else tac['매도금액'] 
            fee = int(mm*0.07)/100
            if opt==2 : fee += round(mm*0.0008)/100
            if tac != self.V : self.D['총수수료'] += fee
            tac['수수료등']  = fee
            tac['현재잔액'] -= fee
        
    def tax(self,tac) :

        if self.D['세금적용'] == 'on' : tac['현재잔액'] -= int(tac['수익현황']*0.22) 
   
    def rebalance_N(self) :

        for i in range(self.M['최대차수']) : self.N['매금단계'][i] = int((self.N['현재잔액']+self.N['총매수금']) * self.M['분할배분'][i]) # RS>N 을 고려한 매수기초금액 재 산정
    
        
    def rebalance(self)  :

        total = self.R['현재잔액']+self.S['현재잔액']+self.N['현재잔액']
        
        # RSN rebalance
        if  self.D['일밸런싱'] == 'on' :
            self.R['현재잔액'] = round(total*self.M['투자배분'][0]/100,2)
            self.S['현재잔액'] = round(total*self.M['투자배분'][1]/100,2)
            self.N['현재잔액'] = total - self.R['현재잔액'] - self.S['현재잔액']

        for tac in (self.V,self.R,self.S) :   
            tac['일매수금'] = int(tac['현재잔액']/self.M['분할횟수']) 
            tac['기초수량'] = my.ceil(tac['일매수금'] / self.M['당일종가'])
        
        self.rebalance_N()

        if  self.stat :
            pzero = my.sv(self.D['손익통계'][0][1])
            pbase = my.sv(self.D['손익통계'][-1][1])
            difft = total - pbase
            diffz = total - pzero
            diffp = difft/pbase * 100
            diff0 = diffz/pzero * 100

            if diffp <= self.D['손익저점'] : self.D['손익저점'] = diffp; self.D['저점날자'] = self.M['현재일자']

            diffd = self.D['월익통계'][-1][0][:7] 
            if   self.M['현재일자'][0:7] == diffd : self.D['월익통계'][-1][1] += difft 
            else : self.D['월익통계'].append([self.M['현재일자'][0:7],difft])
            color = "#F6CECE" if difft >= 0 else "#CED8F6"
            self.D['손익통계'].append([self.M['현재일자'],f"{total:,.2f}",f"{difft:,.2f}",f"{diffp:.2f}",color,self.M['기록시즌'],f"{diff0:.2f}"])

    # -------------------------------------------------------------------------------------------------------------------------------------------
    # today_sell : 당일 매도를 체크한다
    # -------------------------------------------------------------------------------------------------------------------------------------------      
    def today_sell(self) :

        for tac in (self.V,self.R,self.S) : 
            
            if  self.M['당일종가'] >= self.M['매도예가'] : 
                tac['매도수량'] = tac['보유수량']
                
        if  self.M['당일종가'] >= self.N['매도예가'] :  # N 매도예가는 M 매도예가과 같거나 작아야 한다.
            self.N['매도수량']  = self.N['보유수량']

    # -------------------------------------------------------------------------------------------------------------------------------------------
    # today_buy : 당일 매수를 체크한다
    # -------------------------------------------------------------------------------------------------------------------------------------------

    def today_buy_V(self) :

        if  self.M['당일종가'] <= self.V['매수예가'] and self.V['예정수량'] : 
            self.V['매수수량']  = self.V['예정수량']
            self.V['거래코드']  = f"B{self.V['매수수량']}" if self.V['매수수량'] else ' '
                
    def today_buy_R(self) :
        
        if  self.M['당일종가'] <= self.R['매수예가'] and self.R['예정수량']: 
            self.R['매수수량']  = self.R['예정수량']
            self.R['거래코드'] = f"B{self.R['매수수량']}"
            
            if  not self.R['진행시작'] and self.M['현재날수'] > 2 :
                self.R['거래코드'] = f"B{self.R['매수수량']}/{self.R['기초수량']}" 
                self.R['진행시작'] = True
                self.R['잔액이동'] = True if self.D['이밸런싱'] == 'on' else False
    
    def today_buy_S(self) :
        
        if  self.M['당일종가'] <= self.S['매수예가'] and self.S['예정수량'] : 
            self.S['매수수량']  = self.S['예정수량']
            self.S['거래코드']  = f"B{self.S['매수수량']}" 

            if  not self.S['진행시작'] and self.M['현재날수']>self.M['전략대기'] :
                self.S['거래코드'] = f"B{self.S['매수수량']}/{self.S['기초수량']}" 
                self.S['진행시작'] = True
                self.S['잔액이동'] = True if self.D['이밸런싱'] == 'on' else False

    def today_buy_N(self) :
        
        if  self.M['당일종가'] <= self.N['매수예가'] and self.N['예정수량'] :
            self.N['매수수량']  = self.N['예정수량']
            self.N['매수차수']  = self.N['매수차수'] + 1 if self.N['매수차수'] < self.M['최대차수'] else self.M['최대차수']
            self.N['거래코드']  = f"{self.N['매수차수']}B {self.N['매수수량']}"

    # -------------------------------------------------------------------------------------------------------------------------------------------
    # tomorrow_buy : 다음 날의 매수예정 수량을 계산한다 
    # -------------------------------------------------------------------------------------------------------------------------------------------   
    def take_chance(self,tac) :

        H = self.V['보유수량']
        n = self.V['예정수량']
        A = self.V['총매수금']
        if H == 0 : return 0
        p = tac['진입시점'] if self.M['기본진행'] else tac['회복시점']

        N = H + n
        k = N / (1+p/100)
        cp = round(A/(k-n),2)
        # R,S 의 매수가는 V의 매수가보다 낮아야 한다
        return cp if cp < self.V['매수예가'] else self.V['매수예가']
    
    def chance_qty(self,tac) :
            
        if tac['매수예가'] == 0 : return 0
        cq = 0   
        day_limit = 6 if tac == self.R else 7 
        day_count = min(self.M['현재날수']+1+self.M['찬스일가'],day_limit)
        for i in range(0,day_count) : cq += my.ceil( tac['기초수량'] *(i*self.M['비중조절'] + 1))
        # cq에 의한 매수금액 예상치는 현재 잔액을 초과하지 않아야 함
        if cq * tac['매수예가'] > tac['현재잔액'] : cq = int(tac['현재잔액']/tac['매수예가'])
        return cq   
         
    def check_balance(self,tac) :

        if  self.M['첫날기록'] : return
        if  tac['현재잔액'] < tac['예정수량'] * tac['매수예가'] : 
            tac['예정수량'] = my.ceil(tac['기초수량'] * self.M['제한비중']) 
            tac['진행상황'] = '매수제한'
            
            if  tac['현재잔액'] < tac['예정수량'] * tac['매수예가'] : 
                tac['예정수량'] = 0
                tac['진행상황'] = '매수중단'
        
    # V tactic
    def tomorrow_buy_V(self) :
        
        self.V['매수예가'] = round(self.M['당일종가']*self.M['평단가치'],2)
        self.V['예정수량'] = my.ceil(self.V['기초수량'] * (self.M['현재날수']*self.M['비중조절'] + 1))
        self.check_balance(self.V)                  


    # R tactic
    def tomorrow_buy_R(self) :
        
        if not self.R['현재잔액'] : self.R['예정수량'] = 0; self.R['매수예가'] = 0; return
        
        if  self.R['진행시작'] :
            self.R['매수예가'] = round(self.M['당일종가']*self.M['평단가치'],2)
            self.R['예정수량'] = my.ceil(self.R['기초수량'] * (self.M['현재날수']*self.M['비중조절'] + 1))
            
        else :
            if      self.M['현재날수'] == 1 :
                    self.R['매수예가'] = round(self.M['당일종가']*self.M['평단가치'],2)
                    self.R['예정수량'] = my.ceil(self.R['기초수량'] * (self.M['현재날수']*self.M['비중조절'] + 1))
            else :
                    매수예가 = round( self.M['당일종가'] - 0.01, 2 ) if self.M['연속하락'] >= 2 else round(self.M['당일종가'] * self.R['기회진입'],2)  
                    self.R['매수예가'] = min(매수예가,self.take_chance(self.R)) # 순서주의 ( 매수예가 부터 계산해야함 )
                    self.R['예정수량'] = self.chance_qty(self.R)

        self.check_balance(self.R)    
    
    # S tactic    
    def tomorrow_buy_S(self) :
        
        if not self.S['현재잔액'] : self.S['예정수량'] = 0; self.S['매수예가'] = 0; return
        
        if  self.S['진행시작'] :
            self.S['매수예가'] = round(self.M['당일종가']*self.M['평단가치'],2)
            self.S['예정수량'] = my.ceil(self.S['기초수량'] * (self.M['현재날수']*self.M['비중조절'] + 1))
            
        else :
            if      self.M['현재날수'] == 2 : 
                    self.S['매수예가'] = round(self.M['당일종가'] - 0.01, 2) if self.M['연속하락'] == 2 else round(self.M['당일종가'] * self.M['진입가치'],2)  
                    self.S['예정수량'] = my.ceil(self.S['기초수량'] * (self.M['현재날수']*self.M['비중조절'] + 1))
            
            elif    self.M['현재날수'] >= self.M['전략대기'] : 
                    self.S['매수예가'] = self.take_chance(self.S)   # 순서주의 ( 매수예가 부터 계산해야함 )
                    self.S['예정수량'] = self.chance_qty(self.S) 
                
        self.check_balance(self.S)        
    
    # N tactic               
    def tomorrow_buy_N(self) :
        
        if self.N['매수차수'] >= self.M['최대차수']   : self.N['예정수량'] = 0; return
        if self.N['매수차수'] == self.M['최대차수']-1 : self.N['매금단계'][self.M['최대차수']-1] = int(self.N['현재잔액'])
        
        if  self.N['보유수량'] and self.R['진행시작'] : 
            self.N['매수예가'] = round(self.M['당일종가'] * self.M['매입가치'],2 )
        else :
            self.N['매수예가'] = round( self.M['당일종가'] - 0.01, 2 ) if self.M['연속하락'] >=(self.M['진입일자']-1) else round(self.M['당일종가'] * self.M['진입가치'],2)    
        
        self.N['예정수량'] = int( self.N['매금단계'][self.N['매수차수']] / self.N['매수예가'] ) 

    # -------------------------------------------------------------------------------------------------------------------------------------------
    # tomorrow_sell : 다음 날의 매도예가를 계산한다 
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def tomorrow_sel_M(self) :

        if  self.M['첫날기록'] : return
        
        # [기본진행]---------------------------------------------------------------------------------------------

        if  self.M['기본진행'] :

            if  self.V['진행상황'] not in ('매수제한','매수중단') : 
                self.M['매도예가'] = my.round_up(self.V['평균단가'] * self.M['첫매가치'])
            else : 
                self.M['매도예가'] = my.round_up(self.V['평균단가'] * self.M['둘매가치'])  

            if  self.S['진행시작'] : self.M['매도예가'] = min(self.M['매도예가'],my.round_up(self.S['평균단가'] * self.S['매도보정']))
        
        # [전략진행]---------------------------------------------------------------------------------------------

        else :
           
            if  self.M['현재날수'] < self.M['매도대기'] :
                self.M['매도예가'] = my.round_up(self.V['평균단가'] * self.M['전략가치'])
            else :
                self.M['매도예가'] = my.round_up(self.V['평균단가'] * self.M['둘매가치'])
                
            if  self.S['진행시작'] : self.M['매도예가'] = min(self.M['매도예가'],my.round_up(self.S['평균단가'] * self.S['회복탈출']))


    def tomorrow_sel_N(self) :
        
        if self.N['보유수량'] : self.N['매도예가'] = my.round_up(self.N['평균단가']*self.M['각매가치'][self.N['매수차수']-1]) 

    def tomorrow_step(self) :
        self.tomorrow_buy_V()
        self.tomorrow_buy_R()
        self.tomorrow_buy_S()
        self.tomorrow_buy_N()
        # 현재잔액 상태를 파악하기 위해서, buy 검토가 sell 검토보다 빨라야 함, R,S의 매수가격은 V 매수가격보다 작아야 하므로 V부터 검토하여야 함
        self.tomorrow_sel_M()
        self.tomorrow_sel_N()
        
        # [최종 매도가 조율 및 강매진행]-------------------------------------------------------------------------------------------------------------
        
        if  self.M['현재날수'] < self.M['강매시작'] :
            self.M['매도예가'] = min(self.M['매도예가'], my.round_up(self.M['당일종가']*self.M['종가상승'])) 
            self.M['매도예가'] = max(self.M['매도예가'],self.N['매도예가'])
        else :
            self.M['매도예가'] = my.round_up( self.V['평균단가'] * self.M['강매가치'] )
            self.N['매도예가'] = min(self.M['매도예가'],self.N['매도예가'])

        for tac in (self.V,self.R,self.S,self.N) : 
            if tac['매수예가'] >= self.M['매도예가'] : tac['매수예가'] = self.M['매도예가'] - 0.01

    # -------------------------------------------------------------------------------------------------------------------------------------------
    # new_day : 첫날 매수에 대한 처리를 한다 
    # -------------------------------------------------------------------------------------------------------------------------------------------     
    def new_day(self) :

        self.R['진행시작'] = self.S['진행시작'] = False
        self.N['매수차수'] = 0 
        self.set_value(['예정수량','매수예가','매수금액','매수수량','매도수량','매도예가','매도금액','수익현황','현수익률','실현익률','평균단가','평가금액','중익합계','중도합계'],0)
        self.set_value(['진행상황'],'일반매수')
        
        if  self.M['당일종가'] <  round(self.M['전일종가'] * self.M['큰단가치'],2) :
            self.M['기록시즌'] += 1
            self.M['현재날수']  = 1
            
            for tac in (self.V,self.R,self.S) : tac['기초수량']  = my.ceil(tac['일매수금']/self.M['전일종가'])
            
            for tac in (self.V,self.R) :
                tac['매수수량']  = tac['기초수량']
                tac['수익현황']  = tac['현수익률'] = 0.0
                tac['보유수량']  = tac['매수수량']
                tac['평균단가']  = self.M['당일종가'] 
                tac['매수금액']  = self.M['당일종가'] * tac['매수수량']
                tac['총매수금']  = tac['평가금액'] = tac['매수금액']
                tac['현재잔액'] -= tac['매수금액']
                tac['거래코드']  = f"B{tac['매수수량']}" 
                self.commission(tac,1)

            self.M['첫날기록'] = False
            
            # --------------------------------------------------
            # N 전략은 첫날 매수 없음
            # --------------------------------------------------   
               
            return True

        else : return False
        
    # -------------------------------------------------------------------------------------------------------------------------------------------
    # simulate : 메인함수로서 시작일과 종료일까지의 매수매도를 테스트함
    # -------------------------------------------------------------------------------------------------------------------------------------------   
    
    def simulate(self,printOut=False) :

        for idx,BD in enumerate(self.B) : 
            if BD['add0'] < self.D['시작일자'] : idxx = idx; continue

            self.M['현재일자'] = BD['add0']
            self.M['당일종가'] = float(BD['add3'])
            self.M['전일종가'] = float(self.B[idx-1]['add3']) 
            self.M['종가변동'] = float(BD['add8']) 
            self.M['연속상승'] = int(BD['add9'])
            self.M['연속하락'] = int(BD['add10'])
            self.V['거래코드'] = self.R['거래코드'] = self.S['거래코드'] = self.N['거래코드'] = ' '
            self.set_value(['매도수량','매도금액','매수수량','매수금액','수익현황','현수익률','수수료등'],0)
            
            # BD의 기록은 시작일자 보다 전의 데이타(종가기록 등)에서 시작하고, 당일종가가 전일에 비해 설정값 이상으로 상승 시 건너뛰기 위함
            if  idx == idxx + 1 or self.M['첫날기록'] : 
                if  self.new_day() : self.chart_data(); self.tomorrow_step(); self.increase_count(printOut); continue
                else : self.M['첫날기록'] = True; self.chart_data(); continue

            self.today_sell()
            self.today_buy_V()
            self.today_buy_R()
            self.today_buy_S()
            self.today_buy_N()
            self.calculate()
            self.chart_data()
            self.tomorrow_step()
            self.increase_count(printOut)
            
    
    def set_value(self,key,val) :

        for k in key :
            self.V[k] = val
            self.R[k] = val
            self.S[k] = val
            self.N[k] = val

    def result(self) :

        self.D['최장일수'] = self.M['최장일수']
        self.D['최장일자'] = self.M['최장일자']
        self.D['현재일자'] = self.M['현재일자']
        self.D['MDD1'] = f"{self.V['진최하락']:.2f}"; self.D['MDD_DAY1'] = self.V['최하일자'][2:]
        self.D['MDD2'] = f"{self.R['진최하락']:.2f}"; self.D['MDD_DAY2'] = self.R['최하일자'][2:]
        self.D['MDD3'] = f"{self.S['진최하락']:.2f}"; self.D['MDD_DAY3'] = self.S['최하일자'][2:]
        self.D['MDD4'] = f"{self.N['진최하락']:.2f}"; self.D['MDD_DAY4'] = self.N['최하일자'][2:]

        총매입금  = self.R['총매수금'] + self.S['총매수금'] + self.N['총매수금']
        총보유량  = self.R['보유수량'] + self.S['보유수량'] + self.N['보유수량']
        총평가금  = self.M['당일종가'] * 총보유량
        평가손익  = 총평가금 - 총매입금
        
        초기자본1 = self.D['일반자금']; 최종자본1=self.V['평가금액']+self.V['현재잔액']; 최종수익1=최종자본1-초기자본1; self.D['v_profit']=round((최종수익1/초기자본1)*100,2)
        초기자본2 = self.D['기회자금']; 최종자본2=self.R['평가금액']+self.R['현재잔액']; 최종수익2=최종자본2-초기자본2; self.D['r_profit']=round((최종수익2/초기자본2)*100,2)
        초기자본3 = self.D['안정자금']; 최종자본3=self.S['평가금액']+self.S['현재잔액']; 최종수익3=최종자본3-초기자본3; self.D['s_profit']=round((최종수익3/초기자본3)*100,2)
        초기자본4 = self.D['생활자금']; 최종자본4=self.N['평가금액']+self.N['현재잔액']; 최종수익4=최종자본4-초기자본4; self.D['n_profit']=round((최종수익4/초기자본4)*100,2)
        
        초기자본 = 초기자본2 + 초기자본3 + 초기자본4; 최종자본 = 최종자본2 + 최종자본3 + 최종자본4; 최종수익 = 최종자본 - 초기자본 
        self.D['profit_t'] = round((최종수익/초기자본) * 100,2)
        
        self.D['R_총매입금'] = f"{총매입금:,.2f}"
        self.D['R_총평가금'] = f"{총평가금:,.2f}"
        self.D['R_총보유량'] = f"{총보유량:,}"
        self.D['R_평가손익'] = f"{평가손익:,.2f}"
        self.D['R_평가익률'] = self.next_percent(총매입금,총평가금)

        self.D['R_초기자본'] = f"{초기자본:,.0f}"
        self.D['R_최종자본'] = f"{최종자본:,.2f}"
        self.D['R_최종수익'] = f"{최종수익:,.2f}"
        self.D['R_최종익률'] = f"{self.D['profit_t']:,.2f}"
        self.D['R_일반익률'] = f"{self.D['v_profit']:,.2f}"
        self.D['R_기회익률'] = f"{self.D['r_profit']:,.2f}"
        self.D['R_안정익률'] = f"{self.D['s_profit']:,.2f}"
        self.D['R_생활익률'] = f"{self.D['n_profit']:,.2f}"
        self.D['R_총경과일'] = f"{my.diff_day(self.D['시작일자'],self.D['종료일자']):,}"

        if self.chart and self.D['c_date'] : self.D['s_date'] = self.D['c_date'][0]; self.D['e_date'] = self.D['c_date'][-1]

        if  self.stat :
            self.D['월별구분'] = [ x[0] for x in self.D['월익통계']][-24:]
            self.D['월별이익'] = [ round(x[1]) for x in self.D['월익통계']][-24:]
            
            if  self.D['월별이익'][0] == 0 :
                self.D['월별구분'].pop(0)
                self.D['월별이익'].pop(0)

            monthly_total = sum(self.D['월별이익'])
            monthly_lenth = len(self.D['월별이익'])
            
            if monthly_lenth : 
                self.D['월별구분'].append('AVG')
                self.D['월별이익'].append(round(monthly_total/monthly_lenth))

            self.D['손익저점'] = f"{self.D['손익저점']:.2f}"

            # 손익통계 분석
            asis = [float(x[3]) for x in self.D['손익통계']]
            asis = asis[1:]
    
            asis_c = len(asis)
            asis_p = [x for x in asis if x >= 0.0 ]
            asis_u = [x for x in asis if x < 0.0]
            asispc = len(asis_p)
            asisuc = len(asis_u)
            asispm = sum(asis_p) / asispc if asispc else 0.0
            asisum = sum(asis_u) / asisuc if asisuc else 0.0

            win_p = asispc / asis_c * 100 if asis_c else 0.0

            self.D['R_총매도수'] = asis_c; self.D['R_총익절수'] = asispc; self.D['R_총손절수'] = asisuc
            self.D['R_총익승률'] = f"{win_p:.2f}" ; self.D['R_익절평균'] = f"{asispm:.2f}"; self.D['R_손절평균'] = f"{asisum:.2f}"        

    # -------------------------------------------------------------------------------------------------------------------------------------------
    # get_start : 테스트에 필요한 주가 정보를 불러옴
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def get_start(self,s='',e='') :

        self.D['종목코드']  = 'SOXL'

        if not s : s = self.D['시작일자']
        if not e : e = self.D['종료일자']
        
        old_date = my.dayofdate(s,-7)[0]  
        lst_date = self.DB.one("SELECT max(add0) FROM h_stockHistory_board") 
        
        if old_date < '2010-03-15' : old_date = '2010-03-15'; s = '2010-03-22'
        
        if e > lst_date : e = lst_date
        if s > e : s = '2020-01-02'; e = lst_date
        
        self.D['시작일자'] = s
        self.D['종료일자'] = e
          
        self.DB.tbl,self.DB.wre,self.DB.odr = ("h_stockHistory_board",f"add1='{self.D['종목코드']}' AND add0 BETWEEN '{old_date}' AND '{e}'","add0")
        self.B = self.DB.get('add0,add3,add8,add9,add10') # 날자, 종가, 증감, 연상,연하 
        

    def increase_count(self,printOut=False) :
        
        if not self.V['보유수량'] and not self.V['매도수량']: return
        if printOut : self.print_backtest()
        self.M['현재날수'] +=1

    # -------------------------------------------------------------------------------------------------------------------------------------------
    # init_value : 변수 초기화  
    # -------------------------------------------------------------------------------------------------------------------------------------------         
    def init_value(self) :
        
        self.M['기본진행']  = True  
        self.M['기록시즌']  = 0
        self.M['최장일자']  = ' '
        self.M['현재날수']  = 1
        self.M['최장일수']  = 0   # 최고 오래 지속된 시즌의 일수
        self.M['첫날기록']  = False
        self.R['진행시작']  = self.S['진행시작'] = self.N['진행시작']  = False
        self.D['총수수료'] = 0.0
        self.set_value(['예정수량','매수수량','보유수량','매도수량',],0)
        self.set_value(['매수예가','매수금액','총매수금','평균단가','평가금액','매도예가','매도금액','수익현황','현수익률','실현익률','중익합계','중도합계','수수료등'],0.0)
        self.set_value(['진최하락'],0)
        self.set_value(['최하일자'],'')

        if '분할횟수' not in self.M :
            
            ST = self.DB.parameters_dict('매매전략/RSN')
            
            # V tactic 
            self.M['분할횟수']  = ST['TV010']  # TV
            self.M['큰단가치']  = ST['TV020']  # TV003
            self.M['평단가치']  = ST['TV021']  # TV002
            self.M['비중조절']  = ST['TV022']  # TV001 매수수량 가중치
            self.M['제한비중']  = ST['TV023']  # TV008
            self.M['첫매가치']  = ST['TV024']  # TV004
            self.M['매도대기']  = ST['TV025']  # TV
            self.M['둘매가치']  = ST['TV026']  # TV005
            self.M['강매시작']  = ST['TV027']  # TV006
            self.M['강매가치']  = ST['TV028']  # TV007
            self.M['전략가치']  = ST['TV029']  # TV
            self.M['종가상승']  = ST['TV030']  # TV
            
            # RS tactic
            self.M['전략대기']  = ST['TR010']  # TS001
            self.M['찬스일가']  = ST['TR011']  # TS
            self.S['매도보정']  = ST['TS010']  # TS
            self.S['회복탈출']  = ST['TS011']  # TS
            self.R['기회진입']  = ST['TR023']  # TR
            
            # N tactic
            self.M['분할배분']  = my.sf(ST['TN010']) # TN
            self.M['각매가치']  = my.sf(ST['TN011']) # TN
            self.M['최대차수']  = len(self.M['분할배분'])
            self.M['진입일자']  = ST['TN020']  # TN
            self.M['진입가치']  = ST['TN021']
            self.M['매입가치']  = ST['TN022']  # TN 첫날 매수 이후 (-0%)이상 하락 시 매수
            
            self.R['진입시점']  = float(self.D['기회시점']) if '기회시점' in self.D else ST['TR021'] #TR
            self.R['회복시점']  = float(self.D['기회회복']) if '기회회복' in self.D else ST['TR022'] #TR
            self.S['진입시점']  = float(self.D['안정시점']) if '안정시점' in self.D else ST['TS021'] #TS
            self.S['회복시점']  = float(self.D['안정회복']) if '안정회복' in self.D else ST['TS022'] #TS

            # 투자옵션 초기화 ----------------------------------------------------------------------------
            if '가상손실' in self.D  and  self.D['가상손실'] == 'on' : self.M['기본진행']  = False     
            if '수료적용' not in self.D : self.D['수료적용']  = 'on' 
            if '세금적용' not in self.D : self.D['세금적용']  = 'off'
            if '일밸런싱' not in self.D : self.D['일밸런싱']  = 'on'
            if '이밸런싱' not in self.D : self.D['이밸런싱']  = 'on'
            
            # 투자자금 초기화 ----------------------------------------------------------------------------
            self.M['투자자금'] = my.sv(ST['TC010']) if '투자자금' not in self.D else my.sv(self.D['투자자금'])
            self.M['투자배분'] = my.sf(ST['TC011'])    

            self.D['기회자금']  = round(self.M['투자자금']*self.M['투자배분'][0]/100,2)
            self.D['안정자금']  = round(self.M['투자자금']*self.M['투자배분'][1]/100,2)
            self.D['생활자금']  = self.M['투자자금'] - self.D['기회자금'] - self.D['안정자금']
        
        # 통계자료 작성을 위해 RSN 현재잔액은 init_value 호출 때 마다 초기화가 되어야 함
        self.R['현재잔액']  = self.D['기회자금']
        self.S['현재잔액']  = self.D['안정자금']
        self.N['현재잔액']  = self.D['생활자금']
        # 일반잔액은 RSN 전략의 합으로 설정한다
        self.V['현재잔액']  = self.R['현재잔액']+self.S['현재잔액']+self.N['현재잔액']
        self.D['일반자금']  = self.V['현재잔액']
        
        # 매수금 분할 ( N tactic )
        self.N['매금단계'] = [0.0] * self.M['최대차수']
        self.N['매수차수'] = 0
        self.rebalance_N()
        self.V['일매수금'] = int(self.V['현재잔액'] / self.M['분할횟수'])
        self.R['일매수금'] = int(self.R['현재잔액'] / self.M['분할횟수'])
        self.S['일매수금'] = int(self.S['현재잔액'] / self.M['분할횟수'])
        self.R['잔액이동'] = self.S['잔액이동'] = self.V['잔액이동'] = self.N['잔액이동'] = False
         # -------------------------------------------------------------------------------------------
        if  self.chart : # 챠트작성
            
            self.D['TR'] = []
            self.D['c_date'] = []
            self.D['clse_p'] = []
            self.D['avge_v'] = []; self.D['avge_r'] = []; self.D['avge_s'] = []; self.D['avge_n'] = []

        # 통계자료
        if  self.stat :

            self.D['totalV'] = []
            self.D['일정익절'] = 0; self.D['기정익절'] = 0; self.D['안정익절'] = 0; self.D['생정익절'] = 0
            self.D['일정손절'] = 0; self.D['기정손절'] = 0; self.D['안정손절'] = 0; self.D['생정손절'] = 0
            self.D['일회익절'] = 0; self.D['기회익절'] = 0; self.D['안회익절'] = 0; self.D['생회익절'] = 0
            self.D['일회손절'] = 0; self.D['기회손절'] = 0; self.D['안회손절'] = 0; self.D['생회손절'] = 0

            self.D['손익통계'] = [[self.D['시작일자'],f"{self.R['현재잔액']+self.S['현재잔액']+self.N['현재잔액']:,.2f}",'0.00','0.00',"#F6CECE",'','0.00']]
            self.D['월익통계'] = [[self.D['시작일자'][:7],0.00]]
            self.D['손익저점'] = 100.0
            self.D['저점날자'] = ''
            
    # -------------------------------------------------------------------------------------------------------------------------------------------
    # nextStep : 다음 날에 대한 전략을 계산한다  
    # -------------------------------------------------------------------------------------------------------------------------------------------            
    def nextStep(self) :

        self.D['N_일자'] = self.M['현재날수'] 
        self.D['N_종가'] = self.M['당일종가']
        self.D['N_변동'] = round(self.M['종가변동'],2)

        if  self.R['보유수량'] :
            self.D['NT-AVG'] = round((self.R['총매수금']+self.S['총매수금']+self.N['총매수금'])/(self.R['보유수량']+self.S['보유수량']+self.N['보유수량']),2)
        else :
            self.D['NT-AVG'] = '0.00'
            
        self.D['LPRICE'] = my.round_up(self.V['평균단가'] * self.M['강매가치'])
        self.D['CPRICE'] = my.round_up(self.M['당일종가'] * self.M['종가상승']) 

        # 변수초기화 
        # 도종비 : 현재 종가와 매도가의 비율
        self.D['N_기회도종비'] = self.D['N_안정도종비'] = self.D['N_생활도종비'] = ''

        if  self.M['첫날기록'] : 

            self.D['N_일자'] = 1 
            self.D['N_일반기초'] = my.ceil(self.V['일매수금']/self.M['당일종가'])
            self.D['N_기회기초'] = my.ceil(self.R['일매수금']/self.M['당일종가'])
            self.D['N_안정기초'] = my.ceil(self.S['일매수금']/self.M['당일종가'])
            
            self.D['N_일반매수가'] = self.D['N_기회매수가'] = round(self.M['당일종가'] * self.M['큰단가치'],2)
            self.D['N_안정매수가'] = self.D['N_생활매수가'] = 0
            
            self.D['N_일반매수량'] = self.D['N_일반기초']
            self.D['N_기회매수량'] = self.D['N_기회기초']
            self.D['N_안정매수량'] = 0
            self.D['N_생활매수량'] = 0

            self.D['N_일반매도량'] = self.D['N_기회매도량'] = self.D['N_안정매도량'] = self.D['N_생활매도량'] = 0

            self.D['N_일반매도가'] = self.D['N_기회매도가'] = self.D['N_안정매도가'] = self.D['N_생활매도가'] = 0
            self.D['N_일반종대비'] = self.D['N_기회종대비'] = self.next_percent(self.M['당일종가'],self.D['N_기회매수가'])
            self.D['N_안정종대비'] = self.D['N_공통종대비'] = ''
            self.D['N_생활종대비'] = self.next_percent(self.M['당일종가'],self.D['N_생활매수가'])
            
        else : 
            
            self.D['N_일반기초'] = self.V['기초수량']
            self.D['N_기회기초'] = self.R['기초수량']
            self.D['N_안정기초'] = self.S['기초수량']

            self.V['진행시작'] = True
            
            for (tac,key) in [(self.V,'일반'),(self.R,'기회'),(self.S,'안정')] : 
                self.D['N_'+key+'매수량'] = tac['예정수량']
                self.D['N_'+key+'매수가'] = f"{tac['매수예가']:.2f}"
                self.D['N_'+key+'평대비'] = self.next_percent(tac['평균단가'],tac['매수예가'])
                self.D['N_'+key+'종대비'] = self.next_percent(self.M['당일종가'],tac['매수예가'])

                self.D['N_'+key+'매도량'] = tac['보유수량']
                self.D['N_'+key+'매도가'] = f"{self.M['매도예가']:.2f}" if tac['보유수량'] else 0
                self.D['N_'+key+'도평비'] = self.next_percent(tac['평균단가'],self.M['매도예가'])
                self.D['N_'+key+'도종비'] = self.next_percent(self.M['당일종가'],self.M['매도예가'])

            self.D['N_생활매수량'] = self.N['예정수량']
            self.D['N_생활매수가'] = f"{self.N['매수예가']:.2f}"
            self.D['N_생활평대비'] = self.next_percent(self.N['평균단가'],self.N['매수예가']) 
            self.D['N_생활종대비'] = self.next_percent(self.M['당일종가'],self.N['매수예가'])
            
            self.D['N_생활매도량'] = self.N['보유수량']
            self.D['N_생활매도가'] = f"{self.N['매도예가']:.2f}"
            self.D['N_생활도평비'] = self.next_percent(self.N['평균단가'],self.N['매도예가'])
            self.D['N_생활도종비'] = self.next_percent(self.M['당일종가'],self.N['매도예가'])
            
    def next_percent(self,a,b) :
        
        if not a : return ''
        return f"{(b/a-1)*100:.2f}"
    
# ------------------------------------------------------------------------------------------------------------------------------------------
# From rsn.py END
# ------------------------------------------------------------------------------------------------------------------------------------------

    def print_backtest(self) :
        return

    def chart_data(self) :
        return
    
    def get_simResult(self,start='',end='') :
        
        self.D['종료일자'] = self.DB.one("SELECT max(add0) FROM h_stockHistory_board") if not end else end
        self.D['시작일자'] = my.dayofdate(self.D['종료일자'],delta=-365*2)[0] if not start else start 
        self.get_start()
        self.init_value()
        self.simulate()
        self.result()
        self.nextStep()

    def get_simulLog(self,tactic) :
        
        if   tactic == 'V' : tac = self.V; key = '일반'; 초기자금 = self.D['일반자금']
        elif tactic == 'R' : tac = self.R; key = '기회'; 초기자금 = self.D['기회자금']
        elif tactic == 'S' : tac = self.S; key = '안정'; 초기자금 = self.D['안정자금']
        elif tactic == 'N' : tac = self.N; key = '생활'; 초기자금 = self.D['생활자금']
        
        LD = {}
        LD['add1'] = LD['add2'] = '0.00' 
        LD['add3'] = f"{tac['현재잔액']:.2f}"
        LD['add4'] = f"{tac['현재잔액']/(tac['현재잔액'] + tac['평가금액']) * 100:.2f}"
        
        LD['add11'] = f"{tac['매수금액']:.2f}"
        LD['add12'] = f"{tac['매도금액']:.2f}"
        LD['add5']  = f"{tac['매수수량']:}" if not tac['매도수량'] else f"-{tac['매도수량']:}"
        LD['add16'] = f"{tac['평가금액']/(tac['현재잔액'] + tac['평가금액']) * 100:,.2f}"
    
        LD['add14'] = self.M['당일종가']
        LD['add20'] = self.M['종가변동']
        LD['add9']  = f"{tac['보유수량']:}"
        LD['add8']  = f"{tac['현수익률']:.2f}"
        
        LD['add7']  = f"{tac['평균단가']:.4f}"
        LD['add15'] = f"{tac['평가금액']:.2f}"
        LD['add6']  = f"{tac['총매수금']:.2f}"
        LD['add18'] = f"{tac['수익현황']:.2f}"
        
        LD['sub1']  = self.M['기록시즌']
        LD['sub4']  = self.N['매수차수'] if tactic == 'N' else f"{tac['일매수금']:.2f}"
        
        LD['sub12'] = self.M['현재날수'] - 1
        
        매수차수 = self.N['매수차수'] if self.N['매수차수'] < self.M['최대차수'] else self.M['최대차수'] - 1
        LD['sub18'] = f"{self.N['매금단계'][매수차수]}" if tactic == 'N' else tac['기초수량'] 
                  
        LD['sub29'] = tac['진행상황']
        LD['sub5']  = f"+ {self.M['연속상승']}" if self.M['연속상승'] else f"- {self.M['연속하락']}"
        LD['sub6']  = f"{초기자금:.2f}" 
        LD['sub32'] = self.D['시작일자']
                
        LD['add17'] = f"{tac['현재잔액'] +tac['평가금액']:.2f}"
        LD['sub30'] = f"{tac['수수료등']:.2f}"
        LD['sub31'] = f"{tac['현재잔액'] +tac['평가금액']-초기자금:.2f}"
        LD['sub11'] = '특이사항 없음'
        
        LD['sub2']  = f"{self.D['N_'+key+'매수량']:}" 
        LD['sub3']  = f"{self.D['N_'+key+'매도량']:}"
        LD['sub19'] = self.D['N_'+key+'매수가'] 
        LD['sub20'] = self.D['N_'+key+'매도가']
        
        return LD


    def do_tacticsLog(self,logDay) :
        
        sdate = self.DB.parameter('TX050')
        T_mon = my.sv(self.DB.parameter('TX051'))
        mode_ = self.DB.parameter('TX052')
        
        self.D['투자자금'] = f"{T_mon:,.2f}"
        self.D['시작일자'] = sdate
        self.D['종료일자'] = logDay 
        if sdate > logDay : return
        
        self.D['기회시점'] = f"{self.DB.parameter('TR021'):.1f}"
        self.D['기회회복'] = f"{self.DB.parameter('TR022'):.1f}"
        self.D['안정시점'] = f"{self.DB.parameter('TS021'):.1f}"
        self.D['안정회복'] = f"{self.DB.parameter('TS022'):.1f}"      
        
        self.D['수료적용'] = 'off' 
        self.D['세금적용'] = 'off' 
        self.D['일밸런싱'] = 'on' 
        self.D['이밸런싱'] = 'on' 
        self.D['가상손실'] = 'on' if mode_ == '전략진행' else 'off'
        
        self.stat = True
        self.get_simResult(sdate,logDay)
    
#   -------------------------------------------------------------------------------------
#   For Lucky Mode
#   -------------------------------------------------------------------------------------
    def do_luckyLog(self,logDay) :
        
        sdate = self.DB.parameter('L0001') # Lucky 전략에서 사용되는 동기일자
        if sdate > logDay : return

        T_mon = my.sv(self.DB.parameter('TX051'))
        mode_ = self.DB.parameter('TX052')
        
        self.D['투자자금'] = f"{T_mon:,.2f}"
        self.D['시작일자'] = sdate
        self.D['종료일자'] = logDay 
        
        self.D['기회시점'] = f"{self.DB.parameter('TR021'):.1f}"
        self.D['기회회복'] = f"{self.DB.parameter('TR022'):.1f}"
        self.D['안정시점'] = f"{self.DB.parameter('TS021'):.1f}"
        self.D['안정회복'] = f"{self.DB.parameter('TS022'):.1f}"      
        
        self.D['수료적용'] = 'on' 
        self.D['세금적용'] = 'off' 
        self.D['일밸런싱'] = 'on' 
        self.D['이밸런싱'] = 'on' 
        self.D['가상손실'] = 'on' if mode_ == '전략진행' else 'off'
        
        self.get_simResult(sdate,logDay)
        
    def get_luckyLog(self) :
        
        SL = self.DB.parameters_dict('매매전략/LUCKY')
        LD = {}
        
        LD['기록일자'] = self.M['현재일자']
        LD['기록시즌'] = self.M['기록시즌']
        LD['기록날수'] = self.M['현재날수']-1
        
        LD['감시시작'] = True if self.V['현수익률'] < SL['L0022'] else False # S전략 평균단가
        LD['진입가격'] = 0.0 
        
        if  LD['감시시작'] :
            LD['진입가격'] = min(self.take_lucky(SL['L0023']),self.M['당일종가']*SL['L0025'])

        LD['당일종가'] = self.M['당일종가']
        LD['전일종가'] = self.M['전일종가']   
        LD['종가변동'] = self.M['종가변동']   
        LD['매도예가'] = self.M['매도예가'] 
        
        if LD['진입가격'] >= LD['매도예가'] : LD['진입가격'] = LD['매도예가']-0.01
                
        if  self.V['진행상황'] in ('익절매도','손절매도') :
            LD['진행종료'] = True
            LD['진입가격'] = 0.0
        else :
            LD['진행종료'] = False

        LD['진입가격'] = f"{LD['진입가격']:.2f}"

        return LD
    
    def take_lucky(self,check_in) :

        H = self.V['보유수량']
        n = self.V['예정수량']
        A = self.V['총매수금']

        p = check_in
        N = H + n
        k = N / (1+p/100)
        cp = round(A/(k-n),2)
        return cp 
