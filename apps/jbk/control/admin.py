from system.core.load import Control
from flask import session
import system.hand.myfile as hf

class Admin(Control) :
    def index(self) :
        return self.echo("Hellow Mr. Jang")

    def _auto(self) :
        self.DB = self.db('jbk')
        self.D['user_cnt']   = self.DB.one("SELECT count(no) FROM h_user_list")
        self.D['board_cnt']  = self.DB.one("SELECT count(no) FROM h_board_config")
        self.get_message()

    def board(self) :
        D = {'title' : '보드관리자', 'header' : 'BK Admin', 'skin' : 'admin/board.html'}
        self.model('admin-board')
        D['skins'] = hf.get_dirs(self.skin_dir,'board')
        return self.echo(D)


    def board_edit(self) :
        D = {'title' : '보드관리자', 'header' : 'BK Admin', 'skin' : 'admin/board_edit.html'}
        M = self.model('admin-board')
        M.board_edit()
        return self.echo(D)

    def board_delete(self) :
        D = {'title' : '보드관리자', 'header' : 'BK Admin', 'skin' : 'admin/board_delete.html'}
        self.model('admin-board')
        self.D['section_list'] = self.DB.exe("SELECT section FROM h_board_config GROUP BY section ORDER BY sposition")
        return self.echo(D)

    def board_copy(self) :
        D = {'title' : '보드관리자', 'header' : 'BK Admin', 'skin' : 'admin/board_copy.html'}
        self.model('admin-board')
        self.D['section_list'] = self.DB.exe("SELECT section FROM h_board_config GROUP BY section ORDER BY sposition")
        return self.echo(D)

    def board_sort(self) :
        self.model('admin-board')
        tab = int(self.gets.get('tab',0))
        self.D['active_tab'] = ['','','','']
        self.D['active_tab'][tab] = 'active'
        D = {'title' : '보드관리자', 'header' : 'BK Admin', 'skin' : 'admin/board_sort.html'}
        return self.echo(D)

    def get_message(self) :
        msg = self.DB.exe("SELECT * FROM act_message WHERE no=1", many=1, assoc=True)
        if msg['message'] :
            self.D['act_msg'] = f"<script>h_dialog.{msg['type']}('{msg['message']}')</script>"
            self.DB.exe("UPDATE act_message SET type='', message=''")
        else :
            self.D['act_msg'] = ''



