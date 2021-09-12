from system.core.load import Control
import math,json

class Stocks(Control) : 

  
    def _auto(self) :
        self.DB = self.db('stocks')


    def autoinput(self) :
        update = {}
        # 기본정보 받아오기 
        기록일자 = self.D['post']['add0']
        종목코드 = self.D['post']['add1']
        체결단가 = self.D['post']['add4'].replace(',','')
        체결수량 = self.D['post']['add5'].replace(',','')
        매수금액 = self.D['post']['add6'].replace(',','')
        매매전략 = self.D['post']['add2']
        가용잔액 = self.D['post']['add14'].replace(',','')

        self.DB.tbl = 'h_daily_trading_board'
        self.DB.wre = f"add1='{종목코드}'" 
        preChk = self.DB.get_one("max(no)")
        oldChk = self.DB.get_one("min(no)")

        if preChk is None and ( 체결단가 == '' or 체결수량 == '' or 매매전략 == '' or 가용잔액 == ''): 
            update['msg'] = "먼저 기록된 데이타가 없습니다. 추가 정보를 입력하여 주시기 바랍니다"
            update['replyCode'] = 'NMDATA'
            return self.echo(json.dumps(update))
        
        
        # 당일종가 구하기
        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add0='{기록일자}' and add1='{종목코드}'")
        당일종가 = self.DB.get_one("add3")
        if  당일종가 is None : 
            update['msg'] = "기록일에 해당하는 '당일종가'가 존재하지 않습니다. 주가정보를 업데이트 하시기 바랍니다"
            update['replyCode'] = 'NOTICE'
            return self.echo(json.dumps(update))
        else : 
            당일종가 = float(당일종가)

        if preChk is None :
            if preChk is None :
                # 자동계산 1
                체결단가 = float(체결단가) ; 체결수량 = int(체결수량) ; 가용잔액 = float(가용잔액)
                매수금액 = 체결단가 * 체결수량   
                평균단가 = 매수금액 / 체결수량         
                보유수량 = 체결수량                               
                총매수금 = 매수금액
                평가금액 = 당일종가 * 보유수량
                수익현황 = 평가금액 - 총매수금
                현수익률 = (수익현황 / 총매수금) * 100
                진행시즌 = 1 ; 로테이션 = 1
                가용잔액 = 가용잔액 - 총매수금
                진행상황 = '정상진행'

        else :
            # 시작 이전 데이타 입력 방지하기 
            self.DB.tbl, self.DB.wre = ('h_daily_trading_board',f"no='{oldChk}' and add1='{종목코드}'")
            if self.DB.get_one('add0') > 기록일자 :
                update['msg'] = "최초의 기록보다 예전 날자를 선택하였습니다"
                update['replyCode'] = 'NOTICE'
                return self.echo(json.dumps(update))                
 
            # 데이타 중복 방지하기
            self.DB.tbl, self.DB.wre = ('h_daily_trading_board',f"add0='{기록일자}' and add1='{종목코드}'")
            if self.DB.get_one('add0') : 
                update['msg'] = "같은 날자에 입력된 데이타가 존재합니다"
                update['replyCode'] = 'NOTICE'
                return self.echo(json.dumps(update))

            # 전일데이타 가져오기
            self.DB.tbl, self.DB.wre = ('h_daily_trading_board',f"no={preChk}")
            preDATA = self.DB.get_line("add2,add7,add9,add10,add14,add15,add16")
            매매전략 = preDATA['add2']

            # 체결단가 계산하기
            if  체결수량 == '' and 매수금액 == '' :
                체결수량 = 체결수량1 = 체결수량2 =0; 매수금액 = 0.0
                self.DB.tbl, self.DB.wre = ('h_stock_strategy_board',f"add0='{preDATA['add2']}'")
                STRAGY = self.DB.get_line("add1,add2,add3,add4,add5")
                
                일매수금   = (float(preDATA['add9']) + float(preDATA['add14'])) / float(STRAGY['add1'])
                매수금액1  = 일매수금 * float(STRAGY['add2'])
                매수금액2  = 일매수금 - 매수금액1
                전일평단가 = float(preDATA['add10'])
                평단가매수 = 전일평단가 * (1+float(STRAGY['add4']))
                큰단가매수 = 전일평단가 * (1+float(STRAGY['add5']))

                if 당일종가 <= 평단가매수 :  체결수량1 = math.ceil(매수금액1 / 평단가매수)
                
                if 당일종가 <= 큰단가매수 :  체결수량2 = math.ceil(매수금액2 / 큰단가매수)
                
                체결수량 = 체결수량1 + 체결수량2
                체결단가 = 당일종가
                매수금액 = 체결수량 * 당일종가

                
            else :
                체결수량 = int(체결수량)
                매수금액 = float(매수금액)
                체결단가 = 매수금액 / 체결수량

            # 자동 계산2
            가용잔액 = float(preDATA['add14'])
            보유수량 = int(preDATA['add7']) + 체결수량
            총매수금 = float(preDATA['add9']) + 매수금액
            평균단가 = 총매수금 / 보유수량
            평가금액 = 당일종가 * 보유수량
            수익현황 = 평가금액 - 총매수금
            현수익률 = (수익현황 / 총매수금) * 100
            진행시즌 = 1 
            로테이션 = int(preDATA['add16']) + 1
            가용잔액 = 가용잔액 - 매수금액
            진행상황 = '정상진행'


        update['msg']       = "데이타를 자동으로 계산하였습니다. 확인해 보시고 저장하시기 바랍니다"
        update['replyCode'] = "SUCCESS"
        update['add15']  = f"{int(진행시즌):,}"
        update['add16']  = f"{int(로테이션):,}"
        update['add2']   = 매매전략
        update['add3']   = f"{round(당일종가,4):,.3f}"
        update['add4']   = f"{round(체결단가,4):,.3f}"
        update['add5']   = f"{int(체결수량):,}"
        update['add6']   = f"{round(매수금액,4):,.3f}"
        update['add10']  = f"{round(평균단가,4):,.3f}"
        update['add7']   = f"{int(보유수량):,}"
        update['add9']   = f"{round(총매수금,4):,.3f}"
        update['add8']   = f"{round(평가금액,4):,.3f}"
        update['add11']  = f"{round(수익현황,4):,.3f}"
        update['add12']  = f"{round(현수익률,4):,.2f}"
        update['add14']  = f"{round(가용잔액,2):,.3f}"
        update['add17']  = 진행상황

        return self.echo(json.dumps(update))