import system.core.my_utils as my
from system.core.load import SKIN

class 목록_INVEST(SKIN) :

    def _auto(self) :
        self.TrCnt = self.D.get('Tr_cnt',0)
        self.Type = self.D['BCONFIG']['type']
        
    def head(self) : 
        TH_title = {'no':'번호','uname':'작성자','wdate':'작성일','mdate':'수정일','hit':'조회','uid':'아이디'}
        TH_align = {'no':'center','uname':'center','wdate':'center','mdate':'center','hit':'center','uid':'center'}
        THX = {}
        TH_title |= self.D['EXTITLE'] ; TH_align |= self.D['EXALIGN']

        for key in self.D['list_order'] :
            if   key == self.D['Sort']  : THX[key] = f"<th class='list-sort'  onclick=\"sort_go('{key}')\" style='text-align:{TH_align[key]}'>{TH_title[key]}</th>"
            elif key == self.D['Sort1'] : THX[key] = f"<th class='list-sort1' onclick=\"sort_go('{key}')\" style='text-align:{TH_align[key]}'>{TH_title[key]}</th>"
            else : THX[key] = f"<th class='list-sort2' onclick=\"sort_go('{key}')\" style='text-align:{TH_align[key]}'>{TH_title[key]}</th>"
        
        self.D['head_td'] = THX

    def chart(self) :
        self.DB.clear()
        self.DB.tbl = self.D['tbl']
        self.DB.odr = "add0 DESC"

        date1 = self.SYS.gets.get('date1','')
        date2 = self.SYS.gets.get('date2','')
        self.DB.wre = f"add0 >='{date1}' and add0 <= '{date2}'" if date1 and date2 else ''

        chart_data = self.DB.get("add0,add14,add17,add7,sub28,add8",assoc=True)

        if chart_data :

            first_date = chart_data[-1]['add0']
            last_date  = chart_data[ 0]['add0']
            self.D['s_date'] = first_date
            self.D['e_date'] = last_date
            self.D['총경과일'] = my.diff_day(first_date,day2=last_date)

            chart_span = 200
            chart_slice = len(chart_data)
            self.D['chart_start'] = chart_slice - chart_span if chart_slice > chart_span else 0

            chart_data.reverse()
        
            self.D['chart_date']   = [x['add0'][2:] for x in chart_data]
            self.D['close_price']  = [float(x['add14']) for x in chart_data]; close_base = self.D['close_price'][0]
            self.D['close_change'] = [round((x-close_base) / close_base * 100,2) for x in self.D['close_price']]
            self.D['total_value']  = [float(x['add17']) for x in chart_data]; total_base = self.D['total_value'][0]
            self.D['total_profit'] = [round((x-total_base) / total_base * 100,2) for x in self.D['total_value']]
            self.D['soxl_average'] = ['null' if not float(x['add7']) else float(x['add7']) for x in chart_data]
            self.D['lever_change'] = [float(x['add8']) for x in chart_data]
            self.D['sell_price']   = ['null'] * len(chart_data)
            self.D['chance_price'] = ['null'] * len(chart_data)

            self.DB.clear()
            self.DB.tbl = self.D['tbl']
            self.DB.wre = f"add0='{last_date}'"
            
            LD = self.DB.get_line('add4,add6,add7,add9,add14,add15,add16,add17,add19,add20,sub1,sub2,sub3,sub4,sub12,sub14,sub5,sub6,sub15,sub18,sub19,sub20,sub25,sub26,sub27,sub32')
            
            # 가치 비율 for chart
            운용자금 = my.sv(LD['add19']) + my.sv(LD['add20'])
            예치자금 = my.sv(LD['sub32'])
            주식가치 = my.sv(LD['add15'])
            가치합계 = 운용자금 + 예치자금 + 주식가치
            self.D['chart_percent'] = [round(운용자금/가치합계*100,2),round(예치자금/가치합계*100,2),round(주식가치/가치합계*100,2)]

            # -- 환율 가져오기
            # 현재환율 = float(self.DB.one("SELECT usd_krw FROM usd_krw WHERE no=(SELECT max(no) FROM usd_krw)"))
            현재환율 = float(self.DB.one("SELECT usd_krw FROM usd_krw ORDER BY rowid DESC LIMIT 1"))
            
            # --------------

            총투자금 = float(LD['sub27'])
            총수익금 = float(LD['add17']) - 총투자금
            총수익률 = (float(LD['add17'])/총투자금-1) * 100 if 총투자금 else 0
            self.D['총입금'] = f"{float(LD['sub25']):,.0f}"
            self.D['총출금'] = f"{float(LD['sub26']):,.0f}"
            현재총액 = float(LD['add17'])
            self.D['현재총액'] = f"{현재총액:,.0f}"
            self.D['원화총액'] = f"{현재총액 * 현재환율:,.0f}"
            self.D['총수익금'] = f"{총수익금:,.0f}"
            # self.D['원화수익'] = f"{총수익금 * 현재환율:,.0f}"
            self.D['총수익률'] = f"{총수익률:.2f}"
            
            # -- leverage
            self.D['매수금'] = float(LD['sub14'])
            self.D['매도금'] = float(LD['sub15'])
            현재평가 = self.D['매도금']  +  float(LD['add15'])
            수익금2 = 현재평가 - self.D['매수금'] 
            평단가2 = float(LD['add7'])
            수익률2 = (수익금2 / self.D['매수금'] * 100) if self.D['매수금'] else 0
            self.D['평단가2'] = f"{평단가2:,.4f}"
            self.D['수익금2'] = f"{수익금2:,.2f}"
            self.D['수익률2'] = f"{수익률2:.2f}"
            self.D['현재평가'] = f"{현재평가:,.2f}"

            self.D['매수금'] = f"{self.D['매수금']:,.2f}"
            self.D['매도금'] = f"{self.D['매도금']:,.2f}"

            # -- extra-info
            self.D['현매수금'] = f"{float(LD['add6']):,}"
            self.D['현이익률'] = f"{(float(LD['add14'])/평단가2 - 1)*100:,.2f}" if 평단가2 else '0.0'
            self.D['현재시즌'] = LD['sub1'] ; 일수 = int(LD['sub12']); 시즌 = int(self.D['현재시즌'])
            if 일수 == 0 : 시즌 -= 1
            # self.D['시즌첫날'] = self.DB.one(f"SELECT add0 FROM {self.D['tbl']} WHERE sub1='{시즌}' and sub12 =='1'")
            self.D['단기첫날'] = '20'+self.D['chart_date'][-40]
            self.D['경과일수'] = f"{int(LD['sub12']):02d}"

            self.D['매수갯수'] = int(LD['sub2'])
            self.D['매수단가'] = f"{float(LD['sub19']):,.2f}"
            self.D['매수예상'] = f"{(int(LD['sub2']) * float(LD['sub19'])):,.2f}"
            self.D['매도갯수'] = int(LD['sub3'])
            self.D['매도단가'] = f"{float(LD['sub20']):,.2f}"
            self.D['매도예상'] = f"{(int(LD['sub3']) * float(LD['sub20'])):,.2f}"
            예상이익 = float(self.D['매도예상'].replace(',','')) - float(LD['add6'].replace(',',''))
            self.D['예상이익'] = f"{예상이익:,.2f}"
            self.D['연속상승'] = LD['sub5']
            self.D['연속하락'] = LD['sub6']
            self.D['현재환율'] = f"{현재환율:,.2f}"
            찬스가격 = self.take_chance(-5,int(LD['add9']),int(LD['sub2']),float(LD['add6'])) 
            self.D['찬스가격'] = self.D['매도단가'] if 찬스가격 == 0 else 찬스가격
            
            # ------------- 기회 투자 전략 

            if 일수 >= 2 :

                가용잔액 = int( 예치자금 * 2/3)
                일매수금 = int(가용잔액/22)
                매수비율 = 일매수금 / int(LD['sub4']) 
                기초수량 = int(매수비율 * int(LD['sub18']))

                찬스수량 = 0    
                for i in range(0,일수+1) : 
                    찬스수량 += my.ceil(기초수량 *(i*1.25 + 1))

                self.D['찬스일자'] = last_date
                self.D['찬스가오'] = f"{찬스가격:,.2f}"
                self.D['찬스수량'] = f"{찬스수량:,}"
                self.D['찬스자본'] = f"{찬스가격*찬스수량:,.2f}"
                self.D['찬스일수'] = 일수
                self.D['찬스주가'] = LD['add14']
                self.D['찬스변동'] = round((찬스가격/float(LD['add14']) -1) * 100,2)
                self.D['찬스하강'] = LD['sub6']
                self.D['환율변환'] = f"{찬스가격*찬스수량* 현재환율:,.0f}"
                self.D['기초환율'] = f"{현재환율:,.2f}"

    
    def take_chance(self,p,H,n,A) :
        if H == 0 : return 0
        N = H + n
        k = N / (1+p/100)
        return round(A/(k-n),2)

    def list(self) :
        self.head()
        self.chart()

        TR = [] ; tx = {}

        if self.TrCnt :
            self.D['cno'] = -1 ; TrCnt = self.TrCnt

            for idx,item in enumerate(self.D['LIST']) :

                if int(item['no']) == int(self.D['No']) : self.D['cno'] = idx ; cno = True 
                else : cno = False
                
                for key in self.D['list_order'] :

                    style=clas=tmp=''
                    txt = item[key]

                    if   key == 'no'    : 
                        if cno : tx[key] = "<td class='list-current-no'><i class='fa fa-edit'></i></td>"
                        else   : tx[key] = f"<td class='list-no'>{TrCnt}</td>"
                        TrCnt -= 1

                    elif key == 'add8' : 
                        profit = float(txt)
                        if profit != 0 : 
                            tx[key] = f"<td class='list-bulls'>{profit:,.2f}</td>" if profit > 0  else f"<td class='list-bears'>{profit:,.2f}</td>"
                        else : 
                            tx[key] = "<td class='list-normal'>0.00</td>"

                    elif key == 'add18' : 
                        profit = float(txt.replace(',',''))
                        if profit != 0 : 
                            tx[key] = f"<td class='list-bulls2'>{profit:,.2f}</td>" if profit > 0  else f"<td class='list-bears2'>{profit:,.2f}</td>"
                        else : 
                            tx[key] = "<td class='list-normal'>0.00</td>"

                        
                    elif key == 'add0'  : 
                        if self.D['EXCOLOR']['add0'] : style = f"style='color:{self.D['EXCOLOR']['add0']}'"
                        
                        tmp = "<td class='text-center'>"
                        
                        if cno : tmp += f"<span {style}>{txt}</span>"
                        else :
                            href  = f"{self.D['_bse']}board/modify/{self.D['bid']}/no={item['no']}/page={self.D['page']}"
                            tmp += f"<span class='list-subject' data-href='{href}' {style}>{txt}</span>"
                        tmp += '</td>'
                        tx[key] = tmp
                        
                    else : 
                        if self.D['EXALIGN'][key]  : style   = f"text-align:{self.D['EXALIGN'][key]};"
                        if self.D['EXCOLOR'][key]  : style  += f"color:{self.D['EXCOLOR'][key]};"
                        if key =='add4'  : style  += f"border-right:2px solid black;"
                        if key =='add17' : style  += f"border-left:2px solid black;"
                        if self.D['EXWIDTH'][key]  : style  += f"width:{self.D['EXWIDTH'][key]};"
                        
                        txt_format = self.D['EXFORMA'][key] 
                        
                        if   txt_format == 'number' : clas = "class='list-add'"
                        elif txt_format == 'edit'   : clas= f"class='list-live-edit' data-no='{item['no']}' data-fid='{key}'" 
                        elif txt_format == 'n_edit' : clas= f"class='list-live-edit' data-no='{item['no']}' data-fid='{key}'" 
                        elif txt_format == 'mobile' : clas= f"class='list-mobile'" 
                        else : clas=f"class='list-add'"
                        
                    #   if (self.D['EXFTYPE'][key] == 'int') or (txt_format == 'number') or (txt_format == 'n_edit'): txt = f"{int(txt):,}"

                        if (txt and self.D['EXFTYPE'][key] == 'int'   ) : txt = f"{int(txt):,}"
                        if (txt and self.D['EXFTYPE'][key] == 'float' ) : txt = f"{float(txt):,.2f}"

                        tx[key] = f"<td style='{style}' {clas}>{txt}</td>"

                TR.append(tx)
                tx={}

            self.D['TR'] = TR