from system.core.load import SKIN
import system.core.my_utils as my
import math

class 쓰기_VICTORY(SKIN) :

    def write(self) :
        OBODY = self.D.get('OBODY',None)
        self.D['BODY'] = OBODY
        self.D['TR_add'] = []
        self.D['TR_cat'] = []
        self.D['method'] = self.SYS.V['_mtd']
        w_width = 1000
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'

        self.D['ChkField'] = ','.join(self.D['MustCheck'])

        self.D['today'] = None
        if not OBODY :
            prev_date = self.DB.one(f"SELECT max(add0) FROM h_{self.SYS.parm[0]}_board")
            if  prev_date :
                self.D['today'] = self.DB.one(f"SELECT min(add0) FROM h_stockHistory_board WHERE add0 > '{prev_date}'")

            if self.D['today'] : 

                self.init_value()
                # 매도상황 검토
                self.check_sell()
                # 매수상황 검토
                self.check_buy()
                self.calculate()
            
                # 매도전략
                self.normal_sell()
                # 매수전략
                self.normal_buy()
                AutoInput = self.return_value()
                self.D['BODY'] = AutoInput

    def add_all(self,category, exFIDktitle, exFormat, bid, OBODY) :
        CAT_KEY = []
        if category : CAT_KEY = category.split('/')
        if exFIDktitle :
            for key, val in exFIDktitle.items() :
                if   exFormat[key] == 'number' : clss="class='i-number'" 
                elif exFormat[key] == 'n_edit' : clss="class='i-number'" 
                elif exFormat[key] == 'date'   : clss="class='i-date'" 
                else : clss="class='i-text'"
                if key in CAT_KEY : self.user_cat(val,key,'132px',clss,self.D['bid'],OBODY) 
                else : self.user_add(val,key,clss,OBODY)
    
    def user_add(self,val,key,clss,OBODY) :
        if key == 'add0' : return 
        value =''
        if OBODY : value = OBODY.get(key,'')
        tmp  = f"<div class='i-input-div'><div class='write-input-left'>{val}</div>"
        tmp += f"<input type='text' name='{key}' {clss} value='{value}'></div>"
        
        self.D['TR_add'].append(tmp)
    
    def user_cat(self,val,key,xwidth,clss,bid,OBODY) :
        if key == 'add0' : return 
        value =''
        if OBODY : value = OBODY.get(key,'')
        qry = f"SELECT distinct {key} FROM h_{bid}_board ORDER BY {key}"
        ITM = self.DB.exe(qry)

        tmp  = "<div class='myselect' style='margin-right:10px'>"
        tmp += f"<input placeholder='{val}' name='{key}' type='text' value='{value}' style='width:{xwidth};background-color:#363636;border-color:#333333'>"
        tmp += f"<div class='btn-group'>"
        tmp += f"<button class='btn btn-select dropdown-toggle' data-toggle='dropdown' tabindex='-1'><span class='caret'></span></button>"
        tmp += "<ul class='dropdown-menu'>"
        tmp += f"<li><a>{val}</a></li>"
        if ITM :
            for cat in ITM :  
                cat_c = 'N/A' if not cat[0] else cat[0]
                tmp += "<li><a href='#'>"+ cat_c + "</a></li>"
        tmp += "</ul>"
        tmp += "</div></div>" 

        self.D['TR_cat'].append(tmp)


