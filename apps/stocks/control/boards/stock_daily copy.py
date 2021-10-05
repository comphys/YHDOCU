from system.core.load import Control
from datetime import datetime
import math

class Stocks(Control) : 

  
    def _auto(self) :
        self.DB = self.db('stocks')
        self.M = {}

    def init_value(self) :

        # 기본정보 받아오기 
        self.M['기록일자'] = self.D['post']['add0']
        self.M['종목코드'] = self.D['post']['add1']
        self.M['매매전략'] = self.D['post']['add20']
        self.M['체결단가'] = self.D['post'].get('add6',0) 
        self.M['체결수량'] = self.D['post'].get('add7',0)   
        self.M['매수금액'] = self.D['post'].get('add8',0)
        self.M['가용잔액'] = self.D['post'].get('add16',0)
        
        if self.M['체결수량'] : int(self.M['체결수량'].replace(',',''))
        if self.M['체결단가'] : float(self.M['체결단가'].replace(',',''))
        if self.M['가용잔액'] : float(self.M['가용잔액'].replace(',',''))
       

    def old_price(self) :
        now = int(datetime.timestamp())
        old = str(now-3600*24*10) 
        old_date = datetime.fromtimestamp(old).strftime('%Y-%m-%d')
        self.DB.wre = f"add1='{self.M['종목코드']}' and add0 between '{old_date}'' and '{self.M['기록일자']}' ORDER BY add0"
        return self.DB.get_line('add3')

    def cur_price(self) :
        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add0='{self.M['기록일자']}' and add1='{self.M['종목코드']}'")
        return self.DB.get_one('add3')

    def the_first_day(self) :
        # 자동계산 1
        체결단가 = float(체결단가) ; 체결수량 = int(체결수량) ; 가용잔액 = float(가용잔액)
        매수금액 = 체결단가 * 체결수량   
        평균단가 = 매수금액 / 체결수량         
        보유수량 = 체결수량                               
        총매수금 = 매수금액
        평가금액 = 당일종가 * 보유수량
        수익현황 = 평가금액 - 총매수금
        현수익률 = (수익현황 / 총매수금) * 100
        진행시즌 = 1 ; 로테이션 = 1.0
        가용잔액 = 가용잔액 - 총매수금
        진행상황 = '정상진행'

    def autoinput(self) :
        update = {}
        self.DB.tbl = 'h_daily_trading_board'
        self.DB.wre = f"add0  < '{self.M['기록일자']}' and add1='{self.M['종목코드']}'" 
        preChk = self.DB.get_one("max(no)")
        oldChk = self.DB.get_one("min(no)")

        self.init_value()

        if preChk is None : 
            update['msg'] = "첫날 데이타를 자동 입력합니다. 자동입력 데이타를 확인하여 주시기 바랍니다"
            update['replyCode'] = 'NMDATA'
     
            self.M['당일종가'] = self.cur_price()
            # 과거종가 구하기

            과거종가 = self.DB.get_line("add3")

            if  self.M['당일종가'] is None : 
                update['msg'] = "기록일에 해당하는 '당일종가'가 존재하지 않습니다. 주가정보를 업데이트 하시기 바랍니다"
                update['replyCode'] = 'NOTICE'
                return self.json(update)
            else : 
                self.M['당일종가'] = float(self.M['당일종가'])

        else :
            로테이션 = 0.0
            # 시작 이전 데이타 입력 방지하기 
            self.DB.tbl, self.DB.wre = ('h_daily_trading_board',f"no='{oldChk}' and add1='{self.M['종목코드']}'")
            if self.DB.get_one('add0') > self.M['기록일자'] :
                update['msg'] = "최초의 기록보다 예전 날자를 선택하였습니다"
                update['replyCode'] = 'NOTICE'
                return self.json(update)                
 
            # 데이타 중복 방지하기
            self.DB.tbl, self.DB.wre = ('h_daily_trading_board',f"add0='{기록일자}' and add1='{종목코드}'")
            if self.DB.get_one('add0') and self.parm[0] != 'modify': 
                update['msg'] = "같은 날자에 입력된 데이타가 존재합니다"
                update['replyCode'] = 'NOTICE'
                return self.json(update)

            # 전일데이타 가져오기
            self.DB.tbl, self.DB.wre = ('h_daily_trading_board',f"no={preChk}")
            preDATA = self.DB.get_line("add2,add7,add9,add10,add14,add15,add16")
            self.M['매매전략'] = preDATA['add2']

            # 체결단가 계산하기
            if  체결수량 == '' and 매수금액 == '' :
                체결수량 = 체결수량1 = 체결수량2 =0; 매수금액 = 0.0
                self.DB.tbl, self.DB.wre = ('h_stock_strategy_board',f"add0='{preDATA['add2']}'")
                STRAGY = self.DB.get_line("add1,add2,add3,add4,add5,add10")

                일매수금   = (float(preDATA['add9']) + float(preDATA['add14'])) / float(STRAGY['add1'])
                매수금액1  = 일매수금 * float(STRAGY['add2'])/100
                매수금액2  = 일매수금 - 매수금액1
                전일평단가 = float(preDATA['add10'])
                평단가매수 = 전일평단가 * (1+float(STRAGY['add4'])/100)
                큰단가매수 = 전일평단가 * (1+float(STRAGY['add5'])/100)

                if 당일종가 <= 평단가매수 :  
                    체결수량1 = math.ceil(매수금액1 / 평단가매수)
                    로테이션 += 0.5
                
                if 당일종가 <= 큰단가매수 :  
                    체결수량2 = math.ceil(매수금액2 / 큰단가매수)
                    로테이션 += 0.5
                체결수량 = 체결수량1 + 체결수량2
                체결단가 = 당일종가
                매수금액 = 체결수량 * 당일종가

                
            else :
                체결수량 = int(체결수량)
                매수금액 = float(매수금액)
                체결단가 = 매수금액 / 체결수량


            가용잔액 = float(preDATA['add14'])
            보유수량 = int(preDATA['add7']) + 체결수량
            총매수금 = float(preDATA['add9']) + 매수금액
            평균단가 = 총매수금 / 보유수량
            평가금액 = 당일종가 * 보유수량
            수익현황 = 평가금액 - 총매수금
            현수익률 = (수익현황 / 총매수금) * 100
            진행시즌 = 1 
            로테이션 = float(preDATA['add16']) + 로테이션
            가용잔액 = 가용잔액 - 매수금액
            진행상황 = '정상진행'


        update['msg']       = "데이타를 자동으로 계산하였습니다. 확인해 보시고 저장하시기 바랍니다"
        update['replyCode'] = "SUCCESS"
        update['add15']  = f"{int(진행시즌):,}"
        update['add16']  = f"{로테이션:.1f}"
        update['add2']   = self.M['매매전략']
        update['add3']   = f"{round(당일종가,4):,.3f}"
        update['add4']   = f"{round(체결단가,4):,.3f}"
        update['add5']   = f"{int(체결수량):,}"
        update['add6']   = f"{round(매수금액,4):,.3f}"
        update['add10']  = f"{round(평균단가,4):,.4f}"
        update['add7']   = f"{int(보유수량):,}"
        update['add9']   = f"{round(총매수금,4):,.3f}"
        update['add8']   = f"{round(평가금액,4):,.2f}"
        update['add11']  = f"{round(수익현황,4):,.4f}"
        update['add12']  = f"{round(현수익률,4):,.2f}"
        update['add14']  = f"{round(가용잔액,2):,.2f}"
        update['add17']  = 진행상황

        return self.json(update)