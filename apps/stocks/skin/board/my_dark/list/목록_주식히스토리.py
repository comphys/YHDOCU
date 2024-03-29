import system.core.my_utils as ut
from flask import session
from system.core.load import SKIN
from datetime import datetime

class 목록_주식히스토리(SKIN) :

    def _auto(self) :
        self.TrCnt = self.D.get('Tr_cnt',0)

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
                item['mdate'] = ut.timestamp_to_date(item['mdate'],"%m/%d %H:%M")

    def old_price_trace(self,code,today,old_date) :

        qry = f"SELECT add3 FROM h_stockHistory_board WHERE add0 BETWEEN '{old_date}' and '{today}' and add1='{code}' ORDER BY add0"
        aaa= self.DB.exe(qry)
        aaa= [float(x[0]) for x in aaa]

        c_drop = 0
        c_goup = 0
        for i in range(1,len(aaa)) :
            c_drop = c_drop + 1 if aaa[i] <= aaa[i-1] else 0
            c_goup = c_goup + 1 if aaa[i] >  aaa[i-1] else 0
        
        return (c_drop,c_goup)

    def list(self) :
        self.D['TimeNow'] = ut.timestamp_to_date(ts='now')
        self.head()
        self.data_preprocess()

        try :     self.D['code'] = session['CSH']['csh_add1']
        except :  self.D['code'] = 'NONE'
        if self.D['code'] =='' : self.D['code'] = 'NONE'

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
                    elif key == 'add1'  : tx[key] = f"<td class='list-code' style='color:#F7F8E0;cursor:pointer'>{txt}</td>"
                    elif key == 'wdate' : tx[key] = f"<td class='list-wdate'>{txt}</td>"
                    elif key == 'mdate' : tx[key] = f"<td class='list-mdate'>{txt}</td>"                    
                    elif key == 'hit'   : tx[key] = f"<td class='list-hit'>{txt}</td>" 
                    elif key == 'uname' : tx[key] = f"<td class='list-name'>{txt}</td>"
                    elif key == 'add8'  : 
                        txt_val = float(txt)
                        clr = "#F6CECE;" if txt_val > 0 else "#CED8F6"
                        txt = f"{txt_val:.2f}"
                        tx[key] = f"<td style='text-align:right;color:{clr}'>{txt}</td>"
                    
                    elif key == 'add0'  : 
                        if self.D['EXALIGN'][key]  : style  += f"text-align:{self.D['EXALIGN'][key]};"
                        if self.D['EXCOLOR'][key]  : style  += f"color:{self.D['EXCOLOR'][key]};"
                        if self.D['EXWIDTH'][key]  : style  += f"width:{self.D['EXWIDTH'][key]};"
                        
                        tmp = f"<td style='{style}'>"
                        
                        if cno : tmp += f"<span>{txt}</span>"
                        else :
                            href  = f"{self.D['_bse']}board/body/{self.D['bid']}/no={item['no']}"
                            tmp += f"<span class='list-subject' data-href='{href}' >{txt}</span>"

                        tmp += '</td>'
                        tx[key] = tmp

                    else : 
                        if self.D['EXALIGN'][key]  : style  += f"text-align:{self.D['EXALIGN'][key]};"
                        if self.D['EXCOLOR'][key]  : style  += f"color:{self.D['EXCOLOR'][key]};"
                        if self.D['EXWIDTH'][key]  : style  += f"width:{self.D['EXWIDTH'][key]};"
                        
                        if (self.D['EXFTYPE'][key] == 'int'   ) : txt = f"{int(txt):,}"
                        if (self.D['EXFTYPE'][key] == 'float' ) : txt = f"{float(txt):,.2f}"

                        tx[key] = f"<td style='{style}' {clas}>{txt}</td>"

                TR.append(tx)
                tx={}

            self.D['TR'] = TR
