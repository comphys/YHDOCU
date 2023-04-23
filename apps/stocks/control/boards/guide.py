from system.core.load import Control

class Guide(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')
        self.bid   = self.parm[0]
        self.board = 'h_'+self.bid+'_board'
    
    def emptyPick(self) :
        pickDate = self.parm[1]
        qry = f"DELETE FROM {self.board} WHERE add0 >= '{pickDate}'"
        self.DB.exe(qry)
        return self.moveto('board/list/'+self.bid)
    
    def insertPick(self) :
        pickDate = self.parm[1]
        self.DB.tbl, self.DB.wre = ('h_VICTORY_board',f"add0='{pickDate}'")

        line = self.DB.get_line("*")
        del line['no']
        
        qry=self.DB.qry_insert(self.board,line)
        self.DB.exe(qry)
        
        return self.moveto('board/list/'+self.bid)
