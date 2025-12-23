import system.core.my_utils as my
import numpy
from flask import session
from system.core.load import SKIN

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
                item['wdate'] = my.timestamp_to_date(item['wdate'],"%Y/%m/%d")
                item['mdate'] = my.timestamp_to_date(item['mdate'],"%m/%d %H:%M")

    
    def check_updated(self) :

        last_ohlc = self.DB.last_date("h_stockHistory_board")
        delta = 1
        while delta :
            temp = my.dayofdate(last_ohlc,delta)
            weekend = 1 if temp[1] in ('토','일') else 0
            holiday = 1 if self.DB.cnt(f"SELECT key FROM parameters WHERE val='{temp[0]}' and cat='미국증시휴장일'") else 0 
            delta = 0 if not (weekend + holiday) else delta + 1   

        cur_time = my.kor_loc_date("UTC")
        self.D['chk_date'] = temp[0]
        chk_time = my.dayofdate(self.D['chk_date'],1)[0] + " 00:10:00"

        return True if cur_time < chk_time else False

    def list(self) :

        self.D['ot'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.D['ot'][0] = self.DB.one("SELECT count(add0) FROM h_stockHistory_board WHERE add1='SOXL'") # total count
        self.D['ot'][1] = self.DB.one("SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add9 as INTEGER)  > 0 and add1='SOXL'") # updays
        self.D['ot'][2] = f"{self.D['ot'][1]/self.D['ot'][0]*100:.2f}"
        self.D['ot'][3] = self.DB.one("SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) > 0 and add1='SOXL'") # dndays 
        self.D['ot'][4] = f"{self.D['ot'][3]/self.D['ot'][0]*100:.2f}"
        self.D['ot'][5] = self.DB.one("SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add9 as INTEGER) = 0  and CAST(add10 as INTEGER) = 0 and add1='SOXL'") # equal days
        self.D['ot'][6] = f"{self.D['ot'][5]/self.D['ot'][0]*100:.2f}"

        self.D['ot'][7]  = self.DB.one("SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 1 and add1='SOXL'") # dn 1
        self.D['ot'][8]  = f"{self.D['ot'][7]/self.D['ot'][3]*100:.2f}"
        self.D['ot'][9]  = self.DB.one("SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 2 and add1='SOXL'") # dn 2
        self.D['ot'][10] = f"{self.D['ot'][9]/self.D['ot'][3]*100:.2f}"
        self.D['ot'][11] = self.DB.one("SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 3 and add1='SOXL'") # dn 3
        self.D['ot'][12] = f"{self.D['ot'][11]/self.D['ot'][3]*100:.2f}"
        self.D['ot'][13] = self.DB.one("SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 4 and add1='SOXL'") # dn 4
        self.D['ot'][14] = f"{self.D['ot'][13]/self.D['ot'][3]*100:.2f}"
        self.D['ot'][15] = self.DB.one("SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 5 and add1='SOXL'") # dn 5
        self.D['ot'][16] = f"{self.D['ot'][15]/self.D['ot'][3]*100:.2f}"
        self.D['ot'][17] = self.DB.one("SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 6 and add1='SOXL'") # dn 6
        self.D['ot'][18] = f"{self.D['ot'][17]/self.D['ot'][3]*100:.2f}"
        self.D['ot'][19] = self.DB.one("SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 7 and add1='SOXL'") # dn 7
        self.D['ot'][20] = f"{self.D['ot'][19]/self.D['ot'][3]*100:.2f}"        
        self.D['ot'][21] = self.DB.one("SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 8 and add1='SOXL'") # dn 8
        self.D['ot'][22] = f"{self.D['ot'][21]/self.D['ot'][3]*100:.2f}" 


        last_year = my.last_year_day()
        self.D['ot1'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.D['ot1'][0] = self.DB.one(f"SELECT count(add0) FROM h_stockHistory_board WHERE add1='SOXL' and add0 > '{last_year}'") # total count
        self.D['ot1'][1] = self.DB.one(f"SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add9 as INTEGER)  > 0 and add1='SOXL' and add0 > '{last_year}'") # updays
        self.D['ot1'][2] = f"{self.D['ot1'][1]/self.D['ot1'][0]*100:.2f}"
        self.D['ot1'][3] = self.DB.one(f"SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) > 0 and add1='SOXL' and add0 > '{last_year}'") # dndays 
        self.D['ot1'][4] = f"{self.D['ot1'][3]/self.D['ot1'][0]*100:.2f}"
        self.D['ot1'][5] = self.DB.one(f"SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add9 as INTEGER) = 0  and CAST(add10 as INTEGER) = 0 and add1='SOXL' and add0 > '{last_year}'") # equal days
        self.D['ot1'][6] = f"{self.D['ot1'][5]/self.D['ot1'][0]*100:.2f}"

        self.D['ot1'][7]  = self.DB.one(f"SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 1 and add1='SOXL' and add0 > '{last_year}'") # dn 1
        self.D['ot1'][8]  = f"{self.D['ot1'][7]/self.D['ot1'][3]*100:.2f}"
        self.D['ot1'][9]  = self.DB.one(f"SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 2 and add1='SOXL' and add0 > '{last_year}'") # dn 2
        self.D['ot1'][10] = f"{self.D['ot1'][9]/self.D['ot1'][3]*100:.2f}"
        self.D['ot1'][11] = self.DB.one(f"SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 3 and add1='SOXL' and add0 > '{last_year}'") # dn 3
        self.D['ot1'][12] = f"{self.D['ot1'][11]/self.D['ot1'][3]*100:.2f}"
        self.D['ot1'][13] = self.DB.one(f"SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 4 and add1='SOXL' and add0 > '{last_year}'") # dn 4
        self.D['ot1'][14] = f"{self.D['ot1'][13]/self.D['ot1'][3]*100:.2f}"
        self.D['ot1'][15] = self.DB.one(f"SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 5 and add1='SOXL' and add0 > '{last_year}'") # dn 5
        self.D['ot1'][16] = f"{self.D['ot1'][15]/self.D['ot1'][3]*100:.2f}"
        self.D['ot1'][17] = self.DB.one(f"SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 6 and add1='SOXL' and add0 > '{last_year}'") # dn 6
        self.D['ot1'][18] = f"{self.D['ot1'][17]/self.D['ot1'][3]*100:.2f}"
        self.D['ot1'][19] = self.DB.one(f"SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 7 and add1='SOXL' and add0 > '{last_year}'") # dn 7
        self.D['ot1'][20] = f"{self.D['ot1'][19]/self.D['ot1'][3]*100:.2f}"        
        self.D['ot1'][21] = self.DB.one(f"SELECT count(add9) FROM h_stockHistory_board WHERE CAST(add10 as INTEGER) = 8 and add1='SOXL' and add0 > '{last_year}'") # dn 8
        self.D['ot1'][22] = f"{self.D['ot'][21]/self.D['ot'][3]*100:.2f}" 
        

        # 표준편차 구하기(최근5년)
        day_5yr = my.back_day(-1824)
        std_5yr = self.DB.col(f"SELECT CAST(add8 as float) FROM h_stockHistory_board WHERE add1='SOXL' and add0 > '{day_5yr}'")
        std_5yr_val = numpy.std(std_5yr)
        self.D['오년변동률'] = f"{std_5yr_val:.2f}"

        # 표준편차 구하기(일년)
        std_1yr = self.DB.col(f"SELECT CAST(add8 as float) FROM h_stockHistory_board WHERE add1='SOXL' and add0 > '{last_year}'")
        std_1yr_val = numpy.std(std_1yr)
        self.D['일년변동률'] = f"{std_1yr_val:.2f}"

        # 표준편차 구하기(한달)
        one_month = my.back_day(-30)
        std_1mt = self.DB.col(f"SELECT CAST(add8 as float) FROM h_stockHistory_board WHERE add1='SOXL' and add0 > '{one_month}'")
        std_1mt_val = numpy.std(std_1mt)
        self.D['한달변동률'] = f"{std_1mt_val:.2f}"


        self.D['TimeNow'] = my.timestamp_to_date(ts='now')
        self.head()
        self.data_preprocess()
        self.D['업데이트'] = self.check_updated()

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
                    
                    elif key == 'add2'  : 
                        
                        txt = f"{float(txt):,.1f}" if txt else ''
                        tx[key] = f"<td style='text-align:right;color:#D8F6CE'>{txt}</td>"
                    
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

                    elif key in ('add3','add4','add5','add6')  : 
                        if self.D['EXALIGN'][key]  : style  += f"text-align:{self.D['EXALIGN'][key]};"
                        if self.D['EXCOLOR'][key]  : style  += f"color:{self.D['EXCOLOR'][key]};"
                        if self.D['EXWIDTH'][key]  : style  += f"width:{self.D['EXWIDTH'][key]};"
                        
                        txt = f"{float(txt):,.2f}"
                        tx[key] = f"<td style='{style}' {clas}>{txt}</td>"  

                    elif key == 'add7'  : 
                        if self.D['EXALIGN'][key]  : style  += f"text-align:{self.D['EXALIGN'][key]};"
                        if self.D['EXCOLOR'][key]  : style  += f"color:{self.D['EXCOLOR'][key]};"
                        if self.D['EXWIDTH'][key]  : style  += f"width:{self.D['EXWIDTH'][key]};"
                        
                        txt = f"{int(txt):,}"
                        tx[key] = f"<td style='{style}' {clas}>{txt}</td>"  


                    else : 
                        if self.D['EXALIGN'][key]  : style  += f"text-align:{self.D['EXALIGN'][key]};"
                        if self.D['EXCOLOR'][key]  : style  += f"color:{self.D['EXCOLOR'][key]};"
                        if self.D['EXWIDTH'][key]  : style  += f"width:{self.D['EXWIDTH'][key]};"
                        
                        tx[key] = f"<td style='{style}' {clas}>{txt}</td>"

                TR.append(tx)
                tx={}

            self.D['TR'] = TR
