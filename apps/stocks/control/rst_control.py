from system.core.load import Control
from flask import session

class Rst_control(Control) :

    def index(self) :
        if not 'N_NO' in session : return self.moveto('board/login')
        self.DB = self.db('stocks')
        
        RST = self.load_lib('rst')
        # RST.init_capital(38715.40,12906.54,12906.54,12906.54)
        # RST.get_simulated_result('2024-08-24')
        # syncD = RST.get_sync_data(origin=True)

        # RST.get_thisYearResult()
        # RST.result()

        D = RST.get_tacticLog('2024-08-27')

        return self.test(RST.M,D)
   


