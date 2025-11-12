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


class Ajax(Model) :

    def update_parameters(self) :

        key = self.D['post']['key']
        val = self.D['post']['val']
        no  = self.D['post']['no']

        sql = f"UPDATE parameters SET {key}= '{val}' WHERE no={no}"
        self.DB.exe(sql)
            
        return 
    
    def delete_parameters(self) :
        
        no  = self.D['post']['no']
        sql = f"DELETE FROM parameters WHERE no={no}"
        self.DB.exe(sql)
        
        return 
    
    def insert_parameters(self) :
        
        cat = self.D['post']['cat']
        ID  = {'key':'000','name':'XXX','val':'   ','type':'char','description':'-----','cat':cat}
        sql = self.DB.qry_insert('parameters',ID)
        self.DB.exe(sql)

        return 
        
        