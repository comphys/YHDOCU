from system.core.load import Model
import system.core.my_utils as ut
class M_dashboard(Model) :

    def view(self) :

        # 상황
        self.D['첫째상황'] = self.outcome('h_daily_first_board')
        self.D['둘째상황'] = self.outcome('h_daily_second_board')

        today = ut.timestamp_to_date(opt=7)
        weekd = ut.dayofdate(today)
        if   weekd == '월' : ckday = ut.dayofdate(today,delta=-3)
        elif weekd == '토' : ckday = None
        elif weekd == '일' : ckday = None
        else : ckday = ut.dayofdate(today,delta=-1)

        self.D['오늘날자']  = today
        self.D['오늘요일']  = weekd   
        self.D['확인날자']  = ckday[0]
        self.D['확인요일']  = ckday[1]

        # 전략

        self.DB.tbl, self.DB.wre = ('h_daily_first_board',f"add0='{self.D['확인날자']}' and add19='시즌진행'")
        D = self.DB.get_line("add0,add1,buy1,buy11,buy12,buy2,buy21,buy22,buy3,buy31,buy32,buy4,buy41,buy42,buy5,buy51,buy52,sell1,sell11,sell12,sell2,sell21,sell22,sell3,sell31,sell32,sell4,sell41,sell42")
        if D : self.D['첫째전략'] = self.print_out(D,title='첫째일지')
        else : self.D['첫째전략'] = "<div style='text-align:center'>No information for the day. Check it</div>"

        self.DB.tbl, self.DB.wre = ('h_daily_second_board',f"add0='{self.D['확인날자']}' and add19='시즌진행'")
        D = self.DB.get_line("add0,add1,buy1,buy11,buy12,buy2,buy21,buy22,buy3,buy31,buy32,buy4,buy41,buy42,buy5,buy51,buy52,sell1,sell11,sell12,sell2,sell21,sell22,sell3,sell31,sell32,sell4,sell41,sell42")

        if D : self.D['둘째전략'] = self.print_out(D,title='둘째일지')
        else : self.D['둘째전략'] = "<div style='text-align:center'>No information for the day. Check it</div>"

        self.DB.tbl, self.DB.wre = ('h_daily_second_third',f"add0='{self.D['확인날자']}' and add19='시즌진행'")
        D = self.DB.get_line("add0,add1,buy1,buy11,buy12,buy2,buy21,buy22,buy3,buy31,buy32,buy4,buy41,buy42,buy5,buy51,buy52,sell1,sell11,sell12,sell2,sell21,sell22,sell3,sell31,sell32,sell4,sell41,sell42")

        if D : self.D['세째전략'] = self.print_out(D,title='세째일지')
        else : self.D['세째전략'] = "<div style='text-align:center'>No information for the day. Check it</div>"

    def print_out(self,D,title='') :
        sty1 ="style='text-align:center;width:100px'"
        sty2 ="style='text-align:center;width:80px'"
        sty3 ="style='text-align:right;width:80px;padding-right:10px'"
        sty4 ="style='text-align:right;width:100px;padding-right:10px'"
        sty5 ="style='color:#CED8F6'"
        sty6 ="style='color:#F6CECE'"

        output  = f"<div style='text-align:center;margin-bottom:5px'><span style='color:#E0F8E0;text-weight:bold'>{title}</span> <span style='color:#F7F8E0;font-weight:bold'>{D['add1']}</span> 매매전략 " 
        output += f"From <span style='color:#CEECF5'>{self.D['확인날자']}({self.D['확인요일']})</span></div>" 
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
        return output

    def outcome(self,tbl) :

        self.DB.tbl, self.DB.wre = (tbl,"add1='SOXL'")
        start_date, last_date = self.DB.get("min(add0),max(add0)",many=1,assoc=False)

        self.DB.wre = f"add0='{start_date}'"
        기본자산, 추가자산 = self.DB.get("sub7,sub8",many=1,assoc=False) 

        self.DB.wre = f"add0='{last_date}'"
        평가금액, 가용잔액, 추가자본, 현재시즌, 진행률 = self.DB.get("add11,add16,add17,add2,add4",many=1,assoc=False) 

        초기자본 = float(기본자산) + float(추가자산)
        최종자본 = float(평가금액) + float(가용잔액) + float(추가자본)
        최종수익 = 최종자본 - 초기자본 
        최종수익률 = (최종수익/초기자본) * 100 

        초기자본 = f"{초기자본:,}"
        최종자본 = f"{최종자본:,}"
        최종수익 = f"<span style='color:#ced8f6'>{최종수익:,.2f}</span>" if 최종수익 < 0 else f"<span style='color:#f6cece'>{최종수익:,.2f}</span>"
        최종수익률 = f"<span style='color:#ced8f6'>{최종수익률:,.1f}%</span>" if 최종수익률 < 0 else f"<span style='color:#f6cece'>{최종수익률:,.1f}%</span>"

        out = ['S'+현재시즌,진행률,최종자본,초기자본,최종수익,최종수익률]
        return out
