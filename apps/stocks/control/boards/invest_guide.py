from system.core.load import Control
import system.core.my_utils as my

class Invest_guide(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')
        self.bid   = self.parm[0]
        try : self.snd   =  self.parm[1]
        except IndexError : self.snd   = None
        self.board = 'h_'+self.bid+'_board'
        self.target = self.DB.one(f"SELECT extra1 FROM h_board_config WHERE bid='{self.bid}'")
    
    def emptyPick(self) :
        pickDate = self.parm[1]
        qry = f"DELETE FROM {self.board} WHERE add0 >= '{pickDate}'"
        self.DB.exe(qry)
        return self.moveto('board/list/'+self.bid)
    
    def insertPick(self) :
        pickDate = self.parm[1]
        self.DB.tbl, self.DB.wre = ('h_INVEST_board',f"add0='{pickDate}'")

        line = self.DB.get_line("*")
        del line['no']
        line['content'] = "<div><p>Copied by Auto</p></div>"
        for x in line :
            if line[x] == None : line[x] = ''

        qry=self.DB.qry_insert(self.board,line)
        self.DB.exe(qry)
        
        return self.moveto('board/list/'+self.bid)
    
    def oneWrite(self) :
        self.D['prev_date'] = self.DB.one(f"SELECT max(add0) FROM h_{self.bid}_board")
        if  self.D['prev_date'] :
            self.D['today'] = self.DB.one(f"SELECT min(add0) FROM h_stockHistory_board WHERE add0 > '{self.D['prev_date']}'")
        
        if self.D['today'] : 

            self.init_value()
            # 매도상황 검토
            self.today_sell()
            # 매수상황 검토
            self.today_buy()
            self.calculate()

            # 매도전략
            self.tomorrow_sell()
            # 매수전략
            self.tomorrow_buy()
            self.update_value()
        
        else :
            self.set_message(f"{self.D['prev_date']} 이후 업데이트된 정보가 없습니다")

        return self.moveto('board/list/'+self.bid)


# -----------------------------------------------------------------------------------------------------------------------
# From Auto Input 
# -----------------------------------------------------------------------------------------------------------------------
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
            U['add20'] = self.M['추가자금']

        if  U['add12'] : 
            U['sub15'] = float(U['sub15']) + U['add12'] #매도누적
            U['add8']  = round((U['add12'] / float(U['add6']) - 1) * 100,2)
            U['add6'] = 0.00 #현매수금 
            U['add7'] = 0.00 #평균단가 
            U['add18'] = self.M['현재손익']
            U['sub1']  = self.M['시즌']
            U['sub4']  = self.M['일매수금']
            U['sub18'] = my.ceil(self.M['일매수금'] / self.M['당일종가'])
            U['add20'] = self.M['추가자금']
        else : 
            U['add8'] = '0.00'

        if U['add7'] and float(U['add7']) : U['add8'] = round((self.M['당일종가'] / float(U['add7']) - 1) * 100,2)  # 현수익률 if 평균단가 != 0
        
        U['add19'] = self.M['가용잔액']
        
        U['add1']   = '0.00'
        U['add2']   = '0.00'
        U['add3']   = self.M['현재잔액'] + U['add12'] - U['add11'] #현금합계
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
        U['sub20']  = self.M['전매도가'] 
        if U['sub20'] <= U['sub19'] :  U['sub20'] = U['sub19'] + 0.01
        U['sub29']  = self.M['진행상황']
        U['sub7']   = self.M['회복전략'] 
        U['sub30']  = self.M['수수료등']
        U['sub31'] = float(U['sub31']) + self.M['수수료등'] if self.M['경과일수'] != 1 else self.M['수수료등'] # 누적수수료
        U['sub28'] = round((U['add17'] / float(U['sub27']) - 1) * 100,2); # 현수익률
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
        U['add19']  = f"{U['add19']:.2f}"
        U['add20']  = f"{float(U['add20']):.2f}"

        U['sub7']   = f"{float(U['sub7']):.1f}"
        U['sub19']  = f"{U['sub19']:.2f}"
        U['sub30']  = f"{U['sub30']:.2f}"

        if  self.snd == 'chance' : 
            U['sub19'] = self.DB.one(f"SELECT sub19 FROM h_{self.target}_board WHERE add0 = '{self.M['진행일자']}'")
            U['sub20'] = self.DB.one(f"SELECT sub20 FROM h_{self.target}_board WHERE add0 = '{self.M['진행일자']}'")

        U.update({k:'' for k,v in U.items() if v == None})

        qry=self.DB.qry_insert(self.board,U)
        self.DB.exe(qry)


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
        self.DB.wre = f"add0='{self.M['진행일자']}' and add1='SOXL'"; 
        self.M['당일종가'] = float(self.DB.get_one('add3'))
        self.M['전일종가'] = float(self.M['LD']['add14'])
        self.M['연속상승'] = self.DB.get_one('add9')
        self.M['연속하락'] = self.DB.get_one('add10')
        
        # 매매전략 가져오기
        self.M['매매전략'] = 'VICTORY'
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
        self.M['가용잔액'] = float(LD['add19'])
        self.M['추가자금'] = float(LD['add20'])
        self.M['진행상황'] = '매도대기'
        self.M['기초수량'] = int(LD['sub18'])
        self.M['회복전략'] = float(LD['sub7'])

    def calculate(self)  :

        매도가격 = self.M['당일종가']
        매수가격 = self.M['당일종가']

        if self.M['보유수량']  : self.M['경과일수'] +=1

        if  self.M['매도수량'] :
            self.M['매도금액'] = 매도가격 * self.M['매도수량']
            self.M['변동수량'] = -self.M['매도수량'] 
            self.M['진행상황'] = '전량매도' 
            수익금액 = self.M['매도금액'] - self.M['현매수금']
            self.M['회복전략'] = 0 if 수익금액 > 0 else self.S['add22']
            self.M['현재손익'] = f"{수익금액:.2f}"
            self.M['경과일수'] = 0
            self.M['시즌'] += 1
            self.M['기초수량'] = 0   
            self.commission(self.M['매도금액'],2)
   
            # 리밸런싱
            self.rebalance()

        if  self.M['매수수량'] :
            self.M['매수금액']  = 매수가격 * self.M['매수수량']
            self.M['변동수량']  = self.M['매수수량']
            self.M['보유수량'] += self.M['매수수량']
            self.M['평균단가']  = (self.M['현매수금'] + self.M['매수금액']) / self.M['보유수량'] 
            self.commission(self.M['매수금액'],1)

            self.M['가용잔액'] -=  self.M['매수금액']
            if  self.M['가용잔액'] < 0 : 
                self.M['추가자금'] += self.M['가용잔액']
                self.M['가용잔액'] = 0
                
            self.M['진행상황'] = '일반매수'

        if  not self.M['경과일수'] and self.M['매수수량'] : 
            self.M['경과일수'] = 1
            self.M['진행상황'] = '첫날매수'
        if  not self.M['보유수량'] : self.M['진행상황'] = '매수대기'

    def rebalance(self)  :
        total = self.M['매도금액'] + self.M['가용잔액'] + self.M['추가자금']
        self.M['가용잔액'] = int((total * 2)/3)
        self.M['추가자금'] = total - self.M['가용잔액']
        self.M['일매수금'] = int(self.M['가용잔액']/self.M['분할횟수']) 

    def tomorrow_sell(self) :

        if  self.M['경과일수'] ==  0 :
            self.M['전매도량']  =  0
            self.M['전매도가']  =  self.M['당일종가']
            return
        매수단가 = round(self.M['당일종가'] * self.M['평단가치'],2)
        매수수량 = my.ceil(self.M['기초수량'] * (self.M['경과일수']*self.D['비중조절'] + 1))
        매도단가 = my.round_up(self.M['평균단가'] * self.M['첫매가치'])  if self.M['평균단가'] else self.M['당일종가']

        if (매수수량 * 매수단가) > self.M['가용잔액'] + self.M['추가자금'] : 
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

        if  매수수량 * 매수단가 > self.M['가용잔액'] + self.M['추가자금'] : 
            매수수량 = self.M['기초수량'] * self.M['위매비중']
            self.M['진행상황'] = '매수제한'
        if  매수수량 * 매수단가 > self.M['가용잔액'] + self.M['추가자금'] : 
            매수수량 = 0
            self.M['진행상황'] = '매수금지'  

        self.M['전매수량'] = 매수수량
        self.M['전매수가'] = round(매수단가,2)
        self.M['예상금액'] = f"{매수수량 * 매수단가 :,.2f}"
       
                
    def today_sell(self) :
        if  not self.M['경과일수'] : return
        if  self.M['당일종가'] >= float(self.M['LD']['sub20']) : 
            self.M['매도수량']  = int(self.M['LD']['sub3'])
      
    def today_buy(self) :
        if  not self.M['경과일수'] : 
            if  self.M['당일종가'] <= float(self.M['LD']['sub19']) :
                self.M['매수수량']  = self.M['기초수량'] = my.ceil(self.M['일매수금']/self.M['전일종가'])  # 첫날에만 기초수량 재산정
        else :
            if  self.M['당일종가'] <= float(self.M['LD']['sub19']) : self.M['매수수량']  = int(self.M['LD']['sub2'])


    def commission(self,mm,opt) :
        if  opt==1 :  fee = int(mm*0.07)/100
        if  opt==2 :  
            m1 = int(mm*0.07)/100
            m2=round(mm*0.0008)/100
            fee = m1+m2

        self.M['수수료등']  = fee
        self.M['현재잔액'] -= fee
        self.M['추가자금'] -= fee


# -----------------------------------------------------------------------------------------------------------------------
# Initiate  basic / invest
# -----------------------------------------------------------------------------------------------------------------------

    def initiate_invest(self) :
        theDay  = self.D['post']['theDay']
        Balance = float(self.D['post']['Balance'].replace(',',''))

        preDay = self.DB.one(f"SELECT max(add0) FROM h_stockHistory_board WHERE add0 < '{theDay}'")
        self.B = {}
        self.M = {}

        self.DB.clear()
        self.DB.tbl = 'h_stockHistory_board'
        self.DB.wre = f"add0='{theDay}' and add1='SOXL'"; SOXL  = float(self.DB.get_one('add3'))
        CUP = self.DB.get_one('add9'); CDN = self.DB.get_one('add10'); 
        self.DB.wre = f"add0='{preDay}' and add1='SOXL'"; OSOX  = float(self.DB.get_one('add3'))

        self.B['add0']  = theDay
        self.B['add1']  = '0.00';   self.B['add2']  = '0.00';  

        self.B['sub5']  = CUP;  self.B['sub6'] = CDN; self.B['add18'] = '0.00'; self.B['sub7'] = '0.0'      

        self.M['가용잔액'] = int((Balance * 2)/3)
        self.M['추가자금'] = Balance - self.M['가용잔액']
        self.M['일매수금'] = int(self.M['가용잔액']/22) 

        self.M['기초수량'] = my.ceil(self.M['일매수금']/OSOX)

        self.B['add11'] = self.M['기초수량'] * SOXL; # 매수금액
        self.B['add16'] = self.B['add11'] / Balance * 100 # 레버비중
        self.B['add4']  = 100 - self.B['add16'] # 현금비중
        fee = int(self.B['add11']*0.07)/100
        self.M['추가자금'] -= fee
        self.B['add17'] = Balance - fee

        self.B['add12'] = '0.00' ; self.B['add9'] = self.B['add5']  = self.M['기초수량'];  self.B['add8'] = '0.00'
        self.B['add14'] = SOXL ; self.B['add15'] =  self.B['add11']  
        self.B['add7'] = f"{SOXL:,.4f}"; self.B['sub15'] = '0.00'; 

        self.B['add19'] = f"{self.M['가용잔액']-self.B['add11']:,.2f}"; self.B['sub11'] = '0.00'; self.B['sub25'] = f"{Balance:,.2f}"; self.B['sub27'] = f"{Balance:,.2f}"
        self.B['add20'] = self.M['추가자금']; self.B['sub26'] = '0.00'; self.B['sub28'] = '0.00'

        self.B['sub1']  = 1; self.B['sub4'] = self.M['일매수금']; 
        self.B['sub2']  = my.ceil(self.M['기초수량'] * (1 * 1.25 + 1))
        self.B['sub3']  = self.M['기초수량']
        self.B['sub12'] = 1; self.B['sub18'] = self.M['기초수량']; 
        self.B['sub19'] = round(SOXL * 1.022,2)-0.01; 
        self.B['sub20'] = self.B['sub19']+0.01

        self.B['sub29'] = '일반매수'; self.B['sub30'] = fee; self.B['sub31'] = fee; self.B['sub32'] = '0'

        # 포맷팅 && return values 
        self.B['add3']  = f"{Balance-self.B['add11']-fee:,.2f}"
        self.B['add11'] = f"{self.B['add11']:,.2f}"
        self.B['add15'] = f"{self.B['add15']:,.2f}"
        self.B['sub19'] = f"{self.B['sub19']:,.2f}"
        self.B['add20'] = f"{self.B['add20']:,.2f}"
        self.B['add4']  = f"{self.B['add4']:.1f}"
        self.B['add16'] = f"{self.B['add16']:.1f}"
        self.B['add17'] = f"{self.B['add17']:,.2f}"
        self.B['sub14'] = self.B['add6'] = self.B['add11']

        return self.json(self.B) 
    

# -----------------------------------------------------------------------------------------------------------------------
# Initiate  chance / invest
# -----------------------------------------------------------------------------------------------------------------------

    def initiate_chance(self) :
        self.B = {}

        theDay  = self.D['post']['theDay']
        preDay = self.DB.one(f"SELECT max(add0) FROM h_stockHistory_board WHERE add0 < '{theDay}'")
        현재잔액 = my.sv(self.D['post']['Balance'])
        현재수량 = my.sv(self.D['post']['curQty'],'i')
        기초수량 = my.sv(self.D['post']['bseQty'],'i')
        
        self.DB.clear()
        self.DB.tbl, self.DB.wre = (f"h_{self.target}_board",f"add0='{theDay}'")
        TD = self.DB.get_line('add6,add8,add9,add14,sub1,sub2,sub4,sub5,sub6,sub7,sub12,sub18,sub19,sub20')
        self.DB.wre = f"add0='{preDay}'"
        TO = self.DB.get_line('add14, sub19')
        
        오늘종가 = my.sv(TD['add14'])
        어제종가 = my.sv(TO['add14'])
        어제매가 = my.sv(TO['sub19'])
        
        타겟일수 = int(TD['sub12'])
        
        if  not 현재수량 : 
            가용잔액 = int(현재잔액 * 2/3)
            일매수금 = int(가용잔액/22)
            매수비율 = 일매수금 / int(TD['sub4']) 
            기초수량 = my.ceil(매수비율 * int(TD['sub18']))     

        # 실제적 로직 시작 ------------------------------------------------------------------------------------------
        if  타겟일수 < 2 :
            self.B['rsp'] = 0
            self.B['msg'] = f"현재 일 수는 {타겟일수}일 이며 필요 일 수(2일 이상)가 충족되지 않았습니다."
            return self.json(self.B)
        

        elif 타겟일수 == 2 :
            if  오늘종가 <= 어제매가 :
                변동수량  = 기초수량
                매수금액  = 오늘종가 * 기초수량
                
                내일수량 = 0    
                # 여기서의 일수는 오늘 일수임, 타겟데이타의 작성 완료 후 찬스데이타를 초기화 하는 것임
                for i in range(0,타겟일수+2) : 내일수량 += my.ceil(기초수량 *(i*1.25 + 1))
                
                cp00 = self.take_chance( 0,  int(TD['add9']),int(TD['sub2']),float(TD['add6']))
                cp22 = self.take_chance(-2.2,int(TD['add9']),int(TD['sub2']),float(TD['add6']))
                내일가격 = cp00 if (float(TD['add8']) < -2.2 or float(TD['sub7'])) else cp22
                
                self.B['sub19'] = min(float(TD['sub19']),내일가격) 
                self.B['sub2']  = 내일수량                              

            else :
                self.B['rsp'] = 0
                self.B['msg'] = f"종가 기준이 조건을 만족 하지 못하였습니다."
                return self.json(self.B)                

        elif 타겟일수 >= 3 :
            if  현재수량 > 기초수량  :
                self.B['rsp'] = 0
                self.B['msg'] = f"이미 정상 진행 중으로 초기화 작업이 완료된 상태입니다."
                return self.json(self.B) 
            else :
                오늘수량 = 0
                for i in range(0,타겟일수+1) : 오늘수량 += my.ceil(기초수량 *(i*1.25 + 1))
                cp00 = self.take_chance( 0,  int(TD['add9']),int(TD['sub2']),float(TD['add6']))
                cp22 = self.take_chance(-2.2,int(TD['add9']),int(TD['sub2']),float(TD['add6']))
                오늘가격 = cp00 if (float(TD['add8']) < cp22 or float(TD['sub7'])) else cp22
                오늘가격 = min(어제매가,오늘가격)
                
                if  오늘종가 <= 오늘가격 :
                    변동수량  = 오늘수량
                    매수금액  = 오늘종가 * 변동수량
                    self.B['sub19'] = TD['sub19'] # 내일 매수 가격
                    self.B['sub2']  = my.ceil(기초수량 *(타겟일수*1.25 + 1))
                

        # 공통 데이타 및 Formatting
        self.B['rsp'] = 1
        self.B['add14'] = TD['add14'] #오늘종가 
        self.B['sub5']  = TD['sub5'] ; self.B['sub6']  = TD['sub6'] # 연속상승, 연속하강
        self.B['sub1']  = TD['sub1'] ; self.B['sub12'] = int(TD['sub12'])-1 # 현재시즌, 경과일수
        self.B['sub20'] = TD['sub20'] #매도가격
        self.B['sub18'] = f"{기초수량:,}"
        self.B['add5']  = f"{변동수량:,}"
        self.B['add11'] = f"{매수금액:,.2f}"
        
        return self.json(self.B) 


    def take_chance(self,p,H,n,A) :
        if H == 0 : return 0
        N = H + n
        k = N / (1+p/100)
        return round(A/(k-n),2)
    


