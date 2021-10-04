from system.core.load import SKIN
import system.core.my_utils as ut

class 쓰기_매매전략(SKIN) :

    def write(self) :
        OBODY = self.D.get('OBODY',None)
        if not OBODY :
            self.D['BODY'] = {}
            self.D['BODY']['add1'] = ''
            self.D['BODY']['add2'] = '40'
            self.D['BODY']['add3'] = '50'
            self.D['BODY']['add4'] = '0'
            self.D['BODY']['add5'] = '10'

        else : 
            self.D['BODY'] = OBODY


        w_width = 755
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'
        self.D['ChkField'] = ','.join(self.D['MustCheck'])

        dir = self.SYS.V['_pth'] + '/apps/stocks/model/backtest'
        stg = ut.get_files(dir)
        self.D['base_strategy'] = [x[9:14] for x in stg]

        # -------------------
