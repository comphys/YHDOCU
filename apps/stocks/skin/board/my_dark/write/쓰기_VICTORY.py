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

        self.D['today'] = None
        if not OBODY :
            prev_date = self.DB.one(f"SELECT max(add0) FROM h_{self.SYS.parm[0]}_board")
            if  prev_date :
                self.D['today'] = self.DB.one(f"SELECT min(add0) FROM h_stockHistory_board WHERE add0 > '{prev_date}'")

            if self.D['today'] : 


                JBODY = self.DB.line(f"SELECT * FROM h_{self.SYS.parm[0]}_board WHERE add0='{prev_date}'")
                JSTRG = self.DB.line(f"SELECT * FROM h_stock_strategy_board WHERE add0='VICTORY'")
                J_DIV = self.DB.line(f"SELECT * FROM h_stockHistory_board WHERE add0='{self.D['today']}' and add1='JEPQ'")
                J_LEV = self.DB.line(f"SELECT * FROM h_stockHistory_board WHERE add0='{self.D['today']}' and add1='SOXL'")


                JBODY = { k:v for (k,v) in JBODY.items() if k not in {'content','no','brother','tle_color','uid','uname','reply','hit','wdate','mdate'}}
                JSTRG = { k:v for (k,v) in JSTRG.items() if k not in {'content','no','brother','tle_color','uid','uname','reply','hit','wdate','mdate'}}
                if     J_DIV : J_DIV = { k:v for (k,v) in J_DIV.items() if k not in {'content','no','brother','tle_color','uid','uname','reply','hit','wdate','mdate'}}
                else : J_DIV = {"add3": "0.00"}    
                J_LEV = { k:v for (k,v) in J_LEV.items() if k not in {'content','no','brother','tle_color','uid','uname','reply','hit','wdate','mdate'}}

                self.D['JBODY'] = self.SYS.json(JBODY)
                self.D['JSTRG'] = self.SYS.json(JSTRG)
                self.D['J_DIV'] = self.SYS.json(J_DIV)
                self.D['J_LEV'] = self.SYS.json(J_LEV)

# -----------------------------------------------------------------------------------------------------------------------
# From Auto Input 
# -----------------------------------------------------------------------------------------------------------------------