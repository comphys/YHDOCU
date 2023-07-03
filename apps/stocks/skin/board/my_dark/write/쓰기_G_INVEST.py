from system.core.load import SKIN
import system.core.my_utils as my

class 쓰기_G_INVEST(SKIN) :

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

        self.D['today'] = None
        if not OBODY :
            prev_date = self.DB.one(f"SELECT max(add0) FROM h_{self.SYS.parm[0]}_board")
            if  prev_date :
                self.D['today'] = self.DB.one(f"SELECT min(add0) FROM h_stockHistory_board WHERE add0 > '{prev_date}'")

            if self.D['today'] : 


                JBODY = self.DB.line(f"SELECT * FROM h_{self.SYS.parm[0]}_board WHERE add0='{prev_date}'")
                JSTRG = self.DB.line(f"SELECT * FROM h_stock_strategy_board WHERE add0='VICTORY'")
                JHIST = self.DB.line(f"SELECT * FROM h_stockHistory_board WHERE add0='{self.D['today']}' and add1='SOXL'")


                JBODY = { k:v for (k,v) in JBODY.items() if k not in {'content','no','brother','tle_color','uid','uname','reply','hit','wdate','mdate'}}
                JSTRG = { k:v for (k,v) in JSTRG.items() if k not in {'content','no','brother','tle_color','uid','uname','reply','hit','wdate','mdate'}}
                JHIST = { k:v for (k,v) in JHIST.items() if k not in {'content','no','brother','tle_color','uid','uname','reply','hit','wdate','mdate'}}

                self.DB.clear()
                self.DB.tbl, self.DB.wre = ('h_INVEST_board',f"add0='{self.D['today']}'")
                OD = self.DB.get_line("sub19,sub20")
                
                JBODY['LB'] = OD['sub19']
                JBODY['LS'] = OD['sub20']

                self.D['JBODY'] = self.SYS.json(JBODY)
                self.D['JSTRG'] = self.SYS.json(JSTRG)
                self.D['JHIST'] = self.SYS.json(JHIST)

# -----------------------------------------------------------------------------------------------------------------------
# From Auto Input 
# -----------------------------------------------------------------------------------------------------------------------