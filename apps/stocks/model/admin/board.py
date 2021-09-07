from system.core.load import Model
import system.hand.myfile as hf

class M_board(Model) :
    
    def _auto(self) :
        sql = "SELECT section as sec, count(bid) as cnt, acc_sect as acc FROM h_board_config GROUP by section ORDER BY sposition"
        self.D['bgrp'] = self.DB.exe(sql,assoc=True)

        for val in self.D['bgrp'] :
            sql = f"SELECT title,bid,section,acc_board as acc FROM h_board_config WHERE section = '{val['sec']}' ORDER BY bposition"
            self.D[val['sec']] = self.DB.exe(sql,assoc=True)
        
        self.D['sec'] = self.gets.get('sec',None)
        self.D['bid'] = self.gets.get('bid',None)

    def board_edit(self) :
        tab = int(self.gets.get('tab',0))
        self.D['active_tab'] = ['','','','']

        bid = self.D['bid']
        self.D['bconfig'] = self.DB.exe(f"SELECT * FROM h_board_config WHERE bid ='{bid}'",assoc=True,many=1)
        self.D['section_list'] = self.DB.exe("SELECT section FROM h_board_config GROUP BY section ORDER BY sposition")
        
        main_skin = self.D['bconfig']['skin']
        self.D['skin_list']  = hf.get_dirs(self.skin_dir,'board')
        self.D['sub_list']   = hf.get_files(self.skin_dir,'board',main_skin,'list',ext='html')
        self.D['sub_body']  = hf.get_files(self.skin_dir,'board',main_skin,'body',ext='html')
        self.D['sub_write'] = hf.get_files(self.skin_dir,'board',main_skin,'write',ext='html')

        self.D['active_tab'][tab] = 'active'
        # exConf = [title/type/align/color/format/width/must]
        self.D['extitle']  = {}
        self.D['extype']   = {}
        self.D['exalign']  = {}
        self.D['excolor']  = {}
        self.D['excolor_style']  = {}
        self.D['exformat'] = {}
        self.D['exwidth']  = {}
        self.D['exmust']   = {}
        self.D['use_key']  = []
        self.D['not_key']  = []

        for i in range(21) :
            add_index = 'add' + str(i)
            if self.D['bconfig'][add_index] :
                exConf = self.D['bconfig'][add_index].split('/')
                self.D['extitle'][add_index] = exConf[0]
                self.D['extype'][add_index]  = exConf[1]
                self.D['exalign'][add_index] = exConf[2]
                self.D['excolor'][add_index] = exConf[3]
                if exConf[3] :
                    self.D['excolor_style'][add_index] =  "style='background-color:" + exConf[3] + ";text-align:center; width:85px'"
                else :
                    self.D['excolor_style'][add_index] =  "style='text-align:center; width:85px'"
                self.D['exformat'][add_index]= exConf[4]
                self.D['exwidth'][add_index] = exConf[5]
                self.D['exmust'][add_index]  = exConf[6]
                self.D['use_key'].append(add_index)
            else :
                self.D['not_key'].append(add_index)
        


    def board_add(self) :
        SAVE = self.D['post']
  
        # 무결성 확인
        tbl = 'h_board_config'
        bid = SAVE['bid']
        if self.DB.cnt(f"SELECT bid FROM {tbl} WHERE bid='{bid}'") : return "보드 아이디가 중복됩니다."

        self.DB.insert_from_post(tbl) 

        if SAVE['type'] in ("yhboard","yhtable","yhalbum","yhdocu") :
            sql =  f"CREATE TABLE h_{bid}_board (" 
            sql+=   "no         INTEGER PRIMARY KEY AUTOINCREMENT, "
            sql+=   "brother    INTEGER NOT NULL default 0, "
            sql+=   "add0       TEXT NOT NULL default 'NO TITLE', "
            sql+=   "tle_color  TEXT NOT NULL default '', "
            sql+=   "uid        TEXT NOT NULL default '', "
            sql+=   "uname      TEXT NOT NULL default '', "
            sql+=   "content    TEXT NOT NULL default '', "
            sql+=   "reply      INTEGER NOT NULL default 0, "
            sql+=   "hit        INTEGER NOT NULL default 0, "
            sql+=   "wdate      INTEGER NOT NULL default 0, "
            sql+=   "mdate      INTEGER NOT NULL default 0, "
            sql+=   "add1       TEXT,add2 TEXT, add3 TEXT, add4 TEXT, add5 TEXT, add6 TEXT, add7 TEXT, add8 TEXT, add9 TEXT, add10 TEXT, "
            sql+=   "add11 TEXT, add12 TEXT, add13 TEXT, add14 TEXT, add15 TEXT, add16 TEXT, add17 TEXT, add18 TEXT, add19 TEXT, add20 TEXT )"
            self.DB.exe(sql)

        if SAVE['type'] in ("yhboard","yhalbum") :
            sql =  f"CREATE TABLE h_{bid}_reply (" \
                    "no         INTEGER PRIMARY KEY AUTOINCREMENT, "\
                    "uid        TEXT NOT NULL default '', "\
                    "uname      TEXT NOT NULL default '', "\
                    "content    TEXT NOT NULL default '', "\
                    "parent     INTEGER NOT NULL default 0, "\
                    "wdate      INTEGET NOT NULL default 0 )"
            self.DB.exe(sql)





            


        
