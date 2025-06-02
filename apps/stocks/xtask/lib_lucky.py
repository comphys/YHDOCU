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
       
    
    def today_sell(self) :
        
        if  self.M['당일종가'] >= self.M['매도예가'] : self.M['매도수량'] = self.M['보유수량']

    def today_buy(self) :
        
        if  self.M['예정수량'] == 0 : return
        
        if  self.M['당일종가'] <= self.M['매수예가'] : 
            self.M['매수수량']  = self.M['예정수량']
            self.M['진행상황']  = self.M['차수명칭'][self.M['매수차수']] + '차매수' if self.M['예정수량'] else ' '
            self.M['매수차수'] += 1
            
    def tomorrow_buy(self) :
        
        if  self.M['매수차수'] >  self.M['최대차수']-1 : self.M['예정수량'] = 0; return
        if  self.M['매수차수'] == self.M['최대차수']-1 : self.M['매금단계'][self.M['최대차수']-1] = int(self.M['현재잔액'])
        
        self.M['매수예가'] = round(self.M['당일종가'] * self.M['매입가치'],2)
        self.M['예정수량'] = int(  self.M['매금단계'][self.M['매수차수']]/ self.M['매수예가'] ) 
        
    def tomorrow_sell(self) :
        
        if not self.M['보유수량'] : return
        self.M['매도예가'] = my.round_up(self.M['평균단가'] * self.M['각매가치'][self.M['매수차수']-1])


    def tomorrow_step(self)   :

        self.tomorrow_buy()
        self.tomorrow_sell()
        
        if  self.M['매수예가']>= self.M['매도예가'] : self.M['매수예가'] = self.M['매도예가'] - 0.01
        
    
    def new_day(self) :

        pass


    def simulate(self,printOut=False) :

        pass
        
   
    def set_value(self,key,val) :

        for k in key :
            self.M[k] = val

    def result(self) :

        pass
        

    def get_start(self,b='') :

        pass
            

    def init_value(self) :
        
        ST = self.DB.parameters_dict('매매전략/LUCKY')
        # ---------------------------------------------------------
        self.M['시즌자금']  = my.sv(ST['L0001'])
        self.M['럭키일오']  = my.sf(self.DB.parameter('L0015'))
        self.M['럭키이공']  = my.sf(self.DB.parameter('L0020'))
        self.M['럭키이오']  = my.sf(self.DB.parameter('L0025'))
        self.M['럭키삼공']  = my.sf(self.DB.parameter('L0030'))
        #----------------------------------------------------------
        self.M['일오자금']  = round(self.M['시즌자금'] * self.M['럭키일오'][0] / 100,2)
        self.M['일오진입']  = round((100+self.M['럭키일오'][1])/100,2)
        self.M['이공자금']  = round(self.M['시즌자금'] * self.M['럭키이공'][0] / 100,2)
        self.M['이공진입']  = round((100+self.M['럭키이공'][1])/100,2)
        self.M['이오자금']  = round(self.M['시즌자금'] * self.M['럭키이오'][0] / 100,2)
        self.M['이오진입']  = round((100+self.M['럭키이오'][1])/100,2)
        self.M['삼공자금']  = round(self.M['시즌자금'] * self.M['럭키삼공'][0] / 100,2)
        self.M['삼공진입']  = round((100+self.M['럭키삼공'][1])/100,2)
         
        

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
        D['시즌자금']  = self.M['시즌자금']
        pr015 = round(DS['평균단가']*self.M['일오진입'],2); D['매수15'] = int(self.M['일오자금']/pr015)  # 진입수량
        pr020 = round(DS['평균단가']*self.M['이공진입'],2); D['매수20'] = int(self.M['이공자금']/pr020)  # 진입수량
        pr025 = round(DS['평균단가']*self.M['이오진입'],2); D['매수25'] = int(self.M['이오자금']/pr025)  # 진입수량
        pr030 = round(DS['평균단가']*self.M['삼공진입'],2); D['매수30'] = int(self.M['삼공자금']/pr030)  # 진입수량
        D['기준단가'] = DS['평균단가']
        
        return D

    