import system.core.my_utils as ut
from system.core.load import SKIN
from datetime import date
from flask import session

class 목록_매매일지(SKIN) :

    def _auto(self) :
        self.TrCnt = self.D.get('Tr_cnt',0)
        try : 
            self.D['chart_code']   = session['CSH']['csh_add1']
            self.D['chart_season'] = session['CSH']['csh_add2']
        except : 
            self.D['chart_code']   = None 
            self.D['chart_season'] = None

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

    def data_preprocess(self) :
        if self.TrCnt :
            for item in self.D['LIST'] :
                item['wdate'] = ut.timestamp_to_date(item['wdate'],"%Y/%m/%d")
                item['mdate'] = ut.timestamp_to_date(item['mdate'],"%Y/%m/%d")
        
        self.D['code']   = session['CSH'].get('csh_add1','')
        self.D['season'] = session['CSH'].get('csh_add2','')

        if self.D['code'] and self.D['season'] : 
            self.DB.tbl, self.DB.wre = (self.D['tbl'],f"add1='{self.D['code']}' and add2={self.D['season']}")
            c_price = self.DB.get('add5',assoc=False)
            m_price = self.DB.get('add9',assoc=False)
            if  c_price :
                c_price = [float(x) for x in c_price]
                m_price = [float(x) for x in m_price]

                self.D['종가변동'] = f"{(c_price[-1] - c_price[0]) / c_price[0] * 100:5.2f}%"
                self.D['평가변동'] = f"{(m_price[-1] - m_price[0]) / m_price[0] * 100:5.2f}%"
        
            if  self.D['bid'] in ('daily_first','daily_second','daily_third') :
                self.DB.tbl, self.DB.wre = (self.D['tbl'],f"add1='{self.D['code']}'")
                start_date, last_date = self.DB.get("min(add0),max(add0)",many=1,assoc=False)

                self.DB.wre = f"add0='{start_date}'"
                기본자산, 추가자산 = self.DB.get("sub7,sub8",many=1,assoc=False) 

                self.DB.wre = f"add0='{last_date}'"
                평가금액, 가용잔액, 추가자본 = self.DB.get("add11,add16,add17",many=1,assoc=False) 

                d0 = date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10]))
                d1 = date(int(last_date[0:4]),int(last_date[5:7]),int(last_date[8:10]))
                delta = d1-d0
                경과일수 = delta.days            

                초기자본 = float(기본자산) + float(추가자산)
                최종자본 = float(평가금액) + float(가용잔액) + float(추가자본)
                최종수익 = 최종자본 - 초기자본 
                최종수익률 = (최종수익/초기자본) * 100 
                style1 = "<span style='font-weight:bold;color:white'>"
                style2 = "<span style='font-weight:bold;color:#CEF6CE'>"
                style3 = "<span style='font-weight:bold;color:#F6CECE'>"
                self.D['earning_info']  = f"투자기간 : {style1}{경과일수:,}</span>일 "
                self.D['earning_info'] += f"초기자본 {style1}${초기자본:,}</span> 최종평가액 {style1}${최종자본:,.2f}</span> 으로 "
                self.D['earning_info'] += f"수익은 {style2}${최종수익:,.2f}</span> 이며 수익률은 {style3}{최종수익률:,.2f}%</span> 입니다"            

    def list(self) :

        self.head()
        self.data_preprocess()

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

                    elif key == 'add1' : # 종목코드
                        if self.D['EXALIGN'][key]  : style  += f"text-align:{self.D['EXALIGN'][key]};"
                        if self.D['EXCOLOR'][key]  : style  += f"color:{self.D['EXCOLOR'][key]};"
                        if self.D['EXWIDTH'][key]  : style  += f"width:{self.D['EXWIDTH'][key]};"
                        tx[key] = f"<td style='cursor:pointer;{style}' onclick=\"open_stock_chart('{txt}')\">{txt}</td>" 
                    
                    elif key == 'add0'  : 
                        if self.D['EXCOLOR']['add0'] : style = f"style='color:{self.D['EXCOLOR']['add0']}'"
                        
                        tmp = "<td class='text-center'>"
                        
                        if cno : tmp += f"<span {style}>{txt}</span>"
                        else :
                            href  = f"{self.D['_bse']}board/modify/{self.D['bid']}/no={item['no']}/page={self.D['page']}"
                            tmp += f"<span class='list-subject' data-href='{href}' {style}>{txt}</span>"

                        tmp += '</td>'
                        tx[key] = tmp

                    elif key == 'add4' : 
                        txt = f"{float(txt):,.1f}"
                        tx[key] = f"<td class='todo_today' data-no='{item['no']}' style='text-align:right;cursor:pointer'>{txt}</td>"

                    elif key == 'add15' : # 현수익률
                        txt_val = float(txt)
                        clr = "#F6CECE;" if txt_val > 0 else "#CED8F6"
                        txt = f"{txt_val:.2f}"
                        tx[key] = f"<td style='text-align:right;color:{clr}'>{txt}</td>"

                    else : 
                        if self.D['EXALIGN'][key]  : style  += f"text-align:{self.D['EXALIGN'][key]};"
                        if self.D['EXCOLOR'][key]  : style  += f"color:{self.D['EXCOLOR'][key]};"
                        if self.D['EXWIDTH'][key]  : style  += f"width:{self.D['EXWIDTH'][key]};"
                        
                        txt_format = self.D['EXFORMA'][key] 
                        
                        if   txt_format == 'number' : clas = "class='list-add'"
                        elif txt_format == 'edit'   : clas= f"class='list-live-edit' data-no='{item['no']}' data-fid='{key}'" 
                        elif txt_format == 'n_edit' : clas= f"class='list-live-edit' data-no='{item['no']}' data-fid='{key}'" 
                        elif txt_format == 'mobile' : clas= f"class='list-mobile'" 
                        else : clas=f"class='list-add'"
                        

                        if (self.D['EXFTYPE'][key] == 'int'   ) : txt = f"{int(txt):,}"
                        if (self.D['EXFTYPE'][key] == 'float' ) : 
                            if      key == 'add9' : txt = f"{float(txt):,.4f}"
                            elif    key == 'add4' : txt = f"{float(txt):,.1f}"
                            else : txt = f"{float(txt):,.2f}"

                        tx[key] = f"<td style='{style}' {clas}>{txt}</td>"

                TR.append(tx)
                tx={}

            self.D['TR'] = TR
            
            if self.D['BCONFIG']['row_sum'] == 'on' :
                list_order_cnt = len(self.D['list_order'])
                td2 =['<td>&nbsp;</td>' for x in range(list_order_cnt)]
                
                for k in self.D['EXFORMA'].keys() : 
                    if self.D['RS'][k] : td2[self.D['list_order'].index(k)] = f"<td>{self.D['RS'][k]:,.2f}</td>" 

                td2[0] = "<td class='list-no'>합 계</td>"
                self.D['row_sum'] = ''.join(td2)
