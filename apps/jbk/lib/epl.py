from flask import session
import os

class EPL :

    def __init__(self,SYS) :    
        self.SYS = SYS
        self.D = SYS.D
        self.info = SYS.info
        self.delimiter = '/'
        self.path = ''
        self.C = SYS.C
        self.ROOT = self.C['DOCU_ROOT']

        session['epl_path'] = session.get('epl_path',self.ROOT )
        self.path = session['epl_path']

    def push(self,add) :
        new_dir = self.path + self.delimiter + add
        self.path = session['epl_path'] = new_dir

    def pop(self) :
        needle = self.path.rfind(self.delimiter)
        if needle == -1 : return
        session['epl_path'] = self.path = self.path[0:needle]

    def up(self) :
        if self.path == self.ROOT : return "현재 최상위 경로 입니다."
        else : self.pop()

    def root(self) :
        self.path = session['epl_path'] = self.ROOT

    def slice(self) :
        dir_sliced = {}
        path_temp = self.path.replace(self.ROOT,'HOME')
        dirs = path_temp.split(self.delimiter)
        cnt  = len(dirs)

        for val in dirs : 
            cnt = cnt -1 
            dir_sliced[cnt] = val

        return dir_sliced

    
    def dir_list(self) :
        if not os.path.isdir(self.path) :
            self.pop()
            return 
        _dir = self.path
        return [d for d in os.listdir(_dir) if os.path.isdir(os.path.join(_dir, d))]

    def file_list(self) :
        _dir = self.path
        return [f for f in os.listdir(_dir) if os.path.isfile(os.path.join(_dir, f))]

    def get_icon(self,ext) :
        ext = ext.lower()
        if   ext == 'docu': icon = 'docu.png' 
        elif ext == 'php' : icon = 'php.png'
        elif ext == 'css' : icon = 'css.png'
        elif ext == 'js'  : icon = 'js.png'
        elif ext == 'html': icon = 'html.png'
        elif ext in ('jpg','png','gif') : icon = 'jpg.png'
        elif ext == 'pdf' : icon = 'pdf.png'
        elif ext in ('hwp','hox')  : icon = 'hwp.gif'
        elif ext in ('xls','xlsx') : icon = 'excel.png'
        elif ext in ('ppt','pptx','pptm') : icon = 'ppt.png'
        elif ext in ('mp4','wmv','mkv') : icon = 'mpg.png'
        elif ext in ('mp3','wav','mpa') : icon = 'mp3.png'
        elif ext == 'zip' : icon = 'zip.png'
        else : icon = 'unknown.png'

        return icon 

    def number_unit(self,size) :
        if size < 1 : return '0'
        if size / 1048576 > 1 : return str(round(size/1048576,2)) + 'MB'
        if size / 1024 > 1    : return str(round(size/1024,2)) + 'KB'
        if size / 1024 < 1    : return str(size) + 'byte'

    def sort_array_by_ext(self,arr) :
        arr.sort(key=lambda f: os.path.splitext(f))

    












