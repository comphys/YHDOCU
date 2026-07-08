from system.core.load import Model
import system.core.my_utils as my

class Ajax(Model) :
    # Update Log ------------------------------------------------------------------------------------------------------------------------------------------

    def set_value(self,key,val) :

        for k in key : self.M[k] = val

    def commission(self,opt) :
        
        if  self.P['수료적용'] == 'on' :
            mm = self.M['매수금액'] if opt == 1 else self.M['매도금액']
            fee = int(mm*0.07)/100
            if opt==2 : fee += round(mm*0.0008)/100
            self.M['수수료등']  = fee
            self.M['현재잔액'] -= fee

    def calculate(self)  :
        
        if  self.M['보유수량'] : self.M['진행일수'] += 1

        if  self.M['매수수량'] : 
            self.P['매수차수'] += 1
            self.M['매수금액']  = self.M['매수수량'] * self.M['당일종가']
            self.M['보유수량'] += self.M['매수수량']
            self.M['현재잔액'] -= self.M['매수금액']
            self.M['총매수금'] += self.M['매수금액']
            self.M['평균단가'] =  self.M['총매수금'] / self.M['보유수량'] 

            self.M['진행상황'] = self.M['차수명칭'][self.P['매수차수']-1] 
            self.M['카테고리'] = '일반진행'
            
            if  self.P['매수차수'] == 1 : 
                self.M['현재시즌'] = int(self.M['현재시즌']) + 1
                self.M['진행일수'] = 1
            
            # 다음(차수) 배분금액
            self.M['배분금액'] = int( self.M['초기금액'] * self.P['분할배분'][self.P['매수차수']]) 
            
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
            self.M['매수금액'] = 0.00
            self.M['총매수금'] = 0.00
            self.M['평균단가'] = 0.00

            self.M['진행상황'] = '익절매도' if self.M['현재수익'] >= 0 else '손절매도'
            self.P['매수차수'] = 0
            self.M['카테고리'] = '수익실현'

            self.M['초기금액'] = self.M['현재잔액']+self.P['가상증액']
            self.M['배분금액'] = int( self.M['초기금액'] * self.P['분할배분'][0] ) 
            self.M['초기일자'] = self.M['당일날자']


    def today_buy(self) :

        if  not self.M['매수예정'] : return

        if  self.M['당일종가'] <= self.M['매수예가'] : 
            self.M['매수수량']  = self.M['매수예정']
            
  
    def today_sell(self) :
        
        if  not self.M['매도예정'] : return

        if  self.M['당일종가'] >= self.M['매도예가'] : self.M['매도수량'] = self.M['보유수량']


    def tomorrow_buy(self) :
        
        if  not self.P['진행여부']  : 

            self.M['매수예정'] = 0
            self.M['매수예가'] = 0.00
            return 
        
        if self.M['보유수량'] :
            if  self.P['매수차수'] >  self.M['최대차수']-1 : 
                self.M['매수예정'] = 0
                self.M['매수예가'] = 0.00
                return
            
            if  self.P['매수차수'] == self.M['최대차수']-1 : self.M['배분금액'] = int(self.M['현재잔액'])
            
            self.M['매수예가'] = round(self.M['당일종가'] * self.P['매입가치'],2)
            self.M['매수예정'] = int(  self.M['배분금액']/ self.M['매수예가'] ) 

        else :
            self.M['매수예가'] = round(self.M['당일종가']-0.01, 2) if self.M['당일연속'] >= self.P['진입일자']-1 else round(self.M['당일종가'] * self.P['진입가치'],2)    
            self.M['매수예정'] = int(  self.M['배분금액']/ self.M['매수예가'] ) 

    def tomorrow_sell(self) :
        
        if  self.M['보유수량'] : 
            self.M['매도예정'] = self.M['보유수량']
            # rd = self.DB.last_data_one( "CAST(n_20 as FLOAT)",'h_rsnLog_board' )
            self.M['매도예가'] = my.round_up(self.M['평균단가'] * self.P['각매가치'][self.P['매수차수']-1])
            # sp = max(self.M['매도예가'],rd) if rd else self.M['매도예가'] 
            # self.M['매도예가'] = my.round_up(sp)

        else :
            self.M['매도예정'] = 0
            self.M['매도예가'] = 0.00


    def init_value(self) :

        self.P = {}
        self.M = {}

        ST = self.DB.parameters_dict('매매전략/N315A')
        LD = self.DB.last_data_line('*','h_log315A_board')
        uday = max(LD['add0'],LD['add18'])
        uday = my.next_stock_day(uday,self.DB)[0]
        CD = self.DB.line(f"SELECT add0,add3,add8,add10 FROM h_stockHistory_board WHERE add0='{uday}'")

        self.set_value(['매수수량','매도수량'],0)
        self.set_value(['매수금액','매도금액','평균단가','현재수익','현수익률','평가금액','매수예가','수수료등'],0.0)
        # ---------------------------------------------------------
        self.P['분할배분'] = my.sf(ST['A0101'])
        self.P['각매가치'] = my.sf(ST['A0301'])
        self.P['매입가치'] = ST['A0201']
        self.P['진입일자'] = ST['A0202']
        self.P['진입가치'] = ST['A0203']
        self.P['수료적용'] = ST['A0501']
        self.P['세금적용'] = ST['A0502']
        self.P['매수차수'] = ST['A0701']
        self.P['가상증액'] = my.sv(ST['A0702'])
        self.P['진행여부'] = True if ST['A0720'] == 'on' else False
        # 종가 정보
        self.M['당일날자'] = CD['add0']
        self.M['당일종가'] = float(CD['add3']) 
        self.M['당일연속'] = int(CD['add10'])
        self.M['당일증감'] = CD['add8']
        #------------------------------------------------------------
        self.M['진행일자'] = LD['add0']
        self.M['카테고리'] = LD['add20']
        self.M['현재시즌'] = LD['add1']
        self.M['진행일수'] = 0 if LD['add2'] == 'R' else int(LD['add2'])
        self.M['현재잔액'] = float(LD['add5'])
        self.M['진행상황'] = '매수대기' if int(LD['add9']) else ''
        # self.M['매수수량'] = 0
        self.M['매수금액'] = float(LD['add8'])
        self.M['보유수량'] = int(LD['add9'])
        self.M['총매수금'] = float(LD['add11'])
        self.M['평균단가'] = float(LD['add10'])
        self.M['매수예정'] = int(LD['add22'])
        self.M['매수예가'] = float(LD['add23'])
        self.M['매도예정'] = int(LD['add24'])
        self.M['매도예가'] = float(LD['add25'])
        self.M['배분금액'] = float(LD['add17'])
        self.M['초기일자'] = LD['add18']
        self.M['초기금액'] = float(LD['add19'])
        # 잔액 분할
        self.M['최대차수'] = len(self.P['분할배분'])
        self.M['차수명칭'] = ['일차매수','이차매수','삼차매수','사차매수','오차매수','육차매수','칠차매수']
        #-------------------------------------------------------------

        
    def print_data(self) :
        
        X = {}
        X['add0']  = self.M['당일날자'] 
        X['add20'] = self.M['카테고리'] 
        X['add3']  = f"{self.M['당일종가']:.2f}" 
        X['add4']  = self.M['당일증감'] 
        X['add1']  = self.M['현재시즌'] 
        X['add2']  = self.M['진행일수'] 
        X['add5']  = f"{self.M['현재잔액']:.2f}" 
        X['add6']  = self.M['진행상황'] 
        X['add7']  = self.M['매수수량'] 
        X['add8']  = f"{self.M['매수금액']:.2f}" 
        X['add9']  = self.M['보유수량'] 
        X['add11'] = f"{self.M['총매수금']:.2f}"
        X['add12'] = f"{self.M['평가금액']:.2f}"
        X['add10'] = f"{self.M['평균단가']:.4f}"
        X['add13'] = f"{self.M['매도금액']:.2f}"
        X['add14'] = f"{self.M['현재수익']:.2f}"
        X['add15'] = f"{self.M['현수익률']:.2f}"
        X['add16'] = f"{self.M['평가금액'] + self.M['현재잔액']:.2f}"
        X['add22'] = self.M['매수예정']
        X['add23'] = f"{self.M['매수예가']:.2f}" 
        X['add24'] = self.M['매도예정']
        X['add25'] = f"{self.M['매도예가']:.2f}"
        X['add21'] = f"{self.M['수수료등']:.2f}"
        X['add17'] = f"{self.M['배분금액']:.2f}"
        X['add18'] = self.M['당일날자']
        X['add19'] = f"{self.M['초기금액']:.2f}"

        X['uid']   = 'comphys'
        X['uname'] = '정용훈'
        X['wdate'] = X['mdate'] = my.now_timestamp()
        X['content'] = '' 

        self.DB.parameter_update('A0701',self.P['매수차수'])
        return X        

    def update_log(self) :

        self.init_value()

        if  self.P['진행여부'] : 
        
            if self.M['매수예정'] : self.today_buy()
            if self.M['매도예정'] : self.today_sell()
            if self.M['매수수량'] or self.M['매도수량'] or self.M['보유수량'] : self.calculate()

            self.tomorrow_buy()
            self.tomorrow_sell()

            board = 'h_log315A_board'

            if  self.M['매수수량'] or self.M['매도수량'] or self.M['보유수량'] :
                XD = self.print_data()
                qry=self.DB.qry_insert(board,XD)
                self.DB.exe(qry)
                return self.SYS.json("OK")

            else :
                UD = {'add22':self.M['매수예정'],'add23':self.M['매수예가'],'add18':self.M['당일날자'],'add19':f"{self.M['초기금액']:.2f}"}
                con = f"add0 = '{self.M['진행일자']}'"
                qry = self.DB.qry_update(board,UD,con)
                self.DB.exe(qry)
                return self.SYS.json("OK")
        


    # -----------------------------------------------------------------------------------------------------------------------------------------------------
    
    def dailyCheckUpdate(self) :

        odrday = self.D['post']['odrday']
        option = self.D['post']['option']
        
        if  option == 'N315A'  : key = 'A0710'

        self.DB.parameter_update(key,odrday)


    def reset_balance(self) :
        
        n_bl = self.D['post']['n_bl']
        LD = self.DB.last_record('h_log315A_board')
        CD = self.DB.last_record('h_stockHistory_board')
        ST = self.DB.parameters_dict('매매전략/N315A')
        
        # 잔액 및 가치합계 재 설정
        o_mon = my.sv(LD['add5'])
        n_mon = my.sv(n_bl)
        a_mon = my.sv(ST['A0702'])
        b_mon = n_mon + a_mon
        x_mon = f"(증) {n_mon-o_mon:,.2f}" if n_mon > o_mon else f"(감) {o_mon-n_mon:,.2f}"

        당일종가 = float(CD['add3'])
        당일연속 = int(CD['add10'])
        진입일자 = ST['A0202']
        진입가치 = ST['A0203']
        분할배분 = my.sf(ST['A0101'])
        배분금액 = int( b_mon * 분할배분[0])
        매수예가 = round( 당일종가-0.01, 2) if 당일연속 >= 진입일자-1 else round( 당일종가 * 진입가치,2)    
        매수예정 = int( 배분금액/ 매수예가 )         

        LD['add0'] = LD['add18'] = CD['add0'] # 진행일자 및 초기일자 변경
        LD['add5'] = LD['add16'] = LD['add19'] = f"{n_mon:.2f}"
        LD['add6'] = '' # 진행상황
        LD['content'] = f"투자금액 변경 (기존) {o_mon:,.2f} > (변경) {n_mon:,.2f}, {x_mon}, (변경시작일) {LD['add0']}" 
        LD['add2'] = 'R' # 새로운 베이스 임을 표시 
        LD['add3'] = LD['add4'] = LD['add13'] = LD['add14'] = LD['add15'] = LD['add17'] = LD['add21'] = '0.00' 
        LD['add20'] = '기초셋팅'
        LD['add17'] = 배분금액
        LD['add19'] = f"{b_mon:.2f}" #초기금액
        LD['add22'] = 매수예정
        LD['add23'] = f"{매수예가:.2f}"
        
        # 새로운 데이타 
        del(LD['no']); del(LD['brother']); del(LD['tle_color']); del(LD['reply']); del(LD['hit'])
        LD['wdate'] = LD['mdate'] = my.now_timestamp()
        qry=self.DB.qry_insert('h_log315A_board',LD)  
        self.DB.exe(qry)

        # 파라미터 업데이트

        return "___OK____"
    
