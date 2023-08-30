from system.core.load import Control
from flask import session
import system.hand.myfile as hf

class Admin(Control) :
    def index(self) :
        return self.echo("Hellow Jung Yong Hoon")

    def _auto(self) :
        self.DB = self.db('stocks')
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        self.D['user_cnt']   = self.DB.one("SELECT count(no) FROM h_user_list")
        self.D['board_cnt']  = self.DB.one("SELECT count(no) FROM h_board_config")
        self.get_message()

    def board(self) :
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        D = {'title' : '보드관리자', 'header' : 'YH Admin', 'skin' : 'admin/board.html'}
        self.model('admin-board')
        return self.echo(D)


    def board_edit(self) :
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        D = {'title' : '보드관리자', 'header' : 'YH Admin', 'skin' : 'admin/board_edit.html'}
        M = self.model('admin-board')
        M.board_edit()
        return self.echo(D)

    def board_delete(self) :
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        D = {'title' : '보드관리자', 'header' : 'YH Admin', 'skin' : 'admin/board_delete.html'}
        self.model('admin-board')
        self.D['section_list'] = self.DB.exe("SELECT section FROM h_board_config GROUP BY section ORDER BY sposition")
        return self.echo(D)

    def board_copy(self) :
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        D = {'title' : '보드관리자', 'header' : 'YH Admin', 'skin' : 'admin/board_copy.html'}
        self.model('admin-board')
        self.D['section_list'] = self.DB.exe("SELECT section FROM h_board_config GROUP BY section ORDER BY sposition")
        return self.echo(D)

    def board_sort(self) :
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        self.model('admin-board')
        tab = int(self.gets.get('tab',0))
        self.D['active_tab'] = ['','','','']
        self.D['active_tab'][tab] = 'active'
        D = {'title' : '보드관리자', 'header' : 'YH Admin', 'skin' : 'admin/board_sort.html'}
        return self.echo(D)

    def user(self) : 
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        self.model('admin-user')
        D = {'title' : '유저관리자', 'header' : 'YH Admin', 'skin' : 'admin/user.html'}
        return self.echo(D)
        



