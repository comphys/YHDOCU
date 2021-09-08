from system.core.load import Control
from flask import session

class Docueditor(Control) :

    def docuopen(self) :
        
        self.DB = self.db('docu')
        if not 'N_NO' in session : return self.moveto('board/login')
        self.D['f_path'] = self.gets.get('p').replace('-','/')
        self.D['Docu_name'] = self.gets.get('f') 

        self.D['Docu_path']  = self.D['f_path'].replace('DOCU_ROOT',self.C['DOCU_ROOT'])
        self.D['Docu_file']  = self.D['Docu_path'] + '/' + self.D['Docu_name']
        self.D['DOCU_ROOT'] = self.C['DOCU_ROOT']

        with open(self.D['Docu_file'],'r',encoding='utf-8') as f :
            self.D['DOCU_CONT'] = f.read()

        return self.html("docueditor/main.html")       

    def save(self) :
        if not 'N_NO' in session : return self.moveto('board/login')
        save_file = self.D['post']['f_path']+'/'+self.D['post']['f_name']
        
        with open(save_file,'w',encoding='utf-8') as f :
            f.write(self.D['post']['f_txt'])
        return False 

    def dialog(self) :
        if not 'N_NO' in session : return self.moveto('board/login')
        tool = self.gets['dialog'] 
        return self.html('docueditor/dialog/'+tool+'.html')    

    def login(self) :
        D = {'title':'로그인', 'skin':'board/login.html', 'back':'filemanager/login'}
        
        if self.D['post'] :
            qry = f"SELECT no FROM h_user_list WHERE uid='{self.D['post']['userid']}' and upass='{self.D['post']['userpass']}'"

            if self.DB.cnt(qry) == 1 : 
                session['N_NO'] = self.DB.one(qry)
                session['CSH'] = {}
                return self.moveto('filemanager/home')
        
        return self.echo(D)

