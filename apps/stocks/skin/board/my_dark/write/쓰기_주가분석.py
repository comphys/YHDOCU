from system.core.load import SKIN

class 쓰기_주가분석(SKIN) :

    def write(self) :
        OBODY = self.D.get('OBODY',None)

        self.D['TR_add'] = []
        self.D['TR_cat'] = []
        self.D['method'] = self.SYS.I['_mtd']
        w_width = 760
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'

        self.D['ChkField'] = ','.join(self.D['MustCheck'])

        self.D['user_add1']  = self.user_add1( OBODY) # 종목코드
        self.D['BODY'] = OBODY

    def user_add1(self,OBODY) :
        value =''
        if OBODY : value = OBODY.get('add1','')

        qry = f"SELECT distinct add1 FROM h_stockHistory_board ORDER BY add1"
        ITM = self.DB.exe(qry)

        tmp  = "<div class='select' style='margin-right:10px;vertical-align:bottom;border:1px solid yellow'>"
        tmp += f"<input placeholder='종목코드' name='add1' type='text' value='{value}' style='width:122px;background-color:#363636;border-color:#24272D'>"
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

 






 