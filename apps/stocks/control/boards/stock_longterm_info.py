from system.core.load import Control

class Stock_longterm_info(Control) : 
    
    def _auto(self) :
        self.DB = self.db('stocks')

    def get_subinfo(self) :
        opt = self.gets['opt']
        self.tbl = self.gets['tbl']

        if    opt == '입금내역' : qry_opt = 'add1' ; qry_wre = 'add1'
        elif  opt == '출금내역' : qry_opt = 'add2' ; qry_wre = 'add2'
        elif  opt == '배당내역' : qry_opt = 'sub10'; qry_wre = 'sub10'
        elif  opt == '매수금1'  : qry_opt = 'add5,sub8,add7,add8' ; qry_wre = 'add5'
        elif  opt == '매도금1'  : qry_opt = 'add6,sub8,add7,add8' ; qry_wre = 'add6'
        elif  opt == '매수금2'  : qry_opt = 'add11,sub9,add13,add14' ; qry_wre = 'add11'
        elif  opt == '매도금2'  : qry_opt = 'add12,sub9,add13,add14' ; qry_wre = 'add12'


        self.DB.tbl, self.DB.wre, self.DB.odr = (self.tbl, f"{qry_wre} != '0'", "add0 DESC")
        D = self.DB.get(f"add0,{qry_opt}",assoc=False)
        # self.info(self.DB.qry)

        if D and opt in ('입금내역','출금내역','배당내역'):
            output  = "<div style='width:200px;max-height:250px;background-color:black;overflow-x:hidden' ondblclick=\"h_dialog.close('POP_INFO')\">"
            output += "<table class='table table-bordered table-striped;' style='background-color:#0A2229;color:#e1e1e1;'>"
            output += f"<tr style='background-color:#0B2F3A'><td>일자</td><td style='text-align:right'>금액</td></tr>"
            for d in D :
                output += f"<tr><td>{d[0]}</td><td style='text-align:right'>{float(d[1]):,.2f}</td></tr>"
            output += "</table></div>"

        elif D and opt in ('매수금1','매도금1','매수금2','매도금2'):
            output  = "<div style='width:330px;max-height:250px;background-color:black;overflow-x:hidden' ondblclick=\"h_dialog.close('POP_INFO')\">"
            output += "<table class='table table-bordered table-striped;' style='background-color:#0A2229;color:#e1e1e1;'>"
            output += f"<tr style='background-color:#0B2F3A'><td>일자</td><td style='text-align:right'>금액</td><td style='text-align:right'>수량</td><td style='text-align:right'>누적</td><td style='text-align:right'>종가</td></tr>"
            for d in D :
                output += f"<tr><td>{d[0]}</td><td style='text-align:right'>{float(d[1]):,.2f}</td><td style='text-align:right'>{int(d[2])}</td><td style='text-align:right'>{int(d[3])}</td><td style='text-align:right'>{float(d[4]):,.2f}</td></tr>"
            output += "</table></div>"

        else : 
            output  = "<div style='width:330px;max-height:250px;background-color:black;overflow-x:hidden' ondblclick=\"h_dialog.close('POP_INFO')\">"
            output += "<div style='background-color:#0A2229;color:#e1e1e1;'>No data</div></div>"

        return self.echo(output)
