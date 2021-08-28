from system.core.load import Control
from flask import session
import system.core.my_utils as my

class Fedit(Control) : 

    def body_source(self) :
        D = {}
        mode = self.gets['mode']
        if  mode == 'body' :
            D['bid'] = self.gets['bid']
            D['No'] = self.gets['no']
            qry = f"SELECT content FROM h_{D['bid']}_board WHERE no={D['No']}"
            D['content'] = self.html_decode(self.DB.one(qry))
            D['content'] = self.html_pretty(D['content'])
            D['skin'] = 'filemanager/source_editor.html'

        elif mode == 'write' or mode == 'modify' or mode == 'add_body' :
            D['skin'] = 'filemanager/source_write.html'
        elif mode == 'docu' :
            D['skin'] = 'filemanager/source_docu.html'

        return self.echo(D)
    
    def source_save(self) :
        D = {'bid':self.D['post']['bid'], 'No': self.D['post']['no'], 'content': self.D['post']['save_text']}
        D['opener_refresh']  = True
        content = self.html_encode(D['content'])
        qry = f"UPDATE h_{D['bid']}_board SET content='{content}' WHERE no={D['No']}"
        self.DB.exe(qry)   
        D['skin'] = 'filemanager/source_editor.html'
        return self.echo(D)

    def view_file(self) :
        f_name = self.D['f_name']
        f_path = self.D['f_path']
        view_file = f_path + '/' + f_name
        
        self.D['f_ext']  = my.file_split(f_name)[2]
        f = open(view_file,encoding="utf-8")
        self.D['contents'] = f.read()
        f.close()


    def open(self) :
        self.D['f_name'] = self.parm[0]

        if      self.D['f_name'] =='bodyCss.css' : self.D['f_path'] = self.V['_pth'].replace('\\','/') + '/apps/docu/skin/board/my_dark/body' 
        elif    self.D['f_name'] =='docuCss.css' : self.D['f_path'] = self.V['_pth'].replace('\\','/') + '/apps/docu/skin/docueditor' 
        else  : self.D['f_path'] = session['epl_path']  

        self.view_file()
        return self.html('filemanager/fedit.html')
    
    def save(self) :
 
        save_file = self.D['post']['save_path']+'/'+self.D['post']['save_name']
 
        f = open(save_file,'w',encoding='utf-8',newline='\n')
        f.write(self.D['post']['save_text'])
        f.close()

        self.D['f_name'] = self.D['post']['save_name']
        self.D['f_path'] = self.D['post']['save_path']
        self.view_file()
        return self.html('filemanager/fedit.html')


