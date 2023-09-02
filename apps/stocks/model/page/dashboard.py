from system.core.load import Model
import system.core.my_utils as my

class M_dashboard(Model) :

    def view(self) :
    
        self.D['오늘날자']  = my.timestamp_to_date(opt=7) 
        self.D['오늘요일']  = my.dayofdate(self.D['오늘날자'])

        self.DB.tbl = 'h_INVEST_board'
        ckdate = self.DB.get_one("max(add0)")
        self.DB.wre = f"add0='{ckdate}'"

        self.DB.tbl = 'h_I230831_board'
        out1 = self.DB.get_line('sub2,sub19,sub3,sub20,add10,add17,sub25')

        매수수량1 = int(out1['sub2'])
        매수가격1 = float(out1['sub19']) 
        매수가액1 = 매수수량1 * 매수가격1

        self.D['매수수량1'] = f"{매수수량1:3d}"
        self.D['매수가격1'] = f"${매수가격1:,.2f}"
        self.D['매수가액1'] = f"${매수가액1:,.2f}"
        self.D['자산분배1'] = out1['add10']
        self.D['자산총액1'] = float(out1['add17']) 

        매도수량1 = int(out1['sub3'])
        매도가격1 = float(out1['sub20']) 
        매도가액1 = 매도수량1 * 매도가격1

        self.D['매도수량1'] = f"{매도수량1:>3d}"
        self.D['매도가격1'] = f"${매도가격1:,.2f}"
        self.D['매도가액1'] = f"${매도가액1:,.2f}"
        self.D['증가비율1'] = float(out1['add17'])/float(out1['sub25']) * 100
        
        self.DB.tbl = 'h_C230831_board'
        out2 = self.DB.get_line('sub2,sub19,sub3,sub20,add10,add17,sub25')

        매수수량2 = int(out2['sub2'])
        매수가격2 = float(out2['sub19']) 
        매수가액2 = 매수수량2 * 매수가격2

        self.D['매수수량2'] = f"{매수수량2:3d}"
        self.D['매수가격2'] = f"${매수가격2:,.2f}"
        self.D['매수가액2'] = f"${매수가액2:,.2f}"
        self.D['자산분배2'] = out2['add10']
        self.D['자산총액2'] = float(out2['add17'])

        매도수량2 = int(out2['sub3'])
        매도가격2 = float(out2['sub20']) 
        매도가액2 = 매도수량2 * 매도가격2

        self.D['매도수량2'] = f"{매도수량2:>3d}"
        self.D['매도가격2'] = f"${매도가격2:,.2f}"
        self.D['매도가액2'] = f"${매도가액2:,.2f}"
        self.D['증가비율2'] = float(out2['add17'])/float(out2['sub25']) * 100
 






 