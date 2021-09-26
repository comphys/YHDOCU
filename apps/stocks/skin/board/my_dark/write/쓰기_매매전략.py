from system.core.load import SKIN
import system.core.my_utils as ut

class 쓰기_매매전략(SKIN) :

    def write(self) :
        OBODY = self.D.get('OBODY',None)
        if not OBODY :
            self.D['BODY'] = {}
            self.D['BODY']['add1'] = ''
            self.D['BODY']['add2'] = ''
            self.D['BODY']['add3'] = '50'

            self.D['BODY']['add4'] = '50'
            self.D['BODY']['add5'] = '0'
            self.D['BODY']['add6'] = '10'
            
            self.D['BODY']['add7'] = '100'
            self.D['BODY']['add8'] = '10'
            self.D['BODY']['add9'] = '0'

            self.D['BODY']['add10'] = '50'
            self.D['BODY']['add11'] = '0'
            self.D['BODY']['add12'] = '5'

            self.D['BODY']['add14'] = ''
            self.D['BODY']['add15'] = '0/0/0/0/0/0/0/'
            self.D['BODY']['sub5']  = '0'
            self.D['BODY']['sub6']  = '0'
            self.D['BODY']['sub7']  = '0'
            self.D['BODY']['sub8']  = '0'
            self.D['BODY']['sub9']  = '0'
            self.D['BODY']['sub10'] = '0'
            self.D['BODY']['sub11'] = '0'
            self.D['BODY']['sub12'] = '5'
            self.D['BODY']['sub14'] = ''
            self.D['BODY']['sub15'] = '0/0/0/0/0/0/0/'
            self.D['BODY']['sub16'] = 'off'
            self.D['BODY']['sub17'] = 'off'
            self.D['BODY']['sub18'] = 'off'
            self.D['BODY']['sub19'] = '5'

        else : 
            self.D['BODY'] = OBODY
            self.D['BODY']['sub5']  = OBODY['add15'][0:1]
            self.D['BODY']['sub6']  = OBODY['add15'][2:3]
            self.D['BODY']['sub7']  = OBODY['add15'][4:5]
            self.D['BODY']['sub8']  = OBODY['add15'][6:7]
            self.D['BODY']['sub9']  = OBODY['add15'][8:9]
            self.D['BODY']['sub10'] = OBODY['add15'][10:11]
            self.D['BODY']['sub11'] = OBODY['add15'][12:13]

        w_width = 755
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'
        self.D['ChkField'] = ','.join(self.D['MustCheck'])

        dir = self.SYS.V['_pth'] + '/apps/stocks/model/backtest'
        stg = ut.get_files(dir)
        self.D['base_strategy'] = [x[9:14] for x in stg]

        # -------------------
