from system.core.load import Model
import system.hand.myfile as hf

class M_user(Model) :
    
    def _auto(self) :
        sql = "SELECT ugroup as grp, count('uid') as cnt FROM h_user_list GROUP by ugroup ORDER BY gposition"
        self.D['ugrp'] = self.DB.exe(sql,assoc=True)
        
        
        for val in self.D['ugrp'] :
            sql = f"SELECT uid,uname,ugroup FROM h_user_list WHERE ugroup = '{val['grp']}' ORDER BY level DESC"
            self.D[val['grp']] = self.DB.exe(sql,assoc=True)
    
          
        self.D['grp'] = self.gets.get('grp',None)
        self.D['uid'] = self.gets.get('uid',None)

    def user_edit(self) :
        self.D['user'] = self.DB.one(f"SELECT * FROM h_user_list WHERE uid='{self.D['uid']}'")
        




            


        
