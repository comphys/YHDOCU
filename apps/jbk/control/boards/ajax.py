from system.core.load import Control
from flask import session
import easygui,json,os,system.core.my_utils as ut
from PIL import Image


class Ajax(Control) :
    def _auto(self) :
        self.DB = self.db('jbk')
        
    def reply_save(self) :

        qry     = f"SELECT uid, uname FROM h_user_list WHERE no={session['N_NO']}"
        USER    = self.DB.line(qry)

        bid     = self.D['post'].pop('bid')
        tbl     = 'h_'+bid+'_reply'
        parent  = self.D['post'].pop('no')
        replyTxt= self.D['post'].pop('replyTxt')

        self.D['post']['parent'] = parent
        self.D['post']['uid'] = USER['uid']
        self.D['post']['wdate'] = ut.now_timestamp()
        self.D['post']['content'] = replyTxt

        self.DB.exe(f"UPDATE h_{bid}_board SET reply = reply + 1 WHERE no = {parent}") 
        qry = self.DB.qry_insert(tbl,self.D['post']) 
        self.DB.exe(qry)
        return False

    def reply_modify(self) :
        replyTxt= self.D['post']['replyTxt']
        qry     = f"UPDATE h_{self.D['post']['bid']}_reply SET content='{replyTxt}' WHERE no = {self.D['post']['rno']}"
        self.DB.exe(qry)
        return False

    def reply_delete(self) :
        no      = self.D['post']['no']
        bid     = self.D['post']['bid']
        rno     = self.D['post']['rno']
        qry     = f"DELETE FROM h_{bid}_reply WHERE no={rno}"
        self.DB.exe(qry)
        self.DB.exe(f"UPDATE h_{bid}_board SET reply = reply - 1 WHERE no ={no}")
        return False

    def checkdir(self,d=True) :
        check = self.D['post']['check']
        if d : 
            if os.path.isdir(check) : return 'OK'
            else : return 'NFND'
        else :
            if os.path.isfile(check) : return 'OK'
            else : return 'NFND'


    def win_exe(self) :
        f_in = self.D['post']['exe_file']
        if not os.path.isfile(f_in) : return "NFND"
        self.win_run(f_in) 
    
    def win_folder(self) :
        f_in = self.D['post']['exe_file']
        if os.path.isdir(f_in) : self.open_explorer(f_in);  return 'OK'
        else : return "NFND" 
    
    def upload_file_check(self) :
        f_path = self.D['post']['file_location']
        f_name = self.D['post']['file_name']
        D={}
        D['l_chk'] = '#00d068' if os.path.isdir(f_path) else '#ff874d'
        D['f_chk'] = '#00d068' if os.path.isdir(f_path) else '#ff874d'
        return json.dumps(D) 

    def file_select(self) :
        docu_root = self.D['post']['f_path']
        f_in = easygui.fileopenbox("파일을 선택하세요",title="Open",default=docu_root+'/',filetypes=["*.*"])
        f_xx = f_in.replace("\\","/")
        return f_xx

    def file_attach(self) :
        # D:/JYHDOCU/htdocs/YH문서함
        docu_root = self.D['post']['f_path']
        f_in = easygui.fileopenbox("파일을 선택하세요",title="Open",default=docu_root+'/',filetypes=["*.*"])
        f_xx = ut.file_split(f_in.replace("\\","/"))
        if f_xx[2].lower() in ['jpg','png','jpeg','gif'] :
            f_path = f_xx[0].replace(docu_root,'')
            f_attach = f"<span data-myimage='{f_path}'>{f_xx[1]}</span>"
        else :
            f_attach = f"<span data-myfile='{f_xx[0]}'>{f_xx[1]}</span>"
        return f_attach

    def thumb_check(self) :
        thumb_file = self.D['post']['url']
        realX_file = thumb_file.replace('/썸즈네일/','/')
        with Image.open(realX_file) as im : 
            reX = im.size[0]
            reY = im.size[1]

        if os.path.isfile(thumb_file) :
            with Image.open(thumb_file) as im :
                thx = im.size[0]
                thy = im.size[1]
            rst = "썸즈네일이 생성되어 있습니다."
            thm = "DONE"
        else :
            thx = 0
            thy = 0
            rst = "썸즈네일이 존재하지 않습니다."
            thm = "NONE"
        data = {"rst" : rst, "thx": thx, "thy" : thy, "thm" : thm, "reX" : reX, "reY" : reY}
        return json.dumps(data)

    def thumb_make(self) :
        orign_pic = self.D['post']['path'] + '/' + self.D['post']['name']
        thumb_xxx = int(self.D['post']['xxx'])
        thumb_yyy = int(self.D['post']['yyy'])

        with Image.open(orign_pic) as im :
            oriX = im.size[0]
            oriY = im.size[1]
            newX = thumb_xxx
            newY = thumb_yyy
            if newX == 0 : newX = int(oriX/oriY*newY)
            if newY == 0 : newY = int(oriY/oriX*newX)

            resiz_cal = (newX,newY)

            im = im.resize(resiz_cal,Image.LANCZOS)

            new_folder = self.D['post']['path'] + '/썸즈네일'
        
            if not os.path.exists(new_folder) : os.makedirs(new_folder) 

            im.save(new_folder+'/'+ self.D['post']['name'])
    
    def live_edit(self) :
        qry     = f"UPDATE h_{self.D['post']['bid']}_board SET {self.D['post']['fid']}='{self.D['post']['val']}' WHERE no = {self.D['post']['no']}"
        self.DB.exe(qry)
        return False
