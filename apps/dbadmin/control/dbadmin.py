from system.core.load import Control
from flask import session
import pprint, json
from system.hand import myfile

class Dbadmin(Control) :

    def _auto(self) :
        mydb = session.get('mydb','docu')
        if newdb := self.gets.get('mydb',None) : mydb = session['mydb'] = newdb

        self.DB  = self.load_app_lib('appdb')
        self.DB.con(mydb)
        
        self.D['db_list'] = myfile.get_files("mydb")
        self.D['db_list'] = [x.replace('.sqlite','') for x in self.D['db_list']]
        self.D['current_db'] = mydb

    def index(self) :
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        D = {'title':'DB ADMIN','skin':'dbadmin/main.html'}
        M1 = self.model('dbadmin')
        D['db_tables'] = M1.get_tables()

        return self.echo(D)

    def list(self) :
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        D = {'title':'DB ADMIN','skin':'dbadmin/list.html'}
        D['nowtbl']= self.parm[0]
       
        M1 = self.model('dbadmin_list')
        D['db_tables'] = M1.get_tables()
        D['tbl_col_names'] = M1.get_tbl_col_names(D['nowtbl'])
        if 'content' in D['tbl_col_names'] : D['content_index'] = D['tbl_col_names'].index('content')
        M1.get_tbl_rows(D['nowtbl'])
        return self.echo(D)

    def tbl_dbinput(self) :
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        D = {'title':'데이타 입력하기','skin':'dbadmin/tbl_dbinput.html'} 
        if self.D['post'] :
            Test = self.DB.validate_insert()
            if Test['rst'] == 'success' : 
                self.DB.insert_from_post(self.parm[0]) 

            return self.echo(json.dumps(Test)) 
            
        M1 = self.model('dbadmin')
        D['tbl_rows_str'] = M1.get_tbl_rows_str(self.parm[0])
        return self.echo(D)

    def tbl_delete_row(self) :
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        no  = self.D['post']['no']
        tbl = self.D['post']['tbl']
        self.DB.table_delete_from_no(tbl,no) 
        return self.echo(no)     

    def create_tbl(self) :
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        D = {'title':'새 테이블 만들기','skin':'dbadmin/tbl_create.html'}
        copy_tbl = self.D['post'].get('copy_tbl',None)
        if copy_tbl :
            D['tbl_structure'] = self.DB.table_info(copy_tbl,info='copy') ; del D['tbl_structure'][0] # 첫번째 요소인 no 삭제
            D['copy_tbl'] = copy_tbl
        M1 = self.model('dbadmin')
        D['db_tables'] = M1.get_tables()
        return self.echo(D)

    def qry_execute(self) :
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        D = {'title':'POST SENDING','skin':'dbadmin/qry_result.html'}
        if self.D['post'] == None : D['qry_rst'] = "데이타가 넘어오지 않았습니다."
        else : 
            opt = self.D['post']['opt']
            temp = self.DB.exe(self.D['post']['qry'],many=0,assoc=True) if opt =='1' else self.DB.exe(self.D['post']['qry'],many=0)
            D['qry_rst'] = pprint.pformat(temp,indent=2)  # width=200
        return self.echo(D)

    def qry_commit_many(self) :
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        D = {'title':'POST SENDING','skin':'dbadmin/qry_result.html'}
        if self.D['post'] == None : D['qry_rst'] = "데이타가 넘어오지 않았습니다."
        else : 
            self.DB.commit_many(self.D['post']['qry'])
        return self.echo(D)

    def tbl_structure(self) : 
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        D = {'title':'테이블 구조','skin':'dbadmin/tbl_structure.html'}
        D['tbl_structure'] = self.DB.table_info(self.parm[0],info='all') 
        return self.echo(D)

    def copy_dbtable(self) :
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        tbl1 = self.D['post']['tbl1'] 
        if not tbl1 : 
            return self.echo('테이블1 선택되어 있지 않음')
        tbl2 = self.D['post']['tbl2'] 
        if not tbl2 : 
            return self.echo('테이블2 선택되어 있지 않음')
        key1 = self.DB.table_info(tbl1,info='col') ; del key1[0]
        key2 = self.DB.table_info(tbl2,info='col') ; del key2[0]
        str1 = self.DB.qry_str_key(key1)
        str2 = self.DB.qry_str_key(key2)
        qry = f"INSERT INTO {tbl1} ({str1}) SELECT {str2} FROM {tbl2}"    
        return self.echo(qry)

    def tbl_live_edit(self) : 
        if not 'N_NO' in session : return self.moveto('docu/board/login',short=False)
        tbl = self.D['post']['tbl']
        key = self.D['post']['key']
        val = self.D['post']['val']
        no  = self.D['post']['no']
        RST = self.DB.validate_update(tbl,key,val)
        if RST['err'] == 'success' :
            if val == 'null': sql = f"UPDATE {tbl} SET {key}= null WHERE no={no}"
            else            : sql = f"UPDATE {tbl} SET {key}= '{val}' WHERE no={no}"
            self.DB.exe(sql)
            
        return self.echo(json.dumps(RST)) 
    