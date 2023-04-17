from system.core.load import Control

class Stock_longterm_info(Control) : 
    
    def _auto(self) :
        self.DB = self.db('stocks')
        self.tbl = self.gets['tbl']
    
    def get_exinfo(self) :
        ckday = self.gets['ckday']
        self.DB.tbl, self.DB.wre = (self.tbl,f"add0='{ckday}'")
        res = self.DB.get_line('add18,sub16,sub17')
        현매수금 = float(res['sub17'])
        평균단가 = float(res['sub16'])
        현재손익 = float(res['add18'])
        output  = "<div style='text-align:center;font-weight:bold;color:#F7F8E0;background-color:black;padding:10px' ondblclick=\"h_dialog.close('POP_INFO')\">"
        output += f"<div>총매수금 : {현매수금:,.2f} &nbsp; 평균단가 : {평균단가:,.2f} &nbsp; 수익현황 : {현재손익:,.2f}%</div>"
        output += "</div>"
        return self.echo(output)
        

    def get_subinfo(self) :
        opt = self.gets['opt']

        if    opt == '입금내역' : qry = f"SELECT add0,add1 FROM {self.tbl} WHERE add1 != '0' ORDER BY add0 DESC"
        elif  opt == '출금내역' : qry = f"SELECT add0,add2 FROM {self.tbl} WHERE add2 != '0' ORDER BY add0 DESC"
        elif  opt == '배당내역' : qry = f"SELECT add0,sub10 FROM {self.tbl} WHERE sub10 != '0' ORDER BY add0 DESC" 
        elif  opt == '매수금1'  : qry = f"SELECT add0,add5,sub8,add7,add8 FROM {self.tbl} WHERE add5 != '0' ORDER BY add0 DESC"
        elif  opt == '매도금1'  : qry = f"SELECT add0,add6,sub8,add7,add8 FROM {self.tbl} WHERE add6 != '0' ORDER BY add0 DESC"
        elif  opt == '매수금2'  : qry = f"SELECT add0,add11,sub9,add13,add14 FROM {self.tbl} WHERE add11 != '0' ORDER BY add0 DESC"
        elif  opt == '매도금2'  : qry = f"SELECT add0,add12,sub9,add13,add14 FROM {self.tbl} WHERE add12 != '0' ORDER BY add0 DESC"
        elif  opt == '종가1'    : 
            Vm = self.DB.exe(f"SELECT min(CAST(add8 as FLOAT)), max(CAST(add8 as FLOAT)) FROM {self.tbl} WHERE add8 != '0'")[0]
            v1,v2 = Vm
            qry = f"SELECT add0,add8  FROM {self.tbl} WHERE CAST(add8 as FLOAT) = '{v1}' OR CAST(add8 as FLOAT) = '{v2}' ORDER BY add0 ASC"
        elif  opt == '종가2'    : qry = f"SELECT add0,add14 FROM {self.tbl} WHERE add14= (SELECT min(CAST(add14 as FLOAT)) FROM {self.tbl}) OR add14 = (SELECT max(CAST(add14 as FLOAT)) FROM {self.tbl}) ORDER BY add0 ASC"

        D = self.DB.exe(qry,assoc=False)

        if D and opt in ('입금내역','출금내역','배당내역'):
            output  = "<div style='width:230px;max-height:250px;background-color:black;overflow-x:hidden' ondblclick=\"h_dialog.close('POP_INFO')\">"
            output += "<table class='table table-bordered table-striped;' style='background-color:#0A2229;color:#e1e1e1;'>"
            output += f"<tr style='background-color:#0B2F3A'><td>일자</td><td style='text-align:right'>금액</td></tr>"
            for d in D :
                output += f"<tr><td>{d[0]}</td><td style='text-align:right'>{float(d[1]):,.2f}</td></tr>"
            output += "</table></div>"

        elif D and opt in ('매수금1','매도금1','매수금2','매도금2'):
            output  = "<div style='width:350px;max-height:250px;background-color:black;overflow-x:hidden' ondblclick=\"h_dialog.close('POP_INFO')\">"
            output += "<table class='table table-bordered table-striped;' style='background-color:#0A2229;color:#e1e1e1;'>"
            output += f"<tr style='background-color:#0B2F3A'><td>일자</td><td style='text-align:right'>금액</td><td style='text-align:right'>수량</td><td style='text-align:right'>누적</td><td style='text-align:right'>종가</td></tr>"
            for d in D :
                output += f"<tr><td>{d[0]}</td><td style='text-align:right'>{float(d[1]):,.2f}</td><td style='text-align:right'>{int(d[2])}</td><td style='text-align:right'>{int(d[3])}</td><td style='text-align:right'>{float(d[4]):,.2f}</td></tr>"
            output += "</table></div>"

        elif D and opt in ('종가1','종가2'):
            output  = "<div style='width:230px;max-height:250px;background-color:black;overflow-x:hidden' ondblclick=\"h_dialog.close('POP_INFO')\">"
            output += "<table class='table table-bordered table-striped;' style='background-color:#0A2229;color:#e1e1e1;'>"
            output += f"<tr style='background-color:#0B2F3A'><td>일자</td><td style='text-align:right'>종가</td></tr>"
            for d in D :
                output += f"<tr><td>{d[0]}</td><td style='text-align:right'>{float(d[1]):,.2f}</td></tr>"
            output += "</table></div>"

        else : 
            output  = "<div style='width:230px;background-color:black;' ondblclick=\"h_dialog.close('POP_INFO')\">"
            output += "<div style='width:100%;background-color:#0A2229;color:#e1e1e1;'>&nbsp; No data</div></div>"

        return self.echo(output)
