from system.core.load import Model
import system.core.my_utils as my

class M_dashboard(Model) :

    def view(self) :
    
        self.D['오늘날자']  = my.timestamp_to_date(opt=7) 
        self.D['오늘요일']  = my.dayofdate(self.D['오늘날자'])
        self.D['현재환율']  = float(self.DB.one("SELECT usd_krw FROM usd_krw ORDER BY rowid DESC LIMIT 1"))
        ST = self.DB.parameters_dict('매매전략/VRS')
    
        
        today,close_price  = self.DB.exe("SELECT add0,add3 FROM h_stockHistory_board WHERE add1='SOXL' ORDER BY add0 DESC LIMIT 1",many=1,assoc=False)

        last_day = today
        self.D['I_guide'] = ''
        self.D['Vtactic'] = ''
        self.D['Rtactic'] = ''
        self.D['Stactic'] = ''
        
        self.D['V_title'] = ST['031']
        self.D['R_title'] = ST['032']
        self.D['S_title'] = ST['033']
        self.D['자산분배'] = self.DB.parameters_des('038')
        
        select_cols = self.DB.table_cols(ST['034'],('no', 'brother', 'add0', 'tle_color', 'uid', 'uname', 'content', 'reply', 'hit', 'wdate', 'mdate'))
        self.DB.wre = f"add0='{today}'"
        
        self.DB.tbl = ST['034']
        TD = self.DB.get_line(select_cols)
        if not TD : 
            last_day = self.DB.one(f"SELECT max(add0) FROM {self.DB.tbl}")
            self.DB.wre = f"add0='{last_day}'"
            TD = self.DB.get_line(select_cols)
        
        if today != last_day : self.D['I_guide'] = 'Need Updating' 
        
        self.DB.tbl = ST['035']
        VD = self.DB.get_line(select_cols)
        if not VD : 
            last_day = self.DB.one(f"SELECT max(add0) FROM {self.DB.tbl}")
            self.DB.wre = f"add0='{last_day}'" 
            VD = self.DB.get_line(select_cols)
        
        if today != last_day : self.D['Vtactic'] = 'Need Updating'      
        
        self.DB.tbl = ST['036']
        RD = self.DB.get_line(select_cols)
        if not RD : 
            last_day = self.DB.one(f"SELECT max(add0) FROM {self.DB.tbl}")
            self.DB.wre = f"add0='{last_day}'"
            RD = self.DB.get_line(select_cols)
        
        if today != last_day : self.D['Rtactic'] = 'Need Updating'   

        self.DB.tbl = ST['037']
        SD = self.DB.get_line(select_cols)
        if not SD : 
            last_day = self.DB.one(f"SELECT max(add0) FROM {self.DB.tbl}")
            self.DB.wre = f"add0='{last_day}'"
            SD = self.DB.get_line(select_cols)
        
        if today != last_day : self.D['Stactic'] = 'Need Updating' 
        
        
        self.D['기준일자'] = today
        self.D['기준요일'] = my.dayofdate(today)
        self.D['기준종가'] = close_price        
        
        # 키움증권
        매수수량1 = int(VD['sub2'])
        매수가격1 = float(VD['sub19']) 
        매수가액1 = 매수수량1 * 매수가격1
        현매수금1 = float(VD['add6']) 

        self.D['매수수량1'] = f"{매수수량1:,}"
        self.D['매수가격1'] = f"{매수가격1:,.2f}"
        self.D['매수가액1'] = f"{매수가액1:,.2f}"
        self.D['자산총액1'] = float(VD['add17']) 

        매도수량1 = int(VD['sub3'])
        매도가격1 = float(VD['sub20']) 
        매도가액1 = 매도수량1 * 매도가격1
        매도차익1 = 매도가액1 - 현매수금1
        매도차원1 = 매도차익1 * float(self.D['현재환율'])

        sellP1 = (매도가격1/float(close_price) - 1) * 100 if 매도수량1 else 0
        self.D['현수익률1'] = VD['add8']
        self.D['매도시점1'] = f"{sellP1:,.2f}"
        self.D['매도수량1'] = f"{매도수량1:,}"
        self.D['매도가격1'] = f"{매도가격1:,.2f}"
        self.D['매도가액1'] = f"{매도가액1:,.2f}"
        self.D['매도차익1'] = f"{매도차익1:,.2f}"
        self.D['매도차원1'] = f"{매도차원1:,.0f}"
        self.D['현매수금1'] = f"{현매수금1:,.2f}"
        self.D['현평가금1'] = f"{float(VD['add15']):,.2f}"
        self.D['현이익금1'] = f"{float(VD['add18']):,.2f}" 
        self.D['증가비율1'] = round(float(VD['add17'])/(float(VD['sub25'])-float(VD['sub26']))* 100,2)
        

        # ----------------------------------------------------------------------------------------------
        # Revolution
        # ----------------------------------------------------------------------------------------------
        
        타겟일수 = int(TD['sub12'])
        기초수량 = int(RD['sub18'])
        
        if  타겟일수 == 0 :
            매수수량2 = 0
            매수가격2 = 0.00
            매도수량2 = 0
            매도가격2 = 0.00    
            
        elif 타겟일수 == 1 :
            매수수량2 = 기초수량
            매수가격2 = float(TD['add14'])
            매도수량2 = 0
            매도가격2 = 0.00

        elif 타겟일수 >= 2 and int(RD['add9']) <= int(RD['sub18']): 
            # 테스트 상 많이 사는 것이 유리함(수량을 하루 치 더 삼, 어제일수 + 1 +1(추가분))
            찬스수량 = 0
            day_count = min(int(TD['sub12'])+1+ST['026'],6)
            for i in range(0,day_count) : 찬스수량 += my.ceil(기초수량 *(i*1.25 + 1))
                
            cpc = self.take_chance(ST['022'],int(TD['add9']),int(TD['sub2']),float(TD['add6']))
            cpn = self.take_chance(ST['021'],int(TD['add9']),int(TD['sub2']),float(TD['add6']))

            #  p = 0 if (self.M['수익률'] < self.R['기회시점'] or self.M['손실회수']) else self.R['기회시점']
            # 찬스가격 = cp00 if (float(TD['add8']) < -2.2 or float(TD['sub7'])) else cp22
            찬스가격 = cpc if float(TD['sub7']) else cpn
            찬스가격 = min(float(TD['sub19']),찬스가격)
            
            매수수량2 = 찬스수량
            매수가격2 = 찬스가격
            매도수량2 = int(RD['add9'])
            매도가격2 = float(TD['sub20'])
            
        else : # 가이드 및 투자가 진행 중일 때
            매수수량2 = int(RD['sub2'])
            매수가격2 = float(RD['sub19'])
            매도수량2 = int(RD['add9']) 
            매도가격2 = float(RD['sub20'])

        현매수금2 = float(RD['add6']) 
        매수가액2 = 매수수량2 * 매수가격2
        매도가액2 = 매도수량2 * 매도가격2
        매도차익2 = 매도가액2 - 현매수금2
        매도차원2 = 매도차익2 * float(self.D['현재환율'])
        
        sellP2 = (매도가격2/float(close_price) - 1) * 100 if 매도수량2 else 0
        self.D['현수익률2'] = RD['add8']
        self.D['매도시점2'] = f"{sellP2:.2f}"
        self.D['매수수량2'] = f"{매수수량2:,}"
        self.D['매수가격2'] = f"{매수가격2:,.2f}"
        self.D['매수가액2'] = f"{매수가액2:,.2f}"
        self.D['자산총액2'] = float(RD['add17'])
        self.D['매도수량2'] = f"{매도수량2:,}"
        self.D['매도가격2'] = f"{매도가격2:,.2f}"
        self.D['매도가액2'] = f"{매도가액2:,.2f}"
        self.D['증가비율2'] = round(float(RD['add17'])/(float(RD['sub25'])-float(RD['sub26'])) * 100,2)
        self.D['현평가금2'] = f"{float(RD['add15']):,.2f}"
        self.D['현이익금2'] = f"{float(RD['add18']):,.2f}"
        self.D['현매수금2'] = f"{현매수금2:,.2f}"
        self.D['매도차익2'] = f"{매도차익2:,.2f}"
        self.D['매도차원2'] = f"{매도차원2:,.0f}"

        # ----------------------------------------------------------------------------------------------
        # Stability
        # ----------------------------------------------------------------------------------------------
        
        기초수량 = int(SD['sub18'])
        
        if  타겟일수 == 0 or 타겟일수 == 1:
            매수수량3 = 0
            매수가격3 = 0.00
            매도수량3 = 0
            매도가격3 = 0.00    
            
        elif 타겟일수 >= 2 and int(SD['add9']) <= int(SD['sub18']): 
            # 테스트 상 많이 사는 것이 유리함(수량을 하루 치 더 삼, 어제일수 + 1 +1(추가분))
            찬스수량 = 0
            day_count = min(int(TD['sub12'])+1+ST['026'],6)
            for i in range(0,day_count) : 찬스수량 += my.ceil(기초수량 *(i*1.25 + 1))
                
            cpc = self.take_chance(ST['024'],int(TD['add9']),int(TD['sub2']),float(TD['add6']))
            cpn = self.take_chance(ST['023'],int(TD['add9']),int(TD['sub2']),float(TD['add6']))

            찬스가격 = cpc if float(TD['sub7']) else cpn
            찬스가격 = min(float(TD['sub19']),찬스가격)
            
            매수수량3 = 찬스수량
            매수가격3 = 찬스가격
            매도수량3 = int(SD['add9'])
            매도가격3 = float(TD['sub20'])
            
        else : # 가이드 및 투자가 진행 중일 때
            매수수량3 = int(SD['sub2'])
            매수가격3 = float(SD['sub19'])
            매도수량3 = int(SD['add9']) 
            매도가격3 = float(SD['sub20'])

        현매수금3 = float(SD['add6']) 
        매수가액3 = 매수수량3 * 매수가격3
        매도가액3 = 매도수량3 * 매도가격3
        매도차익3 = 매도가액3 - 현매수금3
        매도차원3 = 매도차익3 * float(self.D['현재환율'])
        
        sellP3 = (매도가격3/float(close_price) - 1) * 100 if 매도수량3 else 0
        self.D['현수익률3'] = SD['add8']
        self.D['매도시점3'] = f"{sellP3:.2f}"
        self.D['매수수량3'] = f"{매수수량3:,}"
        self.D['매수가격3'] = f"{매수가격3:,.2f}"
        self.D['매수가액3'] = f"{매수가액3:,.2f}"
        self.D['자산총액3'] = float(SD['add17'])
        self.D['매도수량3'] = f"{매도수량3:,}"
        self.D['매도가격3'] = f"{매도가격3:,.2f}"
        self.D['매도가액3'] = f"{매도가액3:,.2f}"
        self.D['증가비율3'] = round(float(SD['add17'])/(float(SD['sub25'])-float(SD['sub26'])) * 100,2)
        self.D['현평가금3'] = f"{float(SD['add15']):,.2f}"
        self.D['현이익금3'] = f"{float(SD['add18']):,.2f}"
        self.D['현매수금3'] = f"{현매수금3:,.2f}"
        self.D['매도차익3'] = f"{매도차익3:,.2f}"
        self.D['매도차원3'] = f"{매도차원3:,.0f}"

        총가치합 = float(VD['add17'])+float(RD['add17'])+float(SD['add17'])
        총입출입 = float(VD['sub25'])-float(VD['sub26'])+float(RD['sub25'])-float(RD['sub26'])+float(SD['sub25'])-float(SD['sub26'])
        
        self.D['증가비율0'] = round(총가치합/총입출입 * 100,2)

    def take_chance(self,p,H,n,A) :
        if H == 0 : return 0
        N = H + n
        k = N / (1+p/100)
        return round(A/(k-n),2)
    