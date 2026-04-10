import sqlite3,platform 

class SQLITE :

    def __init__(self,SYS) :

        self.SYS  = SYS
        self.info = SYS.info
        self.system = platform.system()

        self.rst = ''

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

    # 하나의 값만을 반환한다. 없을 경우 None 값을 반환
    def one(self,qry) : 
        self.rst = self.cur.execute(qry)
        if  rst_one := self.rst.fetchone() : return rst_one[0] 
        return None
    
    # 특정 필드값 전부를 list 로 반환한다, 없을 경우 None 값을 반환
    def col(self,qry) :
        self.rst = self.cur.execute(qry)
        if  rst_col :=  self.rst.fetchall() : 
            cols = [x[0] for x in rst_col]
            return cols 
        else : return None

    def line_dict(self,qry) :
        return self.exe(qry,many=1,assoc=True)
    
    def line_list(self,qry) :
        return self.exe(qry,many=1,assoc=False)
    
    def last_line_dict(self,tbl) :
        qry = f"SELECT * FROM {tbl} order by rowid desc LIMIT 1"
        return self.exe(qry,many=1,assoc=True)
    
    def last_line_list(self,tbl) :
        qry = f"SELECT * FROM {tbl} order by rowid desc LIMIT 1"
        return self.exe(qry,many=1,assoc=False)
    
    def last_one(self,sel,tbl) :
        qry = f"SELECT {sel} FROM {tbl} order by rowid desc LIMIT 1"
        return self.one(qry)

    def fetch_assoc(self, many=0) :
        if not self.rst : return None
        rst = self.rst.fetchall() if not many else  self.rst.fetchmany(many)
        temp_list = []
        col = [x[0] for x in self.rst.description]
        for row in rst : temp_list.append(dict(zip(col,row)))
        return temp_list[0] if many == 1 else temp_list      

    def fetch(self, many=0) :
        if not self.rst : return None
        if    many == 0 : return self.rst.fetchall()
        elif  many == 1 : return self.rst.fetchmany(1)[0]
        else  : return self.rst.fetchmany(many)

# sql query 실행 

    def exe(self,qry:str,many:int=0,assoc:bool=False) -> any :
        qry = qry.strip()
        try : 
            self.rst = self.cur.execute(qry)
        except sqlite3.Error as err :
            return None

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


# string convert for DB

    def qry_insert(self,tbl,P:dict) :
        keys = self.qry_str_key(P)
        vals = self.qry_str_val(P)
        qry  = f"INSERT INTO {tbl} ({keys}) VALUES ({vals})"
        return qry

    def qry_str_key(self,S) : 
        if type(S) is dict : S = list(S.keys()) 
        if type(S) is list : return ','.join(S)
        if type(S) is str  : return S
        else : return False

    def qry_str_val(self,S) :
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

# parameters

    def cast_key(self,int_keys,float_keys,keys) :
        sel = ''
        if  int_keys : 
            for x in int_keys :   sel += f"CAST({x} as INT) as {x}," 
        if  float_keys : 
            for x in float_keys : sel += f"CAST({x} as FLOAT) as {x}," 
        if  keys : 
            for x in keys : sel += f"{x},"
        return sel.rstrip(',') 

       
    def parameter(self,key) :
        parm = self.exe(f"SELECT val,type FROM parameters WHERE key='{key}'",many=1,assoc=False)
        if    parm[1] == 'float' : return float(parm[0])
        elif  parm[1] == 'int'   : return int(parm[0])
        else  : return parm[0]
    
    def parameter_update(self,key,val) :
        qry = f"UPDATE parameters SET val='{val}' WHERE key='{key}'"
        self.exe(qry)        
    
    def parameter_des(self,key) :
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


# DB table 조작 관련

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
    
    def table_list(self) :
        self.rst = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tmp = self.fetch()
        return [ t[0] for t in tmp]

    def table_delete_from_no(self,tbl,no) : 
        sql = f"DELETE FROM {tbl} WHERE no = {no}"
        self.cur.execute(sql) ; self.con.commit()  
    
