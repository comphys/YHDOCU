from system.lib.db import DB
import re

class APPDB(DB) :

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
        unq    = [  0  for x in temp]
        idx    = [  0  for x in temp]

        sql = "SELECT sql FROM sqlite_master WHERE type='index' and tbl_name='" + tbl + "'"
        rst = self.exe(sql) 

        ux=[]
        ix=[]

        for val in rst :
            ss = val[0]
            nme = ss[ss.find("(")+1:ss.find(")")]
            if   ss.find('CREATE UNIQUE') != -1 : ux.append(nme)
            else : ix.append(nme)

        for x in ux :
            unq[col.index(x)] = 1
        for x in ix :
            idx[col.index(x)] = 1

        if   info == 'col'      : return col
        elif info == 'typ'      : return typ
        elif info == 'col:typ'  : return dict(zip(col,typ)) 
        elif info == 'unq'      : return unq
        elif info == 'idx'      : return idx
        elif info == 'all'      : return list(zip(cid,col,typ,nnl,dft,pky,unq,idx))
        elif info == 'validate' : return list(zip(col,typ,nnl,pky,unq))
        elif info == 'copy'     : return list(zip(col,typ,nnl,dft,unq,idx))


    def validate_update(self,tbl,key,val) :
        '''
        업데이트를 위한  테이블 구조에 맞는지 검사한 결과 리턴  
        '''
        pp    = self.table_info(tbl,info='col')
        xx    = pp.index(key)
        paper = self.table_info(tbl,info='validate')[xx]

        typ,nnl,unq = (1,2,4)
        vi = re.compile('^[-+]?[0-9]+$')
        vf = re.compile(r'^[-+]?\d*(\.?\d*)$')

        if paper[nnl] == 0 and val == 'None' : return {'err':'error','msg':'입력값이 없습니다'}
        if paper[nnl] == 1 and (val == 'None' or val == 'null') : return {'err':'error','msg':'null 값은 허용되지 않습니다.'}
        if paper[typ] == 'INTEGER' and val !='null' and not vi.match(val) : return {'err':'error','msg':'정수값 형식이 아닙니다.'}
        if paper[typ] == 'REAL'    and val !='null' and not vf.match(val) : return {'err':'error','msg':'실수값 형식이 아닙니다.'}

        if paper[unq] == 1 : 
            qry = f"SELECT {key} FROM {tbl} WHERE {key}='{val}'"
            cnt = self.cnt(qry)
            if cnt != 0 : return {'err':'error', 'msg' : '유일성 조건 위반입니다.'}    

        return {'err':'success','msg':'업데이트 값이 타당합니다.'}     


    def validate_insert(self,S=None) :
        '''
        입력된 데이타가 테이블 구조에 맞는지 검사한다. 
        '''
        tbl = self.SYS.parm[0]
        P   = S if S else self.SYS.D['post'] 

        paper = self.table_info(tbl,info='validate') #list[col,typ,nnl,pky,unq]
        col, typ, nnl, pky, unq = (0,1,2,3,4)
        err = []

        vi = re.compile('^[-+]?[0-9]+$')
        vf = re.compile(r'^[-+]?\d*(\.?\d*)$')

        for pp in paper :
            name = pp[col]
            if P[name] == 'null' or P[name] == 'None' : P[name] = ''
            if pp[pky] == 1 : P.pop(name) ; continue # primary Key 는 배제 
            if pp[nnl] == 0 and P[name] =='' : P.pop(name) ; continue # null값 입력은 자동입력으로 배제
            if pp[nnl] == 1 and P[name] =='' : err.append(f'[{name}] 키는 필수 입력 필드입니다.') ; continue
            if pp[typ] == 'INTEGER' : 
                if vi.match(P[name]) : P[name] = int(P[name])
                else : err.append(f'[{name}] 키의 값이 정수형이 아닙니다.') ; continue

            if pp[typ] == 'REAL' :
                if vf.match(P[name]) : P[name] = float(P[name])
                else : err.append(f'[{name}] 키의 값이 실수형이 아닙니다.') ; continue

            if pp[unq] == 1 : 
                qry = f"SELECT {name} FROM {tbl} WHERE {name}='{P[name]}'"
                cnt = self.cnt(qry)
                if cnt != 0 : err.append(f'유일성 조건인 [{name}]키의 값과 동일한 값이 존재합니다.') 

        if not P : err.append('입력할 값이 없습니다.')
        if err : RST = {'rst':'error','err':err}   
        else   : RST = {'rst':'success','err':None}
        return RST  