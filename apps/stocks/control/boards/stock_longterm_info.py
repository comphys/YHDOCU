from system.core.load import Control

class Stock_longterm_info(Control) : 
    
    def _auto(self) :
        self.DB = self.db('stocks')

    def get_subinfo(self) :
        opt = self.gets['opt']
        self.tbl = self.gets['tbl']

        if    opt == '입금내역' : qry_opt = 'add1'
        elif  opt == '출금내역' : qry_opt = 'add2'
        elif  opt == '배당내역' : qry_opt = 'sub10'
        elif  opt == '매수금1'  : qry_opt = 'add5'
        elif  opt == '매도금1'  : qry_opt = 'add6'
        elif  opt == '매수금2'  : qry_opt = 'add11'
        elif  opt == '매도금2'  : qry_opt = 'add12'


        self.DB.tbl, self.DB.wre, self.DB.odr = (self.tbl, f"{qry_opt} != '0'", "add0 DESC")
        D = self.DB.get(f"add0,{qry_opt}",assoc=False)
        output  = "<div style='width:200px;max-height:250px;background-color:black;overflow-x:hidden' ondblclick=\"h_dialog.close('POP_INFO')\">"
        if D :
            output += "<table class='table table-bordered table-striped;' style='background-color:#0A2229;color:#e1e1e1;'>"
            for d in D :
                output += f"<tr><td>{d[0]}</td><td style='text-align:right'>{float(d[1]):,.2f}</td></tr>"
            output += "</table></div>"
        else : 
            output += "<div style='background-color:#0A2229;color:#e1e1e1;'>No data</div></div>"
        return self.echo(output)
