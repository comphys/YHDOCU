from system.core.load import Control

class Stock_today_tips(Control) : 
    
    def _auto(self) :
        self.DB = self.db('stocks')

    def hellow(self) :
        
        no = self.gets['no']

        self.DB.tbl,self.DB.wre = ('h_daily_trading_board',f"no={no}")
        D = self.DB.get_line("add0,add1,buy1,buy11,buy12,buy2,buy21,buy22,buy3,buy31,buy32,buy4,buy41,buy42,buy5,buy51,buy52,sell1,sell11,sell12,sell2,sell21,sell22,sell3,sell31,sell32,sell4,sell41,sell42")
        # 출력시작
        sty1 ="style='text-align:center;width:100px'"
        sty2 ="style='text-align:center;width:80px'"
        sty3 ="style='text-align:right;width:80px;padding-right:10px'"
        sty4 ="style='text-align:right;width:100px;padding-right:10px'"
        sty5 ="style='color:#CED8F6'"
        sty6 ="style='color:#F6CECE'"

        output  = "<div id='stock_tips' style='width:350px;height:250px;padding:10px;background-color:#1d1f24;color:#e1e1e1;border:1px solid #F7F8E0;' >"
        output += f"<div style='text-align:center;width:100%;padding:10px'><span style='color:#CEECF5'>{D['add0']}</span> <span style='color:#F7F8E0;font-weight:bold'>{D['add1']}</span> 매매전략</div>"
        output += "<table class='table table-bordered table-striped'>"
        output += "<thead><tr><th>구분</th><th>방법</th><th style='text-align:right;width:60px;padding-right:10px'>수량</th><th style='text-align:right;width:80px;padding-right:10px'>단가</th></tr></thead>"
        output += "<tbody>"
        if int(D['buy11']) :  output += f"<tr {sty5}><td {sty1}>평단매수</td><td {sty2}>{D['buy1']}</td><td {sty3}>{D['buy11']}</td><td {sty4}>{D['buy12']}</td></tr>"
        if int(D['buy31']) :  output += f"<tr {sty5}><td {sty1}>추종매수</td><td {sty2}>{D['buy3']}</td><td {sty3}>{D['buy31']}</td><td {sty4}>{D['buy32']}</td></tr>"
        if int(D['buy41']) :  output += f"<tr {sty5}><td {sty1}>추가매수</td><td {sty2}>{D['buy4']}</td><td {sty3}>{D['buy41']}</td><td {sty4}>{D['buy42']}</td></tr>"
        if int(D['buy51']) :  output += f"<tr {sty5}><td {sty1}>전략매수</td><td {sty2}>{D['buy5']}</td><td {sty3}>{D['buy51']}</td><td {sty4}>{D['buy52']}</td></tr>"
        if int(D['buy21']) :  output += f"<tr {sty5}><td {sty1}>큰단매수</td><td {sty2}>{D['buy2']}</td><td {sty3}>{D['buy21']}</td><td {sty4}>{D['buy22']}</td></tr>"
        output += "<tr style='background-color:black'><td colspan='4' style='line-height:2px'>&nbsp;</td></tr>"
        if int(D['sell11']) : output += f"<tr {sty6}><td {sty1}>첫째매도</td><td {sty2}>{D['sell1']}</td><td {sty3}>{D['sell11']}</td><td {sty4}>{D['sell12']}</td></tr>"
        if int(D['sell21']) : output += f"<tr {sty6}><td {sty1}>둘째매도</td><td {sty2}>{D['sell2']}</td><td {sty3}>{D['sell21']}</td><td {sty4}>{D['sell22']}</td></tr>"
        if int(D['sell31']) : output += f"<tr {sty6}><td {sty1}>강제매도</td><td {sty2}>{D['sell3']}</td><td {sty3}>{D['sell31']}</td><td {sty4}>{D['sell32']}</td></tr>"
        if int(D['sell41']) : output += f"<tr {sty6}><td {sty1}>전략매도</td><td {sty2}>{D['sell4']}</td><td {sty3}>{D['sell41']}</td><td {sty4}>{D['sell42']}</td></tr>"
        output += "</tbody></table>"
        output += "</div>"
        return self.echo(output)
