from system.core.load import Model
from datetime import datetime,date
import system.core.my_utils as my

class M_backtest_OVERALL(Model) :

# 변동성을 이용한 올타임 전략 V(일반) / R(기회) / S(안정)
 
    def calculate(self)  :
        
        if  self.V['매수수량'] : 
            self.V['일반자금'] -=  self.V['매수금액'];  self.V['보유수량'] += self.V['매수수량'];  self.V['총매수금'] += self.V['매수금액']
            self.V['평균단가']  =  self.V['총매수금'] / self.V['보유수량'] 
            self.V['일반자금'] -=  self.commission(self.V['매수금액'],1)
        
        if  self.R['매수수량'] : 
            self.R['기회자금'] -=  self.R['매수금액'];  self.R['보유수량'] += self.R['매수수량'];  self.R['총매수금'] += self.R['매수금액']
            self.R['평균단가']  =  self.R['총매수금'] / self.R['보유수량'] 
            self.R['기회자금'] -=  self.commission(self.R['매수금액'],1)

        if  self.S['매수수량'] : 
            self.S['안정자금'] -=  self.S['매수금액'];  self.S['보유수량'] += self.S['매수수량'];  self.S['총매수금'] += self.S['매수금액']
            self.S['평균단가']  =  self.S['총매수금'] / self.S['보유수량'] 
            self.S['안정자금'] -=  self.commission(self.S['매수금액'],1)
        
        if  self.S['매도수량'] :
            self.S['실현수익']  = (self.M['당일종가'] - self.S['평균단가']) * self.S['매도수량']
            self.S['보유수량'] -=  self.S['매도수량'];  self.S['안정자금'] += self.S['매도금액']; self.S['총매수금'] = 0.00
            self.S['안정자금'] -=  self.commission(self.S['매도금액'],2)
            self.S['수익현황']  =  self.S['실현수익']
            self.rstCount(self.S['실현수익'],'안')

        if  self.R['매도수량'] :
            self.R['실현수익']  = (self.M['당일종가'] - self.R['평균단가']) * self.R['매도수량']
            self.R['보유수량'] -=  self.R['매도수량'];  self.R['기회자금'] += self.R['매도금액']; self.R['총매수금'] = 0.00
            self.R['기회자금'] -=  self.commission(self.R['매도금액'],2)
            self.R['수익현황']  =  self.R['실현수익'] 
            self.rstCount(self.R['실현수익'],'기')

        if  self.V['매도수량'] :
            self.V['실현수익']  = (self.M['당일종가'] - self.V['평균단가']) * self.V['매도수량']  
            self.V['보유수량'] -=  self.V['매도수량'];  self.V['일반자금'] += self.V['매도금액']; self.V['총매수금'] = 0.00 
            self.V['일반자금'] -=  self.commission(self.V['매도금액'],2)
            self.V['수익현황']  =  self.V['실현수익']
            self.rstCount(self.V['실현수익'],'일')
            
            self.M['첫날기록']  = True
            self.M['매수단계']  = '일반매수'
            self.M['회복전략']  = self.M['손실회수']
            self.rebalance() 
        
        self.V['평가금액'] = self.M['당일종가'] * self.V['보유수량'] 
        self.R['평가금액'] = self.M['당일종가'] * self.R['보유수량'] 
        self.S['평가금액'] = self.M['당일종가'] * self.S['보유수량'] 

        self.V['현수익률']  = (self.M['당일종가']/self.V['평균단가'] -1) * 100  if self.V['평균단가'] else 0.00
        self.R['현수익률']  = (self.M['당일종가']/self.R['평균단가'] -1) * 100  if self.R['평균단가'] else 0.00  
        self.S['현수익률']  = (self.M['당일종가']/self.S['평균단가'] -1) * 100  if self.S['평균단가'] else 0.00
        
        if  not self.V['매도수량'] : 
            self.V['수익현황'] = self.V['평가금액'] - self.V['총매수금']
            self.R['수익현황'] = self.R['평가금액'] - self.R['총매수금']
            self.S['수익현황'] = self.S['평가금액'] - self.S['총매수금']

        self.realMDD()


    def realMDD(self) :

        self.V['실최하락'] = self.V['수익현황'] / (self.V['일반자금'] + self.V['총매수금']) * 100
        self.R['실최하락'] = self.R['수익현황'] / (self.R['기회자금'] + self.R['총매수금']) * 100
        self.S['실최하락'] = self.S['수익현황'] / (self.S['안정자금'] + self.S['총매수금']) * 100

        if self.M['현재날수'] > self.M['최대일수'] : self.M['최대일수'] = self.M['현재날수']; self.M['최대날자'] = self.M['현재일자']
        if self.V['실최하락'] < self.V['진최하락'] : self.V['진최하락'] = self.V['실최하락']; self.V['최하일자'] = self.M['현재일자']
        if self.R['실최하락'] < self.R['진최하락'] : self.R['진최하락'] = self.R['실최하락']; self.R['최하일자'] = self.M['현재일자']
        if self.S['실최하락'] < self.S['진최하락'] : self.S['진최하락'] = self.S['실최하락']; self.S['최하일자'] = self.M['현재일자']

    def rstCount(self,profit,key) :
        if  profit >= 0 : 
            if self.M['회복전략'] : self.D[key+'회익절'] += 1
            else : self.D[key+'정익절'] += 1  
        else : 
            if self.M['회복전략'] : self.D[key+'회손절'] += 1
            else : self.D[key+'정손절'] += 1   

    def commission(self,mm,opt) :
        if  self.M['비용차감'] : 
            fee = int(mm*0.07)/100
            if opt==2 : fee += round(mm*0.0008)/100
            return fee
        
    def rebalance(self)  :
        
        self.V['일매수금'] = int(self.V['일반자금']/self.M['분할횟수']) 
        self.R['일매수금'] = int(self.R['기회자금']/self.M['분할횟수']) 
        self.S['일매수금'] = int(self.S['안정자금']/self.M['분할횟수']) 


    def today_sell(self) :
        
        if  self.M['당일종가'] >= self.M['판매가격'] : 
            self.V['매도수량']  = self.V['보유수량'] 
            self.R['매도수량']  = self.R['보유수량'] 
            self.S['매도수량']  = self.S['보유수량']
            self.M['진행상황']  = '익절매도' 
            self.M['회복전략']  = self.M['손실회수']
            
            if  self.M['당일종가'] < self.V['평균단가'] : 
                self.M['진행상황'] = '손절매도'
                self.M['손실회수'] = True
            else :
                self.M['손실회수'] = False

            self.V['매도금액'] = self.M['당일종가'] * self.V['매도수량']
            self.R['매도금액'] = self.M['당일종가'] * self.R['매도수량']
            self.S['매도금액'] = self.M['당일종가'] * self.S['매도수량']
            #
            self.R['기회가격'] = 0.0;  self.R['기회진행'] = False; self.R['매수금액'] = 0.0; self.R['매수수량'] = 0
            self.S['안정가격'] = 0.0;  self.S['안정진행'] = False; self.S['매수금액'] = 0.0; self.S['매수수량'] = 0
            

    def today_buy(self) :

        if  self.M['당일종가']<= self.M['매수가격'] : 
            self.V['매수수량'] = self.V['구매수량']
            거래코드 = 'L' if self.M['매수단계'] is '매수제한' else 'B'
            self.V['거래코드'] = 거래코드 + str(self.V['매수수량']) if self.V['구매수량'] else ' '
            self.V['매수금액'] = self.V['매수수량'] * self.M['당일종가']
            self.M['진행상황'] = self.M['매수단계']
            
            if  self.M['현재날수'] == 2 and self.M['당일종가'] <= self.M['전일종가'] :
                self.R['거래코드'] = f"R{self.R['기초수량']}"
                self.R['매수수량'] = self.R['기초수량']
                self.R['매수금액'] = self.R['매수수량'] * self.M['당일종가'] 
                
            if  self.R['기회진행'] :
                self.R['매수수량'] = self.R['구매수량'] 
                self.R['매수금액'] = self.R['매수수량'] * self.M['당일종가']   
                self.R['거래코드'] = f"R{self.R['매수수량']}" if self.R['매수수량'] else ' ' 

            if  self.S['안정진행'] :
                self.S['매수수량'] = self.S['구매수량'] 
                self.S['매수금액'] = self.S['매수수량'] * self.M['당일종가']   
                self.S['거래코드'] = f"S{self.S['매수수량']}" if self.S['매수수량'] else ' '
        

        if  not self.R['기회진행'] and self.M['현재날수'] > 2 and self.M['당일종가'] <= min(self.M['매수가격'], self.R['기회가격']) :
            
            매수수량R = self.chance_qty(self.R['기초수량'])
            self.R['거래코드'] = f"R{self.R['기초수량']}/{매수수량R}" 
            self.R['매수수량'] = 매수수량R
            self.R['매수금액'] = self.R['매수수량'] * self.M['당일종가']
            self.R['기회진행'] = True
       
        if  not self.S['안정진행'] and self.M['현재날수'] > 2 and self.M['당일종가'] <= min(self.M['매수가격'], self.S['안정가격']) :
            
            매수수량S = self.chance_qty(self.S['기초수량'])
            self.S['거래코드'] = f"S{self.S['기초수량']}/{매수수량S}" 
            self.S['매수수량'] = 매수수량S
            self.S['매수금액'] = self.S['매수수량'] * self.M['당일종가']
            self.S['안정진행'] = True
    
    def chance_qty(self,basic_qty) :

            찬스수량 = 0    
            day_count = min(self.M['현재날수']+self.M['찬스일가'],6)
            for i in range(0,day_count) : 
                찬스수량 += my.ceil( basic_qty *(i*1.25 + 1))
            return 찬스수량   
        
    def tomorrow_step(self)   :
        
        self.M['매수가격'] = round(self.M['당일종가']*self.M['평단가치'],2)
        self.M['판매가격'] = my.round_up(self.V['평균단가'] * self.M['첫매가치'])
        
        일반수량 = my.ceil(self.V['기초수량'] * (self.M['현재날수']*self.M['비중조절'] + 1))
        기회수량 = 안정수량 = 0

        if  일반수량 * self.M['매수가격'] > self.V['일반자금']   :
            self.M['매수단계'] = '매수제한' 
            
            일반수량 = my.ceil(self.V['기초수량'] * self.M['위매비중'])
            if 일반수량 * self.M['매수가격'] > self.V['일반자금'] : self.M['매수단계'] = '매수중단'; 일반수량 = 0
        
        self.V['구매수량'] = 일반수량  # take_chance 호출 전 결정되어야 함
        
        if  self.R['기회진행'] :
            기회수량 = my.ceil(self.R['기초수량'] * (self.M['현재날수']*self.M['비중조절'] + 1))

            if  기회수량 * self.M['매수가격'] > self.R['기회자금']   : 
                기회수량 = my.ceil(self.R['기초수량'] * self.M['위매비중']) 
                기회수량 = 0 if 기회수량 * self.M['매수가격'] > self.R['기회자금'] else 기회수량
        else : 
            self.R['기회가격'] = self.take_chance('R')

        if  self.S['안정진행'] :
            안정수량 = my.ceil(self.S['기초수량'] * (self.M['현재날수']*self.M['비중조절'] + 1))

            if  안정수량 * self.M['매수가격'] > self.S['안정자금']   : 
                안정수량 = my.ceil(self.S['기초수량'] * self.M['위매비중'])
                안정수량 = 0 if 안정수량 * self.M['매수가격'] > self.S['안정자금'] else 안정수량
        else : 
            self.S['안정가격'] = self.take_chance('S')
        
        내일날수 = self.M['현재날수'] + 1

        if  self.M['매수단계'] in ('매수제한','매수중단') :          self.M['판매가격'] = my.round_up(self.V['평균단가'] * self.M['둘매가치'])
        if  self.M['손실회수'] and 내일날수 <= self.M['매도대기'] :  self.M['판매가격'] = my.round_up(self.V['평균단가'] * self.M['전화위복'])
        if  내일날수 >= self.M['강매시작'] :                        
            self.M['판매가격'] = my.round_up(self.V['평균단가'] * self.M['강매가치'])
        
        if  self.M['매수가격'] >= self.M['판매가격'] : self.M['매수가격'] = self.M['판매가격'] - 0.01 
        
        self.R['구매수량'] = 기회수량
        self.S['구매수량'] = 안정수량
        

    def take_chance(self,opt) :
        H = self.V['보유수량']
        n = self.V['구매수량']
        A = self.V['총매수금']
        if H == 0 : return 0
        if opt == 'R' : p = self.R['기회회복'] if self.M['손실회수'] else self.R['기회시점']
        if opt == 'S' : p = self.S['안정회복'] if self.M['손실회수'] else self.S['안정시점']
        N = H + n
        k = N / (1+p/100)
        return round(A/(k-n),2)
    
    
    def test_it(self) :

        self.init_value()

        for idx,BD in enumerate(self.B) : 
            if BD['add0'] < self.D['시작일자'] : idxx = idx; continue

            self.M['현재일자'] = BD['add0']
            self.M['당일종가'] = float(BD['add3'])
            self.M['종가변동'] = float(BD['add8']) 
            self.M['전일종가'] = float(self.B[idx-1]['add3'])  
            self.V['거래코드'] = ' ' 
            self.R['거래코드'] = ' '
            self.S['거래코드'] = ' '
            self.set_value(['매도수량','매도금액','매수수량','매수금액','수익현황','현수익률'],0)
            
            # BD의 기록은 시작일자 보다 전의 데이타(종가기록 등)에서 시작하고, 당일종가가 전일에 비해 설정(12%)값 이상으로 상승 시 건너뛰기 위함
            if  idx == idxx + 1 or self.M['첫날기록'] : 
                if  self.new_day() : self.tomorrow_step(); self.print_backtest(); continue
                else : self.M['첫날기록'] = True; continue

            self.today_sell()
            self.today_buy()
            self.calculate()
            self.tomorrow_step()
            self.print_backtest()
        # endfor -----------------------------------------------------------------------------------------------------
        self.result()
        self.nextStep()
    
    def set_value(self,key,val) :
        for k in key :
            self.V[k] = val
            self.R[k] = val
            self.S[k] = val


    def result(self) :

        self.D['max_days'] = self.M['최대일수']
        self.D['max_date'] = self.M['최대날자'][2:]
        self.D['MDD1'] = f"{self.V['진최하락']:.2f}"; self.D['MDD_DAY1'] = self.V['최하일자'][2:]
        self.D['MDD2'] = f"{self.R['진최하락']:.2f}"; self.D['MDD_DAY2'] = self.R['최하일자'][2:]
        self.D['MDD3'] = f"{self.S['진최하락']:.2f}"; self.D['MDD_DAY3'] = self.S['최하일자'][2:]
        
        초기자본1 = float(self.D['일반자금'].replace(',','')) 
        최종자본1 = self.V['평가금액'] + self.V['일반자금'] 
        최종수익1 = 최종자본1 - 초기자본1 
        self.D['v_profit'] = round((최종수익1/초기자본1) * 100,2)      
        
        초기자본2 = float(self.D['기회자금'].replace(',',''))
        최종자본2 = self.R['평가금액'] + self.R['기회자금'] 
        최종수익2 = 최종자본2 - 초기자본2 
        self.D['r_profit'] = round((최종수익2/초기자본2) * 100,2)

        초기자본3 = float(self.D['안정자금'].replace(',',''))
        최종자본3 = self.S['평가금액'] + self.S['안정자금'] 
        최종수익3 = 최종자본3 - 초기자본3 
        self.D['s_profit'] = round((최종수익3/초기자본3) * 100,2)
        
        초기자본 = 초기자본1 + 초기자본2 + 초기자본3
        최종자본 = 최종자본1 + 최종자본2 + 최종자본3
        최종수익 = 최종자본 - 초기자본 
        self.D['t_profit'] = round((최종수익/초기자본) * 100,2)
        
        style1 = "<span style='font-weight:bold;color:white'>"
        style2 = "<span style='font-weight:bold;color:#CEF6CE'>"
        style3 = "<span style='font-weight:bold;color:#F6CECE'>"
        self.D['output']  = f"총 {style1}{self.D['days_span']:,}</span>일 "
        self.D['output'] += f"초기 {style1}${초기자본:,.0f}</span> 최종 {style1}${최종자본:,.2f}</span> "
        self.D['output'] += f"수익은 {style2}${최종수익:,.2f}</span> 수익률은 {style3}{self.D['t_profit']:,.2f}( {self.D['v_profit']:,.2f} / {self.D['r_profit']:,.2f} / {self.D['s_profit']:,.2f} ) %</span>"
        
    
    def get_start(self) :

        # 매매전략 가져오기

        # 종가 및 최고가 가져오기
        old_date = my.dayofdate(self.D['시작일자'],-7)[0]
        self.DB.tbl, self.DB.wre, self.DB.odr = ('h_stockHistory_board',f"add1='{self.D['종목코드']}' AND add0 BETWEEN '{old_date}' AND '{self.D['종료일자']}'",'add0')
        self.B = self.DB.get('add0,add3,add8') # 날자, 종가, 증감 

        # 데이타 존재 여부 확인
        self.DB.tbl, self.DB.wre = ("h_stockHistory_board",f"add1='{self.D['종목코드']}'")
        chk_data = self.DB.get_one("min(add0)")
        if chk_data > self.D['시작일자'] : 
            self.D['NOTICE'] = f" {self.D['시작일자']} 에서 {self.D['종료일자']} 까지 분석을 위한 데이타가 부족합니다. 시작 날자를 {chk_data} 이후 3일 뒤로 조정하시기 바랍니다."
            return

        # 기간 계산하기
        self.D['s_day'] = s_day = self.D['시작일자']  ; d0 = date(int(s_day[0:4]),int(s_day[5:7]),int(s_day[8:10]))
        self.D['e_day'] = e_day = self.D['종료일자']  ; d1 = date(int(e_day[0:4]),int(e_day[5:7]),int(e_day[8:10]))
        delta = d1-d0
        self.D['days_span'] = delta.days

    def print_backtest(self) :
        if not self.V['보유수량'] and not self.V['매도수량']: return
        tx = {}
        #--------------------------------------------------------
        tx['현재날수'] = self.M['현재날수']; tx['기록시즌'] = self.M['기록시즌']
        tx['기록일자'] = self.M['현재일자'][2:]
        tx['당일종가'] = f"<span class='clsp{self.M['기록시즌']}'>{round(self.M['당일종가'],4):,.2f}</span>"
        clr = "#F6CECE" if self.M['종가변동'] >= 0 else "#CED8F6"
        tx['종가변동'] = f"<span style='color:{clr}'>{self.M['종가변동']:,.2f}</span>"
        #--------------------------------------------------------
        tx['일반진행'] = f"{round(self.V['매도금액'],4):,.2f}" if self.V['매도금액'] else self.V['거래코드']
        tx['일반평균'] = f"<span class='avgv{self.M['기록시즌']}'>{round(self.V['평균단가'],4):,.4f}</span>" if self.V['평균단가'] else f"<span class='avgv{self.M['기록시즌']}'></span>"
        clr = "#F6CECE" if self.V['현수익률'] > 0 else "#CED8F6"
        tx['일반수익'] = f"<span style='color:{clr}'>{round(self.V['수익현황'],4):,.2f}</span>"
        tx['일반익률'] = f"<span style='color:{clr}'>{round(self.V['현수익률'],4):,.2f}</span>"
        tx['일반잔액'] = f"{self.V['일반자금']:,.2f}"
        #--------------------------------------------------------
        tx['기회진행'] = f"{round(self.R['매도금액'],4):,.2f}" if self.R['매도금액'] else self.R['거래코드']
        tx['기회평균'] = f"<span class='avgr{self.M['기록시즌']}'>{round(self.R['평균단가'],4):,.4f}</span>" if self.R['평균단가'] else f"<span class='avgr{self.M['기록시즌']}'></span>"
        clr = "#F6CECE" if self.R['현수익률'] > 0 else "#CED8F6"
        tx['기회수익'] = f"<span style='color:{clr}'>{round(self.R['수익현황'],4):,.2f}</span>" 
        tx['기회익률'] = f"<span style='color:{clr}'>{round(self.R['현수익률'],4):,.2f}</span>" 
        tx['기회잔액'] = f"{self.R['기회자금']:,.2f}"
        #--------------------------------------------------------
        tx['안정진행'] = f"{round(self.S['매도금액'],4):,.2f}" if self.S['매도금액'] else self.S['거래코드']
        tx['안정평균'] = f"<span class='avgs{self.M['기록시즌']}'>{round(self.S['평균단가'],4):,.4f}</span>" if self.S['평균단가'] else f"<span class='avgs{self.M['기록시즌']}'></span>"
        clr = "#F6CECE" if self.S['현수익률'] > 0 else "#CED8F6"
        tx['안정수익'] = f"<span style='color:{clr}'>{round(self.S['수익현황'],4):,.2f}</span>" 
        tx['안정익률'] = f"<span style='color:{clr}'>{round(self.S['현수익률'],4):,.2f}</span>"
        tx['안정잔액'] = f"{self.S['안정자금']:,.2f}"
        #--------------------------------------------------------
        tx['진행상황'] = self.M['진행상황'] 
        
        self.D['TR'].append(tx)
        
        # 챠트 기록용
        self.D['clse_p'].append(self.M['당일종가'])

        if avg_v := round(self.V['평균단가'],2) : self.D['avge_v'].append(avg_v)
        else : self.D['avge_v'].append('null')
        if avg_r := round(self.R['평균단가'],2) : self.D['avge_r'].append(avg_r)
        else : self.D['avge_r'].append('null')
        if avg_s := round(self.S['평균단가'],2) : self.D['avge_s'].append(avg_s)
        else : self.D['avge_s'].append('null')        
        
        self.D['c_date'].append(self.M['현재일자'][2:])

        self.D['eval_v'].append(round(self.V['일반자금']+self.V['평가금액'],0))
        self.D['eval_r'].append(round(self.R['기회자금']+self.R['평가금액'],0))
        self.D['eval_s'].append(round(self.S['안정자금']+self.S['평가금액'],0))
        
        self.M['현재날수'] +=1


    def init_value(self) :
        self.V = {}
        self.R = {}
        self.S = {}
        
        ST = self.DB.parameters_dict('매매전략/VRS')
        
        self.M['비중조절']  = ST['025']  # 매매일수 에 따른 구매수량 가중치(1.25)
        self.M['평단가치']  = ST['003']  # 매수시 가중치(1.022)
        self.M['큰단가치']  = ST['002']  # 첫날매수 시 가중치(1.12)
        self.M['첫매가치']  = ST['004']  # 일반매도 시 이율(1.022) 
        self.M['둘매가치']  = ST['005']  # 매수제한 시 이율(0.939) 
        self.M['강매시작']  = ST['008']  # 강매시작 일(24) 
        self.M['강매가치']  = ST['007']  # 손절가 범위(0.7)
        self.M['위매비중']  = ST['010']  # 매수제한 시 매수범위 기본수량의 (3)
        self.M['매도대기']  = ST['006']  # 매도대기(18)
        self.M['전화위복']  = ST['009']  # 손절 이후 매도 이율(1.12)
        self.M['분할횟수']  = ST['001']  # 분할 횟수
        self.M['찬스일가']  = ST['026']  # V,R 전략 시 찬스 수량 계산 가중일
        
        self.M['손실회수']  = False  
        self.M['회복전략']  = False      # 현재 진행 중인 상황이 손실회수 상태인지 아닌지를 구분( for 통계정보 )
        self.M['매수단계']  = '일반매수'
        self.M['비용차감']  = True # 수수료 계산날수 초과 후 강매선택
        self.M['기록시즌']  = 0

        
        self.V['일반자금']  = float(self.D['일반자금'].replace(',',''))
        self.R['기회자금']  = float(self.D['기회자금'].replace(',',''))
        self.S['안정자금']  = float(self.D['안정자금'].replace(',',''))
        
        self.V['일매수금']  = int(self.V['일반자금'] / self.M['분할횟수'])
        self.R['일매수금']  = int(self.R['기회자금'] / self.M['분할횟수'])
        self.S['일매수금']  = int(self.S['안정자금'] / self.M['분할횟수'])
        
        self.M['거래코드']  = ' '
        self.M['최대날자']  = ' '

        self.M['현재날수']  = 1
        self.M['최대일수']  = 0   # 최고 오래 지속된 시즌의 일수
        
        self.V['진최하락']  = 0   # 최고 MDD
        self.R['진최하락']  = 0
        self.S['진최하락']  = 0

        self.M['첫날기록']  = False
        self.R['기회진행']  = False 
        self.R['기회시점']  = float(self.D['기회시점']) 
        self.R['기회회복']  = float(self.D['기회회복']) 
        self.S['안정진행']  = False 
        self.S['안정시점']  = float(self.D['안정시점']) 
        self.S['안정회복']  = float(self.D['안정회복']) 
        self.M['전일종가']  = 0.0
        
        self.V['매수수량']  = 0;   self.V['매도수량']  = 0; self.V['매도금액'] = 0.0;  self.V['매수금액'] = 0.0 
        self.V['실현수익']  = 0.0; self.V['구매수량']  = 0; self.V['보유수량'] = 0;    self.V['총매수금'] = 0.0
        self.R['매수수량']  = 0;   self.R['매도수량']  = 0; self.R['매도금액'] = 0.0;  self.R['매수금액'] = 0.0 
        self.R['실현수익']  = 0.0; self.R['구매수량']  = 0; self.R['보유수량'] = 0;    self.R['총매수금'] = 0.0
        self.S['매수수량']  = 0;   self.S['매도수량']  = 0; self.S['매도금액'] = 0.0;  self.S['매수금액'] = 0.0 
        self.S['실현수익']  = 0.0; self.S['구매수량']  = 0; self.S['보유수량'] = 0;    self.S['총매수금'] = 0.0
        
        self.V['최하일자']  = ''
        self.R['최하일자']  = ''
        self.S['최하일자']  = ''
        
        self.R['평균단가']  = 0.0; self.R['수익현황']  = 0.0; self.R['현수익률'] = 0.0; self.R['평가금액'] = 0.0; self.R['기회가격'] = 0.0
        self.S['평균단가']  = 0.0; self.S['수익현황']  = 0.0; self.S['현수익률'] = 0.0; self.S['평가금액'] = 0.0; self.S['안정가격'] = 0.0

        self.D['TR'] = []

        # 챠트작성
        self.D['c_date'] = []
        self.D['clse_p'] = []
        self.D['avge_v'] = []; self.D['avge_r'] = []; self.D['avge_s'] = []
        self.D['eval_v'] = []; self.D['eval_r'] = []; self.D['eval_s'] = []
        self.D['일반횟수'] = 0
        self.D['전략횟수'] = 0
        self.D['기회전량'] = 0
        self.D['기회전략'] = 0
        # 결과작성
        self.D['일정익절'] = 0; self.D['기정익절'] = 0; self.D['안정익절'] = 0
        self.D['일정손절'] = 0; self.D['기정손절'] = 0; self.D['안정손절'] = 0
        self.D['일회익절'] = 0; self.D['기회익절'] = 0; self.D['안회익절'] = 0
        self.D['일회손절'] = 0; self.D['기회손절'] = 0; self.D['안회손절'] = 0
        
    def new_day(self) :

        self.set_value(['매도수량','매도금액','매수수량','매수금액','수익현황','현수익률','평균단가'],0)
            
        if  self.M['당일종가'] <  round(self.M['전일종가'] * self.M['큰단가치'],2) :
            
            self.M['기록시즌'] += 1
            self.M['현재날수'] = 1
            self.V['평균단가']  = self.M['당일종가']
            
            self.V['기초수량']  = my.ceil(self.V['일매수금']/self.M['전일종가'])
            self.R['기초수량']  = my.ceil(self.R['일매수금']/self.M['전일종가'])
            self.S['기초수량']  = my.ceil(self.S['일매수금']/self.M['전일종가'])
            
            self.V['매수수량']  = self.V['기초수량']
            self.V['수익현황']  = self.V['현수익률'] = 0.0
            self.V['보유수량']  = self.V['매수수량']
            self.V['매수금액']  = self.M['당일종가'] * self.V['매수수량'] 
            self.V['총매수금']  = self.V['평가금액'] = self.V['매수금액']
            self.V['일반자금'] -= self.V['매수금액']
            
            self.M['진행상황']  = '첫날매수'
            self.M['첫날기록']  = False
            self.V['거래코드']  = f"S{self.V['매수수량']}" 
            self.M['매수단계'] = '일반매수'

            if  self.M['비용차감'] : self.V['일반자금'] -=  self.commission(self.V['매수금액'],1)
 
            return True

        else : 
            return False


    def nextStep(self) :
        self.M['전일종가'] = self.M['당일종가']

        self.D['next_일자'] = self.M['현재날수'] 
        self.D['next_종가'] = self.M['전일종가']
        self.D['next_변동'] = round(self.M['종가변동'],2)

        self.D['next_단계'] = self.M['매수단계']
        self.D['next_일반기초'] = self.V['기초수량']
        self.D['next_기회기초'] = self.R['기초수량']
        self.D['next_안정기초'] = self.S['기초수량']
        
        self.D['next_일반매수가'] = round(self.M['매수가격'],2)
        self.D['next_기회매수가'] = self.R['기회가격'] if self.R['기회가격'] and not self.R['기회진행'] else round(self.M['매수가격'],2)
        if self.M['현재날수'] == 2 : self.D['next_기회매수가'] = self.M['전일종가']
        self.D['next_안정매수가'] = self.S['안정가격'] if self.S['안정가격'] and not self.S['안정진행'] else round(self.M['매수가격'],2)
        
        self.D['next_일매변동'] = round((self.D['next_일반매수가']/self.M['전일종가']- 1)*100,1)
        self.D['next_기매변동'] = round((self.D['next_기회매수가']/self.M['전일종가']- 1)*100,1)
        self.D['next_안매변동'] = round((self.D['next_안정매수가']/self.M['전일종가']- 1)*100,1)
        
        self.D['next_일반매수량'] = self.V['구매수량'] 
        
        self.D['next_기회매수량'] = 0
        self.D['next_안정매수량'] = 0
        
        if self.R['기회진행'] : self.D['next_기회매수량'] = self.R['구매수량']
        else :
             if   self.M['현재날수'] == 2 : self.D['next_기회매수량'] = self.R['기초수량'] 
             elif self.M['현재날수']  > 2 : self.D['next_기회매수량'] = self.chance_qty(0)
        
        if   self.S['안정진행'] : self.D['next_안정매수량'] = self.S['구매수량']
        elif self.M['현재날수'] > 2 :  self.D['next_안정매수량'] = self.chance_qty(1) 
        
        self.D['next_일반매도량'] = self.V['보유수량']
        self.D['next_기회매도량'] = self.R['보유수량']
        self.D['next_안정매도량'] = self.S['보유수량']
        
        self.D['next_일반매도가'] = self.D['next_기회매도가'] = self.D['next_안정매도가'] =  self.M['판매가격']
        
        if  self.M['첫날기록'] :
            self.rebalance()
            self.D['next_일자'] = 1
            self.D['next_단계'] = '첫날매수'
            
            V_qty  = my.ceil(self.V['일매수금']/self.M['당일종가'])
            R_qty  = my.ceil(self.R['일매수금']/self.M['당일종가'])
            S_qty  = my.ceil(self.S['일매수금']/self.M['당일종가'])
            
            self.D['next_일반기초'] = V_qty
            self.D['next_기회기초'] = R_qty
            self.D['next_안정기초'] = S_qty
            
            self.D['next_일반매수가'] = round(self.M['전일종가'] * self.M['큰단가치'],2)
            self.D['next_기회매수가'] = self.D['next_안정매수가'] = 0.0
            
            self.D['next_일반매수량'] = V_qty
            self.D['next_기회매수량'] = self.D['next_안정매수량'] = 0
            
            self.D['next_일반매도량'] = self.D['next_기회매도량'] = self.D['next_안정매도량'] = 0 
            self.D['next_일반매도가'] = self.D['next_기회매도가'] = self.D['next_안정매도가'] = 0.0

