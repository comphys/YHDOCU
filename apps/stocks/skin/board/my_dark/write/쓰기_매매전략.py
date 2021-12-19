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
            self.D['BODY']['add6'] = 'on'
            self.D['BODY']['add7'] = 'off'
            self.D['BODY']['add8'] = '100'
            self.D['BODY']['add9'] = '12'
            self.D['BODY']['add10'] = '0'
            self.D['BODY']['add11'] = '5'
            self.D['BODY']['add12'] = 'on'
            self.D['BODY']['add14'] = 'off'
            self.D['BODY']['add15'] = 'on'
            self.D['BODY']['add16'] = 'off'
            self.D['BODY']['add17'] = '100'
            self.D['BODY']['add18'] = '10'
            self.D['BODY']['add20'] = ''
            self.D['BODY']['add21'] = 'on'
            self.D['BODY']['add22'] = '-18'
            self.D['BODY']['add23'] = '-6'
            self.D['BODY']['add24'] = '2'
            self.D['BODY']['add25'] = '90'



        else : 
            self.D['BODY'] = OBODY


        w_width = 670
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'
        self.D['ChkField'] = ','.join(self.D['MustCheck'])

        dir = self.SYS.V['_pth'] + '/apps/stocks/model/backtest'
        stg = ut.get_file_names(dir)
        self.D['base_strategy'] = [x[9:] for x in stg]

        # -------------------
