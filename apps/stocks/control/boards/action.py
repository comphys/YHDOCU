from system.core.load import Control
import system.core.my_utils as ut

class Action(Control) : 

    def _auto(self) :
        self.DB = self.db('docu')
        self.bid   = self.parm[0]
        self.board = 'h_'+self.bid+'_board'
        self.page  = self.gets.get('page','1') 
  
    def save(self) :
        # h_{bid}_board : [no,brother,add0,uid,uname,content,reply,hit,wdate,mdate,add1~add15]
        
        # 저장 시 [정수 및 실수] 형식은 형태를 수정하여 저장한다. 
        self.DB.tbl, self.DB.wre = ("h_board_config",f"bid='{self.bid}'")
        BCONFIG = self.DB.get("*",many=1,assoc=True)

        USE_KEY = []
        for i in range(16) :
            key = f'add{i}' 
            if BCONFIG[key] :  USE_KEY.append(key)        

        SAVE = self.D['post']

        self.info(SAVE)

        if SAVE['mode'] == 'add_body' :
            no = int(self.gets.get('no',0))
            origin = int(SAVE['brother']) if int(SAVE['brother']) > 0 else no
            qry = f"UPDATE {self.board} SET brother = brother-1 WHERE no={origin}"
            self.DB.exe(qry)
            SAVE['brother'] = no

 
        SAVE['wdate']   = ut.now_timestamp()
        SAVE['mdate']   = SAVE['wdate']
        SAVE['content'] = self.html_encode(SAVE['content'])
        SAVE.pop('mode')
       
        qry = self.DB.qry_insert(self.board,SAVE)
        self.DB.exe(qry)

        return self.moveto('board/list/'+self.bid+'/page='+self.page)

    def delete(self) :
        no      = self.gets['no']
        bid     = self.parm[0]
        page    = self.gets['page']
        
        board_type = self.DB.one(f"SELECT type FROM h_board_config WHERE bid='{bid}'")
        
        if board_type == 'yhboard' :
            qry =   f"SELECT brother FROM h_{bid}_board WHERE no={no}"
            brother = self.DB.one(qry)

            if brother < 0 : self.echo("추가글이 존재합니다")
            if brother > 0 : self.DB.exe(f"UPDATE h_{bid}_board SET brother = brother + 1 WHERE no={brother}")

            qry = f"DELETE FROM h_{bid}_reply WHERE parent={no}"
            self.DB.exe(qry)
        
        qry = f"DELETE FROM h_{bid}_board WHERE no={no}"
        self.DB.exe(qry)

        return self.moveto(f"board/list/{bid}/page={page}")

    def modify(self) :
        # h_{bid}_board : [no,brother,add0,uid,uname,content,reply,hit,wdate,mdate,add1~add15]
        brother = self.D['post'].get('brother',0)
        tbl     = 'h_'+self.parm[0]+'_board'
        no      = self.gets['no']
        con     = f"no={no}"
        # 업데이트 항목 외에는 pop 시킨다.
        self.D['post'].pop('mode')
        self.D['post'].pop('uid')
        self.D['post'].pop('uname')
        # 
        self.D['post']['mdate'] = ut.now_timestamp()
        self.D['post']['content'] = self.html_encode(self.D['post']['content'])

        qry = self.DB.qry_update(tbl,self.D['post'],con)
        self.DB.exe(qry)

        return self.moveto(f"board/body/{self.parm[0]}/no={no}/brother={brother}")

