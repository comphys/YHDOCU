import system.core.my_utils as my
from system.core.load import SKIN

class 목록_투자로그(SKIN) :

    def _auto(self) :
        
        self.TrCnt = self.D.get('Tr_cnt',0)

    def head(self) : 
        THX = {}
        TH_title = self.D['EXTITLE'] ; TH_align = self.D['EXALIGN']

        for key in self.D['list_order'] :
            THX[key] = f"<th style='text-align:{TH_align[key]}'>{TH_title[key]}</th>"
        
        THX['add0']  = f"<th style='border-top-left-radius:0;text-align:center'>날자</th>"
        THX['add14'] = f"<th style='border-top-right-radius:0;text-align:right'>자산합계</th>"
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
        
        chart_data = self.DB.get("add0,add3,r_09,s_09,n_09",assoc=True)
        
        if chart_data :

            # 다음 거래 일자 가져오기
            self.D['다음날자'], self.D['다음요일'] = self.next_stock_day(last_date)
            현재환율 = self.DB.one("SELECT CAST(usd_krw AS FLOAT) FROM usd_krw ORDER BY rowid DESC LIMIT 1")

            # 챠트 정보 가져오기
            first_date = chart_data[-1]['add0']
            self.D['총경과일'] = my.diff_day(first_date,day2=last_date)
            
            chart_span = 40
            chart_slice = len(chart_data)
            self.D['chart_start'] = chart_slice - chart_span if chart_slice > chart_span else 0
    
            chart_data.reverse()
        
            self.D['chart_date']  = [x['add0'][2:] for x in chart_data]
            self.D['close_price'] = [x['add3'] for x in chart_data]
            
            self.D['Rtactic_avg'] = [x['r_09'] if float(x['r_09']) != 0 else 'null' for x in chart_data]
            self.D['Stactic_avg'] = [x['s_09'] if float(x['s_09']) != 0 else 'null' for x in chart_data]
            self.D['Ntactic_avg'] = [x['n_09'] if float(x['n_09']) != 0 else 'null' for x in chart_data]
            
            # 다음 날 주문정보 갖고오기
            NS = self.DB.get_line("add3,r_09,r_17,r_18,r_19,r_20,s_09,s_17,s_18,s_19,s_20,n_09,n_17,n_18,n_19,n_20") 
            for name, key in [('기회','r'),('안정','s'),('생활','n')] :
                self.D['N_'+name+'매수량'] = f"{int(NS[key+'_17']):,}" if float(NS[key+'_17']) else 0
                self.D['N_'+name+'매수가'] = NS[key+'_18']
                self.D['N_'+name+'평대비'] = self.next_percent(float(NS[key+'_09']), float(NS[key+'_18']))
                self.D['N_'+name+'종대비'] = self.next_percent(float(NS['add3']), float(NS[key+'_18']))
                self.D['N_'+name+'매도량'] = f"{int(NS[key+'_19']):,}" if float(NS[key+'_19']) else 0
                self.D['N_'+name+'매도가'] = NS[key+'_20']
                self.D['N_'+name+'도평비'] = self.next_percent(float(NS[key+'_09']), float(NS[key+'_20']))
                self.D['N_'+name+'도종비'] = self.next_percent(float(NS['add3']), float(NS[key+'_20']))
                
                self.D['N_'+name+'매수가'] = f"{float(self.D['N_'+name+'매수가']):.2f}"
                self.D['N_'+name+'매도가'] = f"{float(self.D['N_'+name+'매도가']):.2f}"

            # 기타 정보 가져오기
            temp = self.DB.oneline(f"SELECT sum(CAST(r_01+s_01+n_01 AS FLOAT)), sum(CAST(r_02+s_02+n_02 AS FLOAT)), sum(CAST(r_04+s_04+n_04 AS FLOAT)), sum(CAST(r_05+s_05+n_05 AS FLOAT)) FROM {self.D['tbl']}")
            self.D['총입금합'] =  f"{temp[0]:,.2f}"
            self.D['총출금합'] =  f"{temp[1]:,.2f}"
            ls_date = self.DB.one(f"SELECT add0 FROM {self.D['tbl']} WHERE add17='수익실현' ORDER BY add0 DESC LIMIT 1")
            temp =self.DB.oneline(f"SELECT sum(CAST(r_04+s_04+n_04 AS FLOAT)), sum(CAST(r_05+s_05+n_05 AS FLOAT)) FROM {self.D['tbl']} WHERE add0<='{ls_date}'")
            self.D['총매수금'] =  f"{temp[0]:,.2f}"
            self.D['총매도금'] =  f"{temp[1]:,.2f}"
            self.D['투자익률'] =  f"{(temp[1]/temp[0]-1)*100:.2f}"
            self.D['주문확인'] =  self.DB.parameter('TX070')
            self.D['주문생활'] =  self.DB.parameter('N0710')
            self.D['주문럭키'] =  self.DB.parameter('L0500')
            
            # 통계 자료 가져오기
            temp = self.DB.exe(f"SELECT add0,CAST(add12 as float),CAST(add10 as float),CAST(r_21+s_21+n_21 as float),add17 FROM {self.D['tbl']} WHERE add17 in ('초기셋팅','수익실현') ORDER BY add0")
            l_b = b_b = cntW =  cntL = accWp = accLp = 0.0
            self.D['수익연혁'] = []
            self.D['수익통계'] = []
            for dte,bal,pro,ini,cat in temp :
                if  cat == '초기셋팅' : 
                    l_b = b_b = ini 
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
            accWp = accWp/cntW if cntW else 0.00
            accLp = accLp/cntL if cntL else 0.00
            dspan = my.diff_day('20'+self.D['수익연혁'][0][0],'20'+self.D['수익연혁'][-1][0])
            self.D['수익통계'] = [f"{dspan:,}",f"{cntA:,.0f}",f"{cntW:,.0f}",f"{cntL:,.0f}",f"{cntW/cntA*100:,.1f}",f"{cntL/cntA*100:,.1f}",f"{accWp:,.2f}",f"{accLp:,.2f}"]
            self.D['수익연혁'].reverse()
            
            # 월별 실현손익
            qry = f"SELECT SUBSTR(add0,1,7), sum(CAST(add10 as float)) FROM {self.D['tbl']} WHERE add17 = '수익실현' GROUP BY SUBSTR(add0,1,7) ORDER BY add0 DESC LIMIT 24"
            monProfit = self.DB.exe(qry)
            qry = f"SELECT SUBSTR(add0,1,7), sum(r_22+s_22+n_22) FROM {self.D['tbl']} WHERE add0 <= '{ls_date}' GROUP BY SUBSTR(add0,1,7) ORDER BY add0 DESC LIMIT 24"
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

                    elif  key == 'add8'  : 
                        if float(txt) :
                            tx[key] = f"<td style='{style}' {clas}>{float(txt):,.4f}</td>"
                        else : 
                            clas = ''; style += "color:gray;"
                            tx[key] = f"<td style='{style}'>0.00</td>"                        

                    elif key in ('add4','add10','add11','add13') :
                        if   float(txt) > 0 : clas = "class='list-bull'"
                        elif float(txt) < 0 : clas = "class='list-bear'"
                        else : clas = ''; style += "color:gray;"
                        tx[key] = f"<td style='{style}' {clas}>{float(txt):,.2f}</td>"
                        
                    elif key in ('add6') :
                        if int(txt) :
                            tx[key] = f"<td style='{style}' {clas}>{int(txt):,}</td>"
                        else :
                            clas = ''; style += "color:gray;"
                            tx[key] = f"<td style='{style}'>0</td>"                            

                    elif key in ('add7','add9','add3') :
                        if float(txt) :
                            tx[key] = f"<td style='{style}' {clas}>{float(txt):,.2f}</td>"
                        else : 
                            style += "color:gray;"
                            tx[key] = f"<td style='{style}'>0.00</td>"

                    elif key in ('add12','add14','add18','add19','add20') :
                        if item['add17'] == '수익실현' :
                            tx[key] = f"<td style='{style}' {clas}>{float(txt):,.2f}</td>"
                        else : 
                            style = "color:gray;text-align:right;"
                            tx[key] = f"<td style='{style}' {clas}>{float(txt):,.2f}</td>"
                    
                    else : 
                        tx[key] = f"<td style='{style}' {clas}>{txt}</td>"

                TR.append(tx)
                tx={}

            self.D['TR'] = TR
