from myutils.DB import DB
import myutils.my_utils as my

class update_lucky :

    def __init__(self) :

        self.DB    = DB('stocks')
        self.skey = self.DB.store("slack_key")

        self.B = {}
        self.M = {}
        self.D = {}

    def send_message(self,message) :
        if self.DB.system == "Linux" : my.post_slack(self.skey,message)
        else : print(message)  

# ------------------------------------------------------------------------------------------------------------------------------------------
# From n315.py in sytem lib
# ------------------------------------------------------------------------------------------------------------------------------------------

    def calculate(self)  :
        
        if  self.M['매수수량'] : 
            self.M['매수금액']  = self.M['매수수량'] * self.M['당일종가']
            self.M['보유수량'] += self.M['매수수량']
            self.M['현재잔액'] -= self.M['매수금액']
            self.M['총매수금'] += self.M['매수금액']
            self.M['평균단가'] =  self.M['총매수금'] / self.M['보유수량'] 
            self.commission(1)

        
        self.M['평가금액'] = self.M['당일종가'] * self.M['보유수량'] 
        self.M['수익현황'] = self.M['평가금액'] - self.M['총매수금']
        self.M['현수익률'] = self.M['수익현황'] / self.M['총매수금']  * 100  if self.M['총매수금'] else 0.00  
        
        if  self.M['매도수량'] :
            self.M['보유수량'] -=  self.M['매도수량']
            self.M['매도금액']  =  self.M['매도수량'] * self.M['당일종가']
            self.M['수익현황'] =  self.M['매도금액'] - self.M['총매수금'] 
            self.M['현수익률'] = round( self.M['수익현황'] / self.M['총매수금'] * 100, 2)  
            self.M['평가금액'] = 0.00
            self.M['총매수금'] = 0.00
            self.M['평균단가'] = 0.00 
            self.M['매도가치'] = 0.00 
            self.M['매수기록'] = ''
            self.M['진행상황'] = '익절매도' if self.M['수익현황'] >= 0 else '손절매도'
            self.M['목표단가'] = 0.00

            self.M['현재잔액'] += self.M['매도금액'] 
            self.commission(2)

    def output(self) :

        if not self.M['당일기록'] and not self.M['보유수량'] : return None
        D = {}
        D['add5']  = f"{self.M['현재잔액']:.2f}"
        D['add6']  =    self.M['매수수량']
        D['add7']  = f"{self.M['매수금액']:.2f}"
        D['add8']  =    self.M['보유수량']
        D['add9']  = f"{self.M['평균단가']:.4f}"
        D['add10'] = f"{self.M['총매수금']:.2f}"
        D['add11'] = f"{self.M['평가금액']:.2f}"
        D['add12'] = f"{self.M['매도금액']:.2f}"
        D['add13'] = f"{self.M['수익현황']:.2f}"
        D['add14'] = f"{self.M['현수익률']:.2f}"
        D['add15'] = f"{self.M['현재잔액'] + self.M['평가금액']:.2f}"
        D['add16'] =    self.M['진행상황']
        D['add17'] = '일반진행' if self.M['보유수량'] else '수익실현'
        D['add18'] = f"{self.M['수수료등']:.2f}"
        D['add19'] = self.M['매수기록']
        D['add20'] = f"{self.M['목표단가']:.2f}"
        return D


    def commission(self,opt) :
        
        mm = self.M['매수금액'] if opt == 1 else self.M['매도금액']
        fee = int(mm*0.07)/100
        if opt==2 : fee += round(mm*0.0008)/100
        self.M['수수료등']  = fee
        self.M['현재잔액'] -= fee
        
    def today_buy_check(self) : 
        
        if self.M['매도수량'] : return

        판단기준 = round((self.M['전일종가']/self.M['기준단가']-1)*100,2)
   
        if   판단기준 < -25.0 : key = 3
        elif 판단기준 < -20.0 : key = 2 
        elif 판단기준 < -15.0 : key = 1 
        else : key = 0
        
        tp = self.M['기준단가'] * self.M['매수시점'][key]/100
        tp = round(min(tp,self.M['전일종가']),2)
        if  self.M['당일종가'] <= tp and str(key) not in self.M['매수기록'] : 
            self.M['매수수량'] = self.M['구매수량'][key]
            매도가치 = self.M['당일종가'] * self.M['목표시점'][key]
            self.M['목표단가'] = min(self.M['목표단가'],매도가치) 
            self.M['진행상황'] = self.M['기호구분'][key]
            self.M['매수기록']+= str(key)
            self.M['당일기록'] = True

                    
        
    def today_sell_check(self) : 
        
        if not self.M['보유수량'] : return

        매도예가 = min(self.M['목표단가'],self.M['매도예가'])
        
        if  self.M['당일종가'] >= 매도예가 : 
            self.M['매도수량']  = self.M['보유수량']
            self.M['당일기록']  = True
        
    
    def today_check(self) :
        self.init_value()
        self.today_sell_check()    # 파라미터 업데이트로 인해 매도 조건이 먼저 검토되어야 함 
        self.today_buy_check()
        self.calculate()
        
    def invest_allot(self) :
        
        self.M['일매수금']  = round(self.M['시즌자금'] / 4,2)
        for i in [0,1,2,3] :
            self.M['구매수량'][i] = int(self.M['일매수금']/round(self.M['기준단가']*self.M['매수시점'][i]/100,2)) 

        
    def init_value(self) :
        
        LD = self.DB.line("SELECT add5,add8,add9,add10,add19,add20 FROM h_log_lucky_board ORDER BY add0 DESC LIMIT 1")  # 현재잔액,보유수량,평균단가,총매수금,매수기록,목표단가
        ST = self.DB.parameters_dict('매매전략/LUCKY')
        # 
        self.M['시즌자금']  = float(LD['add5'])+float(LD['add10'])
        self.M['현재잔액']  = float(LD['add5'])
        self.M['자산배분']  = my.sf(ST['L0021'])
        self.M['대기시점']  = my.sf(ST['L0022'])
        self.M['매수시점']  = my.sf(ST['L0023'])
        self.M['목표시점']  = my.sf(ST['L0024'])
        self.M['기준단가']  = my.sv(ST['L0201'])
        self.M['기호구분']  = ['L15','L20','L25','L30']
        self.M['구매수량']  = [0,0,0,0]
        
        self.invest_allot() # for 수량계산
        
        self.M['보유수량'] = int(LD['add8'])
        self.M['평균단가'] = float(LD['add9'])
        self.M['총매수금'] = float(LD['add10'])
        self.M['목표단가'] = float(LD['add20'])
        self.M['매수수량'] = 0
        self.M['매수금액'] = 0.0
        self.M['매수가치'] = 1.0
        self.M['매도수량'] = 0
        self.M['매도금액'] = 0.0
        self.M['수수료등'] = 0
        self.M['진행상황'] = ''
        self.M['매수기록'] = LD['add19']
        self.M['당일기록'] = False
        if self.M['목표단가'] == 0 : self.M['목표단가'] = 1000.0
        
        # 최근 현황 가져오기
        
         
    # -------------------------------------------------------------------------------------------------------------------------------------------
    # 
    # -------------------------------------------------------------------------------------------------------------------------------------------            
    def next_stock_day(self,today) :
        delta = 1
        while delta :
            temp = my.dayofdate(today,delta)
            weekend = 1 if temp[1] in ('토','일') else 0
            holiday = 1 if self.DB.cnt(f"SELECT key FROM parameters WHERE val='{temp[0]}' and cat='미국증시휴장일'") else 0 
            delta = 0 if not (weekend + holiday) else delta + 1
        return temp




        



    