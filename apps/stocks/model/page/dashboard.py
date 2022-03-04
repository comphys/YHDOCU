from system.core.load import Model
import system.core.my_utils as ut
class M_dashboard(Model) :

    def view(self) :

        # 상황
        self.D['첫째상황'] = self.outcome('h_daily_first_board')
        self.D['둘째상황'] = self.outcome('h_daily_second_board')
        self.D['셋째상황'] = self.outcome('h_daily_third_board')

        self.D['평가합계'] = float(self.D['첫째상황'][2].replace(',','')) + float(self.D['둘째상황'][2].replace(',','')) + float(self.D['셋째상황'][2].replace(',',''))
        self.D['투자합계'] = float(self.D['첫째상황'][3].replace(',','')) + float(self.D['둘째상황'][3].replace(',','')) + float(self.D['셋째상황'][3].replace(',',''))
        self.D['손익현황'] = self.D['평가합계'] - self.D['투자합계']
        self.D['합수익률'] = self.D['손익현황'] / self.D['투자합계'] * 100
        
        self.D['평가합계'] = f"{self.D['평가합계']:,.0f}"
        self.D['투자합계'] = f"{self.D['투자합계']:,.0f}"
        self.D['손익현황'] = f"<span style='color:#ced8f6'>{self.D['손익현황']:,.2f}</span>"  if self.D['손익현황'] < 0 else f"<span style='color:#f6cece'>{self.D['손익현황']:,.2f}</span>"
        self.D['합수익률'] = f"<span style='color:#ced8f6'>{self.D['합수익률']:,.1f}%</span>" if self.D['합수익률'] < 0 else f"<span style='color:#f6cece'>{self.D['합수익률']:,.1f}%</span>"

        today = self.DB.one('SELECT max(add0) FROM h_stockHistory_board')
        today,weekd = ut.dayofdate(today,delta=1)
        if   weekd == '월' : ckday = ut.dayofdate(today,delta=-3)
        elif weekd == '토' : ckday = None
        elif weekd == '일' : ckday = None
        else : ckday = ut.dayofdate(today,delta=-1)

        self.D['오늘날자']  = today
        self.D['오늘요일']  = weekd   
        self.D['확인날자']  = ckday[0]
        self.D['확인요일']  = ckday[1]

        # 전략
        tbl = ('h_daily_first_board','h_daily_second_board','h_daily_third_board')
        tle = ('첫째계좌','둘째계좌','셋째계좌')
        ttt = ('첫째전략','둘째전략','셋째전략')
       
        for i, tbl in enumerate(tbl) :
            self.DB.tbl, self.DB.wre = (tbl,f"add0='{self.D['확인날자']}' and add19='시즌진행'")
            D = self.DB.get_line("*")
            days = self.DB.one(f"SELECT count(no) FROM {tbl} WHERE add19='시즌진행'")
            if D : self.D[ttt[i]] = self.print_out(D,title=tle[i],days=days)
            else : self.D[ttt[i]] = f"<div style='text-align:center'>{self.D['확인날자']}({self.D['확인요일']}) 일에 대한 {tle[i]} 정보가 없습니다</div>"            

    def print_out(self,D,title='',days=0) :

        수익률 = float(D['add15'])
        수익률 = f"<span style='color:#ced8f6'>{수익률:,.2f}"+"%</span>" if 수익률 < 0 else f"<span style='color:#f6cece'>{수익률:,.2f}"+"%</span>"

        sty1 ="style='text-align:center;width:100px'"
        sty2 ="style='text-align:center;width:80px'"
        sty3 ="style='text-align:right;width:80px;padding-right:10px'"
        sty4 ="style='text-align:right;width:100px;padding-right:10px'"
        sty5 ="style='color:#d3d3d3'"
        sty6 ="style='color:#eeeeee'"
        sty7 ="style='color:#f0f0ab'"

        output  = f"<div class='dash-div-head'>"
        output += f"<span style='color:#E0F8E0;text-weight:bold'>{title} : </span>&nbsp;"
        output += f"{days}일 {D['add4']}% ( {D['add5']} | {D['add9']} ) &nbsp;{수익률}</div>"
        output += "<table class='table' style='width:95%'>"
        output += "<tbody>"
        if int(D['buy11']) :  output += f"<tr {sty5}><td {sty1}>일반매수</td><td {sty2}>{D['buy1']}</td><td {sty3}>{D['buy11']}</td><td {sty4}>{D['buy12']}</td></tr>"
        if int(D['buy31']) :  output += f"<tr {sty5}><td {sty1}>추종매수</td><td {sty2}>{D['buy3']}</td><td {sty3}>{D['buy31']}</td><td {sty4}>{D['buy32']}</td></tr>"
        if int(D['buy41']) :  output += f"<tr {sty5}><td {sty1}>추가매수</td><td {sty2}>{D['buy4']}</td><td {sty3}>{D['buy41']}</td><td {sty4}>{D['buy42']}</td></tr>"
        if int(D['buy51']) :  output += f"<tr {sty5}><td {sty1}>전략매수</td><td {sty2}>{D['buy5']}</td><td {sty3}>{D['buy51']}</td><td {sty4}>{D['buy52']}</td></tr>"
        if int(D['buy21']) :  output += f"<tr {sty5}><td {sty1}>터닝매수</td><td {sty2}>{D['buy2']}</td><td {sty3}>{D['buy21']}</td><td {sty4}>{D['buy22']}</td></tr>"
        
        if int(D['sell11']) : output += f"<tr {sty6}><td {sty1}>일반매도</td><td {sty2}>{D['sell1']}</td><td {sty3}>{D['sell11']}</td><td {sty4}>{D['sell12']}</td></tr>"
        if int(D['sell21']) : output += f"<tr {sty6}><td {sty1}>둘째매도</td><td {sty2}>{D['sell2']}</td><td {sty3}>{D['sell21']}</td><td {sty4}>{D['sell22']}</td></tr>"
        if int(D['sell31']) : output += f"<tr {sty6}><td {sty1}>강제매도</td><td {sty2}>{D['sell3']}</td><td {sty3}>{D['sell31']}</td><td {sty4}>{D['sell32']}</td></tr>"
        if int(D['sell41']) : output += f"<tr {sty7}><td {sty1}>전략매도</td><td {sty2}>{D['sell4']}</td><td {sty3}>{D['sell41']}</td><td {sty4}>{D['sell42']}</td></tr>"
        output += "</tbody></table>"
        output += f"<div class='dash-div-tail'><span style='font-weight:bold'>{D['add1']}</span> " 
        output += f"from {self.D['확인날자']}({self.D['확인요일']})&nbsp;</div>" 
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

        초기자본 = f"{초기자본:,.0f}"
        최종자본 = f"{최종자본:,.0f}"
        최종수익 = f"<span style='color:#ced8f6'>{최종수익:,.2f}</span>" if 최종수익 < 0 else f"<span style='color:#f6cece'>{최종수익:,.2f}</span>"
        최종수익률 = f"<span style='color:#ced8f6'>{최종수익률:,.1f}%</span>" if 최종수익률 < 0 else f"<span style='color:#f6cece'>{최종수익률:,.1f}%</span>"

        out = ['S'+현재시즌,진행률,최종자본,초기자본,최종수익,최종수익률]
        return out
