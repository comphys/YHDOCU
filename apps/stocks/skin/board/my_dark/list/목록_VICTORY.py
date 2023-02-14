import system.core.my_utils as ut
from system.core.load import SKIN

"""
add0  : 
sub11 : 배당금합계
"""
class 목록_VICTORY(SKIN) :

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
        self.DB.clear()
        self.DB.tbl = self.D['tbl']
        self.DB.odr = "add0 DESC"

        date1 = self.SYS.gets.get('date1','')
        date2 = self.SYS.gets.get('date2','')
        self.DB.wre = f"add0 >='{date1}' and add0 <= '{date2}'" if date1 and date2 else ''

        chart_data = self.DB.get("add0,add14,add17,sub16,sub33",assoc=True)

        if chart_data :

            first_date = chart_data[-1]['add0']
            last_date  = chart_data[ 0]['add0']
            self.D['s_date'] = first_date
            self.D['e_date'] = last_date
            self.D['총경과일'] = ut.diff_day(first_date,day2=last_date)

            chart_span = 200
            chart_slice = len(chart_data)
            self.D['chart_start'] = chart_slice - chart_span if chart_slice > chart_span else 0

            chart_data.reverse()
        
            self.D['chart_date']   = [x['add0'][2:] for x in chart_data]
            self.D['close_price']  = [float(x['add14']) for x in chart_data]; close_base = self.D['close_price'][0]
            self.D['close_change'] = [round((x-close_base) / close_base * 100,2) for x in self.D['close_price']]
            self.D['total_value']  = [float(x['add17']) for x in chart_data]
            self.D['soxl_average'] = ['null' if not float(x['sub16']) else float(x['sub16']) for x in chart_data]
            self.D['lever_change'] = [float(x['sub33']) for x in chart_data]

            self.DB.clear()
            self.DB.tbl = self.D['tbl']
            self.DB.wre = f"add0='{last_date}'"
            
            LD = self.DB.get_line('*')
            self.D['chart_percent'] = [float(LD['add10']),float(LD['add4']),float(LD['add16'])]

            # --------------

            총투자금 = float(LD['sub27'])
            총수익금 = float(LD['add17']) - 총투자금
            총수익률 = (float(LD['add17'])/총투자금-1) * 100 if 총투자금 else 0
            self.D['총입금'] = f"{float(LD['sub25']):,.0f}"
            self.D['총출금'] = f"{float(LD['sub26']):,.0f}"
            self.D['현재총액'] = f"{float(LD['add17']):,.0f}"
            self.D['총수익금'] = f"{총수익금:,.0f}"
            self.D['총수익률'] = f"{총수익률:.2f}"
            
            # -- dividend
            self.D['매수금1'] = float(LD['sub23'])
            self.D['매도금1'] = float(LD['sub22'])
            수익금1 = float(LD['add9']) - self.D['매수금1'] + self.D['매도금1']
            평단가1 = float(LD['sub21'])
            수익률1 = (float(LD['add8']) - 평단가1) / 평단가1 *100 if 평단가1 else 0
            self.D['평단가1'] = f"{평단가1:,.2f}"
            self.D['수익금1'] = f"{수익금1:,.2f}"
            self.D['수익률1'] = f"{수익률1:.2f}"
            self.D['배당금'] = f"{float(LD['sub11']):,.2f}"

            # -- leverage
            self.D['매수금2'] = float(LD['sub14'])
            self.D['매도금2'] = float(LD['sub15'])
            현재평가 = self.D['매도금2']  +  float(LD['add15'])
            수익금2 = 현재평가 - self.D['매수금2'] 
            평단가2 = float(LD['sub16'])
            수익률2 = (수익금2 / self.D['매수금2'] * 100) if self.D['매수금2'] else 0
            self.D['평단가2'] = f"{평단가2:,.2f}"
            self.D['수익금2'] = f"{수익금2:,.2f}"
            self.D['수익률2'] = f"{수익률2:.2f}"
            self.D['현재평가'] = f"{현재평가:,.2f}"

            self.D['매수금1'] = f"{self.D['매수금1']:,.2f}"
            self.D['매도금1'] = f"{self.D['매도금1']:,.2f}"
            self.D['매수금2'] = f"{self.D['매수금2']:,.2f}"
            self.D['매도금2'] = f"{self.D['매도금2']:,.2f}"

            # -- extra-info
            self.D['현매수금'] = f"{float(LD['sub17']):,}"
            self.D['현이익률'] = f"{(float(LD['add14'])/평단가2 - 1)*100:,.2f}" if 평단가2 else '0.0'
            self.D['현재시즌'] = LD['sub1']
            self.D['경과일수'] = f"{int(LD['sub12']):02d}"

            self.D['매수갯수'] = int(LD['sub2'])
            self.D['매수단가'] = f"{float(LD['sub19']):,.2f}"
            self.D['매수예상'] = f"{(int(LD['sub2']) * float(LD['sub19'])):,.2f}"
            self.D['매도갯수'] = int(LD['sub3'])
            self.D['매도단가'] = f"{float(LD['sub20']):,.2f}"
            self.D['매도예상'] = f"{(int(LD['sub3']) * float(LD['sub20'])):,.2f}"
            self.D['예상이익'] = f"{(float(self.D['매도예상'].replace(',','')) - float(LD['sub17'].replace(',',''))):,.2f}"
            self.D['연속상승'] = LD['sub5']
            self.D['연속하락'] = LD['sub6']


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

                    elif key == 'add12' : 
                        if txt > '0.00' : tx[key] = f"<td class='list-bulls'>{float(txt):,.2f}</td>"
                        else : tx[key] = f"<td class='list-normal'>0.00</td>"
                    elif key == 'add11' : 
                        if txt > '0' : tx[key] = f"<td class='list-bears2'>{float(txt):,.2f}</td>"
                        else : tx[key] = f"<td class='list-normal2'>0.00</td>"
                        
                    elif key == 'add0'  : 
                        if self.D['EXCOLOR']['add0'] : style = f"style='color:{self.D['EXCOLOR']['add0']}'"
                        
                        tmp = "<td class='text-center'>"
                        
                        if cno : tmp += f"<span {style}>{txt}</span>"
                        else :
                            href  = f"{self.D['_bse']}board/modify/{self.D['bid']}/no={item['no']}/page={self.D['page']}"
                            tmp += f"<span class='list-subject' data-href='{href}' {style}>{txt}</span>"
                        tmp += '</td>'
                        tx[key] = tmp
                    elif key == 'add18' : continue
                    elif key == 'add13' : 
                        if item['add12'] > '0' : 
                            profit = float(item['add18'].replace(',',''))
                            if profit > 0 : tx[key] = f"<td class='list-bulls'>{profit:,.2f}</td>"
                            else : tx[key] = f"<td class='list-bears'>{profit:,.2f}</td>"
                        else : tx[key] = f"<td style='text-align:right;' class='list-add'>{txt}</td>"
                        tx[key] += f"<td style='text-align:right;color:#BDBDBD'>{item['sub33']}</td>"
                        
                    else : 
                        if self.D['EXALIGN'][key]  : style   = f"text-align:{self.D['EXALIGN'][key]};"
                        if self.D['EXCOLOR'][key]  : style  += f"color:{self.D['EXCOLOR'][key]};"
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