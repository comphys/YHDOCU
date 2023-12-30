from system.core.load import Model

class M_parameters(Model) :

    def view(self) :
        
        base_cat = '매매전략/VRS'
        
        cat = self.D['post'].get('category',base_cat)
        if not cat : cat=base_cat

        self.D['PM'] = self.DB.exe(f"SELECT * FROM parameters WHERE cat='{cat}' ORDER BY key",assoc=True)
        if not self.D['PM'] : self.D['PM'] = self.DB.exe(f"SELECT * FROM parameters ORDER BY cat",assoc=True)
            
        sel_cats = self.DB.exe("SELECT distinct cat FROM parameters ORDER BY cat")
        
        self.D['sel_cats'] = [v[0] for v in sel_cats]
        self.D['category'] = cat
        
        