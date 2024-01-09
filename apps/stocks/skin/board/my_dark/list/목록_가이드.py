import system.core.my_utils as my
from system.core.load import SKIN

class 목록_가이드(SKIN) :

    def _auto(self) :
        self.TrCnt = self.D.get('Tr_cnt',0)
        self.Type = self.D['BCONFIG']['type']
        
    def head(self) : 
        return

    def chart(self) :
        self.DB.clear()
        self.DB.tbl = self.D['tbl']
        self.DB.odr = "add0 DESC"

        self.D['limit_date'] = self.SYS.gets.get('date2','')
        if self.D['limit_date'] : self.DB.wre = f"add0 <='{self.D['limit_date']}'"

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
            self.D['sell_price']   = ['null'] * chart_slice

            self.DB.clear()
            self.DB.tbl = self.D['tbl']
            self.DB.wre = f"add0='{last_date}'"
            
            LD = self.DB.get_line('add6,add8,add9,add10,add14,add15,add17,add18,add19,add20,sub1,sub2,sub3,sub4,sub7,sub12,sub5,sub6,sub18,sub19,sub20,sub25,sub26,sub27,sub32')
            
            # 가치 비율 for chart
            현재환율 = float(self.DB.one("SELECT usd_krw FROM usd_krw ORDER BY rowid DESC LIMIT 1"))
            
            총투자금 = float(LD['sub25']) - float(LD['sub26'])
            총수익금 = float(LD['add17']) - 총투자금
            총수익률 = (float(LD['add17'])/총투자금-1) * 100 if 총투자금 else 0
            
            self.D['총입금'] = f"{float(LD['sub25']):,.0f}"
            self.D['총출금'] = f"{float(LD['sub26']):,.0f}"
            self.D['현재총액'] = f"{float(LD['add17']):,.0f}"
            self.D['총수익금'] = f"{총수익금:,.0f}"
            self.D['총수익률'] = f"{총수익률:.2f}"        
            # --------------

            # # -- extra-info
            self.D['현재시즌'] = LD['sub1']  
            
            slice_first = -42 if chart_slice > 42 else 0
            self.D['단기첫날'] = '20'+self.D['chart_date'][slice_first]
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
            self.D['자산배분'] = LD['add10']
            self.D['가치합계'] = round(float(LD['add17']))
            
            self.D['필요상승'] = f"({round((float(LD['sub20'])/float(LD['add14']) -1)*100,2)}%)" if int(LD['add9']) else ''
            
            # 월별 실현손익
            qry = f"SELECT SUBSTR(add0,1,7), sum( CAST(add18 as float)) FROM {self.D['tbl']} WHERE CAST(add12 as float) > 0 "
            if self.D['limit_date'] : qry += f"and add0 <='{self.D['limit_date']}' " 
            qry += "GROUP BY SUBSTR(add0,1,7) ORDER BY add0 DESC LIMIT 24"
            monProfit = self.DB.exe(qry)
            if monProfit :
                self.D['월별구분'] = []
                self.D['월별이익'] = []
                for mon, profit in monProfit :
                    self.D['월별구분'].append(mon)
                    self.D['월별이익'].append(round(profit))
                
                monthly_total = sum(self.D['월별이익'])
                monthly_lenth = len(self.D['월별이익'])
                
                self.D['월별구분'].reverse()  
                self.D['월별이익'].reverse()
                self.D['월별구분'].append('AVG')
                self.D['월별이익'].append(round(monthly_total/monthly_lenth))
                self.D['손익합계'] = f"$ {monthly_total:,.0f} ({monthly_total*현재환율:,.0f}원)"
    

    def take_chance(self,H,n,A) :
        if H == 0 : return 0
        기회시점 = -2.2
        p = 0 if (self.D['현수익률'] < 기회시점 or self.D['손실회수']) else 기회시점
        N = H + n
        k = N / (1+p/100)
        return round(A/(k-n),2)



    def list(self) :
        self.chart()
        TR = [] ; tx = {}

        if self.TrCnt :
            self.D['cno'] = -1 ; TrCnt = self.TrCnt

            for item in self.D['LIST'] :

                for key in self.D['list_order'] :

                    style=clas=tmp=''
                    txt = item[key]
                       
                    if key == 'add0'  : 
                        if self.D['EXCOLOR']['add0'] : style = f"style='color:{self.D['EXCOLOR']['add0']}'"
                        tmp = "<td class='text-center'>"
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
                    
                    elif key == 'add20': 
                        profit = float(txt)
                        if profit != 0 : 
                            tx[key] = f"<td class='list-bull'>{profit:,.2f}</td>" if profit > 0  else f"<td class='list-bear'>{profit:,.2f}</td>"
                        else : 
                            tx[key] = "<td class='list-normal'>0.00</td>"

                    else : 
                        if self.D['EXALIGN'][key]  : style   = f"text-align:{self.D['EXALIGN'][key]};"
                        if self.D['EXCOLOR'][key]  : style  += f"color:{self.D['EXCOLOR'][key]};"
                        if self.D['EXWIDTH'][key]  : style  += f"width:{self.D['EXWIDTH'][key]};"
                        if self.D['EXCLASS'][key]  : clas   =  f"class='{self.D['EXCLASS'][key]}'"
                        
                        if (txt and self.D['EXFTYPE'][key] == 'int'   ) : txt = f"{int(txt):,}"
                        if (txt and self.D['EXFTYPE'][key] == 'float' ) : txt = f"{float(txt):,.2f}"

                        tx[key] = f"<td style='{style}' {clas}>{txt}</td>"

                TR.append(tx)
                tx={}

            self.D['TR'] = TR