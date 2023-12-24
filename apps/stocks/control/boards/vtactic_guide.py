from system.core.load import Control
import system.core.my_utils as my

class Vtactic_guide(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')
        self.bid   = self.parm[0]
        self.board = 'h_'+self.bid+'_board'
    
# -----------------------------------------------------------------------------------------------------------------------
# Initiate TACTIC (calller : Vtactic.html)
# -----------------------------------------------------------------------------------------------------------------------

    def initiate_Rtactic(self) :
        pass
    
# -----------------------------------------------------------------------------------------------------------------------
# Basic qty : Recalculate the basic quantity
# -----------------------------------------------------------------------------------------------------------------------
    def basic_qty(self) :
        self.Q = {}
        theDay  = self.D['post']['theDay']
        Balance = my.sv(self.D['post']['Balance']) 
        
        일매수금 = int(int(Balance*2/3)/22)
        bprice = self.DB.one(f"SELECT add14 FROM {self.guide} WHERE sub12='0' and add0 <= '{theDay}' ORDER BY add0 DESC LIMIT 1")
        기초수량 = my.ceil(일매수금/float(bprice))        

        self.Q['sub4'] = 일매수금
        self.Q['sub18'] = 기초수량
        
        return self.json(self.Q)
# -----------------------------------------------------------------------------------------------------------------------
# OneWrite TACTIC
# -----------------------------------------------------------------------------------------------------------------------

    def oneWrite_Vtactic(self) :
        
        self.D['prev_date'] = self.DB.one(f"SELECT max(add0) FROM h_{self.bid}_board")
        
        if not self.D['prev_date'] :
            self.set_message("초기 데이타가 존재하지 않습니다")
            return self.moveto(f"board/list/{self.bid}")
            
        if  self.D['prev_date'] :
            self.D['today'] = self.DB.one(f"SELECT min(add0) FROM h_stockHistory_board WHERE add0 > '{self.D['prev_date']}'")
            
        if self.D['today'] :

            self.init_value()
            self.check_sell()
            self.check_buy()
            self.calculate()

            self.tomorrow_sell()
            self.tomorrow_buy()
            self.update_value()
            return self.moveto(f"board/list/{self.bid}")
        else :
            self.set_message("기록을 모두 완료하였습니다")
            return self.moveto(f"board/list/{self.bid}")
        
    def tomorrow_sell(self) :

        if  self.M['경과일수'] ==  0 :
            self.M['전매도량']  =  0
            self.M['전매도가']  =  self.M['당일종가']
            return

        매수단가 = round(self.M['당일종가'] * self.M['평단가치'],2)
        매수수량 = my.ceil(self.M['기초수량'] * (self.M['경과일수']*self.D['비중조절'] + 1))
        매도단가 = my.round_up(self.M['평균단가'] * self.M['첫매가치'])  if self.M['평균단가'] else self.M['당일종가']

        if (매수수량 * 매수단가) > self.M['현재잔액']  :
            매도단가 = my.round_up(self.M['평균단가']*self.M['둘매가치'])
        if self.M['회복전략'] and self.M['경과일수'] +1 <= self.M['회복기한'] : 매도단가 = my.round_up(self.M['평균단가']* (1+float(self.M['회복전략'])/100))

        if self.M['경과일수']+1 >= self.M['강매시작'] : 매도단가 = my.round_up(self.M['평균단가']*self.M['강매가치'])

        self.M['전매도량'] = self.M['보유수량']
        self.M['전매도가'] = round(매도단가,2)


    def tomorrow_buy(self)  :

        if  self.M['경과일수'] == 0 :
            self.M['기초수량'] = self.M['전매수량'] = my.ceil(self.M['일매수금']/self.M['당일종가'])
            self.M['전매수가'] = round(self.M['당일종가'] * self.M['큰단가치'],2)
            return

        매수단가 = round(self.M['당일종가'] * self.M['평단가치'],2)
        매수수량 = my.ceil(self.M['기초수량'] * (self.M['경과일수']*self.D['비중조절'] + 1))

        if  매수수량 * 매수단가 > self.M['현재잔액']  :
            매수수량 = self.M['기초수량'] * self.M['위매비중']
            self.M['진행상황'] = '매수제한'
        if  매수수량 * 매수단가 > self.M['현재잔액'] :
            매수수량 = 0
            self.M['진행상황'] = '매수금지'

        self.M['전매수량'] = 매수수량
        self.M['전매수가'] = round(매수단가,2)


    def commission(self,mm,opt) :
        if  opt==1 :  fee = int(mm*0.07)/100
        if  opt==2 :
            m1 = int(mm*0.07)/100
            m2=round(mm*0.0008)/100
            fee = m1+m2

        self.M['수수료등']  = fee
        self.M['현재잔액'] -= fee

    def rebalance(self)  :
        가용잔액 = int(self.M['현재잔액'] * 2/3)
        self.M['일매수금'] = int(가용잔액/self.M['분할횟수'])
        self.M['기초수량'] = my.ceil(self.M['일매수금']/float(self.M['당일종가']))


    def calculate(self)  :

        매도가격 = self.M['당일종가']
        매수가격 = self.M['당일종가']

        if self.M['보유수량']  : self.M['경과일수'] +=1
        
        if  self.M['매도수량'] :
            self.M['매도금액'] = 매도가격 * self.M['매도수량']
            self.M['변동수량'] = -self.M['매도수량']
            self.M['현재잔액'] += self.M['매도금액']
            self.M['진행상황'] = '전량매도'
            수익금액 = self.M['매도금액'] - self.M['현매수금']
            self.M['회복전략'] = 0 if 수익금액 > 0 else self.S['add22']
            self.M['현재손익'] = f"{수익금액:.2f}"
            self.M['경과일수'] = 0
            self.M['시즌'] += 1
            self.commission(self.M['매도금액'],2)

            # 리밸런싱
            self.rebalance()

        if  self.M['매수수량'] :
            self.M['매수금액']  = 매수가격 * self.M['매수수량']
            self.M['변동수량']  = self.M['매수수량']
            self.M['보유수량'] += self.M['매수수량']
            self.M['평균단가']  = (self.M['현매수금'] + self.M['매수금액']) / self.M['보유수량']
            self.commission(self.M['매수금액'],1)

            self.M['현재잔액'] -=  self.M['매수금액']
            self.M['진행상황'] = '일반매수'

        if  not self.M['경과일수'] and self.M['매수수량'] :
            self.M['경과일수'] = 1
            self.M['진행상황'] = '첫날매수'
        if  not self.M['보유수량'] : self.M['진행상황'] = '매수대기'

    def check_sell(self) :
        if  not self.M['경과일수'] : return
        if  self.M['당일종가'] >= float(self.M['LD']['sub20']) :
            self.M['매도수량']  = int(self.M['LD']['sub3'])

    def check_buy(self) :
        if  not self.M['경과일수'] :
            if  self.M['당일종가'] <= float(self.M['LD']['sub19']) :
                self.M['매수수량']  = self.M['기초수량'] = my.ceil(self.M['일매수금']/self.M['전일종가'])  # 첫날에만 기초수량 재산정
        else :
            if  self.M['당일종가'] <= float(self.M['LD']['sub19']) : self.M['매수수량']  = int(self.M['LD']['sub2'])



    def init_value(self) :
        self.M = {}
        self.M['진행일자'] = self.D['today']
        self.DB.tbl = f"h_{self.bid}_board"
        self.DB.wre = f"add0='{self.D['prev_date']}'"
        LD = self.M['LD'] = self.DB.get_line('*')
        self.M['현재잔액'] = float(LD['add3'])
                
        # 종가구하기
        self.DB.clear()
        self.DB.tbl = 'h_stockHistory_board'
        self.DB.wre = f"add0='{self.M['진행일자']}' and add1='SOXL'"
        self.M['당일종가'] = float(self.DB.get_one('add3'))
        self.M['종가변동'] = float(self.DB.get_one('add8'))
        self.M['전일종가'] = float(self.M['LD']['add14'])
        self.M['연속상승'] = self.DB.get_one('add9')
        self.M['연속하락'] = self.DB.get_one('add10')

        # 매매전략 가져오기
        self.M['매매전략'] = 'VOLATILITY'
        self.DB.tbl, self.DB.wre = ('h_stock_strategy_board',f"add0='{self.M['매매전략']}'")
        self.S = self.DB.get_line('add2,add3,add4,add5,add9,add10,add11,add17,add18,add22,add25')
        self.M['분할횟수']  = int(self.S['add2'])
        self.D['비중조절']  = 1 + float(self.S['add3'])/100   # 매매일수 에 따른 구매수량 가중치
        self.M['평단가치']  = 1 + float(self.S['add4'])/100   # 일반매수 구매가 범위
        self.M['큰단가치']  = 1 + float(self.S['add5'])/100   # 매수첫날 구매가 범위
        self.M['첫매가치']  = 1 + float(self.S['add9'])/100
        self.M['둘매가치']  = 1 + float(self.S['add10'])/100
        self.M['강매시작']  = int(self.S['add17'])
        self.M['강매가치']  = 1 + float(self.S['add18'])/100
        self.M['위매비중']  = int(self.S['add25'])
        self.M['회복기한']  = int(self.S['add11'])

        # 매수 매도 초기화
        self.M['매수금액']=0.0
        self.M['매도금액']=0.0
        self.M['변동수량'] = 0
        self.M['매수수량'] = 0
        self.M['매도수량'] = 0
        self.M['전매도량'] = 0
        self.M['전매도가'] = 0.0
        self.M['현재손익'] = 0.0
        self.M['수수료등'] = 0.0

        self.M['시즌'] = int(LD['sub1'])
        self.M['평균단가'] = float(LD['add7'])
        self.M['일매수금'] = int(LD['sub4'])
        self.M['경과일수'] = int(LD['sub12'])
        self.M['매매현황'] = ''
        self.M['진행상황'] = '매도대기'
        self.M['보유수량'] = int(LD['add9'])
        self.M['현매수금'] = float(LD['add6'])
        self.M['현재잔액'] = float(LD['add3'])
        self.M['진행상황'] = '매도대기'
        self.M['기초수량'] = int(LD['sub18'])
        self.M['회복전략'] = float(LD['sub7'])
        
    def update_value(self) :
        U = self.M['LD']
        del U['no']
        U['wdate']   = my.now_timestamp()
        U['mdate']   = U['wdate']
        U['add0']    = self.M['진행일자']

        U['add14']   = self.M['당일종가']
        U['sub5']    = self.M['연속상승']
        U['sub6']    = self.M['연속하락']
        U['sub12']   = self.M['경과일수']
        U['sub18']   = self.M['기초수량']

        U['add5']   = self.M['변동수량']
        U['add9']  = int(U['add9']) + self.M['변동수량']

        U['add11']  = round(self.M['매수금액'],2)
        U['add12']  = round(self.M['매도금액'],2)
        if  U['add11'] :
            U['sub14'] = float(U['sub14']) + U['add11'] #매수누적
            U['add6']  = float(U['add6'])  + U['add11'] #현매수금
            U['add7']  = round(U['add6']/U['add9'],4) #평균단가

        if  U['add12'] :
            U['sub15'] = float(U['sub15']) + U['add12'] #매도누적
            U['add8']  = round((U['add12'] / float(U['add6']) - 1) * 100,2)
            U['add6'] = 0.00 #현매수금
            U['add7'] = 0.00 #평균단가
            U['add18'] = self.M['현재손익']
            U['sub1']  = self.M['시즌']
            U['sub4']  = self.M['일매수금']
            U['sub18'] = my.ceil(self.M['일매수금'] / self.M['당일종가'])
        else :
            U['add8'] = '0.00'

        if U['add7'] and float(U['add7']) : U['add8'] = round((self.M['당일종가'] / float(U['add7']) - 1) * 100,2)  # 현수익률 if 평균단가 != 0

        U['add1']   = '0.00'
        U['add2']   = '0.00'
        U['add3']   = self.M['현재잔액'] #현금합계
        U['add15']  = int(U['add9']) * self.M['당일종가'] #레버가치

        if  U['add12'] :
            U['add18'] = self.M['현재손익']
        else :
            U['add18']  = round(U['add15']-float(U['add6']),2) if U['add9'] else 0 # 잔량 존재 시 현재수익 계산

        U['add17']  = U['add3'] + U['add15']  #Total Value

        U['add4']   = round(U['add3']  / U['add17'] * 100,2)
        U['add16']  = round(U['add15'] / U['add17'] * 100,2)

        if self.M['경과일수'] !=0 and self.M['전매수가'] >= self.M['전매도가'] : self.M['전매수가'] = self.M['전매도가'] - 0.01
        U['sub2']   = self.M['전매수량']
        U['sub19']  = self.M['전매수가']
        U['sub3']   = self.M['전매도량']
        if self.M['전매도가'] <= self.M['전매수가'] : self.M['전매도가'] = self.M['전매수가'] + 0.01 # 첫날에 해당
        U['sub20']  = self.M['전매도가']
        U['sub29']  = self.M['진행상황']
        U['sub7']   = self.M['회복전략']
        U['sub30']  = self.M['수수료등']
        U['sub31'] = float(U['sub31']) + self.M['수수료등'] if self.M['경과일수'] != 1 else self.M['수수료등'] # 누적수수료
        U['content'] = "<div><p>Written by Auto</p></div>"

    # Formatting
        U['add3']   = f"{U['add3']:.2f}"
        U['add6']   = f"{float(U['add6']):.2f}"
        U['add7']   = f"{float(U['add7']):.4f}"
        U['add8']   = f"{float(U['add8']):.2f}"
        U['add11']  = f"{U['add11']:.2f}"
        U['add15']  = f"{U['add15']:.2f}"
        U['add16']  = f"{U['add16']:.2f}"
        U['add17']  = f"{U['add17']:.2f}"
        U['add20']  = f"{self.M['종가변동']:.2f}"

        U['sub7']   = f"{float(U['sub7']):.1f}"
        U['sub14']  = f"{float(U['sub14']):.2f}"
        U['sub19']  = f"{U['sub19']:.2f}"
        U['sub30']  = f"{U['sub30']:.2f}"


        U.update({k:'' for k,v in U.items() if v == None})

        qry=self.DB.qry_insert(self.board,U)
        self.DB.exe(qry)

