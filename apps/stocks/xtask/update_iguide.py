from myutils.DB import DB
import myutils.my_utils as my

class update_iguide :

    def __init__(self) :

        self.DB    = DB('stocks')
        self.chart = False
        self.stat  = False
        self.skey  = self.DB.store("slack_key")
        self.board = 'h_IGUIDE_board'

        self.B = {}
        self.V = {}
        self.M = {}
        self.D = {}

    def send_message(self,message) :
        if self.DB.system == "Linux" : my.post_slack(self.skey,message)
        else : print(message)  

    # ------------------------------------------------------------------------------------------------------------------------------------------
    # 
    # ------------------------------------------------------------------------------------------------------------------------------------------
    def calculate(self)  :

        if  self.V['매수수량'] : 
            self.V['현재잔액'] -= self.V['매수금액']
            self.V['보유수량'] += self.V['매수수량']
            self.V['총매수금'] += self.V['매수금액']
            self.V['평균단가'] =  self.V['총매수금'] / self.V['보유수량'] 
            if self.D['수료적용'] == 'on' :  self.V['수수료등']  = self.commission(self.V['매수금액'],1); self.V['현재잔액'] -= self.V['수수료등']
        
        if  self.V['매도수량'] :
            self.V['실현수익']  = (self.M['당일종가'] - self.V['평균단가']) * self.V['매도수량']
            self.V['보유수량'] -=  self.V['매도수량'];  self.V['현재잔액'] += self.V['매도금액']; self.V['총매수금'] = 0.00
            self.V['수익현황']  =  self.V['실현수익']
            
            if self.D['수료적용'] == 'on' : self.V['수수료등']  = self.commission(self.V['매도금액'],2); self.V['현재잔액'] -= self.V['수수료등'] 
            if self.D['세금적용'] == 'on' : self.V['현재잔액'] -=  self.tax(self.V['실현수익'])
            
            self.vCount(self.V['실현수익'])

        self.V['평가금액'] =  self.M['당일종가'] * self.V['보유수량'] 
        self.V['현수익률'] = (self.M['당일종가'] / self.V['평균단가'] -1) * 100  if self.V['평균단가'] else 0.00        

        if  self.V['매도수량'] :
            self.M['첫날기록'] = True
            self.M['회복전략'] = self.M['손실회수']
            self.set_value(['매수단계'],'일반매수')
            self.set_value(['평균단가'],0.0)
            self.rebalance() 
            
        else  : 
            self.V['수익현황'] = self.V['평가금액'] - self.V['총매수금']

        self.realMDD()


    def realMDD(self) :
        
        if not self.stat : return

        self.V['실최하락'] = (self.V['평가금액']-self.V['총매수금']) / (self.V['현재잔액'] + self.V['총매수금']) * 100
        if  self.V['실최하락'] < self.V['진최하락'] : 
            self.V['진최하락'] = self.V['실최하락']; self.V['최하일자'] = self.M['현재일자']

        if  self.M['현재날수'] > self.M['최장일수'] : 
            self.M['최장일수'] = self.M['현재날수'] 
            self.M['최장일자'] = self.M['현재일자']
        
    def vCount(self,profit) :
        
        if not self.stat : return
        if  profit >= 0 : 
            if self.M['회복전략'] : self.D['일회익절'] += 1
            else : self.D['일정익절'] += 1  
        else : 
            if self.M['회복전략'] : self.D['일회손절'] += 1
            else : self.D['일정손절'] += 1   

    def commission(self,mm,opt) :

        fee = int(mm*0.07)/100
        if opt==2 : fee += round(mm*0.0008)/100
        return fee
        
    def tax(self,mm) :

        return int(mm*0.22) 
        
    def rebalance(self)  :

        self.V['일매수금'] = int(self.V['현재잔액']/self.M['분할횟수']) 

        if  self.stat :
            pzero = my.sv(self.D['손익통계'][0][1])
            pbase = my.sv(self.D['손익통계'][-1][1])
            difft = self.V['현재잔액'] - pbase
            diffz = self.V['현재잔액'] - pzero
            diffp = difft/pbase * 100
            diff0 = diffz/pzero * 100

            if diffp <= self.D['손익저점'] : self.D['손익저점'] = diffp; self.D['저점날자'] = self.M['현재일자']

            diffd = self.D['월익통계'][-1][0][:7] 
            if   self.M['현재일자'][0:7] == diffd : self.D['월익통계'][-1][1] += difft 
            else : self.D['월익통계'].append([self.M['현재일자'][0:7],difft])
            color = "#F6CECE" if difft >= 0 else "#CED8F6"
            self.D['손익통계'].append([self.M['현재일자'],f"{self.V['현재잔액']:,.2f}",f"{difft:,.2f}",f"{diffp:.2f}",color,self.M['기록시즌'],f"{diff0:.2f}"])
    
    def today_sell(self) :
        
        if  self.M['당일종가'] >= self.M['매도가격'] : 

            self.M['회복전략']  = self.M['손실회수']

            self.V['매도수량'] = self.V['보유수량']
            self.V['매도금액'] = self.V['매도수량'] * self.M['당일종가']
            self.V['진행상황'] = '익절매도' 

            if  self.M['당일종가'] < self.V['평균단가'] : 
                self.V['진행상황'] = '손절매도'
                self.M['손실회수'] = True
            else :
                self.M['손실회수'] = False

    def today_buy(self) :

        if  self.M['당일종가'] <= self.M['매수가격'] : 
            self.V['매수수량']  = self.V['구매수량']
            거래코드 = 'L' if self.V['매수단계'] == '매수제한' else 'B'
            self.V['거래코드']  = 거래코드 + str(self.V['매수수량']) if self.V['구매수량'] else ' '
            self.V['매수금액']  = self.V['매수수량'] * self.M['당일종가']
            

    def tomorrow_buy(self) :

        self.M['매수가격'] = round(self.M['당일종가']*self.M['평단가치'],2)
        self.V['구매수량'] = my.ceil(self.V['기초수량'] * (self.M['현재날수']*self.M['비중조절'] + 1))
        
        if  self.V['현재잔액'] < self.V['구매수량'] * self.M['매수가격'] :
            self.V['구매수량'] = my.ceil(self.V['기초수량'] * self.M['위매비중'])
            self.V['매수단계'] = '매수제한' 

            if  self.V['현재잔액'] < self.V['구매수량'] * self.M['매수가격'] : 
                self.V['구매수량'] = 0
                self.V['매수단계'] = '매수금지'

    def tomorrow_sell(self) :

        # [일반진행]---------------------------------------------------------------------------------------------
        if  not self.M['손실회수'] :
            
            if  self.V['매수단계'] not in ('매수제한','매수금지') :  
                self.M['매도가격'] = my.round_up(self.V['평균단가'] * self.M['첫매가치'])
                
            else :
                self.M['매도가격'] = my.round_up(self.V['평균단가'] * self.M['둘매가치'])  
        
        # [전략진행]---------------------------------------------------------------------------------------------
        else :
           
            if  self.M['현재날수'] < self.M['매도대기'] :
                self.M['매도가격'] = my.round_up(self.V['평균단가'] * self.M['전략가치'])
            else :
                self.M['매도가격'] = my.round_up(self.V['평균단가'] * self.M['둘매가치'])
                    

    def tomorrow_step(self)   :

        self.V['진행상황'] = self.V['매수단계']
        self.tomorrow_buy()
        self.tomorrow_sell()
        

        if  self.M['매수가격']>= self.M['매도가격'] : self.M['매수가격'] = self.M['매도가격'] - 0.01
        
    
    def new_day(self) :


        self.set_value(['매도수량','매도금액','매수수량','매수금액','수익현황','현수익률','평균단가'],0)
            
        if  self.M['당일종가'] <  round(self.M['전일종가'] * self.M['큰단가치'],2) :
            
            self.M['기록시즌'] += 1
            self.M['현재날수'] = 1
            
            self.V['기초수량']  = my.ceil(self.V['일매수금']/self.M['전일종가'])
 
            self.V['매수수량']  = self.V['기초수량']
            self.V['수익현황']  = self.V['현수익률'] = 0.0
            self.V['보유수량']  = self.V['매수수량']
            self.V['평균단가']  = self.M['당일종가'] 
            self.V['매수금액']  = self.M['당일종가'] * self.V['매수수량']
            self.V['총매수금']  = self.V['평가금액'] = self.V['매수금액']
            self.V['현재잔액'] -= self.V['매수금액']
            self.V['거래코드']  = f"{self.V['매수수량']}" 
            if self.D['수료적용'] == 'on' : self.V['수수료등']  = self.commission(self.V['매수금액'],1); self.V['현재잔액'] -= self.V['수수료등']

            self.V['매수단계'] = '일반매수'
            self.V['진행상황'] = '첫날매수'
            self.M['첫날기록'] = False
 
            return True

        else : 
            return False
    
    
    def simulate(self,printOut=False) :

        for idx,BD in enumerate(self.B) : 
            if BD['add0'] < self.D['시작일자'] : idxx = idx; continue

            self.M['현재일자'] = BD['add0']
            self.M['당일종가'] = float(BD['add3'])
            self.M['종가변동'] = float(BD['add8']) 
            self.M['전일종가'] = float(self.B[idx-1]['add3'])  
            self.V['거래코드'] = ' '
            self.set_value(['매도수량','매도금액','매수수량','매수금액','수익현황','현수익률'],0)
            
            # BD의 기록은 시작일자 보다 전의 데이타(종가기록 등)에서 시작하고, 당일종가가 전일에 비해 설정값 이상으로 상승 시 건너뛰기 위함
            if  idx == idxx + 1 or self.M['첫날기록'] : 
                if  self.new_day() : self.tomorrow_step(); self.increase_count(printOut); continue
                else : self.M['첫날기록'] = True; continue

            self.today_sell()
            self.today_buy()
            self.calculate()
            self.tomorrow_step()
            self.increase_count(printOut)
    
    def set_value(self,key,val) :

        for k in key :
            self.V[k] = val

    def result(self) :

        self.D['최장일수'] = self.M['최장일수']
        self.D['최장일자'] = self.M['최장일자']
        self.D['MDD1'] = f"{self.V['진최하락']:.2f}"; self.D['MDD_DAY1'] = self.V['최하일자'][2:]

        
        초기자본 = float(self.D['일반자금'].replace(',','')); 
        최종자본 = self.V['평가금액']+self.V['현재잔액']; 
        최종수익 = 최종자본-초기자본; 
        self.D['v_profit'] = round((최종수익/초기자본)*100,2)
        
        self.D['R_초기자본'] = f"{초기자본:,.0f}"
        self.D['R_최종자본'] = f"{최종자본:,.2f}"
        self.D['R_최종수익'] = f"{최종수익:,.2f}"
        self.D['R_최종익률'] = f"{self.D['profit_t']:,.2f}"
        self.D['R_일반익률'] = f"{self.D['v_profit']:,.2f}"
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
        self.B = self.DB.get('add0,add3,add8') # 날자, 종가, 증감 

        # 데이타 존재 여부 확인
        self.DB.tbl, self.DB.wre = ("h_stockHistory_board",f"add1='{self.D['종목코드']}'")
        chk_data = self.DB.get_one("min(add0)")
        if  chk_data > self.D['시작일자'] : 
            self.D['NOTICE'] = f" {self.D['시작일자']} 에서 {self.D['종료일자']} 까지 분석을 위한 데이타가 부족합니다. 시작 날자를 {chk_data} 이후 3일 뒤로 조정하시기 바랍니다."

    def increase_count(self,printOut=False) :
        
        if not self.V['보유수량'] and not self.V['매도수량']: return
        if printOut : self.print_backtest()
        self.M['현재날수'] +=1
        
    def init_value(self) :

        if '비중조절' not in self.M :
            
            ST = self.DB.parameters_dict('매매전략/VRS')
            
            self.M['비중조절']  = ST['01001']  
            self.M['평단가치']  = ST['00300']  
            self.M['큰단가치']  = ST['00200']  
            self.M['첫매가치']  = ST['00400'] 
            self.M['둘매가치']  = ST['00500']  
            self.M['강매시작']  = ST['00800']  
            self.M['강매가치']  = ST['00700']  
            self.M['위매비중']  = ST['01000']  
            self.M['종가상승']  = ST['01600']  
            self.M['매도대기']  = ST['00600']  
            self.M['전략가치']  = ST['00900']  
            self.M['분할횟수']  = ST['00100']  
            self.M['찬스일가']  = ST['01002']  

        self.M['손실회수']  = False  
        self.M['회복전략']  = False      # 현재 진행 중인 상황이 손실회수 상태인지 아닌지를 구분( for 통계정보 )
        self.V['매수단계']  = '일반매수'
        self.V['진행상황']  = '매수대기'
        self.M['기록시즌']  = 0

        if '가상손실' in self.D  and  self.D['가상손실'] == 'on' : self.M['손실회수']  = True     
        if '수료적용' not in self.D : self.D['수료적용']  = 'on'
        if '세금적용' not in self.D : self.D['세금적용']  = 'off'
        if '일반자금' not in self.D : self.D['일반자금']  = ST['05100']

        self.V['현재잔액']  = my.sv(self.D['일반자금'])
        self.V['일매수금']  = int(self.V['현재잔액'] / self.M['분할횟수'])
        
        self.M['거래코드']  = ' '
        self.M['최장일자']  = ' '

        self.M['현재날수']  = 1
        self.M['최장일수']  = 0   # 최고 오래 지속된 시즌의 일수
        
        self.M['첫날기록']  = False
        self.M['전일종가']  = 0.0
        
        self.set_value(['매수수량','매도수량','구매수량','보유수량'],0)
        self.set_value(['매수금액','매도금액','실현수익','총매수금','평균단가','수익현황','현수익률','평가금액','매수가격','수수료등'],0.0)

        self.set_value(['진최하락'],0)
        self.set_value(['최하일자'],'')

        if  self.chart : # 챠트작성
            
            self.D['TR'] = []
            self.D['c_date'] = []
            self.D['clse_p'] = []
            self.D['avge_r'] = []; self.D['avge_s'] = []; self.D['avge_t'] = []

        # 통계자료
        if  self.stat :

            self.D['totalV'] = []
            self.D['일정익절'] = self.D['일정손절'] = self.D['일회익절'] = self.D['일회손절'] = 0

            self.D['손익통계'] = [[self.D['시작일자'],f"{self.V['현재잔액']:,.2f}",'0.00','0.00',"#F6CECE",'','0.00']]
            self.D['월익통계'] = [[self.D['시작일자'][:7],0.00]]
            self.D['손익저점'] = 100.0
            self.D['저점날자'] = ''

    def nextStep(self) :

        self.D['N_일자'] = self.M['현재날수'] 
        self.D['N_종가'] = self.M['당일종가']
        self.D['N_변동'] = round(self.M['종가변동'],2)
        self.D['N_단계'] = self.V['매수단계']

        if  self.M['첫날기록'] : 

            self.D['N_일자'] = 1 
            self.D['N_일반기초'] = my.ceil(self.V['일매수금']/self.M['당일종가'])
            
            self.D['N_일반매수가'] = round(self.M['당일종가'] * self.M['큰단가치'],2)
            self.D['N_일반매수량'] = self.D['N_일반기초']
            self.D['N_일반매도량'] = 0

            self.D['N_일반매도가'] = 0.0
            self.D['N_일반종대비'] = self.next_percent(self.M['당일종가'],self.D['N_일반매수가'])
            
        else : 
            
            self.D['N_일반기초'] = self.V['기초수량']
           
            self.D['N_일반매수가'] = self.M['매수가격']
            self.D['N_일반평대비'] = self.next_percent(self.V['평균단가'],self.D['N_일반매수가'])
            self.D['N_일반종대비'] = self.next_percent(self.M['당일종가'],self.D['N_일반매수가'])

            self.D['N_일반매수량'] = self.V['구매수량']
            self.D['N_일반매도량'] = self.V['보유수량']
            self.D['N_일반매도가'] = self.M['매도가격']
            self.D['N_일반도평비'] = self.next_percent(self.V['평균단가'],self.D['N_일반매도가'])
            self.D['N_공통종대비'] = self.next_percent(self.M['당일종가'],self.D['N_일반매도가'])

        # formating...
        self.D['N_일반매수가'] = f"{self.D['N_일반매수가']:.2f}"
        self.D['N_일반매도가'] = f"{self.M['매도가격']:.2f}"

    def next_percent(self,a,b) :
        
        if not a : return '0.00'
        return f"{(b/a-1)*100:.2f}"
    
    # ------------------------------------------------------------------------------------------------------------------------------------------
    # 
    # ------------------------------------------------------------------------------------------------------------------------------------------

    def print_backtest(self) :

        tx = {}
        #--------------------------------------------------------
        tx['현재날수'] = self.M['현재날수']; tx['기록시즌'] = self.M['기록시즌']
        tx['기록일자'] = self.M['현재일자'][2:]
        tx['당일종가'] = f"<span class='clsp{self.M['기록시즌']}'>{round(self.M['당일종가'],4):,.2f}</span>"
        clr = "#F6CECE" if self.M['종가변동'] >= 0 else "#CED8F6"
        tx['종가변동'] = f"<span style='color:{clr}'>{self.M['종가변동']:,.2f}</span>"
        #--------------------------------------------------------
        tx['일반진행'] = f"{round(self.V['매도금액'],4):,.2f}" if self.V['매도금액'] else self.V['거래코드']
        tx['일반평균'] = f"{round(self.V['평균단가'],4):,.4f}" if self.V['평균단가'] else ""
        clr = "#F6CECE" if self.V['현수익률'] > 0 else "#CED8F6"
        tx['일반수익'] = f"<span style='color:{clr}'>{round(self.V['수익현황'],4):,.2f}</span>"
        tx['일반익률'] = f"<span style='color:{clr}'>{round(self.V['현수익률'],4):,.2f}</span>"
        tx['일반잔액'] = f"{self.V['현재잔액']:,.2f}"
        #--------------------------------------------------------
        tx['진행상황'] = self.V['진행상황']
            
        self.D['TR'].append(tx)
        
        self.D['clse_p'].append(self.M['당일종가'])
        self.D['c_date'].append(self.M['현재일자'][2:])
        self.D['totalV'].append(round(self.V['현재잔액']+self.V['평가금액'],0))
        

    def get_simResult(self,start='',end='',result=False) :
        
        self.D['종료일자'] = self.DB.one("SELECT max(add0) FROM h_stockHistory_board") if not end else end
        self.D['시작일자'] = my.dayofdate(self.D['종료일자'],delta=-365*2)[0] if not start else start 
        
        self.get_start()
        self.init_value()
        self.simulate()
        if result : self.result()
    
    def get_thisYearResult(self) :

        end   = my.timestamp_to_date(opt=7)
        start = end[:4]+'-01-01'
        self.get_simResult(start,end,result=True) 
        return self.D['R_최종익률']
    
    def do_viewChart(self) :

        self.chart = True
        self.stat  = True
        self.get_start()
        self.init_value()
        self.simulate(printOut=True)
        self.result()
        self.nextStep()

    def put_initCapital(self,V) :
        
        self.D['일반자금'] = f"{V:,.2f}" 
        
    def get_dateList(self,start_date,end_date) :
        
        qry = f"SELECT add0 FROM h_stockHistory_board WHERE add1='SOXL' AND add0 BETWEEN '{start_date}' AND '{end_date}' ORDER BY add0"
        return self.DB.col(qry)

    
    def get_syncData(self,backto='',origin=False) :
        
        s_date = my.timestamp_to_date(opt=7) if not backto else backto
        order = 'add0 ASC' if origin else 'add0 DESC' 
        V_date  = self.DB.one(f"SELECT add0 FROM {self.board} WHERE add0 <= '{s_date}' and sub12='1' ORDER BY {order} LIMIT 1")
        V_money = self.DB.one(f"SELECT add3 FROM {self.board} WHERE add0 <  '{V_date}' and sub12='0' ORDER BY {order} LIMIT 1")
        V_mode  = self.DB.one(f"SELECT sub7 FROM {self.board} WHERE add0 =  '{V_date}'")
        
        return (V_date,float(V_money),float(V_mode))
    
    def get_nextStrategy(self) :
        
        (V_date,V_money,V_mode) = self.get_syncData()
        self.put_initCapital(V_money)
        if V_mode : self.D['가상손실'] = 'on'
        self.get_simResult(V_date)
        self.nextStep()
        return {'buy_p':self.D['N_일반매수가'],'buy_q':self.D['N_일반매수량'],'yx_b': self.D['N_일반종대비'],
                'sel_p':self.D['N_일반매도가'],'sel_q':self.D['N_일반매도량'],'yx_s': self.D['N_공통종대비']}
      

    def do_tacticsLog(self,theDate) :
        
        (V_date,V_money,V_mode) = self.get_syncData(theDate)
        if V_mode : self.D['가상손실'] = 'on'
        self.put_initCapital(V_money)
        self.get_simResult(V_date,theDate)
        

    def get_tacticLog(self,theDate) :
        
        preDate = self.DB.one(f"SELECT max(add0) FROM {self.board} WHERE add0 < '{theDate}'")
        if not preDate : return 
        LD = self.DB.line(f"SELECT * FROM {self.board} WHERE add0='{preDate}'")
        
        LD['add0'] = theDate
        LD['wdate']= LD['mdate']= my.now_timestamp()
   
        LD['add3'] = f"{self.V['현재잔액']:.2f}"
        LD['add4'] = f"{self.V['현재잔액']/(self.V['현재잔액'] + self.V['평가금액']) * 100:.2f}"
        
        LD['add11'] = f"{self.V['매수금액']:.2f}"
        LD['add12'] = f"{self.V['매도금액']:.2f}"
        LD['add5']  = self.V['매수수량'] 
        if self.V['매도금액'] : LD['add5'] = -self.V['매도수량']
        LD['add8']  = f"{self.V['현수익률']:.2f}"
        
        LD['add14'] = self.M['당일종가']
        LD['add15'] = f"{self.V['평가금액']:.2f}"
        LD['add9']  = self.V['보유수량']
        LD['add16'] = f"{self.V['평가금액']/(self.V['현재잔액'] + self.V['평가금액']) * 100:.2f}"
        
        LD['add7']  = f"{self.V['평균단가']:.4f}"
        LD['sub15'] = f"{float(LD['sub15'])+self.V['매도금액']:.2f}"
        LD['sub14'] = f"{float(LD['sub14'])+self.V['매수금액']:.2f}"
        LD['add6']  = f"{self.V['총매수금']:.2f}"
        
        LD['sub5'], LD['sub6'] = self.DB.oneline(f"SELECT add9,add10 FROM h_stockHistory_board WHERE add0='{theDate}'")
        LD['add20'] = self.M['종가변동']
        LD['add18'] = f"{self.V['수익현황']:.2f}"
        
        LD['sub1']  = int(LD['sub1']) + 1 if self.V['매도금액'] else LD['sub1'] 
        LD['sub4']  = self.V['일매수금']
        
        LD['sub12']  = 0 if self.M['첫날기록'] else self.M['현재날수'] - 1 
        
        LD['add17']  = f"{self.V['현재잔액'] + self.V['평가금액']:.2f}"
        LD['sub7']   = LD['sub7'] 
        if  self.V['매도금액'] :
            LD['sub7'] = '0.00' if self.V['실현수익'] else '1.12'
        
        LD['sub29']  = '전량매도' if self.M['첫날기록'] else self.V['진행상황'] 
        LD['sub30']  = f"{self.V['수수료등']:.2f}" if LD['add5'] else '0.00'
        LD['sub31']  = f"{self.V['수수료등'] + float(LD['sub31']):.2f}" if LD['add5'] else LD['sub31']
        if  self.M['현재날수'] -1 == 1 : 
            LD['sub29'] = '첫날매수'
            LD['sub31'] = LD['sub30']

        if  not self.V['보유수량'] and not self.V['매도금액'] : LD['sub31'] = '0.00'
        
        LD['content'] ="<div><p>Written by Auto</p></div>"
        del LD['no']

        self.nextStep()
        LD['sub2']  = self.D['N_일반매수량']
        LD['sub3']  = self.D['N_일반매도량']
        LD['sub18'] = self.D['N_일반기초']
        LD['sub19'] = self.D['N_일반매수가']
        LD['sub20'] = self.D['N_일반매도가']

        return LD
    
    def get_backDateStat(self) :

        sx = {}

        sx['시작일자'] = self.D['시작일자']
        sx['경과일자'] = self.D['R_총경과일']

        sx['최종수익'] = self.D['R_최종수익']
        sx['종수익률'] = self.D['R_최종익률']
        sx['최장기록'] = f"{self.D['최장일수']}<span style='color:gray'>({self.D['최장일자'][2:]})</span>"

        sx['일반최락'] = f"{self.D['MDD1']}<span style='color:gray'>({self.D['MDD_DAY1']})</span>"    if self.D['MDD_DAY1'] else ''
        sx['저점기록'] = f"<b>{self.D['손익저점']}</b><span style='color:gray'>({self.D['저점날자'][2:]})</span>" if self.D['저점날자'] else ''
        
        if float(self.D['MaxDP']) >= float(self.D['손익저점']) : self.D['MaxDP'] = self.D['손익저점']; self.D['MaxDD'] = self.D['시작일자']

        sx['게임횟수'] = f"{self.D['R_총매도수']}({self.D['R_총익절수']}/{self.D['R_총손절수']})"
        sx['게임승률'] = self.D['R_총익승률']
        sx['게임익평'] = self.D['R_익절평균']
        sx['게임손평'] = self.D['R_손절평균']

        return sx

    def do_viewStat(self) :

        self.chart = False
        self.stat  = True
        B = self.get_dateList(self.D['시작일자'],self.D['종료일자'])
        
        self.D['MaxDP'] = 100.0
        self.D['MaxDD'] = ''
        self.D['SR'] = []
        
        for b in B :
            self.get_start(b)
            self.init_value()
            self.simulate()
            self.result()
            self.D['SR'].append(self.get_backDateStat())
            
        self.D['SR'].pop()    

    # ------------------------------------------------------------------------------------------------------------------------------------------
    # 
    # ------------------------------------------------------------------------------------------------------------------------------------------

today = my.kor_loc_date('US/Eastern')[0:10]
weekd = my.dayofdate(today)
V = update_iguide()

ck_holiday = V.DB.exe(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday[0][0] if ck_holiday else ''

skip = (weekd in ['토','일']) or is_holiday

if  skip :
    pass

else :
    V.do_tacticsLog(today)1002 0741
    D = V.get_tacticLog(today)
    qry=V.DB.qry_insert(V.board,D); V.DB.exe(qry)

    V.send_message(f"{today}일 IGUIDE 업데이트 완료")

