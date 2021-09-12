from system.core.load import SKIN

class 쓰기_매매일지(SKIN) :

    def write(self) :
        OBODY = self.D.get('OBODY',None)
        self.D['BODY'] = OBODY
        self.D['TR_add'] = []
        self.D['TR_cat'] = []
        w_width = 710
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'

        self.D['ChkField'] = ','.join(self.D['MustCheck'])

        if  self.D['Mode'] == 'write' :
            self.D['w_title']='' ; self.D['w_tleClr']=''

        elif self.D['Mode'] == 'modify' :
            self.D['w_title'] = OBODY['add0'] ; self.D['w_tleClr']= OBODY['tle_color']
        
        # -------------------
        self.D['user_add1'] = self.user_add1(OBODY)
        self.D['user_add2'] = self.user_add2(OBODY)

    

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


    def user_add1(self,OBODY) :
        value =''
        if OBODY : value = OBODY.get('add1','')

        qry = f"SELECT distinct add1 FROM h_stockHistory_board ORDER BY add1"
        ITM = self.DB.exe(qry)

        tmp  = "<div class='select' style='margin-right:10px;vertical-align:bottom'>"
        tmp += f"<input placeholder='종목코드' name='add1' type='text' value='{value}' style='width:120px;background-color:#363636;border-color:#24272D'>"
        tmp += f"<div class='btn-group'>"
        tmp += f"<button class='btn btn-select dropdown-toggle' data-toggle='dropdown' tabindex='-1'><span class='caret'></span></button>"
        tmp += "<ul class='dropdown-menu'>"
        tmp += f"<li><a>종목코드</a></li>"
        if ITM :
            for cat in ITM :  
                cat_c = 'N/A' if not cat[0] else cat[0]
                tmp += "<li><a href='#'>"+ cat_c + "</a></li>"
        tmp += "</ul>"
        tmp += "</div></div>" 
        return tmp

    def user_add2(self,OBODY) :
        value =''
        if OBODY : value = OBODY.get('add2','')

        qry = f"SELECT add0 FROM h_stock_strategy_board ORDER BY add0"
        ITM = self.DB.exe(qry)

        tmp  = "<div class='select' style='margin-right:10px;vertical-align:bottom'>"
        tmp += f"<input placeholder='매매전략' name='add2' type='text' value='{value}' style='width:120px;background-color:#363636;border-color:#24272D'>"
        tmp += f"<div class='btn-group'>"
        tmp += f"<button class='btn btn-select dropdown-toggle' data-toggle='dropdown' tabindex='-1'><span class='caret'></span></button>"
        tmp += "<ul class='dropdown-menu'>"
        tmp += f"<li><a>매매전략</a></li>"
        if ITM :
            for cat in ITM :  
                cat_c = 'N/A' if not cat[0] else cat[0]
                tmp += "<li><a href='#'>"+ cat_c + "</a></li>"
        tmp += "</ul>"
        tmp += "</div></div>" 
        return tmp
    
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

