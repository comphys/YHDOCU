from system.core.load import Control

class Update_tactics(Control) :
    
    def _auto(self) :
        self.DB = self.db('stocks')
        self.bid = self.parm[0]
        self.RST = self.load_lib('rst')
        self.theDate = ''
        self.preDate = self.DB.one(f"SELECT max(add0) FROM h_{self.bid}_board")
        if  self.preDate :
            self.theDate = self.DB.one(f"SELECT min(add0) FROM h_stockHistory_board WHERE add0 > '{self.preDate}'")

    def update_vr(self,tactic) :

        if  self.theDate :
            
            self.RST.do_tacticsLog(self.theDate)
            D = self.RST.get_tacticLog(self.theDate,tactic)
            self.RST.nextStep()
            X = self.RST.get_nextStrategyLog(tactic)
            D |= X
            
            D.update({k:'' for k,v in D.items() if v == None})
            board = f"h_{self.bid}_board"
            qry=self.DB.qry_insert(board,D)
            self.DB.exe(qry)
            self.set_message(f"{self.theDate}일 정보를 업데이트 하였습니다")
            return self.moveto(f"board/list/{self.bid}")
        
        else :
            self.set_message(f"{self.bid} {self.preDate} 이후 업데이트된 정보가 없습니다")
            return self.moveto(f"board/list/{self.bid}")
        
    def update_st(self,tactic) :

        if  self.theDate :
            
            self.RST.do_tacticsLog(self.theDate)
            D = self.RST.get_tacticLog(self.theDate,tactic)
            self.RST.nextStep()
            X = self.RST.get_nextStrategyLog(tactic)
            D |= X
            
            D.update({k:'' for k,v in D.items() if v == None})
            
            upDate = float(D['add1']) == 0 and float(D['add2']) == 0 and float(D['add11']) == 0 and float(D['add12']) == 0 and int(D['add9']) == 0
            board = f"h_{self.bid}_board"
            if  upDate :
                qry=self.DB.qry_update(board,D,f"add0='{self.preDate}'")
                self.DB.exe(qry)

            else :
                qry=self.DB.qry_insert(board,D)
                self.DB.exe(qry)

            self.set_message(f"{self.theDate}일 정보를 업데이트 하였습니다")
            return self.moveto(f"board/list/{self.bid}")
        
        else :
            self.set_message(f"{self.bid} {self.preDate} 이후 업데이트된 정보가 없습니다")
            return self.moveto(f"board/list/{self.bid}")

    def update_v(self) :
        self.update_vr('V')

    def updat_r(self) :
        self.update_vr('R')

    def update_s(self) :
        self.update_st('S')

    def update_t(self) :
        self.update_st('T')