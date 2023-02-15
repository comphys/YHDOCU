from system.core.load import Model
import system.core.my_utils as my

class M_dashboard(Model) :

    def view(self) :
    
        self.D['오늘날자']  = my.timestamp_to_date(opt=7) 
        self.D['오늘요일']  = my.dayofdate(self.D['오늘날자'])

        self.DB.tbl = 'h_VICTORY_board'
        ckdate = self.DB.get_one("max(add0)")
        self.DB.wre = f"add0='{ckdate}'"

        out = self.DB.get_line("sub2,sub19,sub3,sub20")
        매수수량 = int(out['sub2'])
        매수가격 = float(out['sub19']) 
        매수가액 = 매수수량 * 매수가격

        self.D['매수수량'] = f"{매수수량:3d}"
        self.D['매수가격'] = f"${매수가격:,.2f}"
        self.D['매수가액'] = f"${매수가액:,.2f}"

        매도수량 = int(out['sub3'])
        매도가격 = float(out['sub20']) 
        매도가액 = 매도수량 * 매도가격

        self.D['매도수량'] = f"{매도수량:>3d}"
        self.D['매도가격'] = f"${매도가격:,.2f}"
        self.D['매도가액'] = f"${매도가액:,.2f}"


 