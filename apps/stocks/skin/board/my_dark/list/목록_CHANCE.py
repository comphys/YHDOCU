import system.core.my_utils as my
from system.core.load import SKIN

class 목록_CHANCE(SKIN) :

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
        target = self.DB.one(f"SELECT extra1,extra2 FROM h_board_config WHERE bid='{self.SYS.parm[0]}'")
        self.DB.clear()
        self.DB.tbl = f"h_{target}_board"
        self.DB.odr = "add0 DESC"
        self.DB.lmt = '40'
        chart_data = self.DB.get("add0,add14,add17,add7,sub28,add8",assoc=True)

        if chart_data :

            first_date = chart_data[-1]['add0']
            last_date  = chart_data[ 0]['add0']
            self.D['s_date'] = first_date
            self.D['e_date'] = last_date
            self.D['총경과일'] = my.diff_day(first_date,day2=last_date)
    

            chart_data.reverse()
        
            self.D['chart_date']   = [x['add0'][2:] for x in chart_data]
            self.D['close_price']  = [float(x['add14']) for x in chart_data]; 
            self.D['soxl_average'] = ['null' if not float(x['add7']) else float(x['add7']) for x in chart_data]

            self.DB.clear()
            self.DB.tbl = self.D['tbl']
            prev_date = self.DB.one(f"SELECT max(add0) FROM {self.DB.tbl}")
            self.DB.wre = f"add0='{prev_date}'"
            LD = self.DB.get_line('add3,add4,add6,add7,add9,add14,add16,add17,sub2,sub3,sub5,sub6,sub19,sub20,sub25,sub26,sub27,sub28')
            CD = self.DB.exe(f"SELECT add0, CAST(add7 as FLOAT) FROM {self.DB.tbl} WHERE CAST(add7 as FLOAT) != 0.0 AND add0 BETWEEN '{first_date}' AND '{last_date}'") 
            cx = {}
            self.D['chance_average'] = []
            if CD :
                for c in CD : cx[c[0][2:]] = c[1]
                for x in self.D['chart_date'] : self.D['chance_average'].append(cx.get(x,'null'))
                    
            # --------------
            현재환율 = self.DB.one("SELECT CAST(usd_krw AS FLOAT) FROM usd_krw ORDER BY rowid DESC LIMIT 1")
            총투자금 = float(LD['sub27'])
            총수익금 = float(LD['add17']) - 총투자금
            총수익률 = (float(LD['add17'])/총투자금-1) * 100 if 총투자금 else 0
            self.D['총입금'] = f"{float(LD['sub25']):,.0f}"
            self.D['총출금'] = f"{float(LD['sub26']):,.0f}"
            self.D['현재총액'] = f"{float(LD['add17']):,.0f}"
            self.D['총수익금'] = f"{총수익금:,.0f}"
            self.D['총수익률'] = f"{총수익률:.2f}"
            
            # -- extra-info
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
            self.D['원화예상'] = f"{예상이익 * 현재환율:,.0f}"
            self.D['현재환율'] = f"{현재환율:,.2f}"

            # ------------- taget data 불러오기
            self.DB.clear()
            self.DB.tbl = f"h_{target}_board"
            self.DB.wre = f"add0 = '{last_date}'"
            TD = self.DB.get_line("add6,add8,add9,add14,sub2,sub4,sub6,sub7,sub12,sub18,sub19,sub20,sub28")

            self.D['chart_percent'] = [float(LD['add4']),float(LD['add16'])]

            chart_len = len(chart_data)
            self.D['target_value'] = [TD['sub20']] * chart_len 
            self.D['chance_value'] = ['null'] * chart_len                  
            
            self.D['찬스상황'] = '대기상태'
            self.D['찬스주가'] = TD['add14']
            self.D['찬스일수'] = TD['sub12']
            self.D['찬스일자'] = last_date
            self.D['찬스하강'] = TD['sub6']
            self.D['찬스근거'] = target
            
            
            if int(TD['sub12']) > 0 :

                가용잔액 = int( float(LD['add3']) * 2/3)
                일매수금 = int(가용잔액/22)
                매수비율 = 일매수금 / int(TD['sub4']) 
                기초수량 = my.ceil(매수비율 * int(TD['sub18']))

                찬스수량 = 0    
                # 테스트 상 많이 사는 것이 유리함(수량을 하루 치 더 삼, 어제일수 + 1 +1(추가분))
                day_count = min(int(TD['sub12'])+2,6)
                for i in range(0,day_count) : 
                    찬스수량 += my.ceil(기초수량 *(i*1.25 + 1))

                self.D['cp'] = []
                for p in [0,-1.1,-2.2,-3.3,-4.4,-5.5] :
                    cp = self.take_chance(p,int(TD['add9']),int(TD['sub2']),float(TD['add6']))
                    self.D['cp'].append(cp)
                
                # 찬스가격은 타겟 데이타의 -2.2% 지점
                찬스가격 = self.D['cp'][0]  if (float(TD['add8']) < self.D['cp'][2]or float(TD['sub7'])) else self.D['cp'][2]
                찬스가격 = min(float(TD['sub19']),찬스가격)
                self.D['찬스가격'] = f"{찬스가격:,.2f}"
                self.D['찬스수량'] = f"{찬스수량:,}"
                self.D['찬스자본'] = f"{찬스가격*찬스수량:,.2f}"
                self.D['찬스변동'] = round((찬스가격/float(TD['add14']) -1) * 100,2)
                self.D['환율변환'] = f"{찬스가격*찬스수량* 현재환율:,.0f}"
                self.D['기초수량'] = 기초수량
   
                self.D['chance_value'] = [self.D['찬스가격']] * chart_len
                
                self.D['타겟상태'] = [int(TD['add9']),int(TD['sub2']),float(TD['add6'])]
                
                if int(LD['add9'].replace(',','')) != 0 :
                    self.D['찬스상황'] = '현재진행'
                    self.D['기회상태'] = [int(LD['add9']),int(LD['sub2']),float(LD['add6'])]
                    self.D['찬스수량'] = f"{int(LD['sub2']):,}"
                else :
                    self.D['찬스상황'] = '예약상태'
                    self.D['기회상태'] = [0,찬스수량,0.0]



    def take_chance(self,p,H,n,A) :
        if H == 0 : return 0
        N = H + n
        k = N / (1+p/100)
        return round(A/(k-n),2)


    def list(self) :
        self.head()

        TR = [] ; tx = {}

        if self.TrCnt :
            self.chart()
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