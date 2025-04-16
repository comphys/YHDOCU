from system.core.load import Control
from flask import session

class Rst_log(Control) :

    def index(self) :
        if not 'N_NO' in session : return self.moveto('board/login')
        self.DB = self.db('stocks')
        
        RST = self.load_app_lib('rst')
        RST.op = 'jrst'
        theDate = self.parm[1]
        tactic  = self.parm[0].upper()

        RST.do_tacticsLog(theDate)
        D = RST.get_tacticLog(theDate,tactic)
        RST.nextStep()
        X = RST.get_nextStrategyLog(tactic)
        D |= X
        
        return self.test(RST.D,D)
    
    def rsn(self) :
        if not 'N_NO' in session : return self.moveto('board/login')
        self.DB = self.db('stocks')
        
        RSN = self.load_app_lib('rsn')
        theDate = self.parm[1]
        tactic  = self.parm[0].upper()

        RSN.do_tacticsLog(theDate)
        D = RSN.get_tacticLog(theDate,tactic)
        RSN.nextStep()
        X = RSN.get_nextStrategyLog(tactic)
        D |= X
        
        return self.test(RSN.D,D)
    
    def vtac(self) :
        self.DB = self.db('stocks')
        V = self.load_app_lib('vtactic')
        theDate = self.parm[0]

        D = V.get_tacticLog(theDate)

        return self.test(V.M,D)
   


