from myutils.DB import DB
import myutils.my_utils as my

class update_Log315 :

    def __init__(self) :

        self.DB    = DB('stocks')
        self.chart = False
        self.stat  = False
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
            
            self.vCount(self.M['수익현황'])
            self.rebalance() 
            

        self.realMDD()


    def realMDD(self) :
        
        if not self.stat : return

        self.M['실최하락'] = (self.M['평가금액']-self.M['총매수금']) / (self.M['현재잔액'] + self.M['총매수금']) * 100
        
        if  self.M['실최하락'] < self.M['진최하락'] : self.M['진최하락'] = self.M['실최하락']; self.M['최하일자'] = self.M['현재일자']
        if  self.M['현재날수'] > self.M['최장일수'] : self.M['최장일수'] = self.M['현재날수']; self.M['최장일자'] = self.M['현재일자']
        
    def vCount(self,profit) :
        
        if not self.stat : return
        if  profit >= 0 : self.D['익절횟수'] += 1
        else : self.D['손절횟수'] += 1

    def commission(self,opt) :
        
        if  self.D['수료적용'] == 'on' :
            mm = self.M['매수금액'] if opt == 1 else self.M['매도금액']
            fee = int(mm*0.07)/100
            if opt==2 : fee += round(mm*0.0008)/100
            self.M['수수료등']  = fee
            self.M['현재잔액'] -= fee
        
    def rebalance(self)  :

        for i in range(self.M['최대차수']) : self.M['매금단계'][i] = int( self.M['현재잔액'] * self.M['분할배분'][i]) 
       
        if  self.stat :
            pzero = my.sv(self.D['손익통계'][0][1])
            pbase = my.sv(self.D['손익통계'][-1][1])
            difft = self.M['현재잔액'] - pbase
            diffz = self.M['현재잔액'] - pzero
            diffp = difft/pbase * 100
            diff0 = diffz/pzero * 100

            if diffp <= self.D['손익저점'] : self.D['손익저점'] = diffp; self.D['저점날자'] = self.M['현재일자']

            diffd = self.D['월익통계'][-1][0][:7] 
            if   self.M['현재일자'][0:7] == diffd : self.D['월익통계'][-1][1] += difft 
            else : self.D['월익통계'].append([self.M['현재일자'][0:7],difft])
            color = "#F6CECE" if difft >= 0 else "#CED8F6"
            self.D['손익통계'].append([self.M['현재일자'],f"{self.M['현재잔액']:,.2f}",f"{difft:,.2f}",f"{diffp:.2f}",color,self.M['기록시즌'],f"{diff0:.2f}"])
    
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

        self.set_value(['매도수량','매도금액','매수수량','매수금액','수익현황','현수익률','평균단가','매수예가','예정수량','매도예가','매수차수'],0)
        
        진입단가 = round(self.M['전일종가']-0.01, 2) if self.M['당일연속'] >= self.M['진입일자'] else round(self.M['전일종가'] * self.M['진입가치'],2)
        
        if  self.M['당일종가'] <=  진입단가  :
            
            self.M['기록시즌'] += 1
            self.M['현재날수'] = 1
            self.M['매수수량']  = int( self.M['매금단계'][0]/진입단가 )
            self.M['수익현황']  = self.M['현수익률'] = 0.0
            self.M['보유수량']  = self.M['매수수량']
            self.M['평균단가']  = self.M['당일종가'] 
            self.M['매수금액']  = self.M['당일종가'] * self.M['매수수량']
            self.M['총매수금']  = self.M['평가금액'] = self.M['매수금액']
            self.M['현재잔액'] -= self.M['매수금액']
            self.commission(1)

            self.M['진행상황'] = '일차매수'
            self.M['매수차수']  = 1
            self.M['첫날기록'] = False

            return True

        else : 
            return False


    def chart_data(self) :
        
        if not self.chart : return
        self.D['clse_p'].append(self.M['당일종가'])
        if avg_v := round(self.M['평균단가'],2) : self.D['avge_v'].append(avg_v)
        else : self.D['avge_v'].append('null')
    
        self.D['c_date'].append(self.M['현재일자'][2:])
        self.D['totalV'].append(round(self.M['현재잔액'] + self.M['평가금액'],0))

    def simulate(self,printOut=False) :

        for idx,BD in enumerate(self.B) : 
            if BD['add0'] < self.D['시작일자'] : idxx = idx; continue

            self.M['현재일자'] = BD['add0']
            self.M['당일종가'] = float(BD['add3'])
            self.M['종가변동'] = float(BD['add8']) 
            self.M['당일연속'] = int(BD['add10']) 
            self.M['전일종가'] = float(self.B[idx-1]['add3'])  
            self.M['진행상황'] = ''
            self.set_value(['매도수량','매도금액','매수수량','매수금액','수익현황','현수익률'],0)
            
            # BD의 기록은 시작일자 보다 전의 데이타(종가기록 등)에서 시작하고, 당일종가가 전일에 비해 설정값 이상으로 상승 시 건너뛰기 위함
            if  idx == idxx + 1 or self.M['첫날기록'] : 
                
                if  self.new_day() : self.tomorrow_step(); self.chart_data(); self.increase_count(printOut); continue
                else : self.M['첫날기록'] = True; self.chart_data(); continue

            self.today_sell()
            self.today_buy()
            self.calculate()
            self.chart_data()
            self.tomorrow_step()
            self.increase_count(printOut)
        
   
    def set_value(self,key,val) :

        for k in key :
            self.M[k] = val

    def result(self) :

        self.D['최장일수'] = self.M['최장일수']
        self.D['최장일자'] = self.M['최장일자']
        self.D['MDD1'] = f"{self.M['진최하락']:.2f}"; self.D['MDD_DAY1'] = self.M['최하일자'][2:]
        
        초기자본 = float(self.D['일반자금'].replace(',','')); 
        최종자본 = self.M['평가금액']+self.M['현재잔액']; 
        최종수익 = 최종자본-초기자본; 
        self.D['v_profit'] = round((최종수익/초기자본)*100,2)
        
        self.D['R_초기자본'] = f"{초기자본:,.0f}"
        self.D['R_최종자본'] = f"{최종자본:,.2f}"
        self.D['R_최종수익'] = f"{최종수익:,.2f}"
        self.D['R_최종익률'] = f"{self.D['v_profit']:,.2f}"
        self.D['R_총경과일'] = f"{my.diff_day(self.D['시작일자'],self.D['종료일자']):,}"

        if self.chart and self.D['c_date'] : self.D['s_date'] = self.D['c_date'][0]; self.D['e_date'] = self.D['c_date'][-1]

        if  self.stat :
            self.D['월별구분'] = [ x[0] for x in self.D['월익통계']][-28:]
            self.D['월별이익'] = [ round(x[1]) for x in self.D['월익통계']][-28:]

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

    def get_start(self,b='') :

        self.D['종목코드']  = 'SOXL'
        if b : self.D['시작일자'] = b
        old_date = my.dayofdate(self.D['시작일자'],-7)[0]
        self.DB.tbl, self.DB.wre, self.DB.odr = ('h_stockHistory_board',f"add1='{self.D['종목코드']}' AND add0 BETWEEN '{old_date}' AND '{self.D['종료일자']}'",'add0')
        self.B = self.DB.get('add0,add3,add8,add10') # 날자, 종가, 증감, 연속하락 

        # 데이타 존재 여부 확인
        self.DB.tbl, self.DB.wre = ("h_stockHistory_board",f"add1='{self.D['종목코드']}'")
        chk_data = self.DB.get_one("min(add0)")
        if  chk_data > self.D['시작일자'] : 
            self.D['NOTICE'] = f" {self.D['시작일자']} 에서 {self.D['종료일자']} 까지 분석을 위한 데이타가 부족합니다. 시작 날자를 {chk_data} 이후 3일 뒤로 조정하시기 바랍니다."
            

    def increase_count(self,printOut=False) :
        
        if not self.M['보유수량'] and not self.M['매도수량']: return
        if printOut : self.print_backtest()
        self.M['현재날수'] +=1
        
    def init_value(self) :
        
        ST = self.DB.parameters_dict('매매전략/N315')
        # ---------------------------------------------------------
        self.M['분할배분']  = my.sf(ST['N0101'])
        self.M['각매가치']  = my.sf(ST['N0301'])
        self.M['매입가치']  = ST['N0201']
        self.M['진입일자']  = ST['N0202']
        self.M['진입가치']  = ST['N0203']
        #----------------------------------------------------------
        self.M['진행상황']  = '매수대기'
        self.M['기록시즌']  = 0
        
        if '수료적용' not in self.D : self.D['수료적용']  = 'on'
        if '세금적용' not in self.D : self.D['세금적용']  = 'off'

        self.M['현재잔액']  = my.sv(self.D['일반자금'])
   
        # 잔액 분할
        self.M['최대차수'] = len(self.M['분할배분'])
        self.M['차수명칭'] = ['일','이','삼','사','오','육','칠']
        self.M['매금단계'] = [0.0] * self.M['최대차수']
        for i in range(self.M['최대차수']) : self.M['매금단계'][i] = int( self.M['현재잔액'] * self.M['분할배분'][i]) 
        self.M['매수차수'] = 0
        
        self.M['최장일자']  = ' '
        self.M['현재날수']  = 1
        self.M['최장일수']  = 0   # 최고 오래 지속된 시즌의 일수
        self.M['첫날기록']  = False
        self.M['전일종가']  = 0.0
        
        self.set_value(['매수수량','매도수량','예정수량','보유수량','진최하락'],0)
        self.set_value(['매수금액','매도금액','총매수금','평균단가','수익현황','현수익률','평가금액','매수예가','수수료등'],0.0)
        self.M['최하일자'] = ''
        self.D['익절횟수'] = self.D['손절횟수'] = 0
        
        if  self.chart : # 챠트작성
            
            self.D['TR'] = []
            self.D['c_date'] = []
            self.D['clse_p'] = []
            self.D['avge_v'] = []


        # 통계자료
        if  self.stat :

            self.D['totalV'] = []
            self.D['일정익절'] = self.D['일정손절'] = self.D['일회익절'] = self.D['일회손절'] = 0

            self.D['손익통계'] = [[self.D['시작일자'],f"{self.M['현재잔액']:,.2f}",'0.00','0.00',"#F6CECE",'','0.00']]
            self.D['월익통계'] = [[self.D['시작일자'][:7],0.00]]
            self.D['손익저점'] = 100
            self.D['저점날자'] = ''

    # -------------------------------------------------------------------------------------------------------------------------------------------
    # nextStep : 다음 날에 대한 전략을 계산한다  
    # -------------------------------------------------------------------------------------------------------------------------------------------            
    def nextStep(self) :

        self.D['다음날자'],  self.D['다음요일'] = self.next_stock_day(self.D['종료일자'])
        self.D['현재날자'] = self.M['현재일자']
        self.D['현재종가'] = self.M['당일종가']
        self.D['현재연속'] = self.M['당일연속']
        # 매수차수는 매수가 이루어졌을 경우에 증가함
        if     self.M['매수차수'] >  self.M['최대차수']-1 : self.D['배분금액'] = 0
        elif   self.M['매수차수'] == self.M['최대차수']-1 : self.D['배분금액'] = int(self.M['현재잔액'])
        else : self.D['배분금액'] =  int(self.M['매금단계'][self.M['매수차수']])
        
        self.D['배분금액'] = int(self.M['매금단계'][self.M['매수차수']]) if self.M['예정수량'] else 0

        self.D['N_변동'] = round(self.M['종가변동'],2)
        
        if  self.M['첫날기록'] or not self.M['보유수량'] : 

            self.D['N_생활매수가'] = round(self.M['당일종가'] * self.M['진입가치'],2)
            if self.M['당일연속'] == self.M['진입일자']-1 : self.D['N_생활매수가'] = round(self.M['당일종가'] -0.01,2 ) 
            
            self.D['N_생활매수량'] = int( self.M['매금단계'][1] / self.D['N_생활매수가'] )
            self.D['N_생활종대비'] = self.next_percent(self.M['당일종가'],self.D['N_생활매수가'])
            self.D['N_생활매도량'] = 0
            self.D['N_생활매도가'] = 0
            self.D['N_생활도평비'] = 0
            self.D['N_생활도종비'] = 0
            self.D['N_생활평대비'] = 0
            
        else : 
            self.D['N_생활매수량'] = self.M['예정수량']
            self.D['N_생활매수가'] = self.M['매수예가']
            self.D['N_생활평대비'] = self.next_percent(self.M['평균단가'],self.D['N_생활매수가']) 
            self.D['N_생활종대비'] = self.next_percent(self.M['당일종가'],self.D['N_생활매수가'])
            self.D['N_생활매수가'] = self.D['N_생활매수가']
            
            self.D['N_생활매도량'] = self.M['보유수량']
            self.D['N_생활매도가'] = self.M['매도예가']
            self.D['N_생활도평비'] = self.next_percent(self.M['평균단가'],self.M['매도예가'])
            self.D['N_생활도종비'] = self.next_percent(self.M['당일종가'],self.M['매도예가'])
            
    def next_percent(self,a,b) :
        
        if not a : return ''
        return f"{(b/a-1)*100:.2f}"
    
