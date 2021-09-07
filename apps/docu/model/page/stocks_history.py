from system.core.load import Model

class M_stocks_history(Model) :

    def view(self) :

        DB = self.SYS.db('stocks')
        DB.tbl = 'stocks_history'
        DB.wre = "code = 'TQQQ'"
        
        S_DATA = DB.get('no,Date,Close,Open,High,Low,Volume,Change')
        

        self.D['message'] = f"현재 {DB.num}개의 데이타가 검색되었습니다."  
        self.D['S_DATA']  = S_DATA  
