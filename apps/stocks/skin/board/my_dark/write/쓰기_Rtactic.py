from system.core.load import SKIN

class 쓰기_Rtactic(SKIN) :

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
                
                target = self.DB.one(f"SELECT extra1 FROM h_board_config WHERE bid='{self.SYS.parm[0]}'")
                
                JBODY = self.DB.line(f"SELECT * FROM h_{self.SYS.parm[0]}_board WHERE add0='{prev_date}'")
                GBODY = self.DB.line(f"SELECT * FROM h_{target}_board WHERE add0='{self.D['today']}'")
                JSTRG = self.DB.parameters_dict('매매전략/VRS')
                
                JBODY = { k:v for (k,v) in JBODY.items() if k not in {'content','no','brother','tle_color','uid','uname','reply','hit','wdate','mdate'}}
                GBODY = { k:v for (k,v) in GBODY.items() if k not in {'content','no','brother','tle_color','uid','uname','reply','hit','wdate','mdate'}}
                
                if not GBODY : self.SYS.set_message(f"{target} 보드에 해당 일자 매매 데이타가 존재하지 않습니다.")
                # 종가변동 구하기
                p_change = self.DB.one(f"SELECT add8 FROM h_stockHistory_board WHERE add0='{self.D['today']}' and add1='SOXL'")
                GBODY['add20'] = f"{float(p_change):.2f}"                
                                
                self.D['JBODY'] = self.SYS.json(JBODY)
                self.D['GBODY'] = self.SYS.json(GBODY)
                self.D['JSTRG'] = self.SYS.json(JSTRG)

# -----------------------------------------------------------------------------------------------------------------------
# From Auto Input 
# -----------------------------------------------------------------------------------------------------------------------