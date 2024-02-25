from system.core.load import Model
import system.core.my_utils as my

class M_dashboard2(Model) :

    def view(self) :
        ST = self.DB.parameters_dict('매매전략/VRS')
        self.M['boards'] = [ST['035'],ST['036'],ST['037']]
        self.M['monthlyProfit'] = {}
        self.M['eachSellTotal'] = {} 

        self.M['구간시작'] = self.gets.get('ss','')
        self.M['구간종료'] = self.gets.get('se','')
        
        if  self.M['구간종료'] :
            self.D['오늘날자']  = self.M['구간종료']
            self.D['오늘요일']  = my.dayofdate(self.D['오늘날자'])
            self.D['현재환율']  = float(self.DB.one(f"SELECT usd_krw FROM usd_krw WHERE date <='{self.M['구간종료']}' ORDER BY rowid DESC LIMIT 1"))
            self.D['chk_off'] = "특정 구간 확인 모드입니다."
        else :
            self.D['오늘날자']  = my.timestamp_to_date(opt=7) 
            self.D['오늘요일']  = my.dayofdate(self.D['오늘날자'])
            self.D['현재환율']  = float(self.DB.one("SELECT usd_krw FROM usd_krw ORDER BY rowid DESC LIMIT 1")) 
                    
        self.progressGraph()
        self.monthlyProfitTotal()
        self.total_value_allot()
        self.show_strategy(ST)   
           
    def progressGraph(self) :
        
        cond = f" WHERE add0 <= '{self.M['구간종료']}' " if self.M['구간종료'] else ''

        self.D['최종날자'] = last_date = self.DB.one(f"SELECT max(add0) FROM {self.M['boards'][0]} {cond}")
        self.D['최종요일']  = my.dayofdate(self.D['최종날자'])

        self.DB.clear()
        self.DB.tbl = self.M['boards'][0]
        self.DB.wre = f"add0 <='{last_date}'"
        self.DB.odr = "add0 DESC"

        if  self.M['구간시작'] : 
            self.DB.wre += f" AND add0 >= '{self.M['구간시작']}'"
        else : 
            self.DB.lmt = '200'        
        
        chart_data = self.DB.get("add0,add14,add17,add7,sub28,add8",assoc=True)
        if chart_data :

            first_date = chart_data[-1]['add0']
            self.D['s_date'] = first_date
            self.D['e_date'] = last_date
            self.D['총경과일'] = my.diff_day(first_date,day2=last_date)

            chart_span = 40
            chart_slice = len(chart_data)
            self.D['chart_start'] = chart_slice - chart_span if chart_slice > chart_span else 0
    
            chart_data.reverse()     

            self.D['chart_date']  = [x['add0'][2:] for x in chart_data]
            self.D['close_price'] = [float(x['add14']) for x in chart_data]; 
            self.D['Vtactic_avg'] = ['null' if not float(x['add7']) else float(x['add7']) for x in chart_data]
            self.D['Vtactic_pro'] = [float(x['add8']) for x in chart_data]   

            self.D['최종종가'] = self.D['close_price'][-1]
            self.D['종가변동'] = self.percent_diff(float(self.D['close_price'][-2]),float(self.D['최종종가']))
        
            cond = f"add0 BETWEEN '{first_date}' AND '{last_date}'"
            RD = self.DB.exe(f"SELECT add0,CAST(add7 as FLOAT),CAST(add8 as FLOAT),CAST(add9 as INT),CAST(add17 as FLOAT) FROM {self.M['boards'][1]} WHERE {cond}") 
            SD = self.DB.exe(f"SELECT add0,CAST(add7 as FLOAT),CAST(add8 as FLOAT),CAST(add9 as INT),CAST(add17 as FLOAT) FROM {self.M['boards'][2]} WHERE {cond}") 

            cx = {};dx = {}
            self.D['Rtactic_avg'] = []; self.D['Rtactic_pro'] = []
            if RD :
                for c in RD : 
                    if c[3] : cx[c[0][2:]] = c[1]
                    if c[2] or c[3]: dx[c[0][2:]] = c[2]
                for x in self.D['chart_date'] : self.D['Rtactic_avg'].append(cx.get(x,'null')); self.D['Rtactic_pro'].append(dx.get(x,'null')) 
                
            cx.clear();dx.clear()
            self.D['Stactic_avg'] = []; self.D['Stactic_pro'] = []
            if SD :
                for c in SD : 
                    if c[3] : cx[c[0][2:]] = c[1]
                    if c[2] or c[3] : dx[c[0][2:]] = c[2]
                for x in self.D['chart_date'] : self.D['Stactic_avg'].append(cx.get(x,'null')); self.D['Stactic_pro'].append(dx.get(x,'null'))
                
            # 매도한 날 매도금 합 가져오기
            for bid in self.M['boards'] :
                qry = f"SELECT SUBSTR(add0,3,10), CAST(add18 as float) FROM {bid} WHERE CAST(add12 as float) > 0 and {cond}"
                eachSellTotal = dict(self.DB.exe(qry))
                self.merge_dict(self.M['eachSellTotal'],eachSellTotal)
            
            self.D['eachSellTotal'] = []
            for x in self.D['chart_date'] : self.D['eachSellTotal'].append(self.M['eachSellTotal'].get(x,'null'))
            
           
    def monthlyProfitTotal(self) :

        for bid in self.M['boards'] :
            qry = f"SELECT SUBSTR(add0,1,7), sum( CAST(add18 as float)) FROM {bid} WHERE CAST(add12 as float) > 0 "
            if  self.M['구간종료'] : 
                qry += f" AND add0 BETWEEN '{self.M['구간시작']}' AND '{self.M['구간종료']}' "
            qry += "GROUP BY SUBSTR(add0,1,7) ORDER BY add0 DESC LIMIT 24"
            
            monthlyProfit = dict(self.DB.exe(qry))
            self.merge_dict(self.M['monthlyProfit'],monthlyProfit)
 
        if self.M['monthlyProfit'] :
            self.D['월별구분'] = list(self.M['monthlyProfit'].keys())
            self.D['월별이익'] = list(self.M['monthlyProfit'].values())
            monthly_total = sum(self.D['월별이익'])
            monthly_lenth = len(self.D['월별이익'])
            
            self.D['월별구분'].reverse()  
            self.D['월별이익'].reverse()
            self.D['월별구분'].append('AVG')
            self.D['월별이익'].append(monthly_total/monthly_lenth)
            self.D['월별이익'] = [int(x) for x in self.D['월별이익']] # list(map(int,self.D['월별이익']))
            self.D['손익합계'] = f"$ {monthly_total:,.0f} ({monthly_total*self.D['현재환율']:,.0f}원)"
        

    def total_value_allot(self) :
        self.D['E자산분배1'] = self.D['E자산분배2'] = self.D['E자산분배3'] = "{YH:0, YW:0, HJ:0, YG:0}"
        self.D['E자산총액1'] = self.D['E자산총액2'] = self.D['E자산총액3'] = 0.0

        self.D['환율표기']  = f"{self.D['현재환율']:,.1f}"

        self.D['처음순증'] = []
        for odr in [0,1,2] :
            cond = f"WHERE add0 <= '{self.D['s_date']}'"  
            qry = f"SELECT add17, sub25, sub26 FROM {self.M['boards'][odr]} {cond} ORDER BY add0 DESC LIMIT 1"
            qrs = self.DB.exe(qry)
            if not qrs : qrs=[('0','0','0'),]
            rst = qrs[0] 
            key = str(odr+1)
            self.M['S자산총액'+key] = float(rst[0])
            self.M['S총입금액'+key] = float(rst[1])
            self.M['S총출금액'+key] = float(rst[2])
            self.M['S순자증액'+key] = self.M['S자산총액'+key]-self.M['S총입금액'+key]+self.M['S총출금액'+key]
            self.D['처음순증'].append(self.M['S순자증액'+key])


        self.D['나중순증'] = []
        for odr in [0,1,2] :
            cond = f"WHERE add0 <= '{self.D['e_date']}'" 
            qry = f"SELECT add10, add17, sub25, sub26 FROM {self.M['boards'][odr]} {cond} ORDER BY add0 DESC LIMIT 1"
            qrs = self.DB.exe(qry)
            if not qrs : qrs=[('{YH:0, YW:0, HJ:0, YG:0}','0','0','0'),]
            rst = qrs[0] 
            key = str(odr+1)
            self.D['E자산분배'+key] = rst[0]
            self.D['E자산총액'+key] = float(rst[1])
            self.M['E총입금액'+key] = float(rst[2])
            self.M['E총출금액'+key] = float(rst[3])
            self.M['E순자증액'+key] = self.D['E자산총액'+key]-self.M['E총입금액'+key]+self.M['E총출금액'+key]
            self.D['나중순증'].append(self.M['E순자증액'+key])
        
            
    def show_strategy(self,ST) :

        if self.M['구간종료'] : return
        self.D['증권계좌1'] = ST['031']; self.D['식별색상1'] = "#f78181"
        self.D['증권계좌2'] = ST['032']; self.D['식별색상2'] = "yellow" 
        self.D['증권계좌3'] = ST['033']; self.D['식별색상3'] = "lightgreen"

        today = self.DB.one("SELECT add0 FROM h_stockHistory_board WHERE add1='SOXL' ORDER BY add0 DESC LIMIT 1")
        
        self.D['추정합계'] = 0.0
        
        for odr in [0,1,2] :
            qry = f"SELECT CAST(sub2 as INT), CAST(sub19 as float), CAST(sub3 as INT), CAST(sub20 as float),sub1,sub12,add3,add8,add7,add4,add0,add6 FROM {self.M['boards'][odr]} ORDER BY add0 DESC LIMIT 1"
            rst = self.DB.oneline(qry)
            key = str(odr+1)
            self.D['매수수량'+key] = rst[0] if rst[0] else ''
            self.D['매수가격'+key] = rst[1] if rst[0] else ''
            self.D['타겟지점'+key] = self.percent_diff(float(self.D['최종종가']),rst[1]) if rst[0] else ''
            self.D['매도수량'+key] = rst[2] if rst[2] else ''
            self.D['매도가격'+key] = rst[3] if rst[2] else ''
            매도금액 = rst[2]*rst[3]
            self.D['매도금액'+key] = f"{매도금액:,.2f}" if rst[2] else ''
            self.D['현재시즌'+key] = rst[4]
            self.D['현재일수'+key] = rst[5]
            self.D['현재잔액'+key] = f"{float(rst[6]):,.2f}"
            self.D['현수익률'+key] = rst[7]
            self.D['평균단가'+key] = rst[8]
            self.D['현금비중'+key] = rst[9]
            if today != rst[10] : self.D['증권계좌'+key] = "확인필요"
            
            # 추정이익 계산
            추정손익 = rst[2]*rst[3] - float(rst[11]); self.D['추정합계'] += 추정손익
            self.D['추정손익'+key] = f"{추정손익 * self.D['현재환율']:,.0f}" if rst[2] else ''
        
        self.D['추정합계'] = f"{self.D['추정합계']* self.D['현재환율']:,.0f}" if self.D['추정합계'] else ''
        self.D['필요상승'] = self.percent_diff(float(self.D['최종종가']),self.D['매도가격1']) 
            
            
        chk_off = self.DB.exe(f"SELECT description FROM parameters WHERE val='{self.D['오늘날자']}' AND cat='미국증시휴장일'")
        self.D['chk_off'] = chk_off[0][0] if chk_off else ''    

        if  self.D['증권계좌3'] == "확인필요" : self.D['chk_off'] = "Not all information is updated. Please Check it."

        if  self.D['오늘요일'] in ('토','일') : self.D['chk_off'] = "Today is weekend. Take a rest!" 

        return

    def percent_diff(self,a,b) :
        if not a or not b : return ''
        return f"{(b/a - 1) * 100:.2f}%"        
    
    def merge_dict(self,A,B) :
        
        for k in B : A[k] = B[k] if k not in A.keys() else A[k] + B[k]    
        