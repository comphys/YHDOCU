from system.core.load import Control
from flask import session, request
import system.core.my_utils as my

class Board(Control) : 

    def index(self) :
        return self.moveto('board/list')

    def _auto(self) :

        self.DB = self.db('stocks')
        self.D['platform'] = 'On Local' if  self.D['_lcl'] else ''

        if '__u_Ino__' in session :
            self.D['bid']  = self.parm[0] if self.parm else self.C['init_board']
            self.D['tbl']  = 'h_'+self.D['bid']+'_board'
            self.D['USER'] = self.DB.line(f"SELECT * FROM h_user_list WHERE uid='{session['__u_Ino__']}'")
            self.D['BCONFIG'] = self.DB.line(f"SELECT * FROM h_board_config WHERE bid='{self.D['bid']}'")

            self.lAccess = True if self.D['USER']['level'] >= self.D['BCONFIG']['acc_list']  else False
            self.bAccess = True if self.D['USER']['level'] >= self.D['BCONFIG']['acc_body']  else False
            self.wAccess = True if self.D['USER']['level'] >= self.D['BCONFIG']['acc_write'] else False

            self.skin = 'board/'+self.D['BCONFIG']['skin']
            self.model('board-board_main')
            self.D['DOCU_ROOT'] = self.C['DOCU_ROOT']



    def list(self) :

        if not self.lAccess : return self.moveto(self.D['USER']['home'])
        M = self.model('board-board_list')
        M.list_head()
        M.list_main()
        D={'skin': self.skin + '/list/' + self.D['BCONFIG']['sub_list'] }
        self.get_message()
        return self.echo(D)

    def body(self) :

        if not self.bAccess : return self.moveto(self.D['USER']['home'])
        M = self.model('board-board_list')
        M.list_head()
        M.list_main()

        M = self.model('board-board_body')
        M.body_main()
        D={'skin': self.skin + '/body/' + self.D['BCONFIG']['sub_body'] }
        return self.echo(D)      

    def write(self) :
        
        if not self.wAccess : return self.moveto(self.D['USER']['home'])
        self.D['Mode'] = 'write'
        M = self.model('board-board_write')
        M.write_main()
        D={'skin': self.skin + '/write/' + self.D['BCONFIG']['sub_write']}
        self.get_message()
        return self.echo(D)

    def add_body(self) :

        if not self.wAccess : return self.moveto(self.D['USER']['home'])
        self.D['Mode'] = 'add_body'
        self.D['No'] = self.gets['no']
        self.D['Brother']  = int(self.gets.get('brother','0')) 
        self.D['Form_act'] = self.D['_bse'] + 'boards-action/save/' + self.D['bid']
        o_no = self.D['Brother'] if self.D['Brother'] > 0 else self.D['No']
        sql = f"SELECT add0 FROM h_{self.parm[0]}_board WHERE no={o_no}"
        self.D['B_title'] = self.DB.one(sql)
        self.D['Form_act'] += "/no=" + self.D['No']
        self.D['MustCheck'] = "'add0','추가 타이틀'"
        if self.D['BCONFIG']['width'] : w_width  = int( (self.D['BCONFIG']['width']).replace('px','') )
        else : w_width = 815
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'
        D={'skin': self.skin + '/write/' + self.D['BCONFIG']['sub_write']}
        return self.echo(D)

    def modify(self,mode='modify') :

        if not self.wAccess : return self.moveto(self.D['USER']['home'])
        self.D['Mode'] = 'modify'
        M = self.model('board-board_write')
        M.write_main()
        D={'skin': self.skin + '/write/' + self.D['BCONFIG']['sub_write']}
        return self.echo(D)

   
    def ajax(self) :

        if not self.lAccess : return self.moveto(self.D['USER']['home'])
        M = self.load_bajax(self.D['bid'],self.parm[1])
        return M()
