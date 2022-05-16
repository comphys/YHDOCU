from contextlib import nullcontext
import system.core.my_utils as ut
from system.core.load import SKIN

class 목록_장투일지(SKIN) :

    def _auto(self) :
        self.TrCnt = self.D.get('Tr_cnt',0)
        self.Type = self.D['BCONFIG']['type']

    def chart(self) :
        self.DB.tbl = self.D['tbl']
        self.DB.wre = ''
        self.DB.lmt = '60'
        self.DB.odr = "add0 DESC"

        chart_data = self.DB.get("add0,add18,add19,add15,add20,add17,add9,add3",assoc=False)
        if chart_data :

            last_date  = chart_data[0][0]
            self.D['경과일수'] = ut.diff_day('2022-04-12',last_date)

            self.D['chart_date'] = [x[0][2:] for x in chart_data]
            self.D['chart_min'] = [float(x[1]) for x in chart_data]
            self.D['chart_target'] = [float(x[2]) for x in chart_data]
            self.D['chart_cur'] = [float(x[3]) for x in chart_data]
            self.D['chart_max'] = [float(x[4]) for x in chart_data]
            self.D['chart_total'] = [float(x[5])*0.6 for x in chart_data]
            self.D['chart_dividend'] = [float(x[6])*3 for x in chart_data]
            self.D['chart_cash'] = [float(x[7])*3 for x in chart_data]

            self.D['chart_date'].reverse()
            self.D['chart_min'].reverse()
            self.D['chart_target'].reverse()
            self.D['chart_cur'].reverse()
            self.D['chart_max'].reverse()
            self.D['chart_total'].reverse()
            self.D['chart_dividend'].reverse()
            self.D['chart_cash'].reverse()

            self.D['target_value']  = f"{float(self.D['chart_target'][-1])/0.6:,.0f}"
            self.D['current_value'] = f"{int(chart_data[0][5]):,}"
            
            
            for i, x in enumerate(self.D['chart_max']) :
                if self.D['chart_cur'][i]  < self.D['chart_min'][i]*0.8 or self.D['chart_cur'][i]  > self.D['chart_max'][i]*1.2 : self.D['chart_cur'][i]  = 'null'
                if self.D['chart_dividend'][i]  < self.D['chart_min'][i]*0.8 or self.D['chart_dividend'][i]  > self.D['chart_max'][i]*1.2 : self.D['chart_dividend'][i]  = 'null'
                if self.D['chart_total'][i]  < self.D['chart_min'][i]*0.8 or self.D['chart_total'][i]  > self.D['chart_max'][i]*1.5 : self.D['chart_total'][i]  = 'null'
                if self.D['chart_cash'][i]  < self.D['chart_min'][i] * 0.8 or self.D['chart_cash'][i]  > self.D['chart_max'][i] : self.D['chart_cash'][i]  = 'null'
            
            self.D['need_cash'] = self.D['chart_cur'][-1] - self.D['chart_target'][-1]
            self.D['need_cash'] = f"{self.D['need_cash']:,.0f}"

            # ------------------------------------------------------------------------------------
            self.DB.clear()
            self.DB.tbl = self.D['tbl']
            self.DB.wre = f"add0='{last_date}'"
            
            LD = self.DB.get_line('*')
            self.D['chart_percent'] = [float(LD['add4']),float(LD['add10']),float(LD['add16'])]
            
            bottom_price = self.D['chart_min'][-1] / int(LD['add13'])
            bottom_count = int(LD['add3']) / bottom_price

            self.D['bottom_price'] = f"{bottom_price:,.2f}"
            self.D['bottom_count'] = f"{bottom_count:,.0f}"
            # --------------
            qry = f"SELECT sum(add1), sum(add2), sum(add5), sum(add6), sum(add11), sum(add12), sum(sub10) FROM {self.DB.tbl}"
            invest = self.DB.exe(qry,many=1,assoc=False)

            총투자금 = int(invest[0]) - int(invest[1])
            총수익금 = int(LD['add17']) - 총투자금
            총수익률 = 총수익금/총투자금 * 100
            self.D['총입금'] = f"{int(invest[0]):,}"
            self.D['총출금'] = f"{int(invest[1]):,}"
            self.D['총수익금'] = f"{총수익금:,}"
            self.D['총수익률'] = f"{총수익률:.2f}"
            self.D['배당금'] = f"{float(invest[6]):,.2f}"
            # -- dividend
            매수금1 = float(invest[2]) - float(invest[3])
            수익금1 = float(LD['add9']) - 매수금1
            평단가1 = 매수금1/int(LD['add7'])
            수익률1 = (float(LD['add8']) - 평단가1) / 평단가1 *100
            self.D['평단가1'] = f"{평단가1:,.2f}"
            self.D['수익금1'] = f"{수익금1:,.2f}"
            self.D['수익률1'] = f"{수익률1:.2f}"
            # -- leverage
            매수금2 = float(invest[4]) - float(invest[5])
            수익금2 = float(LD['add15']) - 매수금2
            평단가2 = 매수금2/int(LD['add13'])
            수익률2 = (float(LD['add14']) - 평단가2) / 평단가2 *100
            self.D['평단가2'] = f"{평단가2:,.2f}"
            self.D['수익금2'] = f"{수익금2:,.2f}"
            self.D['수익률2'] = f"{수익률2:.2f}"

            self.D['info_color']= 'white' 
            if LD['add15'] < LD['add18'] : self.D['info_color'] = '#F6CECE' 
            if LD['add15'] > LD['add20'] : self.D['info_color'] = '#CEF6F5'


    def list(self) :
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