# -----------------------------------------------------------------------------------------------------------------------
# From Auto Input 
# -----------------------------------------------------------------------------------------------------------------------

    def init_value(self) :
        self.DB = self.SYS.db('stocks')
        self.M = {}
        self.M['진행일자'] = self.D['today']
        self.DB.tbl, self.DB.wre = (f"h_{self.SYS.parm[0]}_board", f"add0 < '{self.M['진행일자']}'")
        old_date = self.DB.get_one("max(add0)")
        self.DB.wre = f"add0='{old_date}'"
        LD = self.M['LD'] = self.DB.get_line('*')

        # 종가구하기
        self.DB.clear()
        self.DB.tbl = 'h_stockHistory_board'
        self.DB.wre = f"add0='{self.M['진행일자']}' and add1='JEPQ'"; self.M['JEPQ']  = self.DB.get_one('add3')
        self.DB.wre = f"add0='{self.M['진행일자']}' and add1='SOXL'"; 
        self.M['당일종가'] = float(self.DB.get_one('add3'))
        self.M['전일종가'] = float(self.M['LD']['add14'])
        self.M['연속상승'] = self.DB.get_one('add9')
        self.M['연속하락'] = self.DB.get_one('add10')
        
        # 매매전략 가져오기
        self.M['매매전략'] = 'VICTORY'
        self.DB.tbl, self.DB.wre = ('h_stock_strategy_board',f"add0='{self.M['매매전략']}'")
        self.S = self.DB.get_line('add2,add3,add4,add5,add9,add10,add11,add17,add18,add22,add25')
        self.M['분할횟수']  = int(self.S['add2'])
        self.D['비중조절']  = 1 + float(self.S['add3'])/100   # 매매일수 에 따른 구매수량 가중치
        self.M['평단가치']  = 1 + float(self.S['add4'])/100   # 일반매수 구매가 범위
        self.M['큰단가치']  = 1 + float(self.S['add5'])/100   # 매수첫날 구매가 범위
        self.M['첫매가치']  = 1 + float(self.S['add9'])/100
        self.M['둘매가치']  = 1 + float(self.S['add10'])/100
        self.M['강매시작']  = int(self.S['add17'])
        self.M['강매가치']  = 1 + float(self.S['add18'])/100
        self.M['위매비중']  = int(self.S['add25'])
        self.M['회복기한']  = int(self.S['add11'])

        # 매수 매도 초기화
        self.M['매수금액']=0.0
        self.M['매도금액']=0.0  
        self.M['변동수량'] = 0
        self.M['매수수량'] = 0
        self.M['매도수량'] = 0
        self.M['전매도량'] = 0
        self.M['전매도가'] = 0.0

        self.M['시즌'] = int(LD['sub1'])
        self.M['평균단가'] = float(LD['sub16'])
        self.M['일매수금'] = int(LD['sub4'])
        self.M['경과일수'] = int(LD['sub12']) 
        self.M['매매현황'] = ''
        self.M['진행상황'] = '매도대기'
        self.M['보유수량'] = int(LD['add13'])
        self.M['현매수금'] = float(LD['sub17'])
        self.M['가용잔액'] = float(LD['add19'])
        self.M['추가자금'] = float(LD['add20'])
        self.M['진행상황'] = '매도대기'
        self.M['기초수량'] = int(LD['sub18'])
        self.M['회복전략'] = float(LD['sub7'])

    def calculate(self)  :

        매도가격 = self.M['당일종가']
        매수가격 = self.M['당일종가']
        if self.M['보유수량'] : self.M['경과일수'] +=1

        if  self.M['매도수량'] :
            self.M['매도금액'] = 매도가격 * self.M['매도수량']
            self.M['변동수량'] = -self.M['매도수량'] 
            self.M['진행상황'] = '전량매도' 
            수익금액 = self.M['매도금액'] - self.M['현매수금']
            self.M['회복전략'] = 0 if 수익금액 > 0 else self.S['add22']
            self.M['진행상황'] = f"{수익금액:,.2f}"
            self.M['경과일수'] = 0
            self.M['시즌'] += 1
            self.M['기초수량'] = 0           
            # 리밸런싱
            self.rebalance()

        if  self.M['매수수량'] :
            self.M['매수금액']  = 매수가격 * self.M['매수수량']
            self.M['변동수량']  = self.M['매수수량']
            self.M['보유수량'] += self.M['매수수량']
            self.M['평균단가']  = (self.M['현매수금'] + self.M['매수금액']) / self.M['보유수량'] 

            self.M['가용잔액'] -=  self.M['매수금액']
            if  self.M['가용잔액'] < 0 : 
                self.M['추가자금'] += self.M['가용잔액']
                self.M['가용잔액'] = 0
                
            self.M['진행상황'] = '일반매수'

        if  not self.M['경과일수'] and self.M['매수수량'] : self.M['경과일수'] = 1
        if  not self.M['보유수량'] : self.M['진행상황'] = '매수대기'

    def rebalance(self)  :
        total = self.M['매도금액'] + self.M['가용잔액'] + self.M['추가자금']
        self.M['가용잔액'] = round(total * 0.67)
        self.M['추가자금'] = int(total - self.M['가용잔액'])
        self.M['일매수금'] = round(self.M['가용잔액']/self.M['분할횟수']) 

    def normal_sell(self) :

        if  self.M['경과일수'] ==  0 :
            self.M['전매도량']  =  0
            self.M['전매도가']  =  self.M['당일종가']
            return

        매수수량 = math.ceil(self.M['기초수량'] * (self.M['경과일수']*self.D['비중조절'] + 1))
        매도단가 = self.M['평균단가'] * self.M['첫매가치']  if self.M['평균단가'] else self.M['당일종가']

        if (매수수량 * self.M['전일종가']) > self.M['가용잔액'] + self.M['추가자금'] : 
            매도단가 = self.M['평균단가']*self.M['둘매가치']
        if self.M['회복전략'] and self.M['경과일수'] +1 <= self.M['회복기한'] : 매도단가 = self.M['평균단가']* (1+self.M['회복전략']/100)

        if self.M['경과일수']+1 >= self.M['강매시작'] : 매도단가 = self.M['평균단가']*self.M['강매가치']

        self.M['전매도량'] = self.M['보유수량']
        self.M['전매도가'] = round(매도단가,2)

    def normal_buy(self)  :

        if  self.M['경과일수'] == 0 :
            self.M['기초수량'] = self.M['전매수량'] = math.ceil(self.M['일매수금']/self.M['당일종가'])
            self.M['전매수가'] = self.M['당일종가'] * self.M['큰단가치']
            return

        매수단가 = self.M['당일종가'] * self.M['평단가치']
        매수수량 = math.ceil(self.M['기초수량'] * (self.M['경과일수']*self.D['비중조절'] + 1))

        if  매수수량 * 매수단가 > self.M['가용잔액'] + self.M['추가자금'] : 
            매수수량 = self.M['기초수량'] * self.M['위매비중']
            self.M['진행상황'] = '매수제한'
        if  매수수량 * 매수단가 > self.M['가용잔액'] + self.M['추가자금'] : 
            매수수량 = 0
            self.M['진행상황'] = '매수금지'  

        self.M['전매수량'] = 매수수량
        self.M['전매수가'] = round(매수단가,2)
        self.M['예상금액'] = f"{매수수량 * 매수단가 :,.2f}"
       
                
    def check_sell(self) :
        if  not self.M['경과일수'] : return
        if  self.M['당일종가'] >= float(self.M['LD']['sub20']) : 
            self.M['매도수량']  = int(self.M['LD']['sub3'])
      
    def check_buy(self) :
        if  not self.M['경과일수'] : 
            if  self.M['당일종가'] <= float(self.M['LD']['sub19']) :
                self.M['매수수량']  = self.M['기초수량'] = math.ceil(self.M['일매수금']/self.M['전일종가'])  # 첫날에만 기초수량 재산정
        else :
            if  self.M['당일종가'] <= float(self.M['LD']['sub19']) : self.M['매수수량']  = int(self.M['LD']['sub2'])


    def return_value(self) :
        ud = {}
        LD = self.M['LD']
        # 현금투자
        ud['add3']=f"{float(LD['add3']):,.2f}"
        # JEPQ
        ud['add7']=LD['add7']; ud['sub21']=LD['sub21']; ud['sub22']=LD['sub22'] 
        ud['sub23']=f"{float(LD['sub23']):,.2f}"; ud['sub24']=f"{float(LD['sub24']):,.2f}"
        ud['sub8'] = 0
        # SOXL
        ud['add13']=LD['add13']; ud['sub16']=LD['sub16']; 
        ud['sub15']=f"{float(LD['sub15']):,.2f}";  ud['sub14']=f"{float(LD['sub14']):,.2f}"; ud['sub17']=LD['sub17']
        ud['sub7'] =self.M['회복전략'] 
        # 투자상황
        ud['sub11']=f"{round(float(LD['sub11']),4):,.2f}"
        ud['sub25']=f"{float(LD['sub25']):,}"; ud['sub27']=f"{float(LD['sub27']):,}"
        ud['sub26']=f"{int(LD['sub26']):,}"; 
        # 종가
        ud['add8']  = self.M['JEPQ'] if self.M['JEPQ'] else 0
        ud['add14'] = self.M['당일종가']
        ud['sub5'] = self.M['연속상승']
        ud['sub6'] = self.M['연속하락']
        # 매매결과
        ud['add11'] = f"{round(self.M['매수금액'],4):,.2f}"
        ud['add12'] = f"{round(self.M['매도금액'],4):,.2f}"
        ud['sub9']  = self.M['변동수량']
        if self.M['매수금액'] : ud['sub9'] =  self.M['매수수량']
        if self.M['매도금액'] : ud['sub9'] = -self.M['매도수량']
        # 매매상황
        ud['add18'] = self.M['진행상황']
        # 매매전략
        if self.M['경과일수'] !=0 and self.M['전매수가'] >= self.M['전매도가'] : self.M['전매수가'] = self.M['전매도가'] - 0.01
        ud['sub1'] = self.M['시즌'];      ud['sub12'] = self.M['경과일수']
        ud['sub4'] = self.M['일매수금'];  ud['sub18'] = self.M['기초수량']
        ud['sub2'] = self.M['전매수량'];  ud['sub19'] = f"{self.M['전매수가']:,.2f}"
        ud['sub3'] = self.M['전매도량'];  ud['sub20'] = f"{self.M['전매도가']:,.2f}"
        # 자금상황
        ud['add19'] = f"{round(self.M['가용잔액'],4):,.2f}"
        ud['add20'] = f"{round(self.M['추가자금'],4):,.2f}"
        # 투자목표
        ud['sub29'] = LD['sub29']
        diff_day = my.diff_day(LD['add0'], self.M['진행일자'])
        target_value = math.ceil(int(LD['sub30']) * (1+float(LD['sub29']))**diff_day)
        ud['sub30'] = f"{target_value:,}"
        ud['sub31'] = LD['sub31']
        ud['sub32'] = LD['sub32']
        return ud

