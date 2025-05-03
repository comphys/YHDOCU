import system.core.my_utils as my
from system.core.load import SKIN

class 목록_투자로그(SKIN) :

    def _auto(self) :
        
        self.TrCnt = self.D.get('Tr_cnt',0)

    def head(self) : 
        TH_title = {'no':'번호','uname':'작성자','wdate':'작성일','mdate':'수정일','hit':'조회','uid':'아이디'}
        TH_align = {'no':'center','uname':'center','wdate':'center','mdate':'center','hit':'center','uid':'center'}
        THX = {}
        TH_title |= self.D['EXTITLE'] ; TH_align |= self.D['EXALIGN']

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
            holiday = 1 if self.DB.cnt(f"SELECT key FROM parameters WHERE val='{temp[0]}'") else 0 
            delta = 0 if not (weekend + holiday) else delta + 1
        return temp
    

    def chart(self) :
        
        last_date = self.D['LIST'][0]['add0']
        
        self.DB.clear()
        self.DB.tbl = self.D['tbl']
        self.DB.wre = f"add0 <='{last_date}'"
        self.DB.odr = "add0 DESC"
        self.DB.lmt = '200'
        
        chart_data = self.DB.get("add0,add3,r_08,r_09,s_08,s_09,n_08,n_09",assoc=True)
        
        if chart_data :

            # 다음 거래 일자 가져오기
            self.D['다음날자'], self.D['다음요일'] = self.next_stock_day(last_date)
            # 누적 수익 가져오기
            profit = self.DB.one(f"SELECT cast(sum(r_12+s_12+n_12) as float) FROM {self.D['tbl']} WHERE add17='수익실현'")
            feesum = self.DB.one(f"SELECT cast(sum(r_22+s_22+n_22) as float) FROM {self.D['tbl']}")
            if  profit : 
                self.D['실현수익'] = f"{profit:,.2f}"
                self.D['수수료합'] = f"{feesum:,.2f}"
                self.D['누적수익'] = f"{profit-feesum:,.2f}"


            # 챠트 정보 가져오기
            first_date = chart_data[-1]['add0']
            self.D['s_date'] = first_date
            self.D['e_date'] = last_date
            self.D['총경과일'] = my.diff_day(first_date,day2=last_date)
            
            chart_span = 40
            chart_slice = len(chart_data)
            self.D['chart_start'] = chart_slice - chart_span if chart_slice > chart_span else 0
    
            chart_data.reverse()
        
            self.D['chart_date']  = [x['add0'][2:] for x in chart_data]
            self.D['close_price'] = [x['add3'] for x in chart_data]
            
            self.D['Rtactic_avg'] = [x['r_09'] if float(x['r_09']) != 0 else 'null' for x in chart_data]
            self.D['Rtactic_pro'] = [x['r_08'] if float(x['r_08']) != 0 else 'null' for x in chart_data]
            self.D['Stactic_avg'] = [x['s_09'] if float(x['s_09']) != 0 else 'null' for x in chart_data]
            self.D['Stactic_pro'] = [x['s_08'] if float(x['s_08']) != 0 else 'null' for x in chart_data]
            self.D['Ntactic_avg'] = [x['n_09'] if float(x['n_09']) != 0 else 'null' for x in chart_data]
            self.D['Ntactic_pro'] = [x['n_08'] if float(x['n_08']) != 0 else 'null' for x in chart_data]
            
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
            temp = self.DB.oneline(f"SELECT sum(CAST(r_01+s_01+n_01 AS FLOAT)), sum(CAST(r_02+s_02+n_02 AS FLOAT)) FROM {self.D['tbl']}")
            self.D['총입금'] =  f"{temp[0]:,.2f}"
            self.D['총출금'] =  f"{temp[1]:,.2f}"
        
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
                        
                    elif key in ('add4','add10','add11') :
                        if   float(txt) > 0 : clas = "class='list-bull'"
                        elif float(txt) < 0 : clas = "class='list-bear'"
                        else : clas = ''; style += "color:gray;"
                        tx[key] = f"<td style='{style}' {clas}>{float(txt):.2f}</td>"
                        
                    elif key in ('add6') :
                        tx[key] = f"<td style='{style}' {clas}>{int(txt):,}</td>"

                    elif key in ('add7','add9','add18','add19','add20','add12','add14','add3') :
                        tx[key] = f"<td style='{style}' {clas}>{float(txt):,.2f}</td>"
                    
                    else : 
                        tx[key] = f"<td style='{style}' {clas}>{txt}</td>"

                TR.append(tx)
                tx={}

            self.D['TR'] = TR
