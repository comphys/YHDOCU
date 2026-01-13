from system.core.load import SKIN

class 쓰기_투자315(SKIN) :

    def write(self) :

        self.D['TR_add'] = []
        self.D['TR_cat'] = []
        
        w_width = 1000
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'

        self.D['ChkField'] = ','.join(self.D['MustCheck'])
        
        self.D['초기가능']  = False

        if  self.D['Mode'] == 'modify' :
            l_pd = self.DB.last_date("h_stockHistory_board")
            l_rd = self.DB.last_date(self.D['tbl'])

            if  l_pd > l_rd and self.D['BODY']['add0'] == l_rd and self.D['BODY']['add9'] == '0' : 
                self.D['초기가능'] = True
                self.D['현재잔액'] = self.D['BODY']['add5']


# -----------------------------------------------------------------------------------------------------------------------
# From Auto Input 
# -----------------------------------------------------------------------------------------------------------------------