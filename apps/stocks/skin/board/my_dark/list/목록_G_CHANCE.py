import system.core.my_utils as my
from system.core.load import SKIN

"""
add0  : 
sub11 : 배당금합계
"""
class 목록_G_CHANCE(SKIN) :

    def _auto(self) :
        self.TrCnt = self.D.get('Tr_cnt',0)
        self.Type = self.D['BCONFIG']['type']

    def head(self) : 
        TH_title = {'no':'번호','uname':'작성자','wdate':'작성일','mdate':'수정일','hit':'조회','uid':'아이디'}
        TH_align = {'no':'center','uname':'center','wdate':'center','mdate':'center','hit':'center','uid':'center'}
        THX = {}
        TH_title |= self.D['EXTITLE'] ; TH_align |= self.D['EXALIGN']

        for key in self.D['list_order'] : THX[key] = f"<th style='text-align:{TH_align[key]}'>{TH_title[key]}</th>"
        
        self.D['head_td'] = THX

    def chart(self) :
        target = self.DB.one(f"SELECT extra1 FROM h_board_config WHERE bid='{self.SYS.parm[0]}'")
        self.DB.clear()
        self.DB.tbl = f"h_{target}_board"
        self.DB.odr = "add0 DESC"
        self.DB.lmt = '60'

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
            self.D['close_price']  = [float(x['add14']) for x in chart_data]; 
            self.D['soxl_average'] = ['null' if not float(x['add7']) else float(x['add7']) for x in chart_data]


            self.DB.clear()
            self.DB.tbl = self.D['tbl']
            prev_date = self.DB.one(f"SELECT max(add0) FROM {self.DB.tbl}")
            
            self.DB.wre = f"add0='{prev_date}'"
            
            LD = self.DB.get_line('*')
  
            # --------------

            총투자금 = float(LD['sub27'])
            총수익금 = float(LD['add17']) - 총투자금
            총수익률 = (float(LD['add17'])/총투자금-1) * 100 if 총투자금 else 0
            self.D['총입금'] = f"{float(LD['sub25']):,.0f}"
            self.D['총출금'] = f"{float(LD['sub26']):,.0f}"
            self.D['현재총액'] = f"{float(LD['add17']):,.0f}"
            self.D['총수익금'] = f"{총수익금:,.0f}"
            self.D['총수익률'] = f"{총수익률:.2f}"
            
            # -- leverage
            평단가 = float(LD['add7'])
            # -- extra-info
            self.D['현매수금'] = f"{float(LD['add6']):,}"
            self.D['현이익률'] = f"{(float(LD['add14'])/평단가 - 1)*100:,.2f}" if 평단가 else '0.0'

            self.D['매수갯수'] = int(LD['sub2'])
            self.D['매수단가'] = f"{float(LD['sub19']):,.2f}"
            self.D['매수예상'] = f"{(int(LD['sub2']) * float(LD['sub19'])):,.2f}"
            self.D['매도갯수'] = int(LD['sub3'])
            self.D['매도단가'] = f"{float(LD['sub20']):,.2f}"
            self.D['매도예상'] = f"{(int(LD['sub3']) * float(LD['sub20'])):,.2f}"
            self.D['예상이익'] = f"{(float(self.D['매도예상'].replace(',','')) - float(LD['add6'].replace(',',''))):,.2f}"
            self.D['연속상승'] = LD['sub5']
            self.D['연속하락'] = LD['sub6']

            # ------------- taget data 불러오기
            self.DB.clear()
            self.DB.tbl = f"h_{target}_board"
            self.DB.wre = f"add0 = '{last_date}'"
            TD = self.DB.get_line("add6,add9,add14,sub2,sub4,sub6,sub12,sub18,sub20")

            if int(TD['add9']) :

                가용잔액 = int( float(LD['add3']) * 2/3)
                일매수금 = int(가용잔액/22)
                매수비율 = 일매수금 / int(TD['sub4']) 
                기초수량 = int(매수비율 * int(TD['sub18']))

                찬스수량 = 0    
                for i in range(0,int(TD['sub12'])+1) : 
                    찬스수량 += my.ceil(기초수량 *(i*1.25 + 1))

                찬스가격 = self.take_chance(-5,int(TD['add9']),int(TD['sub2']),float(TD['add6']))
                self.D['찬스가격'] = f"{찬스가격:,.2f}"
                self.D['찬스수량'] = f"{찬스수량:,}"
                self.D['찬스자본'] = f"{찬스가격*찬스수량:,.2f}"
                self.D['찬스일수'] = TD['sub12']
                self.D['찬스주가'] = TD['add14']
                self.D['찬스하강'] = TD['sub6']
                self.D['찬스근거'] = target




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

                       
                    elif key == 'add0'  : 
                        if self.D['EXCOLOR']['add0'] : style = f"style='color:{self.D['EXCOLOR']['add0']}'"
                        
                        tmp = "<td class='text-center'>"
                        
                        if cno : tmp += f"<span {style}>{txt}</span>"
                        else :
                            href  = f"{self.D['_bse']}board/modify/{self.D['bid']}/no={item['no']}/page={self.D['page']}"
                            tmp += f"<span class='list-subject' data-href='{href}' {style}>{txt}</span>"
                        tmp += '</td>'
                        tx[key] = tmp

                    elif key in ('add18','add8') : 
                        profit = float(txt)
                        if profit != 0 : 
                            tx[key] = f"<td class='list-bulls'>{float(txt):,.2f}</td>" if profit > 0  else f"<td class='list-bears'>{float(txt):,.2f}</td>"
                        else : 
                            tx[key] = "<td class='list-normal'>0.00</td>"
                        
                    else : 
                        if self.D['EXALIGN'][key]  : style   = f"text-align:{self.D['EXALIGN'][key]};"
                        if self.D['EXCOLOR'][key]  : style  += f"color:{self.D['EXCOLOR'][key]};"
                        if self.D['EXWIDTH'][key]  : style  += f"width:{self.D['EXWIDTH'][key]};"
                        if key =='add4'  : style  += f"border-right:2px solid black;"
                        if key =='add17' : style  += f"border-left:2px solid black;"
                        
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