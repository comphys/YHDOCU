import sqlite3 

class DB :
    def __init__(self,SYS) :
        self.info = SYS.info
        self.SYS = SYS

        self.wre = ''
        self.odr = ''
        self.lmt = ''
        self.qry = ''
        self.num = 0
        self.tbl = ''
        self.err = ''

    def clear(self) :
        self.wre =  self.odr = self.lmt = self.qry = self.tbl = self.err = ''
        
    def con(self,dbname) :
        mydb = 'mydb/' + dbname + '.sqlite'
        self.con = sqlite3.connect(mydb, check_same_thread=True)
        self.cur = self.con.cursor() 

    def change_db(self,db) :
        self.close()
        mydb = 'mydb/' + db + '.sqlite'
        self.con = sqlite3.connect(mydb, check_same_thread=True)
        self.cur = self.con.cursor()        

    def close(self) :
        self.con.close()

    def cnt(self,qry) :
        self.rst = self.cur.execute(qry)
        return len(self.rst.fetchall())
    
    def one(self,qry) : 
        self.rst = self.cur.execute(qry)
        if  rst := self.rst.fetchone() : return rst[0] 
        return None

    def line(self,qry) :
        return self.exe(qry,many=1,assoc=True)

    def oneline(self,qry,assoc=False) :
        return self.exe(qry,many=1,assoc=assoc)

    def get_one(self,fld) :
        return self.get(fld,many=1,assoc=False)

    def get_line(self,fld) :
        return self.get(fld,many=1,assoc=True)    
    
    def get(self,fld,many=0,assoc=True) :
        if not self.tbl : 
            self.err = "No table name is specified"
            return False
        if fld == '' : 
            self.err = "No fields are specified"
            return False

        fld = ','.join(fld) if type(fld) is list else fld

        wre = "WHERE "      + self.wre if self.wre else ''
        odr = "ORDER BY "   + self.odr if self.odr else ''
        lmt = "LIMIT "      + self.lmt if self.lmt else ''
        qry = f"SELECT {fld} FROM {self.tbl} {wre} {odr} {lmt}"
        self.qry = qry.strip()

        try : 
            self.rst = self.cur.execute(qry)
        except sqlite3.OperationalError :
            self.err = "SQLITE3 OPERATIONAL ERROR"
            return False

        rst = self.rst.fetchall() if not many else  self.rst.fetchmany(many)
        self.num = len(rst)
        if self.num == 0 : return None 
        if assoc : 
            temp_list = []
            col = [x[0] for x in self.rst.description]
            for row in rst : temp_list.append(dict(zip(col,row)))
            # many = 1 일 경우 결과값을 dict로 전달하기 위해 temp_list[0]을 리턴 
            return temp_list[0] if many == 1 else temp_list  

        else :
            if fld.find(',') == -1 : # 필드가 하나일 경우 
                rst = [x[0] for x in rst]
            return rst[0] if many == 1 else rst


    def fetch_assoc(self, many=0) :
        if not self.rst : return ''
        rst = self.rst.fetchall() if not many else  self.rst.fetchmany(many)
        temp_list = []
        col = [x[0] for x in self.rst.description]
        for row in rst : temp_list.append(dict(zip(col,row)))
        return temp_list[0] if many == 1 else temp_list      

    def fetch(self, many=0) :
        if not self.rst : return ''
        if    many == 0 : return self.rst.fetchall()
        elif  many == 1 : return self.rst.fetchmany(1)[0]
        else  : return self.rst.fetchmany(many)

# sql query 실행 

    def exe(self,qry:str,many:int=0,assoc:bool=False) -> any :
        qry = qry.strip()
        try : 
            self.rst = self.cur.execute(qry)
        except sqlite3.Error as err :
            return err

        if qry.upper().startswith(('SELECT','PRAGMA')) : 
            return self.fetch(many) if not assoc else self.fetch_assoc(many)
        else :
            self.con.commit()
            return "The job you requested is done"
       
    def commit_many(self,qry) : 
        qry2 = qry.split(';')
        for x in qry2 :
            try : self.cur.execute(x) 
            except sqlite3.OperationalError : return "SQLITE3 OPERATIONAL ERROR"
        
        self.con.commit()
        return "The job you requested is done"


# 테이블 리스트 및 생성

    def table_list(self) :
        self.rst = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tmp = self.fetch()
        return [ t[0] for t in tmp]

    def table_delete_from_no(self,tbl,no) : 
        sql = f"DELETE FROM {tbl} WHERE no = {no}"
        self.cur.execute(sql) ; self.con.commit()       

