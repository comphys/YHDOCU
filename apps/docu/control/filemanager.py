from flask.globals import request
from system.core.load import Control
from flask import session
import system.core.my_utils as my

class filemanager(Control) : 

    def _auto(self) :
        self.DB = self.db('docu')
        self.epl = self.load_app_lib('epl')
        self.D['ROOT'] = self.epl.ROOT
        self.F ={}

    def _base(self) :
        if not 'N_NO' in session : return self.moveto('filemanager/login')
        self.D['DIR_LIST']      = self.epl.dir_list()
        self.D['DIR_SLICED']    = self.epl.slice()
        ht = self.gets.get('fname',False)

        file_lists = self.epl.file_list()
        if file_lists :
            FILES = []
            for val in file_lists :
                fname   =   session['epl_path'] + '/' + val
                ctime   =   my.file_ctime(fname)
                size    =   self.epl.number_unit(my.file_size(fname))
                fext    =   my.file_split(fname)[2]
                icon_src=   self.epl.get_icon(fext)
                ht_tr   =   "class='file-found'" if ht == val else ''

                FILES.append({'icon':icon_src, 'name':val, 'size':size, 'ctime':ctime, 'f_found':ht_tr})
            
            self.D['FILE_LIST'] = FILES

    
    def move(self) :
        if not 'N_NO' in session : return self.moveto('filemanager/login')
        dest2 = [x for x in self.parm if x.find('fname=') == -1]
        if dest2[0] =='home' : self.moveto('filemanager/home')
        dests = self.epl.ROOT + '/' + '/'.join(dest2)
        if my.checkdir(dests) :
            session['epl_path'] = self.epl.path = dests
            self._base()
            self.footer()
            return self.echo(self.F)
        else : return "요청하신 경로가 존재하지 않습니다."

    def ndir(self) :
        if not 'N_NO' in session : return self.moveto('filemanager/login')
        ndir = self.parm[0]
        self.epl.push(ndir)
        self._base()
        self.footer()
        return self.echo(self.F)

    def home(self) :
        if not 'N_NO' in session : return self.moveto('filemanager/login')
        session['epl_path'] = self.epl.path = self.epl.ROOT
        self._base()
        self.footer()
        return self.echo(self.F)

    def set(self) :
        if not 'N_NO' in session : return self.moveto('filemanager/login')
        times = int(self.parm[0])
        for x in range(times) : self.epl.up()
        self._base()
        self.footer()
        return self.echo(self.F)

    def footer(self) :
        self.D['JS_CUR_PATH'] = session['epl_path']
        self.D['JS_F_PATH'] = '' if self.D['JS_CUR_PATH'] == self.D['ROOT']  else self.D['JS_CUR_PATH'].replace(self.D['ROOT']+'/','')
        self.F = {'skin':'filemanager/filemanager.html'}
    
    def up(self) :
        if not 'N_NO' in session : return self.moveto('filemanager/login')
        self.epl.up()
        self._base()
        self.footer()
        return self.echo(self.F)

    def login(self) :
        D = {'title':'로그인', 'skin':'board/login.html', 'back':'filemanager/login'}
        
        if self.D['post'] :
            qry = f"SELECT no FROM h_user_list WHERE uid='{self.D['post']['userid']}' and upass='{self.D['post']['userpass']}'"

            if self.DB.cnt(qry) == 1 : 
                session['N_NO'] = self.DB.one(qry)
                session['CSH'] = {}
                return self.moveto('filemanager/home')
        
        return self.echo(D)

    def logout(self) : 
        if 'N_NO' in session : del session['N_NO'] ; del session['CSH']
        return self.moveto('filemanager/login')

    # AJAX SECTION -----------------------------------------------------------------------------------------------------------------------
    def file_exec(self) :
        f_in = session['epl_path'] +'/'+self.D['post']['f_name']
        self.win_run(f_in)
        

    def add_file(self) :
        operation = self.D['post']['operation']
        new_name  = self.D['post']['new_file_name']
        new_fx    = session['epl_path'] + '/' + new_name

        if operation == 'file' :
            ext = my.file_split(new_fx)[2]
            if not ext : new_fx += '.docu'
            if my.makefile(new_fx) : return self.echo('OK')
        
        elif operation == 'folder' :
            if my.makedir(new_fx) : return self.echo('OK')

    def del_file(self) :
        operation = self.D['post']['operation']

        if operation == 'del_file' : 
            del_fx = session['epl_path'] + '/' + self.D['post']['f_name']
            my.delete_file(del_fx) 
            return self.echo('delete_ok')
        elif operation == 'del_folder' :
            del_fx = session['epl_path'] 
            if my.delete_foler(del_fx) : return self.echo('OK')
    
    def file_dropUp(self) :
        f = request.files['drop_file']
        save_dir = request.form["save_dir"]
        f.save(save_dir+'/'+f.filename)
        return self.echo('OK')
    
    def openFolderInWindow(self) :
        folder_path = self.D['post']['f_path']
        self.open_explorer(folder_path)
    
    def file_rename(self) : 
        f_old = self.D['post']['f_oname']
        f_new = self.D['post']['f_rname']
        f_pth = my.file_split(f_old)[0]

        f_old = self.C['DOCU_ROOT'] + '/' + f_old
        f_new = self.C['DOCU_ROOT'] + '/' + f_pth + '/' + f_new
        my.rename_file(f_old,f_new)
        return False

        


        


