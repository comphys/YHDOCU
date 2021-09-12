from system.core.load import Model
from system.core.my_utils import dequote
import copy

class M_dbadmin(Model) :

    def get_tables(self) :
        tbls = self.DB.table_list()
        if tbls : tbls.remove('sqlite_sequence')
        return tbls  

    def get_tbl_rows_str(self,tbl) :
        '''
        테이블 구조를 검사하여 구조에 맞게 가이드 입력양식을 작성하는 함수
        '''
        RS = []
        rs = []
        TS = self.DB.table_info(tbl,info='all')
        col,typ,nnl,dft,pky,unq,idx = (1,2,3,4,5,6,7)

        for tt in TS :
            placeholder = ''
            readonly = 'readonly' if tt[pky] == 1 else '' 
            rs.append("<span class='text-warning'>"+tt[col]+"</span>")
            rs.append(tt[typ])
        #   rs.append(tt[nnl])
            default = '' if tt[dft] == None else dequote(tt[dft])
            txt_color = 'text-white' if tt[dft] == None else 'text-info'
            bg_color = 'bg-dark'
            if tt[pky] == 1 : placeholder = 'auto increment value'
            if tt[unq] == 1 : bg_color = 'bg-danger'    ; placeholder = 'unique index required'
            if tt[nnl] == 1 : bg_color = 'bg-primary' ; placeholder = 'no null value'
            if tt[idx] == 1 : bg_color = 'bg-secondary' ; placeholder = 'index key'
            rs.append("<input type='text' class='form-control {} w-100 {}' name='{}' value='{}' placeholder='{}' {}>"\
                .format(bg_color,txt_color,tt[col],default,placeholder,readonly) )
            
            RS.append(copy.deepcopy(rs))
            rs.clear()
  
        return RS    