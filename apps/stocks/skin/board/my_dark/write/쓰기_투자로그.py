from system.core.load import SKIN

class 쓰기_투자로그(SKIN) :

    def write(self) :

        self.D['TR_add'] = []
        self.D['TR_cat'] = []

        w_width = 1000
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'

        self.D['ChkField'] = ','.join(self.D['MustCheck'])

# -----------------------------------------------------------------------------------------------------------------------
# From Auto Input 
# -----------------------------------------------------------------------------------------------------------------------