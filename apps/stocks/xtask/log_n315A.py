import myutils.my_utils as my
from myutils.DB import DB

class log :

    def __init__(self) :

        self.DB = DB('stocks')
        self.D = {}
        self.M = {}

    def set_value(self,key,val) :

        for k in key :
            self.M[k] = val

    def commission(self,opt) :
        
        if  self.D['수료적용'] == 'on' :
            mm = self.M['매수금액'] if opt == 1 else self.M['매도금액']
            fee = int(mm*0.07)/100
            if opt==2 : fee += round(mm*0.0008)/100
            self.M['수수료등']  = fee
            self.M['현재잔액'] -= fee

    def calculate(self)  :
        
        self.D['진행상황'] = '매수대기'

        if  self.M['매수수량'] : 
            self.M['매수금액']  = self.M['매수수량'] * self.M['당일종가']
            self.M['보유수량'] += self.M['매수수량']
            self.M['현재잔액'] -= self.M['매수금액']
            self.M['총매수금'] += self.M['매수금액']
            self.M['평균단가'] =  self.M['총매수금'] / self.M['보유수량'] 

            self.M['진행여부'] = '매매진행'
            self.D['진행상황'] = self.M['차수명칭'][self.M['매수차수']] 
            self.D['카테고리'] = '일반진행'
            
            self.M['매수차수']+= 1
            self.D['배분금액'] = int( self.M['초기금액'] * self.M['분할배분'][0]) 
            

            self.commission(1)
        
        self.M['평가금액'] = self.M['당일종가'] * self.M['보유수량'] 
        self.M['현재수익'] = self.M['평가금액'] - self.M['총매수금']
        self.M['현수익률'] = self.M['현재수익'] / self.M['총매수금']  * 100  if self.M['총매수금'] else 0.00  
        
        if  self.M['매도수량'] :
            self.M['매도금액']  =  self.M['매도수량'] * self.M['당일종가']
            self.M['현재수익']  =  self.M['매도금액'] - self.M['총매수금']
            self.M['보유수량'] -=  self.M['매도수량'];  self.M['현재잔액'] += self.M['매도금액'] 
            self.M['현수익률'] = round( self.M['현재수익'] / self.M['초기금액'] * 100, 2 )   
            self.commission(2) 
            
            self.M['평가금액'] = 0.00
            self.M['총매수금'] = 0.00
            self.M['평균단가'] = 0.00

            self.M['진행상황'] = '익절매도' if self.M['현재수익'] >= 0 else '손절매도'
            self.M['매수차수'] = 0

            self.M['진행여부'] = '진입대기'
            self.D['진행상황'] = '익절매도' if self.M['현재수익'] >= 0 else '손실매도'
            self.D['카테고리'] = '수익실현'

            self.D['배분금액'] = int( self.M['현재잔액'] * self.M['분할배분'][0]) 
            self.D['초기금액'] = self.M['현재잔액']


    def today_buy(self) :
        
        if  self.M['당일종가'] <= self.M['매수예가'] : 
            self.M['매수수량']  = self.M['매수예정']
            
  
    def today_sell(self) :
        
        if  self.M['당일종가'] >= self.M['매도예가'] : self.M['매도수량'] = self.M['보유수량']


    def tomorrow_buy(self) :
        
        if  self.M['진행여부'] == '진행중단' : 
            self.D['매수예정'] = '0'
            self.D['매수예가'] = '0.00'
        
        elif self.M['진행여부'] == '매매진행' :

            if  self.M['매수차수'] >  self.M['최대차수']-1 : 
                self.D['매수예정'] = '0'
                self.D['매수예가'] = '0.00'
                return
            
            if  self.M['매수차수'] == self.M['최대차수']-1 : self.M['매금단계'][self.M['최대차수']-1] = int(self.M['현재잔액'])
            
            self.D['매수예가'] = round(self.M['당일종가'] * self.M['매입가치'],2)
            self.D['예정수량'] = int(  self.M['매금단계'][self.M['매수차수']]/ self.M['매수예가'] ) 

        else :
            self.D['매수예가'] = round(self.M['당일종가']-0.01, 2) if self.M['당일연속'] >= self.M['진입일자']-1 else round(self.M['당일종가'] * self.M['진입가치'],2)     
            self.D['예정수량'] = int(  self.M['매금단계'][0]/ self.M['매수예가'] ) 
        
    def tomorrow_sell(self) :
        
        if  not self.M['보유수량'] : 
            self.D['매도예정'] = '0'
            self.D['매도예가'] = '0.00'
        else :
            self.D['매도예정'] = self.M['보유수량']
            self.D['매도예가'] = my.round_up(self.M['평균단가'] * self.M['각매가치'][self.M['매수차수']-1])


    def init_value(self) :

        ST = self.DB.parameters_dict('매매전략/N315A')
        LD = self.DB.last_data_line('*','h_log315A_board')
        CD = self.DB.last_data_line('add0,add3,add8,add10','h_stockHistory_board')
        # ---------------------------------------------------------
        self.M['분할배분'] = my.sf(ST['A0101'])
        self.M['각매가치'] = my.sf(ST['A0301'])
        self.M['매입가치'] = ST['A0201']
        self.M['진입일자'] = ST['A0202']
        self.M['진입가치'] = ST['A0203']
        #---------------------------------------------------------- 
        if  ST['A0720'] == 'on' : 
            self.M['진행여부'] = '매매진행' if LD['add20'] == '일반진행' else '진입대기'
        else :
            self.M['진행여부'] = '진행중단'

        self.M['진행상황'] = LD['add20']
        self.M['기록시즌'] = int(LD['add1'])
        self.M['수료적용'] = 'off'
        self.M['세금적용'] = 'off'
        self.M['초기금액'] = my.sv(LD['add19'])
        # 종가 정보
        self.M['당일종가'] = float(CD['add3']) 
        self.M['당일날자'] = CD['add0']
        self.M['당일연속'] = CD['add10']
        self.M['당일증감'] = CD['add8']
        # 잔액 분할
        self.M['최대차수'] = len(self.M['분할배분'])
        self.M['차수명칭'] = ['일차매수','이차매수','삼차매수','사차매수','오차매수','육차매수','칠차매수']
        self.M['매금단계'] = [0.0] * self.M['최대차수']
        for i in range(self.M['최대차수']) : self.M['매금단계'][i] = int( self.M['초기금액'] * self.M['분할배분'][i]) 
        self.M['매수차수'] = self.M['차수명칭'].index(LD['add6']) if LD['add6'] in self.M['차수명칭'] else 0

        #------------------------------------------------------------
        self.D['진행일자'] = CD['add0']
        self.D['카테고리'] = LD['add20']
        self.D['당일종가'] = CD['add3']
        self.D['종가변동'] = CD['add8']
        self.D['현재시즌'] = LD['add1']
        self.D['진행일수'] = LD['add2']
        self.M['현재잔액'] = float(LD['add5'])
        self.D['진행상황'] = LD['add6']
        self.D['매수수량'] = LD['add7']
        self.D['매수금액'] = LD['add8']
        self.M['보유수량'] = int(LD['add9'])
        self.M['총매수금'] = float(LD['add11'])
        self.D['평가금액'] = LD['add12']
        self.D['평균단가'] = LD['add10']
        self.D['매도금액'] = LD['add13']
        self.D['현재수익'] = LD['add14']
        self.D['현수익률'] = LD['add15']
        self.D['가치합계'] = LD['add16']
        self.M['매수예정'] = int(LD['add22'])
        self.M['매수예가'] = float(LD['add23']) 
        self.M['매도예정'] = int(LD['add24'])
        self.M['매도예가'] = float(LD['add25'])
        self.D['수수료등'] = '0.00'
        self.D['배분금액'] = LD['add17']
        self.D['초기일자'] = LD['add18']
        self.M['초기금액'] = float(LD['add19'])
        #-------------------------------------------------------------
        self.set_value(['매수수량','매도수량'],0)
        self.set_value(['매수금액','매도금액','총매수금','평균단가','현재수익','현수익률','평가금액','매수예가','수수료등'],0.0)

    def print_data(self) :
        X = {}
        X['add0']  = self.M['당일날자'] 
        X['add20'] = self.D['카테고리'] 
        X['add3']  = self.D['당일종가'] 
        X['add8']  = self.D['종가변동'] 
        X['add1']  = self.D['현재시즌'] 
        X['add2']  = self.D['진행일수'] 
        X['add5']  = self.M['현재잔액'] 
        X['add6']  = self.D['진행상황'] 
        X['add7']  = self.D['매수수량'] 
        X['add8']  = self.D['매수금액'] 
        X['add9']  = self.M['보유수량'] 
        X['add11'] = self.M['총매수금']
        X['add12'] = self.D['평가금액']
        X['add10'] = self.D['평균단가']
        X['add13'] = self.D['매도금액']
        X['add14'] = self.D['현재수익']
        X['add15'] = self.D['현수익률']
        X['add16'] = self.D['가치합계']
        X['add22'] = self.M['매수예정']
        X['add23'] = self.M['매수예가'] 
        X['add24'] = self.M['매도예정']
        X['add25'] = self.M['매도예가']
        X['add21'] = self.D['수수료등']
        X['add17'] = self.D['배분금액']
        X['add18'] = self.D['초기일자']
        X['add19'] = str(self.M['초기금액'])



# -------
# 로그
# -------
today = my.kor_loc_date('US/Eastern')[0:10]
weekd = my.dayofdate(today)

ck_holiday = DB.exe(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday[0][0] if ck_holiday else ''

skip = (weekd in ['토','일']) or is_holiday

if  skip : pass

else :
  
    LD = DB.oneline("SELECT add18,add19 FROM h_log315_board ORDER BY add0 DESC LIMIT 1")

    L = log()
    L.init_value()


         