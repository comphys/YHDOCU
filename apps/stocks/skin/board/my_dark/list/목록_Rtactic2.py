import system.core.my_utils as my
from system.core.load import SKIN

class 목록_Rtactic2(SKIN) :

    def _auto(self) :
        self.TrCnt = self.D.get('Tr_cnt',0)

    def head(self) : 
        return
        

    def chart(self) :
        
        last_date = self.DB.one(f"SELECT max(add0) FROM {self.D['tbl']}")
        VtacBoard = self.DB.parameters('035') 
        
        self.DB.clear()
        self.DB.tbl = VtacBoard
        self.DB.wre = f"add0 <='{last_date}'"
        self.DB.odr = "add0 DESC"
        self.DB.lmt = '200'
        
        chart_data = self.DB.get("add0,add14",assoc=True)

        if chart_data :

            first_date = chart_data[-1]['add0']
            self.D['s_date'] = first_date
            self.D['e_date'] = last_date
            self.D['총경과일'] = my.diff_day(first_date,day2=last_date)

            chart_span = 40
            chart_slice = len(chart_data)
            self.D['chart_start'] = chart_slice - chart_span if chart_slice > chart_span else 0
    
            chart_data.reverse()
        
            self.D['chart_date']   = [x['add0'][2:] for x in chart_data]
            self.D['close_price']  = [float(x['add14']) for x in chart_data]; 

            self.DB.clear()
            self.DB.tbl = self.D['tbl']
            self.DB.wre = f"add0='{last_date}'"
            LD = self.DB.get_line('add3,add4,add6,add7,add9,add14,add16,add17,sub2,sub3,sub5,sub6,sub18,sub19,sub20,sub25,sub26,sub27,sub28')
            
            RD = self.DB.exe(f"SELECT add0, CAST(add7 as FLOAT), CAST(add8 as FLOAT), CAST(add9 as INT) FROM {self.DB.tbl} WHERE add0 BETWEEN '{first_date}' AND '{last_date}'") 
                 
            cx = {};dx = {}
            self.D['Rtactic_avg'] = []; self.D['Rtactic_pro'] = []
            if RD :
                # cx[날자] = 평균단가, dx[날자] = 현수익률
                for c in RD : 
                    if c[3] : cx[c[0][2:]] = c[1] 
                    if c[2] or c[3] : dx[c[0][2:]] = c[2]
                for x in self.D['chart_date'] : 
                    self.D['Rtactic_avg'].append(cx.get(x,'null')) 
                    self.D['Rtactic_pro'].append(dx.get(x,'null'))
            
            # ------------- taget record 불러오기
            self.DB.clear()
            self.DB.tbl = VtacBoard
            self.DB.wre = f"add0 = '{last_date}'"
            VD = self.DB.get_line("add0,add1,add2,add3,add4,add5,add6,add7,add8,add9,add11,add12,add14,add15,add16,add17,add18,sub1,sub2,sub4,sub5,sub6,sub7,sub12,sub18,sub19,sub20,sub28,sub29")
            
            chart_len = len(chart_data)
            # --------------
            현재환율 = self.DB.one("SELECT CAST(usd_krw AS FLOAT) FROM usd_krw ORDER BY rowid DESC LIMIT 1")
            
            총투자금 = float(LD['sub25']) - float(LD['sub26'])
            총수익금 = float(LD['add17']) - 총투자금
            총수익률 = (float(LD['add17'])/총투자금-1) * 100 if 총투자금 else 0
            
            self.D['총입금'] = f"{float(LD['sub25']):,.0f}"
            self.D['총출금'] = f"{float(LD['sub26']):,.0f}"
            self.D['현재총액'] = f"{float(LD['add17']):,.0f}"
            self.D['총수익금'] = f"{총수익금:,.0f}"
            self.D['총수익률'] = f"{총수익률:.2f}"

            # -- extra-info by invest guide
            타겟일수 = int(VD['sub12']) 
            기초수량 = int(LD['sub18'])
  
            if  타겟일수 == 0 :
                self.D['매수갯수'] = 기초수량
                self.D['매수단가'] = LD['sub19']
                self.D['매수예상'] = f"{기초수량 * float(LD['sub19']):,.2f}"
                self.D['매도갯수'] = '0' 
                self.D['매도단가'] = '0.00' 
                self.D['매도예상'] = '0.00'
                self.D['예상이익'] = '0.00'
                self.D['원화예상'] = '0'
                self.D['V_tact_value'] = [VD['sub20']] * chart_len 
                self.D['chance_value'] = [LD['sub19']] * chart_len 
            
            elif 타겟일수 == 1 :
                self.D['매수갯수'] = int(LD['sub2'])
                self.D['매수단가'] = f"{float(LD['sub19']):,.2f}"
                self.D['매수예상'] = f"{(int(LD['sub2']) * float(LD['sub19'])):,.2f}"
                self.D['매도갯수'] = int(LD['sub3'])
                self.D['매도단가'] = f"{float(LD['sub20']):,.2f}"
                self.D['매도예상'] = f"{(int(LD['sub3']) * float(LD['sub20'])):,.2f}"
                예상이익 = float(self.D['매도예상'].replace(',','')) - float(LD['add6'].replace(',',''))
                self.D['예상이익'] = f"{예상이익:,.2f}" 
                self.D['원화예상'] = f"{예상이익*현재환율:,.0f}"
                self.D['V_tact_value'] = [VD['sub20']] * chart_len 
                self.D['chance_value'] = [LD['sub19']] * chart_len                
            
            elif 타겟일수 >= 2 and int(LD['add9']) <= int(LD['sub18'])*3.5: 
                # 테스트 상 많이 사는 것이 유리함(수량을 하루 치 더 삼, 어제일수 + 1 +1(추가분))
                찬스수량 = 0
                day_count = min(int(VD['sub12'])+1+self.DB.parameters('026'),6)
                for i in range(0,day_count) : 찬스수량 += my.ceil(기초수량 *(i*1.25 + 1))

                cpn = self.take_chance(self.DB.parameters('021'),int(VD['add9']),int(VD['sub2']),float(VD['add6']))    
                cpc = self.take_chance(self.DB.parameters('022'),int(VD['add9']),int(VD['sub2']),float(VD['add6']))

                #  p = 0 if (self.M['수익률'] < self.R['기회시점'] or self.M['손실회수']) else self.R['기회시점']
                # 찬스가격 = cp00 if (float(VD['add8']) < -2.2 or float(VD['sub7'])) else cp22
                찬스가격 = cpc if float(VD['sub7']) else cpn
                찬스가격 = min(float(VD['sub19']),찬스가격)
                
                self.D['매수갯수'] = f"{찬스수량:,}"
                self.D['매수단가'] = f"{찬스가격:,.2f}"
                self.D['매수예상'] = f"{찬스수량 * 찬스가격:,.2f}"
                self.D['매도갯수'] = LD['add9']; self.D['매도단가'] = VD['sub20']; 
                self.D['매도예상'] = f"{(int(LD['add9']) * float(VD['sub20'])):,.2f}"
                예상이익 = float(self.D['매도예상'].replace(',','')) - float(LD['add6'].replace(',',''))
                self.D['예상이익'] = f"{예상이익:,.2f}"
                self.D['원화예상'] = f"{예상이익*현재환율:,.0f}"
                self.D['V_tact_value'] = [VD['sub20']] * chart_len
                self.D['chance_value'] = [찬스가격] * chart_len
                
            else : # 가이드 및 투자가 진행 중일 때
                self.D['매수갯수'] = int(LD['sub2'])
                self.D['매수단가'] = f"{float(LD['sub19']):,.2f}"
                self.D['매수예상'] = f"{(int(LD['sub2']) * float(LD['sub19'])):,.2f}"
                self.D['매도갯수'] = int(LD['sub3'])
                self.D['매도단가'] = f"{float(LD['sub20']):,.2f}"
                self.D['매도예상'] = f"{(int(LD['sub3']) * float(LD['sub20'])):,.2f}"
                예상이익 = float(self.D['매도예상'].replace(',','')) - float(LD['add6'].replace(',',''))
                self.D['예상이익'] = f"{예상이익:,.2f}"
                self.D['원화예상'] = f"{예상이익*현재환율:,.0f}"
                self.D['V_tact_value'] = [VD['sub20']] * chart_len
                self.D['chance_value'] = [VD['sub19']] * chart_len
            
            self.D['연속상승'] = VD['sub5']
            self.D['연속하락'] = VD['sub6']
            self.D['현재환율'] = f"{현재환율:,.2f}"
            self.D['자산배분'] = self.DB.parameters_des('038')
            self.D['가치합계'] = round(float(LD['add17']))

            # GD : Guide Data
            yy = my.sv(VD['add14'])
            bb = my.sv(self.D['매수단가'])
            ss = my.sv(self.D['매도단가'])
            self.D['yx_b'] = f"{round(bb/yy - 1,4) * 100:.2f}" if bb else ''
            self.D['yx_s'] = f"{round(ss/yy - 1,4) * 100:.2f}" if ss else ''
            
            # 월별 실현손익
            qry = f"SELECT SUBSTR(add0,1,7), sum( CAST(add18 as float)) FROM {self.D['tbl']} WHERE CAST(add12 as float) > 0 "
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

    def take_chance(self,p,H,n,A) :
        if H == 0 : return 0
        N = H + n
        k = N / (1+p/100)
        return round(A/(k-n),2)

    def list(self) :

        TR = [] ; tx = {}

        if self.TrCnt :
            self.chart()
 
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
                    
                    elif key == 'add12' : 
                        money = float(txt)
                        if money : 
                            tx[key] = f"<td class='list-normal' style='font-weight:bold;'>{money:,.2f}</td>" 
                        else : 
                            tx[key] = "<td class='list-normal'>0.00</td>"                           
                    
                    elif key == 'add20': 
                        profit = float(txt)
                        if profit != 0 : 
                            tx[key] = f"<td class='list-bull'>{profit:,.2f}</td>" if profit > 0  else f"<td class='list-bear'>{profit:,.2f}</td>"
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
                        if self.D['EXCLASS'][key]  : clas   =  f"class='{self.D['EXCLASS'][key]}'"
                        
                        if (txt and self.D['EXFTYPE'][key] == 'int'   ) : txt = f"{int(txt):,}"
                        if (txt and self.D['EXFTYPE'][key] == 'float' ) : txt = f"{float(txt):,.2f}"

                        tx[key] = f"<td style='{style}' {clas}>{txt}</td>"

                TR.append(tx)
                tx={}

            self.D['TR'] = TR