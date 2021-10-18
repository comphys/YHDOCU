import system.core.my_utils as ut
from system.core.load import SKIN

class 목록_표준(SKIN) :

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

    def data_preprocess(self) :
        if self.TrCnt :
            for item in self.D['LIST'] :
                item['wdate'] = ut.timestamp_to_date(item['wdate'],"%Y/%m/%d")
                item['mdate'] = ut.timestamp_to_date(item['mdate'],"%Y/%m/%d")
                item['add0']  = item['add0'][0:self.D['BCONFIG']['subject_len']]
 
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
                    
                    elif key == 'add0'  : 
                        if self.D['EXCOLOR']['add0'] : style = f"style='color:{self.D['EXCOLOR']['add0']}'"
                        if item['tle_color'] : style = f"style='color:{item['tle_color']};font-weight:bold'"
                        
                        tmp = "<td class='text-left'>"
                        
                        if cno : tmp += f"<span {style}>{txt}</span>"
                        else :
                            href  = f"{self.D['_bse']}board/body/{self.D['bid']}/no={item['no']}"
                            if item['brother'] : href += f"/brother={item['brother']}"
                            tmp += f"<span class='list-subject' data-href='{href}' {style}>{txt}</span>"

                        if item['reply']   and item['reply']   > 0 :   tmp += f"&nbsp;<span class='list-reply'>{item['reply']}</span>"
                        if item['brother'] and item['brother'] < 0 :   tmp += f"&nbsp;<span class='list-brother'>{abs(item['brother'])}</span>"    

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
                        if (txt and self.D['EXFTYPE'][key] == 'float' ) : txt = f"{float(txt):,}"

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


            if self.D['BCONFIG']['row_flt'] == 'on' :
                self.D['row_flt'] = f"<td id='filter-reset'>필 터</td><td id='filter-qry' contenteditable colspan='{list_order_cnt-2}'>{self.D['list_filter']}</td><td id='list-filter-submit'>전송</td>"
