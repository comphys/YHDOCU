from system.core.load import Control
from flask import session

class Board(Control) : 

    def index(self) :
        return self.moveto('board/list')


    def _auto(self) :

        self.DB = self.db('jbk')
        if 'JBK_KHJM' in session :
            self.D['bid']     = self.parm[0] if self.parm else 'estimate'
            self.D['tbl']     = 'h_'+self.D['bid']+'_board'
            self.DB.tbl, self.DB.wre = ("h_board_config",f"bid='{self.D['bid']}'")
            self.D['BCONFIG'] = self.DB.get("*",many=1,assoc=True)

            self.skin = 'board/'+self.D['BCONFIG']['skin']
            self.model('board-board_main')
            self.D['DOCU_ROOT'] = self.C['DOCU_ROOT']
  
    def list(self) :
        if not 'JBK_KHJM' in session : return self.moveto('board/login')
        M = self.model('board-board_list')
        M.list_head()
        M.list_main()
        D={'skin': self.skin + '/list/' + self.D['BCONFIG']['sub_list'] }
        self.get_message()
        return self.echo(D)

    def body(self) :
        if not 'JBK_KHJM' in session : return self.moveto('board/login')
        M = self.model('board-board_list')
        M.list_head()
        M.list_main()

        M = self.model('board-board_body')
        M.body_main()
        D={'skin': self.skin + '/body/' + self.D['BCONFIG']['sub_body'] }
        return self.echo(D)      

    def write(self) :
        if not 'JBK_KHJM' in session : return self.moveto('board/login')
        self.D['Mode'] = 'write'
        M = self.model('board-board_write')
        M.write_main()
        D={'skin': self.skin + '/write/' + self.D['BCONFIG']['sub_write']}
        self.get_message()
        return self.echo(D)


    def modify(self) :
        if not 'JBK_KHJM' in session : return self.moveto('board/login')
        self.D['Mode'] = 'modify'
        M = self.model('board-board_write')
        M.write_main()
        D={'skin': self.skin + '/write/' + self.D['BCONFIG']['sub_write']}
        return self.echo(D)
    
    def login(self) :
        session['JBK_KHJM'] = 'ESTIMATE_PROGRAM 20230816'
        session['CSH'] = {}
        return self.moveto('board/list')
       

