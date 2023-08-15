from flask.globals import request
from system.core.load import Control
from flask import session
import system.core.my_utils as my

class Filemanager(Control) : 

    def _auto(self) :
        self.DB = self.db('jbk')
        self.F ={}

    # AJAX SECTION -----------------------------------------------------------------------------------------------------------------------
    def file_exec(self) :
        f_in = session['epl_path'] +'/'+self.D['post']['f_name']
        self.win_run(f_in)
        

    def del_file(self) :
        operation = self.D['post']['operation']

        if operation == 'del_file' : 
            del_fx = session['epl_path'] + '/' + self.D['post']['f_name']
            my.delete_file(del_fx) 
            return self.echo('delete_ok')
        elif operation == 'del_folder' :
            del_fx = session['epl_path'] 
            if my.delete_foler(del_fx) : return self.echo('OK')
    
    def delete_file(self) :
        src = self.C['DOCU_ROOT'] + '/' + self.D['post']['f_name']
        my.delete_file(src)


    def clear_folder(self) :
        folder_pass = session['epl_path']
        my.clear_folder(folder_pass)

    def file_dropUp(self) :
        f = request.files['drop_file']
        save_dir = request.form["save_dir"]
        file_full_name = save_dir+'/'+f.filename
        file_path_name = file_full_name.replace(self.C['DOCU_ROOT'],'/DOCU_ROOT')
        f.save(save_dir+'/'+f.filename)
        return self.echo(file_path_name)
    
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

    def copy_paste_file(self) :
        f_src = self.D['post']['src'] ; src = self.D['ROOT'] + '/' + f_src
        f_tgt = self.D['post']['tgt'] ; tgt = self.D['ROOT'] + '/' + f_tgt
        opt   = self.D['post']['opt'] ; 
        if   opt == 'copy' : my.copy_file(src,tgt)
        elif opt == 'move' : my.move_file(src,tgt)
        return self.echo('OK')

        


        


