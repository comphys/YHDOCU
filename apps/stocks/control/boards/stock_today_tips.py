from system.core.load import Control
import math

class Stock_today_tips(Control) : 
    
    def _auto(self) :
        self.DB = self.db('stocks')

    def hellow(self) :
        no = self.gets['no']       
        # 기본데이타 갖고 오기
        self.DB.tbl, self.DB.wre = ('h_daily_trading_board', f"no={no}")
        preDATA = self.DB.get_line("add1,add2,add7,add9,add10,add14")
        매매전략 = preDATA['add2']

        # 주문전략 갖고 오기
        self.DB.tbl, self.DB.wre = ("h_stock_strategy_board",f"add0='{매매전략}'")
        STRAGY = self.DB.get_line("add1,add2,add3,add4,add5,add6,add7,add8,add9")
        
        # 주문가격 계산
        일매수금   = (float(preDATA['add9']) + float(preDATA['add14'])) / float(STRAGY['add1'])
        매수금액1  = 일매수금 * float(STRAGY['add2'])/100
        매수금액2  = 일매수금 - 매수금액1
        전일평단가 = float(preDATA['add10'])
        평단가매수 = 전일평단가 * (1+float(STRAGY['add4'])/100)
        큰단가매수 = 전일평단가 * (1+float(STRAGY['add5'])/100)

        평단가주문 = math.ceil(매수금액1/평단가매수)
        큰단가주문 = math.ceil(매수금액2/큰단가매수)

        보유수량   = int(preDATA['add7'])
        매도비중1  = float(STRAGY['add6'])/100
        매도비중2  = float(STRAGY['add7'])/100
        
        매도분할   = False
        if  매도비중2 == 0.0 :
            매도수량 = 보유수량
            매도가격 = 전일평단가 * (1+float(STRAGY['add8'])/100)
        else : 
            매도분할 = True
            매도수량1  = math.ceil(보유수량 * 매도비중1)
            매도수량2  = 보유수량 - 매도수량1

            매도가격1  = 전일평단가 * (1+float(STRAGY['add8'])/100)
            매도가격2  = 전일평단가 * (1+float(STRAGY['add9'])/100)

        # 출력시작
        style1 ="<span style='font-weight:bold;color:#A9F5BC;font-size:16px'>"
        style2 ="<span style='font-weight:bold;color:#F6CECE;font-size:16px'>"
        style3 ="<span style='font-weight:bold;color:yellow;font-size:16px'>"
        style4 ="<span style='font-weight:bold;color:#e8f6cd;font-size:14px'>"

        output  = "<div id='stock_tips' style='padding:10px;background-color:#424242;color:#F2F2F2;' >"
        output += f"{style3}{preDATA['add1']} </span>&nbsp;{style4}(매매전략 : {매매전략})</span>&nbsp;&nbsp; 금일 매수 조건 : (평단가) {style1}{평단가주문} * ${평단가매수:,.2f} </span> &nbsp;&nbsp;"
        output += f"(큰단가) <span {style1}{큰단가주문} * ${큰단가매수:,.2f}</span> &nbsp;&nbsp;&nbsp;"
        if 매도분할 : 
            output += f"금일 매도 조건 : (주문단가1) {style2}{매도수량1} * ${매도가격1:,.2f}</span>  / (주문단가2) {style2}{매도수량2} * ${매도가격2:,.2f} * </span>"
        else : 
            output += f"금일 매도 조건 : (주문단가) {style2}{매도수량} * ${매도가격:,.2f}</span>"
        output += "</div>"
        return self.echo(output)
