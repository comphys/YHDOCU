from system.core.load import Control
import system.core.my_utils as my
import subprocess

class Vrts_guide(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')
        self.bid   = self.parm[0]
    
    
# -----------------------------------------------------------------------------------------------------------------------
# Basic qty : Recalculate the basic quantity
# -----------------------------------------------------------------------------------------------------------------------
    def basic_qty(self) :
        self.Q = {}
        theDay  = self.D['post']['theDay']
        Balance = my.sv(self.D['post']['Balance']) 

        일매수금 = int(int(Balance*2/3)/22)
        bprice = self.DB.one(f"SELECT add14 FROM {self.guide} WHERE sub12='0' and add0 <= '{theDay}' ORDER BY add0 DESC LIMIT 1")
        기초수량 = my.ceil(일매수금/float(bprice))        

        self.Q['sub4'] = 일매수금
        self.Q['sub18'] = 기초수량
        self.Q['add17'] = f"{Balance:,.2f}"
        
        return self.json(self.Q)
# -----------------------------------------------------------------------------------------------------------------------
# OneWrite TACTIC
# -----------------------------------------------------------------------------------------------------------------------

    def oneWrite(self) :
        
        key = self.parm[1]
        self.D['prev_date'] = self.DB.one(f"SELECT max(add0) FROM h_{self.bid}_board")
        
        if not self.D['prev_date'] :
            self.set_message("초기 데이타가 존재하지 않습니다")
            return self.moveto(f"board/list/{self.bid}")
            
        self.D['today'] = self.DB.one(f"SELECT min(add0) FROM h_stockHistory_board WHERE add0 > '{self.D['prev_date']}'")
            
        if self.D['today'] :
            subprocess.call(f"python.exe apps/stocks/xtask/update_{key}.py",shell=False)
            self.set_message(f"{self.D['today']}일 자료를 업데이트 하였습니다")
            return self.moveto(f"board/list/{self.bid}")

        else :
            self.set_message("업데이트가 완료된 상태입니다")
            return self.moveto(f"board/list/{self.bid}")
        
