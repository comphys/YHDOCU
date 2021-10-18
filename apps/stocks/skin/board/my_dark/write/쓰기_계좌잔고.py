from system.core.load import SKIN

class 쓰기_계좌잔고(SKIN) :

    def write(self) :
        OBODY = self.D.get('OBODY',None)
        if not OBODY :
            self.D['BODY'] = {}
            self.D['BODY']['add1'] = ''
            self.D['BODY']['add2'] = '0'
            self.D['BODY']['add3'] = '0'
            self.D['BODY']['add4'] = '0.00'
            self.D['BODY']['add5'] = '0.00'
            self.D['BODY']['add7'] = '0'
            self.D['BODY']['add8'] = '0.00'

        else : 
            self.D['BODY'] = OBODY

        self.D['TR_add'] = []
        self.D['TR_cat'] = []
        self.D['method'] = self.SYS.V['_mtd']
        w_width = 815
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'

        self.D['ChkField'] = ','.join(self.D['MustCheck'])






 