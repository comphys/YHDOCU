from system.core.load import SKIN

class 쓰기_계좌잔고(SKIN) :

    def write(self) :
        OBODY = self.D.get('OBODY',None)
        if not OBODY :
            self.D['BODY'] = {}
            self.D['BODY']['add1'] = ''
            self.D['BODY']['add2'] = '0'
            self.D['BODY']['add3'] = '0'
            self.D['BODY']['add4'] = '0.00'
            self.D['BODY']['add5'] = '0.00'
            self.D['BODY']['add7'] = '0'
            self.D['BODY']['add8'] = '0.00'

        else : 
            self.D['BODY'] = OBODY

        self.D['TR_add'] = []
        self.D['TR_cat'] = []
        self.D['method'] = self.SYS.V['_mtd']
        w_width = 760
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'

        self.D['ChkField'] = ','.join(self.D['MustCheck'])

        self.D['user_add0']  = self.user_add0( OBODY) # 종목코드

    def user_add0(self,OBODY) :
        value =''
        if OBODY : value = OBODY.get('add0','')

        qry = f"SELECT distinct add0 FROM h_stock_balance_board ORDER BY add0"
        ITM = self.DB.exe(qry)

        tmp  = "<div id='auto-fill' class='select' style='margin-right:10px;vertical-align:bottom;border:1px solid yellow'>"
        tmp += f"<input placeholder='계좌구분' name='add0' type='text' value='{value}' style='width:122px;background-color:#363636;border-color:#24272D'>"
        tmp += f"<div class='btn-group'>"
        tmp += f"<button class='btn btn-select dropdown-toggle' data-toggle='dropdown' tabindex='-1'><span class='caret'></span></button>"
        tmp += "<ul class='dropdown-menu'>"
        tmp += f"<li><a>계좌구분</a></li>"
        if ITM :
            for cat in ITM :  
                cat_c = 'N/A' if not cat[0] else cat[0]
                tmp += "<li><a href='#'>"+ cat_c + "</a></li>"
        tmp += "</ul>"
        tmp += "</div></div>" 
        return tmp






 