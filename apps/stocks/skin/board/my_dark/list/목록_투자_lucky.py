import system.core.my_utils as my
from system.core.load import SKIN

class 목록_투자_lucky(SKIN) :

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
        
        last_date = self.DB.last_date('h_stockHistory_board')
        self.D['다음날자'],self.D['다음요일'] = self.next_stock_day(last_date)
        
        self.DB.clear()
        self.DB.tbl = 'h_stockHistory_board'
        self.DB.wre = f"add0 <='{last_date}' and add1='SOXL'"
        self.DB.odr = "add0 DESC"
        self.DB.lmt = '25'
        
        chart_data = self.DB.get("add0,add3",assoc=True)
        rsn_V_data = self.DB.exe(f"SELECT add0,v_09 FROM h_rsnLog_board WHERE add0 <='{last_date}' ORDER BY add0 DESC LIMIT {self.DB.lmt}",assoc=True)

        chart_len  = len(chart_data)
        chart_data.reverse()
        rsn_V_data.reverse()
        self.D['chart_date']  = [x['add0'][2:] for x in chart_data]
        self.D['close_price'] = [x['add3'] for x in chart_data]
        self.D['rsn_V_price'] = [x['v_09'] if x['add0'][2:] in self.D['chart_date'] else 'null' for x in rsn_V_data ]
        self.D['rsn_V_price'] = [x if float(x) else 'null' for x in self.D['rsn_V_price']]

        self.D['기준가격'] = ['null'] * chart_len
        self.D['매수가격'] = ['null'] * chart_len
        self.D['매도가격'] = ['null'] * chart_len
        
        ST = self.DB.parameters_dict('매매전략/LUCKY')
        self.D['진행시작'] = False
        
        if  int(ST['L0200']) :  # 진행중인 시즌 정보를 불러옴, '0'인 경우 진행중이지 않음

            self.D['진행시작'] = True
            
            self.D['주문확인'] = ST['L0500']
            

                    

                
    def list(self) :
        self.chart()
        
        if self.TrCnt :

            self.head()

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
                        
                    elif  key == 'add16' : tx[key] = f"<td style='{style}' {clas}>{txt}</td>" if txt != '매수대기' else "<td>&nbsp;</td>"

                    elif  key == 'add9'  : # 평균 단가
                        if float(txt) :
                            tx[key] = f"<td style='{style}' {clas}>{float(txt):,.4f}</td>"
                        else : 
                            clas = ''; style += "color:gray;"
                            tx[key] = f"<td style='{style}'>0.00</td>"                        

                    elif key in ('add4','add13','add14') : # 손익 구분 실수
                        if   float(txt) > 0 : clas = "class='list-bull'"
                        elif float(txt) < 0 : clas = "class='list-bear'"
                        else : clas = ''; style += "color:gray;"
                        tx[key] = f"<td style='{style}' {clas}>{float(txt):,.2f}</td>"
                        
                    elif key in ('add1','add2','add6','add8') : # 정수 일반
                        if int(txt) :
                            tx[key] = f"<td style='{style}' {clas}>{int(txt):,}</td>"
                        else :
                            clas = ''; style += "color:gray;"
                            tx[key] = f"<td style='{style}'>0</td>"                            

                    elif key in ('add3','add5','add7','add10','add11','add12','add15') : # 실수 일반
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
