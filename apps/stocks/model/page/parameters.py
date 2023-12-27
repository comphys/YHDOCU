from system.core.load import Model

class M_parameters(Model) :

    def view(self) :
        cat = '매매전략/VRS'
        self.D['PM'] = self.DB.exe(f"SELECT * FROM parameters WHERE cat='{cat}' ORDER BY key",assoc=True)
        
        self.info(self.D['PM'])

        