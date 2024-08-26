from system.core.load import Control
from flask import session

class Rst_control(Control) :

    def index(self) :
        if not 'N_NO' in session : return self.moveto('board/login')
        self.DB = self.db('stocks')
        
        RST = self.load_lib('rst')
        RST.init_capital(60000,120000,120000,120000)
        RST.get_simulated_result()

        return self.echo(RST.D['R_최종수익'])

