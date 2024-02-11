from system.core.load import Model
import system.core.my_utils as my

class M_dashboard2(Model) :

    def view(self) :
        ST = self.DB.parameters_dict('매매전략/VRS')
        self.M['boards'] = [ST['035'],ST['036'],ST['037']]
        self.M['monthlyProfit'] = {}
        self.M['eachSellTotal'] = {} 

        self.D['오늘날자']  = my.timestamp_to_date(opt=7) 
        self.D['오늘요일']  = my.dayofdate(self.D['오늘날자'])
        
        self.monthlyProfitTotal()
        self.progressGraph()
        self.total_value_allot()
        self.show_strategy(ST)
        

    
    def progressGraph(self) :
        
        # add7 평균단가, add8 현수익률, add9 보유수량
        self.D['최종날자'] = last_date = self.DB.one(f"SELECT max(add0) FROM {self.M['boards'][0]}")
        self.D['최종요일']  = my.dayofdate(self.D['최종날자'])
        
        self.DB.clear()
        self.DB.tbl = self.M['boards'][0]
        self.DB.wre = f"add0 <='{last_date}'"
        self.DB.odr = "add0 DESC"
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
        
            self.DB.clear(); self.DB.wre = f"add0='{last_date}'"
            
            self.DB.tbl = self.M['boards'][1]
            RD = self.DB.exe(f"SELECT add0,CAST(add7 as FLOAT),CAST(add8 as FLOAT),CAST(add9 as INT),CAST(add17 as FLOAT) FROM {self.DB.tbl} WHERE add0 BETWEEN '{first_date}' AND '{last_date}'") 
            self.DB.tbl = self.M['boards'][2]
            SD = self.DB.exe(f"SELECT add0,CAST(add7 as FLOAT),CAST(add8 as FLOAT),CAST(add9 as INT),CAST(add17 as FLOAT) FROM {self.DB.tbl} WHERE add0 BETWEEN '{first_date}' AND '{last_date}'") 

            cx = {};dx = {}
            self.D['Rtactic_avg'] = []; self.D['Rtactic_pro'] = []
            if RD :
                for c in RD : 
                    if c[3] : cx[c[0][2:]] = c[1]
                    if c[2] or c[3]: dx[c[0][2:]] = c[2]
                for x in self.D['chart_date'] : self.D['Rtactic_avg'].append(cx.get(x,'null')); self.D['Rtactic_pro'].append(dx.get(x,'null')) 
                
            cx = {};dx = {}
            self.D['Stactic_avg'] = []; self.D['Stactic_pro'] = []
            if SD :
                for c in SD : 
                    if c[3] : cx[c[0][2:]] = c[1]
                    if c[2] or c[3] : dx[c[0][2:]] = c[2]
                for x in self.D['chart_date'] : self.D['Stactic_avg'].append(cx.get(x,'null')); self.D['Stactic_pro'].append(dx.get(x,'null'))
                
            # self.D['표준편차'] = numpy.std(self.D['close_price'])

            # 매도한 날 매도금 합 가져오기
            for bid in self.M['boards'] :
                qry = f"SELECT SUBSTR(add0,3,10), CAST(add18 as float) FROM {bid} WHERE CAST(add12 as float) > 0 and add0 BETWEEN '{first_date}' AND '{last_date}'"
                eachSellTotal = dict(self.DB.exe(qry))
                self.merge_dict(self.M['eachSellTotal'],eachSellTotal)
            
            self.D['eachSellTotal'] = []
            for x in self.D['chart_date'] : self.D['eachSellTotal'].append(self.M['eachSellTotal'].get(x,'null'))
            
           
    
    def monthlyProfitTotal(self) :
        # 월별 실현손익
        for bid in self.M['boards'] :
            qry = f"SELECT SUBSTR(add0,1,7), sum( CAST(add18 as float)) FROM {bid} WHERE CAST(add12 as float) > 0 "
            qry += "GROUP BY SUBSTR(add0,1,7) ORDER BY add0 DESC LIMIT 24"
            monthlyProfit = dict(self.DB.exe(qry))
            self.merge_dict(self.M['monthlyProfit'],monthlyProfit)
        
        self.D['월별구분'] = list(self.M['monthlyProfit'].keys())
        self.D['월별이익'] = list(self.M['monthlyProfit'].values())
        monthly_total = sum(self.D['월별이익'])
        monthly_lenth = len(self.D['월별이익'])
        
        self.D['월별구분'].reverse()  
        self.D['월별이익'].reverse()
        self.D['월별구분'].append('AVG')
        self.D['월별이익'].append(monthly_total/monthly_lenth)
        self.D['월별이익'] = [int(x) for x in self.D['월별이익']] # list(map(int,self.D['월별이익']))
        

    def total_value_allot(self) :
        
        self.D['현재환율']  = float(self.DB.one("SELECT usd_krw FROM usd_krw ORDER BY rowid DESC LIMIT 1"))
        self.D['환율표기']  = f"{self.D['현재환율']:,.1f}"
        for odr in [0,1,2] :
            qry = f"SELECT add10, add17, sub25, sub26 FROM {self.M['boards'][odr]} ORDER BY add0 DESC LIMIT 1"
            rst = self.DB.oneline(qry)
            key = str(odr+1)
            self.D['자산분배'+key] = rst[0]
            self.D['자산총액'+key] = float(rst[1])
            self.D['총입금액'+key] = float(rst[2])
            self.D['총출금액'+key] = float(rst[3])
            self.D['증가비율'+key] = round(self.D['자산총액'+key]/(self.D['총입금액'+key]-self.D['총출금액'+key])* 100,2)
            
        총가치합 = self.D['자산총액1']+self.D['자산총액2']+self.D['자산총액3']
        총입출입 = self.D['총입금액1']-self.D['총출금액1']+self.D['총입금액2']-self.D['총출금액2']+self.D['총입금액3']-self.D['총출금액3']
        
        self.D['증가비율0'] = round(총가치합/총입출입 * 100,2)    
            
    def show_strategy(self,ST) :
        self.D['Vtactic'] = ST['031']
        self.D['Rtactic'] = ST['032'] 
        self.D['Stactic'] = ST['033']
        
        chk_off = self.DB.exe(f"SELECT description FROM parameters WHERE val='{self.D['오늘날자']}' AND cat='미국증시휴장일'")
        self.D['chk_off'] = chk_off[0][0] if chk_off else ''

        for odr in [0,1,2] :
            qry = f"SELECT CAST(sub2 as INT), CAST(sub19 as float), CAST(sub3 as INT), CAST(sub20 as float),sub1,sub12,add3,add8,add9,add7,add4 FROM {self.M['boards'][odr]} ORDER BY add0 DESC LIMIT 1"
            rst = self.DB.oneline(qry)
            key = str(odr+1)
            self.D['매수수량'+key] = rst[0]
            self.D['매수가격'+key] = rst[1] if rst[0] else ' '
            self.D['매수금액'+key] = f"{rst[0]*rst[1]:,.2f}" if rst[0] else ' '
            self.D['매도수량'+key] = rst[2]
            self.D['매도가격'+key] = rst[3] if rst[2] else ' '
            self.D['매도금액'+key] = f"{rst[2]*rst[3]:,.2f}" if rst[2] else ' '
            self.D['현재시즌'+key] = rst[4]
            self.D['현재일수'+key] = rst[5]
            self.D['현재잔액'+key] = f"{float(rst[6]):,.2f}"
            self.D['현수익률'+key] = rst[7]
            self.D['보유수량'+key] = rst[8]
            self.D['평균단가'+key] = rst[9]
            self.D['현금비중'+key] = rst[10]
        
        return

            
    
    def merge_dict(self,A,B) :
        
        for k in B : A[k] = B[k] if k not in A.keys() else A[k] + B[k]    
        