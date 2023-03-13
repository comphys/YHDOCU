from system.core.load import Model
import system.core.my_utils as my

class M_dashboard(Model) :

    def view(self) :
    
        self.D['오늘날자']  = my.timestamp_to_date(opt=7) 
        self.D['오늘요일']  = my.dayofdate(self.D['오늘날자'])

        self.DB.tbl = 'h_VICTORY_board'
        ckdate = self.DB.get_one("max(add0)")
        self.DB.wre = f"add0='{ckdate}'"

        out = self.DB.get_line("add13,add17,add18,sub1,sub2,sub3,sub12,sub19,sub20,sub25,sub26,sub28,sub33")
        매수수량 = int(out['sub2'])
        매수가격 = float(out['sub19']) 
        매수가액 = 매수수량 * 매수가격

        self.D['매수수량'] = f"{매수수량:3d}"
        self.D['매수가격'] = f"${매수가격:,.2f}"
        self.D['매수가액'] = f"${매수가액:,.2f}"
        self.D['현재시즌'] = out['sub1']
        self.D['경과일수'] = out['sub12']

        매도수량 = int(out['sub3'])
        매도가격 = float(out['sub20']) 
        매도가액 = 매도수량 * 매도가격

        self.D['매도수량'] = f"{매도수량:>3d}"
        self.D['매도가격'] = f"${매도가격:,.2f}"
        self.D['매도가액'] = f"${매도가액:,.2f}"

        self.D['총입금'] = f"{float(out['sub25']):,.0f}"
        self.D['총출금'] = f"{float(out['sub26']):,.0f}"
        self.D['현재액'] = f"{float(out['add17']):,.0f}"
        self.D['수익금'] = f"{float(out['add17'])-float(out['sub25'])-float(out['sub26']):,.0f}"
        self.D['수익률'] = f"{float(out['sub28']):,.1f}"

        self.D['현재수량'] = out['add13']    
        self.D['현재수익'] = out['add18']
        self.D['현수익률'] = out['sub33']

        self.chart()

    def chart(self) :
        self.DB.clear()
        self.DB.tbl = 'h_VICTORY_board'
        self.DB.odr = "add0 DESC"
        self.DB.lmt = '20'

        chart_data = self.DB.get("add0,add14,add17,sub16,sub33",assoc=True)

        if chart_data :

            first_date = chart_data[-1]['add0']
            last_date  = chart_data[ 0]['add0']
            self.D['s_date'] = first_date
            self.D['e_date'] = last_date
  
            chart_data.reverse()
        
            self.D['chart_date']   = [x['add0'][5:] for x in chart_data]
            self.D['close_price']  = [float(x['add14']) for x in chart_data]; close_base = self.D['close_price'][0]
            self.D['close_change'] = [round((x-close_base) / close_base * 100,2) for x in self.D['close_price']]
            self.D['total_value']  = [float(x['add17']) for x in chart_data]
            self.D['soxl_average'] = ['null' if not float(x['sub16']) else float(x['sub16']) for x in chart_data]
            self.D['lever_change'] = [float(x['sub33']) for x in chart_data]



 