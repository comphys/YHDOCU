from system.core.load import Control
import system.core.my_utils as my

class Update_tactics(Control) :
    
    def _auto(self) :
        self.DB = self.db('stocks')
        self.bid = self.parm[0]
        self.RST = self.load_lib('rst')

    def update_v(self) :

        theDate = ''
        preDate = self.DB.one(f"SELECT max(add0) FROM h_{self.bid}_board")
        if  preDate :
            theDate = self.DB.one(f"SELECT min(add0) FROM h_stockHistory_board WHERE add0 > '{preDate}'")
        
        if  theDate :
            
            self.RST.do_tacticsLog(theDate)
            D = self.RST.get_tacticLog(theDate,'V')
            self.RST.nextStep()
            X = self.RST.get_nextStrategyLog('V')
            D |= X
            
            D.update({k:'' for k,v in D.items() if v == None})
            board = f"h_{self.bid}_board"
            qry=self.DB.qry_insert(board,D)
            self.DB.exe(qry)
            self.set_message(f"{theDate}일 정보를 업데이트 하였습니다")
            return self.moveto(f"board/list/{self.bid}")
        
        else :
            self.set_message(f"{self.bid} {preDate} 이후 업데이트된 정보가 없습니다")
            return self.moveto(f"board/list/{self.bid}")
        
    def update_r(self) :

        theDate = ''
        preDate = self.DB.one(f"SELECT max(add0) FROM h_{self.bid}_board")
        if  preDate :
            theDate = self.DB.one(f"SELECT min(add0) FROM h_stockHistory_board WHERE add0 > '{preDate}'")
        
        if  theDate :
            
            self.RST.do_tacticsLog(theDate)
            D = self.RST.get_tacticLog(theDate,'R')
            self.RST.nextStep()
            X = self.RST.get_nextStrategyLog('R')
            D |= X
            
            D.update({k:'' for k,v in D.items() if v == None})
            board = f"h_{self.bid}_board"
            qry=self.DB.qry_insert(board,D)
            self.DB.exe(qry)
            self.set_message(f"{theDate}일 정보를 업데이트 하였습니다")
            return self.moveto(f"board/list/{self.bid}")
        
        else :
            self.set_message(f"{self.bid} {preDate} 이후 업데이트된 정보가 없습니다")
            return self.moveto(f"board/list/{self.bid}")
        
    def update_s(self) :

        theDate = ''
        preDate = self.DB.one(f"SELECT max(add0) FROM h_{self.bid}_board")
        if  preDate :
            theDate = self.DB.one(f"SELECT min(add0) FROM h_stockHistory_board WHERE add0 > '{preDate}'")
        
        if  theDate :
            
            self.RST.do_tacticsLog(theDate)
            D = self.RST.get_tacticLog(theDate,'S')
            self.RST.nextStep()
            X = self.RST.get_nextStrategyLog('S')
            D |= X
            
            D.update({k:'' for k,v in D.items() if v == None})
            
            upDate = float(D['add1']) == 0 and float(D['add2']) == 0 and float(D['add11']) == 0 and float(D['add12']) == 0 and int(D['add9']) == 0
            board = f"h_{self.bid}_board"
            if  upDate :
                qry=self.DB.qry_update(board,D,f"add0='{preDate}'")
                self.DB.exe(qry)

            else :
                qry=self.DB.qry_insert(board,D)
                self.DB.exe(qry)

            self.set_message(f"{theDate}일 정보를 업데이트 하였습니다")
            return self.moveto(f"board/list/{self.bid}")
        
        else :
            self.set_message(f"{self.bid} {preDate} 이후 업데이트된 정보가 없습니다")
            return self.moveto(f"board/list/{self.bid}")
        
    def update_t(self) :

        theDate = ''
        preDate = self.DB.one(f"SELECT max(add0) FROM h_{self.bid}_board")
        if  preDate :
            theDate = self.DB.one(f"SELECT min(add0) FROM h_stockHistory_board WHERE add0 > '{preDate}'")
        
        if  theDate :
            
            self.RST.do_tacticsLog(theDate)
            D = self.RST.get_tacticLog(theDate,'T')
            self.RST.nextStep()
            X = self.RST.get_nextStrategyLog('T')
            D |= X
            
            D.update({k:'' for k,v in D.items() if v == None})
            
            upDate = float(D['add1']) == 0 and float(D['add2']) == 0 and float(D['add11']) == 0 and float(D['add12']) == 0 and int(D['add9']) == 0
            board = f"h_{self.bid}_board"
            if  upDate :
                qry=self.DB.qry_update(board,D,f"add0='{preDate}'")
                self.DB.exe(qry)

            else :
                qry=self.DB.qry_insert(board,D)
                self.DB.exe(qry)

            self.set_message(f"{theDate}일 정보를 업데이트 하였습니다")
            return self.moveto(f"board/list/{self.bid}")
        
        else :
            self.set_message(f"{self.bid} {preDate} 이후 업데이트된 정보가 없습니다")
            return self.moveto(f"board/list/{self.bid}")

