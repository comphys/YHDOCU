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
            self.M['매도금액']  =  self.M['매도수량'] * self.M['당일종가']
            self.M['수익현황']  =  self.M['매도금액'] - self.M['총매수금']
            self.M['보유수량'] -=  self.M['매도수량'];  self.M['현재잔액'] += self.M['매도금액'] 
            self.M['현수익률'] = round( self.M['수익현황'] / self.M['총매수금'] * 100, 2 )   
            self.commission(2) 
            
            self.M['평가금액'] = 0.00
            self.M['총매수금'] = 0.00
            self.M['평균단가'] = 0.00

            self.M['진행상황'] = '익절매도' if self.M['수익현황'] >= 0 else '손절매도'
            self.M['매수차수'] = 0
            self.M['첫날기록'] = True
            
            self.rebalance() 
            
    def commission(self,opt) :
        
        mm = self.M['매수금액'] if opt == 1 else self.M['매도금액']
        fee = int(mm*0.07)/100
        if opt==2 : fee += round(mm*0.0008)/100
        self.M['수수료등']  = fee
        self.M['현재잔액'] -= fee
        
    def rebalance(self)  :

        pass
       
    
    def new_day(self) :

        pass


    def set_value(self,key,val) :

        for k in key :
            self.M[k] = val

    def result(self) :

        pass
        

    def get_start(self,b='') :

        pass
            
    def today_buy_check(self,cp,key) : 
        
        n = self.M['별칭구분'][key]
        if self.M[n+'목표'] : return
        tp = self.M['기준단가'] * self.M['매수시점'][key]/100; tp = round(min(tp,cp),2)
        if tp <= cp : self.M['매수수량'] += self.M[n+'수량']
        
    def today_sell_check(self,cp,key) : 
        
        n = self.M['별칭구분'][key]
        if not self.M[n+'목표'] : return
        if cp <= self.M[n+'목표'] : self.M['매도수량'] += self.M[n+'수량']
        
            
    def invest_allot(self) :
        
        self.M['일오자금']  = round(self.M['현재잔액'] * self.M['자산배분'][0]/100,2)
        self.M['이공자금']  = round(self.M['현재잔액'] * self.M['자산배분'][1]/100,2)
        self.M['이오자금']  = round(self.M['현재잔액'] * self.M['자산배분'][2]/100,2)
        self.M['삼공자금']  = round(self.M['현재잔액'] * self.M['자산배분'][3]/100,2)        
        
        
    def init_value(self) :
        
        ST = self.DB.parameters_dict('매매전략/LUCKY')
        # 
        self.M['현재잔액']  = my.sv(ST['L0001'])
        self.M['자산배분']  = my.sf(self.DB.parameter('L0021'))
        self.M['대기시점']  = my.sf(self.DB.parameter('L0022'))
        self.M['매수시점']  = my.sf(self.DB.parameter('L0023'))
        self.M['목표시점']  = my.sf(self.DB.parameter('L0024'))
        self.M['기준단가']  = my.sv(ST['L0201'])
        self.M['별칭구분']  = ['일오','이공','이오','삼공']
        # 
        self.M['일오수량']  = int(ST['L0215']); self.M['일오목표'] = float(ST['L0216'])
        self.M['이공수량']  = int(ST['L0220']); self.M['이공목표'] = float(ST['L0221'])
        self.M['이오수량']  = int(ST['L0225']); self.M['이오목표'] = float(ST['L0226'])
        self.M['삼공수량']  = int(ST['L0230']); self.M['삼공목표'] = float(ST['L0231'])
        
        self.invest_allot() # for 자산배분
        
        self.M['매수수량'] = 0
        self.M['매도수량'] = 0
        #----------------------------------------------------------

         
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


    def do_log_setting(self,DS) :
        
        self.init_value()
        
        D = {}
    
        D['진행시즌']  = DS['기록시즌']
        D['시즌자금']  = self.M['현재잔액']
        D['일오수량'] = int(self.M['일오자금']/round(DS['평균단가']*self.M['매수시점'][0]/100,2))  # 진입수량
        D['이공수량'] = int(self.M['이공자금']/round(DS['평균단가']*self.M['매수시점'][1]/100,2))  # 진입수량
        D['이오수량'] = int(self.M['이오자금']/round(DS['평균단가']*self.M['매수시점'][2]/100,2))  # 진입수량
        D['삼공수량'] = int(self.M['삼공자금']/round(DS['평균단가']*self.M['매수시점'][3]/100,2))  # 진입수량
        D['기준단가'] = DS['평균단가']
        
        return D

    