from system.core.load import Control
from flask import session
import os

class Board(Control) : 

    def index(self) :
        return self.moveto('board/list')


    def _auto(self) :

        self.DB = self.db('stocks')
        
        if 'N_NO' in session :

            self.DB.tbl, self.DB.wre = ("h_user_list",f"no={session['N_NO']}")
            self.D['USER'] = self.DB.get("*",many=1, assoc=True)

            self.D['bid']     = self.parm[0] if self.parm else self.C['init_board']
            self.DB.tbl, self.DB.wre = ("h_board_config",f"bid='{self.D['bid']}'")
            self.D['BCONFIG'] = self.DB.get("*",many=1,assoc=True)

            self.skin = 'board/'+self.D['BCONFIG']['skin']
            self.model('board-board_main')
            self.D['DOCU_ROOT'] = self.C['DOCU_ROOT']


    def list(self) :
        if not 'N_NO' in session : return self.moveto('board/login')
        M = self.model('board-board_list')
        M.list_head()
        M.list_main()
        D={'skin': self.skin + '/list/' + self.D['BCONFIG']['sub_list'] }
        return self.echo(D)

    def body(self) :
        if not 'N_NO' in session : return self.moveto('board/login')
        M = self.model('board-board_list')
        M.list_head()
        M.list_main()

        M = self.model('board-board_body')
        M.body_main()
        D={'skin': self.skin + '/body/' + self.D['BCONFIG']['sub_body'] }
        return self.echo(D)      

    def write(self) :
        if not 'N_NO' in session : return self.moveto('board/login')
        self.D['Mode'] = 'write'
        M = self.model('board-board_write')
        M.write_main()
        D={'skin': self.skin + '/write/' + self.D['BCONFIG']['sub_write']}
        return self.echo(D)

    def modify(self,mode='modify') :
        if not 'N_NO' in session : return self.moveto('board/login')
        self.D['Mode'] = 'modify'
        M = self.model('board-board_write')
        M.write_main()
        D={'skin': self.skin + '/write/' + self.D['BCONFIG']['sub_write']}
        return self.echo(D)

    def login(self) :
        D = {'title':'로그인', 'skin':'board/login.html', 'back':'board/login'}
        
        if self.D['post'] :
            qry = f"SELECT no FROM h_user_list WHERE uid='{self.D['post']['userid']}' and upass='{self.D['post']['userpass']}'"

            if self.DB.cnt(qry) == 1 : 
                session['N_NO'] = self.DB.one(qry)
                session['CSH'] = {}
                return self.moveto('board/list')
        
        return self.echo(D)

    def logout(self) : 
        if 'N_NO' in session : del session['N_NO'] ; del session['CSH']
        return self.moveto('board/login')
