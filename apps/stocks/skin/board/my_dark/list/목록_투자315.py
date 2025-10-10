import system.core.my_utils as my
from system.core.load import SKIN

class 목록_투자315(SKIN) :

    def _auto(self) :
        
        self.TrCnt = self.D.get('Tr_cnt',0)

    def head(self) : 
        THX = {}
        TH_title = self.D['EXTITLE'] ; TH_align = self.D['EXALIGN']

        for key in self.D['list_order'] :
            THX[key] = f"<th style='text-align:{TH_align[key]}'>{TH_title[key]}</th>"
            
        THX['add0']  = f"<th style='border-top-left-radius:0;text-align:center'>날자</th>"
        THX['add16'] = f"<th style='border-top-right-radius:0;text-align:right'>자산합계</th>"
        
        self.D['head_td'] = THX 


    def next_percent(self,a,b) :
        
        if not a or not b : return ''
        return f"{(b/a-1)*100:.2f}"

    def next_stock_day(self,today) :
        
        delta = 1
        while delta :
            temp = my.dayofdate(today,delta)
            weekend = 1 if temp[1] in ('토','일') else 0
            holiday = 1 if self.DB.cnt(f"SELECT key FROM parameters WHERE val='{temp[0]}' and cat='미국증시휴장일'") else 0 
            delta = 0 if not (weekend + holiday) else delta + 1
        return temp
    

    def chart(self) :
        
        last_date = self.DB.last_date(self.D['tbl'])
        
        self.DB.clear()
        self.DB.tbl = self.D['tbl']
        self.DB.wre = f"add0 <='{last_date}'"
        self.DB.odr = "add0 DESC"
        self.DB.lmt = '200'
        
        chart_data = self.DB.get("add0,add10",assoc=True)
        
        if chart_data :

            # 다음 거래 일자 가져오기
            self.D['다음날자'], self.D['다음요일'] = self.next_stock_day(last_date)
            현재환율 = self.DB.one("SELECT CAST(usd_krw AS FLOAT) FROM usd_krw ORDER BY rowid DESC LIMIT 1")

            # # 챠트 정보 가져오기
            first_date = chart_data[-1]['add0']
            stock_data = self.DB.exe(f"SELECT add0,add3 FROM h_stockHistory_board WHERE add0 >= '{first_date}' ORDER BY add0 DESC",assoc=True)
            last_date  = stock_data[0]['add0']
            self.D['총경과일'] = my.diff_day(first_date,day2=last_date)
            
            chart_span = 40
            chart_slice = len(stock_data)
            self.D['chart_start'] = chart_slice - chart_span if chart_slice > chart_span else 0
            
            chart_data.reverse()
            stock_data.reverse()
            self.D['chart_date']  = [x['add0'][2:] for x in stock_data]
            self.D['close_price'] = [x['add3'] for x in stock_data]
            self.D['Ntactic_avg'] = []
            ax = {}
            
            for C in chart_data : # 날자를 인덱스로 하는 평균값과 수익률 dict 생성
                ax[C['add0'][2:]] = float(C['add10']) if float(C['add10']) else 'null'
            
            self.D['Ntactic_avg'] = [ax[x] if x in ax else 'null' for x in self.D['chart_date']]    
                
            # 다음 날 주문정보 갖고오기
            ini_data   = self.DB.oneline(f"SELECT add18,add19 FROM {self.D['tbl']} ORDER BY add0 DESC LIMIT 1")
            ini_date = ini_data[0]
            ini_capital = f"{float(ini_data[1]):,.2f}"

            self.info(ini_data)
            
            T315 = self.SYS.load_app_lib('n315')
            NS = T315.get_nextStrategy(ini_date,last_date,ini_capital)
            
            self.D['초기금액'] = ini_capital 
            self.D['초기일자'] = ini_date 
            self.D['예정수량'] = f"{NS['예정수량']:,}" if NS['예정수량'] else 0 
            self.D['예정매가'] = f"{NS['예정매가']:.2f}" 
            self.D['매평대비'] = NS['매평대비'] 
            self.D['매종대비'] = NS['매종대비'] 
            self.D['예정도수'] = f"{NS['예정도수']:,}" if NS['예정도수'] else 0 
            self.D['예정도가'] = f"{NS['예정도가']:.2f}" 
            self.D['도평대비'] = NS['도평대비'] 
            self.D['도종대비'] = NS['도종대비'] 
            self.D['배분금액'] = f"{NS['배분금액']:,}" 
            
            self.D['타겟매가'] = NS['예정매가'] if NS['예정수량'] else 'null' 
            self.D['타겟도가'] = NS['예정도가'] if NS['예정도수'] else 'null' 
            
            # 기타 정보 가져오기
            self.D['주문확인'] =  self.DB.parameter('N0710')
            self.D['주문메인'] =  self.DB.parameter('TX070')
            self.D['주문럭키'] =  self.DB.parameter('L0500')

            # 통계 자료 가져오기
            # add5(현재잔액), add14(현재수익), add19(초기금액), add20(카테고리)
            temp = self.DB.exe(f"SELECT add0,CAST(add5 as float),CAST(add14 as float),CAST(add19 as float),add20 FROM {self.D['tbl']} WHERE add20 in ('초기셋팅','수익실현') ORDER BY add0")
            l_b = b_b = cntW =  cntL = accWp = accLp = 0.0
            self.D['수익연혁'] = []
            self.D['수익통계'] = []
            for dte,bal,pro,ini,cat in temp :
                if  cat == '초기셋팅' : 
                    l_b = b_b = ini 
                    cntW =  cntL = accWp = accLp = 0.0
                    ini_date = dte
                    self.D['수익연혁'].append([dte[2:],f"{ini:,.2f}",'0.00','0.00','0.00','0.00',cat])
                else :
                    l_p = (bal/l_b - 1)*100   
                    b_p = (bal/b_b - 1)*100
                    a_p =  bal-b_b
                    self.D['수익연혁'].append([dte[2:],f"{bal:,.2f}",f"{pro:,.2f}",f"{l_p:.2f}",f"{b_p:.2f}",f"{a_p:,.2f}",cat])
                    l_b = bal
                    
                    if  pro >= 0 : cntW += 1; accWp += l_p
                    else : cntL += 1; accLp += l_p
            
            cntA = cntW + cntL
            winCp = cntW/cntA*100 if cntA else 0.00
            LosCp = cntL/cntA*100 if cntA else 0.00
            accWp = accWp/cntW if cntW else 0.00
            accLp = accLp/cntL if cntL else 0.00
            dspan = my.diff_day(ini_date,'20'+self.D['수익연혁'][-1][0])
            self.D['수익통계'] = [f"{dspan:,}",f"{cntA:,.0f}",f"{cntW:,.0f}",f"{cntL:,.0f}",f"{winCp:,.1f}",f"{LosCp:,.1f}",f"{accWp:,.2f}",f"{accLp:,.2f}"]
            self.D['수익연혁'].reverse()



            # 월별 실현손익
            ls_date = self.DB.one(f"SELECT add0 FROM {self.D['tbl']} WHERE add20='수익실현' ORDER BY add0 DESC LIMIT 1")
            qry = f"SELECT SUBSTR(add0,1,7), sum(CAST(add14 as float)) FROM {self.D['tbl']} WHERE add20 = '수익실현' GROUP BY SUBSTR(add0,1,7) ORDER BY add0 DESC LIMIT 24"
            monProfit = self.DB.exe(qry)
            qry = f"SELECT SUBSTR(add0,1,7), sum(CAST(add21 as float)) FROM {self.D['tbl']} WHERE add0 <='{ls_date}' GROUP BY SUBSTR(add0,1,7) ORDER BY add0 DESC LIMIT 24"
            monthlyFee = self.DB.exe(qry)
            
            if monthlyFee :

                월별이익 = {x[0]:float(x[1]) for x in monProfit}
                월수수료 = {x[0]:float(x[1]) for x in monthlyFee}
                
                self.D['월별구분'] = []
                self.D['월별이익'] = []
                self.D['월수수료'] = []
                self.D['월별순익'] = []
                
                for key in 월수수료 :
                    
                    self.D['월별구분'].append(key)
                    self.D['월수수료'].append(월수수료[key])
                    if  key in 월별이익 : 
                        self.D['월별이익'].append(월별이익[key])
                        self.D['월별순익'].append(월별이익[key]-월수수료[key])
                    else : 
                        self.D['월별이익'].append(0.0)
                        self.D['월별순익'].append(-월수수료[key])
                
                self.D['월별구분'].reverse()
                self.D['월별이익'].reverse()
                self.D['월수수료'].reverse()
                self.D['월별순익'].reverse()
                    
                monthly_total = sum(self.D['월별이익'])
                monthly_ntsum = sum(self.D['월별순익'])
                monthly_lenth = len(self.D['월별이익'])
                fee_sum       = sum(self.D['월수수료'])
                
                self.D['월별구분'].append('AVG')
                self.D['월별순익'].append(round(monthly_ntsum/monthly_lenth))
                
                self.D['손익합계'] = f"$ {monthly_ntsum:,.0f} ({monthly_ntsum*현재환율:,.0f}원)" 
                
                self.D['월별순익'] = [round(x) for x in self.D['월별순익']]      
                # 누적 수익 가져오기
                self.D['실현수익'] = f"{monthly_total:,.2f}"
                self.D['수수료합'] = f"{fee_sum:,.2f}"
                self.D['누적수익'] = f"{monthly_total-fee_sum:,.2f}"      
            
            
    def list(self) :
        
        if self.TrCnt :

            self.head()
            self.chart()

            TR = [] ; tx = {}

            for item in self.D['LIST'] :

                for key in self.D['list_order'] :

                    style=clas=tmp=''
                    txt = item[key]
                    
                    if self.D['EXALIGN'][key]  : style =  f"text-align:{self.D['EXALIGN'][key]};"
                    if self.D['EXCOLOR'][key]  : style += f"color:{self.D['EXCOLOR'][key]};"
                    if self.D['EXWIDTH'][key]  : style += f"width:{self.D['EXWIDTH'][key]};"
                    if self.D['EXCLASS'][key]  : clas  =  f"class='{self.D['EXCLASS'][key]}'"
                     
                    if  key == 'add0'  : 
                        tmp = f"<td style='{style}'>"
                        href= f"{self.D['_bse']}board/modify/{self.D['bid']}/no={item['no']}/page={self.D['page']}"
                        tmp+= f"<span class='list-subject' data-href='{href}'>{txt}</span>"
                        tmp+= '</td>'
                        tx[key] = tmp
                        
                    elif  key == 'add6' : tx[key] = f"<td style='{style}' {clas}>{txt}</td>" if txt != '매수대기' else "<td>&nbsp;</td>"

                    elif  key == 'add10'  : # 평균 단가
                        if float(txt) :
                            tx[key] = f"<td style='{style}' {clas}>{float(txt):,.4f}</td>"
                        else : 
                            clas = ''; style += "color:gray;"
                            tx[key] = f"<td style='{style}'>0.00</td>"                        

                    elif key in ('add4','add14','add15') : # 손익 구분 실수
                        if   float(txt) > 0 : clas = "class='list-bull'"
                        elif float(txt) < 0 : clas = "class='list-bear'"
                        else : clas = ''; style += "color:gray;"
                        tx[key] = f"<td style='{style}' {clas}>{float(txt):,.2f}</td>"
                        
                    elif key in ('add1','add2','add7','add9') : # 정수 일반
                        if int(txt) :
                            tx[key] = f"<td style='{style}' {clas}>{int(txt):,}</td>"
                        else :
                            clas = ''; style += "color:gray;"
                            tx[key] = f"<td style='{style}'>0</td>"                            

                    elif key in ('add3','add5','add8','add11','add12','add13','add16') : # 실수 일반
                        if float(txt) :
                            tx[key] = f"<td style='{style}' {clas}>{float(txt):,.2f}</td>"
                        else : 
                            style += "color:gray;"
                            tx[key] = f"<td style='{style}'>0.00</td>"

                    else : 
                        tx[key] = f"<td style='{style}' {clas}>{txt}</td>"

                TR.append(tx)
                tx={}

            self.D['TR'] = TR
