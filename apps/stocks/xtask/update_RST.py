from myutils.DB import DB
import myutils.my_utils as my


class RST :

    def __init__(self) :
        self.D = {}
        self.M = {}
        today = my.timestamp_to_date(opt=7)
        self.week_day = my.dayofdate(today)
        self.DB = DB('stocks')
        self.skey = self.DB.store("slack_key")
        
        self.getStrategy()

    def init_each(self,bid) :
        self.D['prev_date'] = self.DB.one(f"SELECT max(add0) FROM h_{bid}_board")
        if  self.D['prev_date'] :
            self.D['today'] = self.DB.one(f"SELECT min(add0) FROM h_stockHistory_board WHERE add0 > '{self.D['prev_date']}'")
        
        self.M['진행일자'] = self.D['today']
        self.DB.tbl = f"h_{bid}_board"
        self.DB.wre = f"add0='{self.D['prev_date']}'"
        self.M['LD'] = self.DB.get_line('*')

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
            self.M['회복전략'] = 0 if 수익금액 > 0 else self.M['전략가치']
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

    def getStrategy(self) :
        # 매매전략 가져오기
        ST = self.DB.parameters_dict('매매전략/VRS')
        self.M['분할횟수']  = ST['001']  # 분할 횟수
        self.M['비중조절']  = ST['025']  # 매매일수 에 따른 구매수량 가중치(1.25)
        self.M['평단가치']  = ST['003']  # 매수시 가중치(1.022)
        self.M['큰단가치']  = ST['002']  # 첫날매수 시 가중치(1.12)
        self.M['첫매가치']  = ST['004']  # 일반매도 시 이율(1.022) 
        self.M['둘매가치']  = ST['005']  # 매수제한 시 이율(0.939) 
        self.M['강매시작']  = ST['008']  # 강매시작 일(24) 
        self.M['강매가치']  = ST['007']  # 손절가 범위(0.7)
        self.M['위매비중']  = ST['010']  # 매수제한 시 매수범위 기본수량의 (3)
        self.M['매도대기']  = ST['006']  # 매도대기(18)
        self.M['전략가치']  = ST['009']  # 1.12
        self.M['종가상승']  = ST['016']  # 종가상승 폭이 설정 수치 이상일 경우 전체 매도 가격

    def init_value(self) :

        LD = self.M['LD']

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

        U['sub7']   = f"{float(U['sub7']):.2f}"
        U['sub14']  = f"{float(U['sub14']):.2f}"
        U['sub19']  = f"{U['sub19']:.2f}"
        U['sub30']  = f"{U['sub30']:.2f}"


        U.update({k:'' for k,v in U.items() if v == None})
    
        qry=self.DB.qry_insert(f"h_{self.bid}_board",U)
        self.DB.exe(qry)

    def send_message(self,message) :
        if self.DB.system == "Linux" : my.post_slack(self.skey,message)
        else : print(message)

    def commission(self,mm,opt) :
        if  opt==1 :  fee = int(mm*0.07)/100
        if  opt==2 :
            m1 = int(mm*0.07)/100
            m2=round(mm*0.0008)/100
            fee = m1+m2

        self.M['수수료등']  = fee
        self.M['현재잔액'] -= fee

    def my_ceil(self,val) :
        return my.ceil(val)
    
    def my_roundup(self,val) :
        return my.round_up(val)
    