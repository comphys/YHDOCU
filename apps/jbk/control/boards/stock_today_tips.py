from system.core.load import Control
from datetime import datetime
import time,math

class Stock_today_tips(Control) : 
    
    def _auto(self) :
        self.DB = self.db('jbk')

    def hellow(self) :
        
        no = self.gets['no']
        self.tbl = self.gets['tbl']

        self.DB.tbl,self.DB.wre = (self.tbl,f"no={no}")
        D = self.DB.get_line("add0,add1,buy1,buy11,buy12,buy2,buy21,buy22,buy3,buy31,buy32,buy4,buy41,buy42,buy5,buy51,buy52,sell1,sell11,sell12,sell2,sell21,sell22,sell3,sell31,sell32,sell4,sell41,sell42")
        # 출력시작
        sty1 ="style='text-align:center;width:100px'"
        sty2 ="style='text-align:center;width:80px'"
        sty3 ="style='text-align:right;width:80px;padding-right:10px'"
        sty4 ="style='text-align:right;width:100px;padding-right:10px'"
        sty5 ="style='color:#CED8F6'"
        sty6 ="style='color:#F6CECE'"

        output  = "<div id='stock_tips' style='width:350px;height:250px;padding:10px;background-color:#1d1f24;color:#e1e1e1;border:1px solid #F7F8E0;' ondblclick=\"h_dialog.close('ST_TIPS')\">"
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
    
    def season_close(self) :
        tbl  = self.D['post']['tbl']
        code = self.D['post']['code']
        season = self.D['post']['season']

        qry = f"UPDATE h_{tbl}_board SET add19='시즌종료' WHERE add1='{code}' and add2='{season}'"
        self.DB.exe(qry)
        return "해당 시즌을 종료하였습니다"
    
    def buy_suggest(self) :
        date = self.gets['date']
        code = self.gets['code']
        daym = self.gets['daym']
        daym = float(daym.replace(',',''))

        일매수금 = int(daym / 27)
        now_date = int(time.mktime(datetime.strptime(date,'%Y-%m-%d').timetuple()))
        old_date = datetime.fromtimestamp(now_date-3600*24*14).strftime('%Y-%m-%d')
        qry = f"SELECT add3 FROM h_stockHistory_board WHERE add0 BETWEEN '{old_date}' and '{date}' and add1='{code}' ORDER BY add0"
        aaa= self.DB.exe(qry)
        bbb= [float(x[0].replace(',','')) for x in aaa ]
        yes= bbb[-1]
        c_drop = 0
        c_goup = 0
        for i in range(1,len(bbb)) :
            c_drop = c_drop + 1 if bbb[i] <= bbb[i-1] else 0
            c_goup = c_goup + 1 if bbb[i] >  bbb[i-1] else 0
        
        매수수량 = math.ceil(일매수금/yes) 
        회차 = 1.0
        if c_drop : 
            매수수량 += 매수수량 * c_drop 
            회차 = 2.0 

        매수단가 = yes * 1.1
        output  = "<div style='width:350px;height:250px;padding:10px;background-color:#1d1f24;color:#e1e1e1;border:1px solid #F7F8E0;' >"
        output += "<span style='color:yellow'>DNA 2002 전략을 위한 해당종목의 첫날 매수방법</span><br>"
        output += f"주식종목 : {code}<br>"
        output += f"매수예정 : {date}<br>"
        output += f"일매수금 : {일매수금:,}<br>"
        output += f"연속하락 : {c_drop}<br>"
        output += f"연속상승 : {c_goup}<br>"
        output += f"전일종가 : {yes}<br>"
        output += "---------------------------------<br>"
        output += f"매수단가 : LOC {매수단가:.2f}<br>"
        output += f"매수수량 : {매수수량}<br>"
        output += f"회차 : {회차}<br>"
        output += "</div>"

        return self.echo(output)


    def autoinput_price(self) :
        # 종가구하기
        ud = {}
        self.DB.clear()
        self.DB.tbl = 'h_stockHistory_board'
        self.DB.wre = f"add0='{self.D['post']['add0']}' and add1='JEPQ'"; ud['add8']   = self.DB.get_one('add3') 
        self.DB.wre = f"add0='{self.D['post']['add0']}' and add1='SOXL'"; ud['add14']  = self.DB.get_one('add3')
        if not ud['add8'] : ud['add8'] = 0
        return self.json(ud) 

