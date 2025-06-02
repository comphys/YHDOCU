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
        
        chart_data = self.DB.get("add0,add10,add15",assoc=True)
        
        if chart_data :

            # 다음 거래 일자 가져오기
            self.D['다음날자'], self.D['다음요일'] = self.next_stock_day(last_date)
            # 누적 수익 가져오기
            profit = self.DB.one(f"SELECT cast(sum(add14) as float) FROM {self.D['tbl']} WHERE add17='수익실현'")
            feesum = self.DB.one(f"SELECT cast(sum(add21) as float) FROM {self.D['tbl']}")
            if  profit : 
                self.D['실현수익'] = f"{profit:,.2f}"
                self.D['수수료합'] = f"{feesum:,.2f}"
                self.D['누적수익'] = f"{profit-feesum:,.2f}"


            # # 챠트 정보 가져오기
            first_date = chart_data[-1]['add0']
            stock_data = self.DB.exe(f"SELECT add0,add3 FROM h_stockHistory_board WHERE add0 >= '{first_date}' ORDER BY add0 DESC",assoc=True)
            last_date  = stock_data[0]['add0']
            self.D['s_date'] = first_date
            self.D['e_date'] = stock_data[-1]['add0']
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
            
            for x in self.D['chart_date'] :    
                self.D['Ntactic_avg'].append(ax.get(x,'null'))
                
                
            # 다음 날 주문정보 갖고오기
            ini_data   = self.DB.oneline(f"SELECT add18,add19 FROM {self.D['tbl']}")
            ini_date = ini_data[0]
            ini_capital = f"{float(ini_data[1]):,.2f}"
            
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
                        tx[key] = f"<td style='{style}' {clas}>{float(txt):.2f}</td>"
                        
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
