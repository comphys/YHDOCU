from system.core.load import SKIN

class 쓰기_표준(SKIN) :

    def write(self) :
        OBODY = self.D.get('OBODY',None)
        self.D['TR_add'] = []
        self.D['TR_cat'] = []
        if self.D['BCONFIG']['width'] : w_width  = int( (self.D['BCONFIG']['width']).replace('px','') )
        else : w_width = 815
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'

        self.D['ChkField'] = ','.join(self.D['MustCheck'])

        if  self.D['Mode'] == 'write' :
            self.D['w_title']='' ; self.D['w_tleClr']=''

        elif self.D['Mode'] == 'modify' :
            self.D['w_title'] = OBODY['add0'] ; self.D['w_tleClr']= OBODY['tle_color']

        if self.D['Mode'] != 'add_body' and int(self.D['Brother']) <= 0 :
            self.add_all(self.D['BCONFIG']['category'], self.D['EXTITLE'], self.D['EXFORMA'], self.D['bid'], OBODY) 
    

    def add_all(self,category, exFIDktitle, exFormat, bid, OBODY) :
        CAT_KEY = []
        if category : CAT_KEY = category.split('/')
        if exFIDktitle :
            for key, val in exFIDktitle.items() :
                if   exFormat[key] == 'number' : clss="class='i-number'" 
                elif exFormat[key] == 'n_edit' : clss="class='i-number'" 
                elif exFormat[key] == 'date'   : clss="class='i-date'" 
                else : clss="class='i-text'"
                if key in CAT_KEY : self.user_cat(val,key,'132px',clss,self.D['bid'],OBODY) 
                else : self.user_add(val,key,clss,OBODY)
    
    def user_add(self,val,key,clss,OBODY) :
        if key == 'add0' : return 
        value =''
        if OBODY : value = OBODY.get(key,'')
        tmp  = f"<div class='i-input-div'><div class='write-input-left'>{val}</div>"
        tmp += f"<input type='text' name='{key}' {clss} value='{value}'></div>"
        
        self.D['TR_add'].append(tmp)
    
    def user_cat(self,val,key,xwidth,clss,bid,OBODY) :
        if key == 'add0' : return 
        value =''
        if OBODY : value = OBODY.get(key,'')
        qry = f"SELECT distinct {key} FROM h_{bid}_board ORDER BY {key}"
        ITM = self.DB.exe(qry)

        tmp  = "<div class='myselect' style='margin-right:10px'>"
        tmp += f"<input placeholder='{val}' name='{key}' type='text' value='{value}' style='width:{xwidth};background-color:#363636;border-color:#333333'>"
        tmp += f"<div class='btn-group'>"
        tmp += f"<button class='btn btn-select dropdown-toggle' data-toggle='dropdown' tabindex='-1'><span class='caret'></span></button>"
        tmp += "<ul class='dropdown-menu'>"
        tmp += f"<li><a>{val}</a></li>"
        if ITM :
            for cat in ITM :  
                cat_c = 'N/A' if not cat[0] else cat[0]
                tmp += "<li><a href='#'>"+ cat_c + "</a></li>"
        tmp += "</ul>"
        tmp += "</div></div>" 

        self.D['TR_cat'].append(tmp)

