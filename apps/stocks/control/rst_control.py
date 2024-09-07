from system.core.load import Control
from flask import session

class Rst_control(Control) :

    def index(self) :
        if not 'N_NO' in session : return self.moveto('board/login')
        self.DB = self.db('stocks')
        
        RST = self.load_lib('rst')
        theDate = self.parm[1]
        tactic  = self.parm[0]

        RST.do_tacticsLog(theDate)
        D = RST.get_tacticLog(theDate,tactic)
        RST.nextStep()
        X = RST.get_nextStrategyLog(tactic)
        D |= X
        
        return self.test(RST.D,D)
    
    def vtac(self) :
        self.DB = self.db('stocks')
        V = self.load_lib('vtactic')
        theDate = self.parm[0]

        V.do_tacticsLog(theDate)
        D = V.get_tacticLog(theDate)

        return self.test(V.M,D)
   


