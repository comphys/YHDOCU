from system.core.load import SKIN
import system.core.my_utils as my

class 쓰기_VICTORY(SKIN) :

    def write(self) :
        OBODY = self.D.get('OBODY',None)
        self.D['BODY'] = OBODY
        self.D['TR_add'] = []
        self.D['TR_cat'] = []
        self.D['method'] = self.SYS.V['_mtd']
        w_width = 1000
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'

        self.D['ChkField'] = ','.join(self.D['MustCheck'])

        prev_date = self.DB.one("SELECT max(add0) FROM h_VICTORY_board")
        if  prev_date :
            prev_day  = my.dayofdate(prev_date)
            if prev_day == '금' : self.D['today'] = my.dayofdate(prev_date,delta=3)[0]
            else : self.D['today'] = my.dayofdate(prev_date,delta=1)[0]

   

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

