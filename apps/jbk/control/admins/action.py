from system.core.load import Control

class Action(Control) :

    def _auto(self) :
        self.DB = self.db('jbk')

    def set_message(self,msg,typ='alert') :
        self.DB.exe(f"UPDATE act_message SET type='{typ}', message='{msg}' WHERE no=1")

    def board_add(self) :
        M = self.model('admin-board')
        notice = M.board_add()
        if notice : self.set_message(notice)
        return self.moveto('admin/board')

    def board_delete(self) :
        bid     = self.D['post']['d_bid']
        empty   = self.D['post'].get('empty',None)

        if bid == 'system' :
            self.set_message(f"삭제할 수 없는 보드({bid}) 입니다")
            return self.moveto('admin/board_delete')

        DEL = self.DB.exe(f"SELECT folder,type,title FROM h_board_config WHERE bid='{bid}'",many=1,assoc=True)

        if not empty :
            self.DB.exe(f"DELETE FROM h_board_config WHERE bid='{bid}'")
            self.DB.exe(f"DROP TABLE h_{bid}_board")
            self.DB.exe(f"DROP TABLE h_{bid}_reply")
            self.set_message(f"{bid}({DEL['title']}) 보드를 삭제하였습니다.")
        else :
            self.DB.exe(f"DELETE FROM h_{bid}_board")
            self.DB.exe(f"DELETE FROM h_{bid}_reply")
            self.set_message(f"{bid}({DEL['title']}) 보드를 초기화 하였습니다.")
        
        return self.moveto('admin/board_delete')

    def add_exfield(self) :
        # exConf = [title/type/align/color/format/width/must]
        add_fset = f"{self.D['post']['addFieldTitle']}/{self.D['post']['addFieldType']}/{self.D['post']['addFieldAlign']}////"
        qry = f"UPDATE h_board_config SET {self.D['post']['addFieldKey']} = '{add_fset}' WHERE bid='{self.D['post']['bid']}'"
        self.DB.exe(qry)
        return self.moveto(f"admin/board_edit/bid={self.D['post']['bid']}/sec={self.D['post']['sec']}/tab=2")

    def board_edit_basic(self) :
        bid = self.D['post'].pop('bid')
        wre = f"bid = '{bid}'"
        qry = self.DB.qry_update('h_board_config', self.D['post'], wre)
        self.DB.exe(qry)
        return self.moveto(f"admin/board_edit/bid={bid}/sec={self.D['post']['section']}/tab=0")

    def board_edit_access(self) :
        bid = self.D['post'].pop('bid')
        sec = self.D['post'].pop('sec')
        wre = f"bid = '{bid}'"
        qry = self.DB.qry_update('h_board_config', self.D['post'], wre)
        self.DB.exe(qry)
        return self.moveto(f"admin/board_edit/bid={bid}/sec={sec}/tab=1")

    def board_edit_output(self) :
        bid = self.D['post'].pop('bid')
        sec = self.D['post'].pop('sec')
        self.D['post']['row_sum'] = self.D['post'].get('row_sum','off')
        self.D['post']['row_flt'] = self.D['post'].get('row_flt','off')
        self.D['post']['stayfom'] = self.D['post'].get('stayfom','off')
        wre = f"bid = '{bid}'"
        qry = self.DB.qry_update('h_board_config', self.D['post'], wre)
        self.DB.exe(qry)
        return self.moveto(f"admin/board_edit/bid={bid}/sec={sec}/tab=3")

    def section_sort(self) :
        for key,val in self.D['post'].items() :
            ix = key.find('_acc_')
            if ix != -1 :
                self.DB.exe(f"UPDATE h_board_config SET acc_sect={val} WHERE section='{key[0:ix]}'")
            else :
                self.DB.exe(f"UPDATE h_board_config SET sposition={val} WHERE section='{key}'")
        
        return self.moveto(f"admin/board_sort/tab=0")


    def board_sort(self) :
        tab = self.parm[0]
        for key,val in self.D['post'].items() :
            ix = key.find('_acc_')
            if ix != -1 :
                self.DB.exe(f"UPDATE h_board_config SET acc_board={val} WHERE bid='{key[0:ix]}'")
            else :
                self.DB.exe(f"UPDATE h_board_config SET bposition={val} WHERE bid='{key}'")
        
        return self.moveto(f"admin/board_sort/tab={tab}")

    def board_copy(self) :
        cbid = self.D['post']['c_bid']
        nbid = self.D['post']['n_bid']
        ntle = self.D['post']['n_tle']

        self.DB.tbl,self.DB.wre = ('h_board_config',f"bid='{cbid}'")
        config_data = self.DB.get_line("*")
        config_data.pop('no')
        config_data['bid']   = nbid
        config_data['title'] = ntle

        insert_data = {key: value for key, value in config_data.items() if value != None}
        qry = self.DB.qry_insert('h_board_config',insert_data)
        self.DB.exe(qry)

        self.DB.clear()
        self.DB.tbl,self.DB.wre = ('sqlite_master', f"name='h_{cbid}_board'")
        qry = self.DB.get_one('sql')
        qry = qry.replace(f"h_{cbid}_board",f"h_{nbid}_board")
        self.DB.exe(qry)
        return self.moveto('admin/board')


   