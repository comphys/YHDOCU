from system.core.load import Model
import system.core.my_utils as my

class M_dashboard(Model) :

    def view(self) :
    
        self.D['오늘날자']  = my.timestamp_to_date(opt=7) 
        self.D['오늘요일']  = my.dayofdate(self.D['오늘날자'])
        
        today,close_price  = self.DB.exe("SELECT add0,add3 FROM h_stockHistory_board WHERE add1='SOXL' ORDER BY add0 DESC LIMIT 1",many=1,assoc=False)

        last_day = today
        self.D['투자안내'] = ''
        self.D['키움증권'] = ''
        self.D['하이투자'] = ''
        
        select_cols = self.DB.table_cols('h_INVEST_board',('no', 'brother', 'add0', 'tle_color', 'uid', 'uname', 'content', 'reply', 'hit', 'wdate', 'mdate'))
        self.DB.wre = f"add0='{today}'"
        
        self.DB.tbl = 'h_INVEST_board'
        TD = self.DB.get_line(select_cols)
        if not TD : 
            last_day = self.DB.one(f"SELECT max(add0) FROM {self.DB.tbl}")
            self.DB.wre = f"add0='{last_day}'"
            TD = self.DB.get_line(select_cols)
        
        if today != last_day : self.D['투자안내'] = 'Need Updating' 
        
        self.DB.tbl = 'h_I230831_board'
        ID = self.DB.get_line(select_cols)
        if not ID : 
            last_day = self.DB.one(f"SELECT max(add0) FROM {self.DB.tbl}")
            self.DB.wre = f"add0='{last_day}'" 
            ID = self.DB.get_line(select_cols)
        
        if today != last_day : self.D['키움증권'] = 'Need Updating'      
        
        self.DB.tbl = 'h_C230831_board'
        CD = self.DB.get_line(select_cols)
        if not CD : 
            last_day = self.DB.one(f"SELECT max(add0) FROM {self.DB.tbl}")
            self.DB.wre = f"add0='{last_day}'"
            CD = self.DB.get_line(select_cols)
        
        if today != last_day : self.D['하이투자'] = 'Need Updating'   

        # 키움증권
        
        매수수량1 = int(ID['sub2'])
        매수가격1 = float(ID['sub19']) 
        매수가액1 = 매수수량1 * 매수가격1

        self.D['매수수량1'] = f"{매수수량1:,}"
        self.D['매수가격1'] = f"{매수가격1:,.2f}"
        self.D['매수가액1'] = f"{매수가액1:,.2f}"
        self.D['자산분배1'] = ID['add10']
        self.D['자산총액1'] = float(ID['add17']) 

        매도수량1 = int(ID['sub3'])
        매도가격1 = float(ID['sub20']) 
        매도가액1 = 매도수량1 * 매도가격1

        sellP1 = (매도가격1/float(close_price) - 1) * 100
        self.D['현수익률1'] = ID['add8']
        self.D['매도시점1'] = f"{sellP1:,.2f}"
        self.D['매도수량1'] = f"{매도수량1:,}"
        self.D['매도가격1'] = f"{매도가격1:,.2f}"
        self.D['매도가액1'] = f"{매도가액1:,.2f}"
        self.D['증가비율1'] = round(float(ID['add17'])/float(ID['sub25']) * 100,2)
        

        # 하이투자
        
        타겟일수 = int(TD['sub12'])
        
        if  타겟일수 == 0 :
            매수수량2 = 0
            매수가격2 = 0.00
            매도수량2 = 0
            매도가격2 = 0.00    
            
        elif 타겟일수 == 1 :
            매수수량2 = self.chance_init(float(CD['add3']),float(TD['sub4']),int(TD['sub18']))
            매수가격2 = float(TD['sub19'])
            매도수량2 = 0
            매도가격2 = 0.00

        elif 타겟일수 >= 2 and int(CD['add9']) <= int(CD['sub18']): 
            기초수량 = int(CD['sub18']) if int(CD['add9']) else self.chance_init(float(CD['add3']),float(TD['sub4']),int(TD['sub18']))
            # 테스트 상 많이 사는 것이 유리함(수량을 하루 치 더 삼, 어제일수 + 1 +1(추가분))
            찬스수량 = 0
            day_count = min(int(TD['sub12'])+2,6)
            for i in range(0,day_count) : 찬스수량 += my.ceil(기초수량 *(i*1.25 + 1))
                
            cp00 = self.take_chance( 0,  int(TD['add9']),int(TD['sub2']),float(TD['add6']))
            cp22 = self.take_chance(-2.2,int(TD['add9']),int(TD['sub2']),float(TD['add6']))

            #  p = 0 if (self.M['수익률'] < self.R['기회시점'] or self.M['손실회수']) else self.R['기회시점']
            찬스가격 = cp00 if (float(TD['add8']) < -2.2 or float(TD['sub7'])) else cp22
            찬스가격 = min(float(TD['sub19']),찬스가격)
            
            매수수량2 = 찬스수량
            매수가격2 = 찬스가격
            매도수량2 = int(CD['add9'])
            매도가격2 = float(TD['sub20'])
            
        else : # 가이드 및 투자가 진행 중일 때
            매수수량2 = int(CD['sub2'])
            매수가격2 = float(CD['sub19'])
            매도수량2 = int(CD['add9']) 
            매도가격2 = float(CD['sub20'])

        매수가액2 = 매수수량2 * 매수가격2
        매도가액2 = 매도수량2 * 매도가격2
        
        sellP2 = (매도가격2/float(close_price) - 1) * 100
        self.info(매도가격2)
        self.info(sellP2)
        self.D['현수익률2'] = CD['add8']
        self.D['매도시점2'] = f"{sellP2:.2f}"
        self.D['매수수량2'] = f"{매수수량2:,}"
        self.D['매수가격2'] = f"{매수가격2:,.2f}"
        self.D['매수가액2'] = f"{매수가액2:,.2f}"
        self.D['자산분배2'] = CD['add10']
        self.D['자산총액2'] = float(CD['add17'])
        self.D['매도수량2'] = f"{매도수량2:,}"
        self.D['매도가격2'] = f"{매도가격2:,.2f}"
        self.D['매도가액2'] = f"{매도가액2:,.2f}"
        self.D['증가비율2'] = round(float(CD['add17'])/float(CD['sub25']) * 100,2)
        self.D['기준일자'] = today
        self.D['기준종가'] = close_price


    def chance_init(self,balance,t_day_amount,t_basic_qty) :
        # -- 기초수량 구하기
        가용잔액 = int( balance * 2/3); 일매수금 = int(가용잔액/22); 
        매수비율 = 일매수금 / int(t_day_amount) 
        return my.ceil(매수비율 * t_basic_qty)

    def take_chance(self,p,H,n,A) :
        if H == 0 : return 0
        N = H + n
        k = N / (1+p/100)
        return round(A/(k-n),2)
    