# string convert for DB
    def qry_select(self,sel,tbl,wre=None) :
        qry = f"SELECT {sel} FROM {tbl}"
        if wre : 
            qry += " WHERE "
            if type(wre) is str : qry += wre
            elif type(wre) is dict : qry += ' and '.join(["{}='{}'".format(k,v) for k,v in wre.items()])
        return qry 


    def qry_insert(self,tbl,P:dict) :
        keys = self.qry_str_key(P)
        vals = self.qry_str_val(P)
        qry  = f"INSERT INTO {tbl} ({keys}) VALUES ({vals})"
        return qry

    def qry_str_key(self,S:dict) : 
        if type(S) is dict : S = list(S.keys()) 
        if type(S) is list : return ','.join(S)
        if type(S) is str  : return S
        else : return False

    def qry_str_val(self,S:dict) :
        if type(S) is dict : S = list(S.values()) 
        if type(S) is list : return f"{S}"[1:-1]
        if type(S) is str  : return S
        else : return False

    def qry_update(self,tbl:str,S:dict,con=None) :
        tmp = ''
        for key, val in S.items() :
            if val == 'None':  tmp += f"{key}= null,"
            else            :  tmp += f"{key}='{val}',"
        tmp = tmp[:-1] + " "  
        wre = ' WHERE ' + con if con else ''  
        qry = f"UPDATE {tbl} SET {tmp} {wre}"
        return qry 

    def insert_from_post(self,tbl,S=None) :
        P    = S if S else self.SYS.D['post'] 
        qry  = self.qry_insert(tbl,P)
        self.exe(qry)

    def cast_key(self,int_keys,float_keys,keys) :
        sel = ''
        if  int_keys : 
            for x in int_keys :   sel += f"CAST({x} as INT) as {x}," 
        if  float_keys : 
            for x in float_keys : sel += f"CAST({x} as FLOAT) as {x}," 
        if  keys : 
            for x in keys : sel += f"{x},"
        return sel.rstrip(',') 

    # json 형태처럼 key 값과 value 값으로 데이터를 저장 및 불러오기
    def store(self,key,val=None) :
        if  val :
            qry = f"INSERT INTO STORAGE (key,val) values ('{key}','{val}')"
            self.exe(qry)
        else :
            qry = f"SELECT val FROM STORAGE WHERE key='{key}'"
            rst = self.cur.execute(qry)
            return rst.fetchone()[0]
        
    def store_update(self,key,val) :
        qry = f"UPDATE STORAGE SET val='{val}' WHERE key='{key}'"
        self.exe(qry)
    
    def store_delete(self,key) :
        qry = f"DELETE FROM STORAGE WHERE key='{key}'"
        self.exe(qry)
        
    def parameters(self,key) :
        parm = self.exe(f"SELECT val,type FROM parameters WHERE key='{key}'",many=1,assoc=False)
        if    parm[1] == 'float' : return float(parm[0])
        elif  parm[1] == 'int'   : return int(parm[0])
        else  : return parm[0]
    
    def parameters_des(self,key) :
        parm = self.one(f"SELECT description FROM parameters WHERE key='{key}' LIMIT 1")
        return parm

    def parameters_dict(self,cat=None) :
        con = f"WHERE cat ='{cat}'" if cat else ''
        parm = self.exe(f"SELECT key,val,type FROM parameters {con}",assoc=False)   
        if not parm : return None
        
        D = {}
        for k,v,t in parm :
            if   t == 'float' : D[k] = float(v)
            elif t == 'int'   : D[k] = int(v)
            else : D[k] = v
            
        return D
        
    def table_info(self,tbl,info='col') :
        # [cid / Integer / Column index ], [name / Text / Column name] , [type/Text/Colunm type, as given]
        # [notnull/Integer/Has a Not NULL], [dflt_value/Text/Default value], [pk/Integer/Is part of the PK]
        temp = self.exe(f"pragma table_info({tbl})")
        cid    = [x[0] for x in temp]
        col    = [x[1] for x in temp]
        typ    = [x[2] for x in temp]
        nnl    = [x[3] for x in temp]
        dft    = [x[4] for x in temp]
        pky    = [x[5] for x in temp]

        if   info == 'col'      : return col
        elif info == 'typ'      : return typ
        elif info == 'col:typ'  : return dict(zip(col,typ)) 
        elif info == 'all'      : return list(zip(cid,col,typ,nnl,dft,pky))
        
    def table_cols(self,tbl,omit=None) :
        cols = self.table_info(tbl,'col')
        if omit : cols = [x for x in cols if x not in omit]
        return cols
    
