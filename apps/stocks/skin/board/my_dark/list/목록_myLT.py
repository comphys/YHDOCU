from contextlib import nullcontext
import system.core.my_utils as ut
from system.core.load import SKIN

class 목록_myLT(SKIN) :

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
        self.DB.tbl = self.D['tbl']
        self.DB.wre = ''
        # self.DB.lmt = '180'
        self.DB.odr = "add0 DESC"

        chart_data = self.DB.get("add0,add18,add19,add15,add20,add17,add9,add3,add11",assoc=True)
        if chart_data :

            chart_data.reverse()

            last_date  = chart_data[-1]['add0']

            self.D['경과일수'] = ut.diff_day('2022-04-12',last_date) + 1
            self.D['profit_limit'] = []
            acc = 0.0
            for x in chart_data :
                acc = acc + float(x['add11'])
                self.D['profit_limit'].append(acc)
            
            self.D['chart_date'] = [x['add0'][2:] for x in chart_data]
            self.D['chart_min'] = [float(x['add18']) for x in chart_data]
            self.D['chart_target'] = [float(x['add19']) for x in chart_data]
            self.D['chart_cur'] = [float(x['add15']) for x in chart_data]
            self.D['chart_max'] = [float(x['add20']) for x in chart_data]
            # self.D['chart_total'] = [float(x['add17'])*0.6 for x in chart_data]
            # self.D['chart_dividend'] = [float(x['add9'])*3 for x in chart_data]
            # self.D['chart_cash'] = [float(x['add3'])*3 for x in chart_data]

            self.D['target_value']  = f"{float(self.D['chart_target'][-1]):,.0f}"
            self.D['current_value'] = f"{float(chart_data[-1]['add15']):,.0f}"
            
            # check_items = ('chart_cur','chart_dividend','chart_total','chart_cash')
            # for item in check_items :
            #     for i, x in enumerate(self.D['chart_max']) :
            #         if self.D[item][i]  < self.D['chart_min'][i]*0.8 : self.D[item][i] = self.D['chart_min'][i]*0.8
            #         if self.D[item][i]  > self.D['chart_max'][i]*1.2 : self.D[item][i] = self.D['chart_max'][i]*1.2
            
            # ------------------------------------------------------------------------------------
            self.DB.clear()
            self.DB.tbl = self.D['tbl']
            self.DB.wre = f"add0='{last_date}'"
            
            LD = self.DB.get_line('*')
            self.D['chart_percent'] = [float(LD['add4']),float(LD['add10']),float(LD['add16'])]
            
            # --------------
            qry = f"SELECT sum(add1), sum(add2), sum(add5), sum(add6), sum(add11), sum(add12), sum(sub10) FROM {self.DB.tbl}"
            invest = self.DB.exe(qry,many=1,assoc=True)

            총투자금 = int(invest['sum(add1)']) - int(invest['sum(add2)'])
            총수익금 = int(LD['add17']) - 총투자금
            총수익률 = 총수익금/총투자금 * 100
            self.D['총입금'] = f"{int(invest['sum(add1)']):,}"
            self.D['총출금'] = f"{int(invest['sum(add2)']):,}"
            self.D['총수익금'] = f"{총수익금:,}"
            self.D['총수익률'] = f"{총수익률:.2f}"
            self.D['배당금'] = f"{float(invest['sum(sub10)']):,.2f}"
            # -- dividend
            self.D['매수금1'] = float(invest['sum(add5)'])
            self.D['매도금1'] = float(invest['sum(add6)'])
            매수금1 = self.D['매수금1'] - self.D['매도금1']
            수익금1 = float(LD['add9']) - 매수금1
            평단가1 = 매수금1/int(LD['add7'])
            수익률1 = (float(LD['add8']) - 평단가1) / 평단가1 *100
            self.D['평단가1'] = f"{평단가1:,.2f}"
            self.D['수익금1'] = f"{수익금1:,.2f}"
            self.D['수익률1'] = f"{수익률1:.2f}"
            # -- leverage
            self.D['매수금2'] = float(invest['sum(add11)'])
            self.D['매도금2'] = float(invest['sum(add12)'])
            매수금2 = self.D['매수금2'] - self.D['매도금2']
            수익금2 = float(LD['add15']) - 매수금2
            평단가2 = 매수금2/int(LD['add13'])
            수익률2 = (float(LD['add14']) - 평단가2) / 평단가2 *100
            self.D['평단가2'] = f"{평단가2:,.2f}"
            self.D['수익금2'] = f"{수익금2:,.2f}"
            self.D['수익률2'] = f"{수익률2:.2f}"

            self.D['매수금1'] = f"{self.D['매수금1']:,.2f}"
            self.D['매도금1'] = f"{self.D['매도금1']:,.2f}"
            self.D['매수금2'] = f"{self.D['매수금2']:,.2f}"
            self.D['매도금2'] = f"{self.D['매도금2']:,.2f}"

            self.D['info_color']= 'white' 
            if LD['add15'] < LD['add18'] : 
                self.D['need_cash'] = self.D['chart_cur'][-1] - self.D['chart_target'][-1]
                bottom_price = self.D['chart_min'][-1] / int(LD['add13'])
                self.D['대응전략'] = 'Buy guide'
                self.D['info_color'] = '#F6CECE' 

            elif LD['add15'] > LD['add20'] : 
                self.D['need_cash'] =  self.D['chart_cur'][-1] - self.D['chart_max'][-1]
                bottom_price = self.D['chart_max'][-1] / int(LD['add13'])
                self.D['대응전략'] = 'Sell guide'
                self.D['info_color'] = '#CEF6F5'
            
            else :
                self.D['need_cash'] =  self.D['chart_target'][-1] - self.D['chart_cur'][-1]
                bottom_price = self.D['chart_min'][-1] / int(LD['add13'])
                self.D['대응전략'] = 'Stay watch'
                self.D['info_color'] = 'white'  

            bottom_count = self.D['need_cash'] / bottom_price
            self.D['need_cash'] = f"{self.D['need_cash']:,.0f}" 
            self.D['bottom_price'] = f"{bottom_price:,.2f}"
            self.D['bottom_count'] = f"{bottom_count:,.0f}"
            # For Chart
            chart_back_limit = -120
            self.D['chart_date'] = self.D['chart_date'][chart_back_limit:] 
            self.D['chart_min'] = self.D['chart_min'][chart_back_limit:]
            self.D['chart_target'] = self.D['chart_target'][chart_back_limit:]
            self.D['chart_cur'] = self.D['chart_cur'][chart_back_limit:]
            self.D['chart_max'] = self.D['chart_max'][chart_back_limit:]
            self.D['profit_limit'] = self.D['profit_limit'][chart_back_limit:]


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

                    elif key == 'wdate' : tx[key] = f"<td class='list-wdate'>{txt}</td>"
                    elif key == 'mdate' : tx[key] = f"<td class='list-mdate'>{txt}</td>"                    
                    elif key == 'hit'   : tx[key] = f"<td class='list-hit'>{txt}</td>" 
                    elif key == 'uname' : tx[key] = f"<td class='list-name'>{txt}</td>"
                    
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


            if self.D['BCONFIG']['row_sum'] == 'on' :
                list_order_cnt = len(self.D['list_order'])
                td2 =['<td>&nbsp;</td>' for x in range(list_order_cnt)]
                
                for k in self.D['EXFORMA'].keys() : 
                    if self.D['RS'][k] : td2[self.D['list_order'].index(k)] = f"<td>{self.D['RS'][k]:,}</td>" 

                td2[0] = "<td class='list-no'>합 계</td>"
                self.D['row_sum'] = ''.join(td2)
