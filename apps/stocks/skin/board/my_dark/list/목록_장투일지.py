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
        self.DB.odr = "add0 ASC"

        chart_data = self.DB.get("add0,add18,add19,add17,add20",assoc=False)
        last_date  = chart_data[-1][0]

        self.D['chart_date'] = [x[0][2:] for x in chart_data]
        self.D['chart_min'] = [float(x[1]) for x in chart_data]
        self.D['chart_target'] = [float(x[2]) for x in chart_data]
        self.D['chart_cur'] = [float(x[3]) for x in chart_data]
        self.D['chart_max'] = [float(x[4]) for x in chart_data]

        self.DB.wre = f"add0='{last_date}'"
        percent = self.DB.get("add4,add10,add16",many=1,assoc=False)
        self.D['chart_percent'] = [float(x) for x in percent]
        

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
