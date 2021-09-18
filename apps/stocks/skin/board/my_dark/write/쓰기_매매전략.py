from system.core.load import SKIN

class 쓰기_매매전략(SKIN) :

    def write(self) :
        OBODY = self.D.get('OBODY',None)
        self.D['BODY'] = OBODY
        self.D['TR_add'] = []
        self.D['TR_cat'] = []
        self.D['method'] = self.SYS.V['_mtd']
        w_width = 770
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'

        self.D['ChkField'] = ','.join(self.D['MustCheck'])

        # -------------------
        self.D['user_add10'] = self.user_add10(OBODY)


    def user_add10(self,OBODY) :
        value =''
        if OBODY : value = OBODY.get('add10','')

        qry = f"SELECT distinct add10 FROM h_stock_strategy_board ORDER BY add10"
        ITM = self.DB.exe(qry)

        tmp  = "<div class='select' style='margin-right:10px;vertical-align:bottom'>"
        tmp += f"<input placeholder='기본전략' name='add10' type='text' value='{value}' style='width:120px;background-color:#363636;border-color:#24272D'>"
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
