from myutils.DB import DB
import myutils.my_utils as my


class update_Rtactic :

    def __init__(self) :
        self.D = {}
        self.DB = DB('stocks')
        self.skey = self.DB.store("slack_key")
        self.guide = 'h_IGUIDE_board'


    def oneWrite(self) :
        
        self.D['prev_date'] = self.DB.one(f"SELECT max(add0) FROM h_{self.bid}_board")
        
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

        else :
            self.send_message(f"{self.bid} {self.D['prev_date']} 이후 업데이트된 정보가 없습니다")
            return

        self.send_message(f"{self.bid} {self.D['today']} 업데이트")
    
    def send_message(self,message) :
        if self.DB.system == "Linux" : my.post_slack(self.skey,message)
        else : print(message)


    def tomorrow_sell(self) : 

        if  self.M['경과일수'] ==  0 :
            self.M['전매도량']  =  0
            self.M['전매도가']  =  self.M['당일종가']
            return

        self.M['전매도량'] = self.M['보유수량']
        self.M['전매도가'] = float(self.M['GD']['sub20'])


    def tomorrow_buy(self)  :

        if  self.M['경과일수'] == 0 :
            self.M['전매수량'] = 0
            self.M['전매수가'] = round(self.M['당일종가'] * self.M['큰단가치'],2)
        
        elif self.M['경과일수'] == 1 :
            self.M['전매수량'] = self.M['기초수량']
            self.M['전매수가'] = self.M['당일종가']

        elif self.M['경과일수'] >= 2 and int(self.M['보유수량']) <= int(self.M['기초수량']): 
            
            # 테스트 상 많이 사는 것이 유리함(수량을 하루 치 더 삼, 어제일수 + 1 +1(추가분))
            찬스수량 = 0
            day_count = min(int(self.M['GD']['sub12'])+1+self.M['날수가산'],6)
            for i in range(0,day_count) : 찬스수량 += my.ceil(int(self.M['기초수량']) *(i*1.25 + 1))
                
            cpn = self.take_chance(self.M['기회시점'])
            cpc = self.take_chance(self.M['기회회복'])

            찬스가격 = cpc if float(self.M['GD']['sub7']) else cpn
            찬스가격 = min(float(self.M['GD']['sub19']),찬스가격)
            
            self.M['전매수량'] = 찬스수량
            self.M['전매수가'] = 찬스가격
            
        else : # 가이드 및 투자가 진행 중일 때
            매수단가 = float(self.M['GD']['sub19'])
            매수수량 = my.ceil(self.M['기초수량'] * (self.M['경과일수']*self.M['비중조절'] + 1))

            if  매수수량 * 매수단가 > self.M['현재잔액'] :
                매수수량 = self.M['기초수량'] * self.M['위매비중']
                self.M['진행상황'] = '매수제한'
            if  매수수량 * 매수단가 > self.M['현재잔액'] :
                매수수량 = 0
                self.M['진행상황'] = '매수금지'

            self.M['전매수량'] = 매수수량
            self.M['전매수가'] = 매수단가


    def commission(self,mm,opt) :
        if  opt==1 :  fee = int(mm*0.07)/100
        if  opt==2 :
            m1 = int(mm*0.07)/100
            m2=round(mm*0.0008)/100
            fee = m1+m2

        self.M['수수료등']  = fee
        self.M['현재잔액'] -= fee

    def rebalance(self)  :
        self.M['일매수금'] = int(self.M['현재잔액']/self.M['분할횟수'])
        self.M['기초수량'] = my.ceil(self.M['일매수금']/float(self.M['기초종가']))


    def calculate(self)  :

        매도가격 = self.M['당일종가']
        매수가격 = self.M['당일종가']

        if  self.M['매도수량'] :
            self.M['매도금액'] = 매도가격 * self.M['매도수량']
            self.M['변동수량'] = -self.M['매도수량']
            self.M['현재잔액'] += self.M['매도금액']
            self.M['진행상황'] = '전량매도'
            수익금액 = self.M['매도금액'] - self.M['현매수금']
            self.M['현재손익'] = f"{수익금액:.2f}"
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

        if  self.M['보유수량'] == self.M['매수수량'] :
            self.M['진행상황'] = '초기매수'
        if  not self.M['보유수량'] : self.M['진행상황'] = '매수대기'



    def check_sell(self) :
 
        if  self.M['당일종가'] >= float(self.M['LD']['sub20']) :
            self.M['매도수량']  = int(self.M['LD']['sub3'])

    def check_buy(self) :
        if  self.M['당일종가'] <= float(self.M['LD']['sub19']) : self.M['매수수량']  = int(self.M['LD']['sub2'])


    def init_value(self) :
        self.M = {}
        
        self.M['진행일자'] = self.D['today']
        # 가이드 데이타 가져오기
        select_cols = self.DB.table_cols(self.guide,('no', 'brother', 'add0', 'tle_color', 'uid', 'uname', 'content', 'reply', 'hit', 'wdate', 'mdate'))
        self.DB.wre =  f"add0='{self.D['today']}'"
        self.DB.tbl = self.guide
        GD = self.M['GD'] = self.DB.get_line(select_cols)
                
        self.DB.tbl = f"h_{self.bid}_board"
        self.DB.wre = f"add0='{self.D['prev_date']}'"
        LD = self.M['LD'] = self.DB.get_line('*')
        self.M['업데이트'] = float(LD['add1']) == 0 and float(LD['add2']) == 0 and float(LD['add11']) == 0 and float(LD['add12']) == 0 and int(LD['add9']) == 0
        self.M['현재잔액'] = float(LD['add3'])
        self.M['최종매도'] = float(LD['add12'])

        # 종가구하기
        self.M['당일종가'] = float(GD['add14'])
        self.M['전일종가'] = float(self.M['LD']['add14'])
        p_change = self.DB.one(f"SELECT add8 FROM h_stockHistory_board WHERE add0='{self.M['진행일자']}' and add1='SOXL'")
        self.M['종가변동'] = f"{float(p_change):.2f}"
        self.M['연속상승'] = GD['sub5']
        self.M['연속하락'] = GD['sub6']

        # 매매전략 가져오기
        ST = self.DB.parameters_dict('매매전략/VRS')
        self.M['분할횟수']  = ST['001']  # 분할 횟수
        self.M['비중조절']  = ST['025']  # 매매일수 에 따른 구매수량 가중치(1.25)
        self.M['큰단가치']  = ST['002']  # 첫날매수 시 가중치(1.12)
        self.M['위매비중']  = ST['010']  # 매수제한 시 매수범위 기본수량의 (3)
        self.M['기회시점']  = ST['021']  # S전략 일반 매수시점
        self.M['기회회복']  = ST['022']  # S전략 회복 매수시점
        self.M['날수가산']  = ST['026']  # day_count 계산 시 날수 가산

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
        self.M['경과일수'] = int(GD['sub12'])
        self.M['매매현황'] = ''
        self.M['진행상황'] = '매도대기'
        self.M['보유수량'] = int(LD['add9'])
        self.M['현매수금'] = float(LD['add6'])
        self.M['현재잔액'] = float(LD['add3'])
        self.M['진행상황'] = '매도대기'
        
        # 기초수량 구하기
        self.M['기초종가'] = self.DB.one(f"SELECT add14 FROM {self.guide} WHERE sub12='0' and add0 <= '{self.M['진행일자']}' ORDER BY add0 DESC LIMIT 1")
        self.M['기초수량'] = my.ceil(self.M['일매수금']/float(self.M['기초종가']))


    def update_value(self) :
        
        U = self.M['LD']
        del U['no']
        U['wdate']   = my.now_timestamp()
        U['mdate']   = U['wdate']
        U['add0']    = self.M['진행일자']
        U['sub12']   = self.M['GD']['sub12']

        U['add14']   = self.M['당일종가']
        U['sub5']    = self.M['연속상승']
        U['sub6']    = self.M['연속하락']
        U['sub18']   = self.M['기초수량']
        U['add5']    = self.M['변동수량']
        U['add9']    = int(U['add9']) + self.M['변동수량']

        U['add11']  = round(self.M['매수금액'],2)
        U['add12']  = round(self.M['매도금액'],2)
        if  U['add11'] :
            U['sub14'] = round(float(U['sub14']) + U['add11'],2) #매수누적
            U['add6']  = round(float(U['add6'])  + U['add11'],2) #현매수금
            U['add7']  = round(U['add6']/U['add9'],4) #평균단가

        if  U['add12'] :
            U['sub15'] = round(float(U['sub15']) + U['add12'],2) #매도누적
            U['add8']  = round((U['add12'] / float(U['add6']) - 1) * 100,2)
            U['add6'] = 0.00 #현매수금
            U['add7'] = 0.00 #평균단가
            U['add18'] = self.M['현재손익']
            U['sub1']  = self.M['시즌']
            U['sub4']  = self.M['일매수금']
        else :
            U['add8'] = '0.00'

        if U['add7'] and float(U['add7']) : U['add8'] = round((self.M['당일종가'] / float(U['add7']) - 1) * 100,2)  # 현수익률 if 평균단가 != 0

        U['add1']   = '0.00'
        U['add2']   = '0.00'
        U['add3']   = self.M['현재잔액'] 
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
        if self.M['전매도가'] <= self.M['전매수가'] : self.M['전매도가'] = self.M['전매수가'] + 0.01 # 첫 날 큰수매일 경우에 적용됨
        U['sub20']  = self.M['전매도가']
        U['sub29']  = self.M['진행상황']
        U['sub30']  = self.M['수수료등']
        U['sub31'] = float(U['sub31']) + self.M['수수료등'] if self.M['경과일수'] != 1 else self.M['수수료등'] # 누적수수료
        U['add20'] = self.M['종가변동']
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

        U['sub19']  = f"{U['sub19']:.2f}"
        U['sub20']  = f"{U['sub20']:.2f}"
        U['sub30']  = f"{U['sub30']:.2f}"

        # DATA INSERT OR UPDATE
        U.update({k:'' for k,v in U.items() if v == None})

        board = f"h_{self.bid}_board"
        if  self.M['업데이트'] :
            qry=self.DB.qry_update(board,U,f"add0='{self.D['prev_date']}'")
            self.DB.exe(qry)

        else :
            qry=self.DB.qry_insert(board,U)
            self.DB.exe(qry)

    def take_chance(self,p) :
        H = int(self.M['GD']['add9'])
        n = int(self.M['GD']['sub2'])
        A = float(self.M['GD']['add6'])
        if H == 0 : return 0
        N = H + n
        k = N / (1+p/100)
        return round(A/(k-n),2)

today = my.timestamp_to_date(opt=7)
week_day = my.dayofdate(today)

if week_day in ['일','월'] : pass
else :
    B = update_Rtactic()
    B.bid = 'R230831'
    B.oneWrite()