# ------------------------------------------------------------------------------------------------------------------------------------------
# From n315.py END
# ------------------------------------------------------------------------------------------------------------------------------------------
    def next_stock_day(self,today) :
        delta = 1
        while delta :
            temp = my.dayofdate(today,delta)
            weekend = 1 if temp[1] in ('토','일') else 0
            holiday = 1 if self.DB.cnt(f"SELECT key FROM parameters WHERE val='{temp[0]}' and cat='미국증시휴장일'") else 0 
            delta = 0 if not (weekend + holiday) else delta + 1
        return temp

    def print_backtest(self) :
        return

    def do_tacticLog(self,start,end,ini_money) :
        self.chart = False
        self.stat  = False
        self.D['시작일자'] = start
        self.D['종료일자'] = end
        self.D['일반자금'] = ini_money
        self.get_start()
        self.init_value()
        self.simulate(printOut=False)

    def get_simulLog(self) :
        
        D = {}
        D['첫날기록']= self.M['첫날기록']
        D['add0']   = self.M['현재일자'] # 날자
        D['add1']   = self.M['기록시즌'] # 시즌
        D['add2']   = self.M['현재날수']-1 # 날수
        D['add3']   = self.M['당일종가'] # 종가
        D['add4']   = self.M['종가변동'] # 변동
        D['add5']   = f"{self.M['현재잔액']:.2f}" # 현재잔액
        D['add6']   = self.M['진행상황'] if self.M['진행상황'] else '매수대기' # 진행상황
        D['add7']   = self.M['매수수량'] # 매수량
        D['add8']   = f"{self.M['매수금액']:.2f}" # 매수금액
        D['add9']   = self.M['보유수량'] # 보유수량
        D['add10']  = f"{self.M['평균단가']:.4f}" # 평균단가
        D['add11']  = f"{self.M['총매수금']:.2f}" # 총매수금
        D['add12']  = f"{self.M['평가금액']:.2f}" # 평가금액
        D['add13']  = f"{self.M['매도금액']:.2f}" # 매도금액
        D['add14']  = f"{self.M['수익현황']:.2f}" # 수익현황
        D['add15']  = f"{self.M['현수익률']:.2f}" # 현수익률
        D['add16']  = f"{self.M['현재잔액'] + self.M['평가금액']:.2f}" # 가치합계
        D['add17']  = f"{self.M['매금단계'][self.M['매수차수']]:.0f}"  # 배분금액
        D['add18']  = self.D['시작일자'] # 초기일자
        D['add19']  = self.D['일반자금'] # 초기금액
        D['add20']  = '수익실현' if self.M['매도금액'] else '일반진행' # 초기금액
        D['add21']  = f"{self.M['수수료등']:.2f}" # 수수료등
        return D
    