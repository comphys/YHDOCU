from system.core.load import Control
from flask import session

class Docueditor(Control) :

    def docuopen(self) :

        self.D['f_path'] = self.gets.get('p').replace('-','/')
        self.D['Docu_name'] = self.gets.get('f') 

        self.D['Docu_path']  = self.D['f_path'].replace('DOCU_ROOT',self.C['DOCU_ROOT'])
        self.D['Docu_file']  = self.D['Docu_path'] + '/' + self.D['Docu_name']
        self.D['DOCU_ROOT'] = self.C['DOCU_ROOT']

        with open(self.D['Docu_file'],'r',encoding='utf-8') as f :
            self.D['DOCU_CONT'] = f.read()

        return self.html("docueditor/main.html")       

    def save(self) :
        save_file = self.D['post']['f_path']+'/'+self.D['post']['f_name']
        
        with open(save_file,'w',encoding='utf-8') as f :
            f.write(self.D['post']['f_txt'])
        return False 

    def dialog(self) :
        tool = self.gets['dialog'] 
        return self.html('docueditor/dialog/'+tool+'.html')    
