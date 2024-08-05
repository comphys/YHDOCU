from update_RST import RST
import myutils.my_utils as my

class update_Vtactic3(RST) :

    def check_sell(self) :
        if  not self.M['경과일수'] : return #첫날일 경우 리턴
        if  self.M['당일종가'] >= float(self.M['LD']['sub20']) : self.M['매도수량']  = int(self.M['LD']['sub3'])

    def check_buy(self) :
        if  not self.M['경과일수'] :
            if  self.M['당일종가'] <= float(self.M['LD']['sub19']) :
                self.M['매수수량']  = self.M['기초수량'] = self.my_ceil(self.M['일매수금']/self.M['전일종가'])  # 첫날에만 기초수량 재산정
        else :
            if  self.M['당일종가'] <= float(self.M['LD']['sub19']) : self.M['매수수량']  = int(self.M['LD']['sub2'])

    def tomorrow_sell(self) :

        if  self.M['경과일수'] ==  0 :
            self.M['전매도량']  =  0
            self.M['전매도가']  =  self.M['당일종가']
            return

        매수단가 = round(self.M['당일종가'] * self.M['평단가치'],2)
        매수수량 = self.my_ceil(self.M['기초수량'] * (self.M['경과일수']*self.M['비중조절'] + 1))
        매도단가 = self.my_roundup(self.M['평균단가'] * self.M['첫매가치'])  if self.M['평균단가'] else self.M['당일종가']

        if (매수수량 * 매수단가) > self.M['현재잔액']  :
            매도단가 = self.my_roundup(self.M['평균단가']*self.M['둘매가치'])
        if self.M['회복전략'] and self.M['경과일수'] +1 <= self.M['매도대기'] : 매도단가 = self.my_roundup(self.M['평균단가']* self.M['전략가치'])

        if self.M['경과일수']+1 >= self.M['강매시작'] : 매도단가 = self.my_roundup(self.M['평균단가']*self.M['강매가치'])

        self.M['전매도량'] = self.M['보유수량']
        self.M['전매도가'] = round(매도단가,2)
        

    def tomorrow_buy(self)  :

        if  self.M['경과일수'] == 0 :
            self.M['기초수량'] = self.M['전매수량'] = self.my_ceil(self.M['일매수금']/self.M['당일종가'])
            self.M['전매수가'] = round(self.M['당일종가'] * self.M['큰단가치'],2)
            return

        매수단가 = round(self.M['당일종가'] * self.M['평단가치'],2)
        매수수량 = self.my_ceil(self.M['기초수량'] * (self.M['경과일수']*self.M['비중조절'] + 1))

        if  매수수량 * 매수단가 > self.M['현재잔액']  :
            매수수량 = self.M['기초수량'] * self.M['위매비중']
            self.M['진행상황'] = '매수제한'
        if  매수수량 * 매수단가 > self.M['현재잔액'] :
            매수수량 = 0
            self.M['진행상황'] = '매수금지'

        self.M['전매수량'] = 매수수량
        self.M['전매수가'] = round(매수단가,2)


    def rebalance(self)  :
        self.M['일매수금'] = int(self.M['현재잔액']/self.M['분할횟수'])
        self.M['기초수량'] = self.my_ceil(self.M['일매수금']/float(self.M['당일종가']))


    def oneWrite(self) :
    
        self.init_each(self.bid)
        
        if self.D['today'] :
            self.init_value()
            self.check_sell()
            self.check_buy()
            self.calculate()
            
            self.tomorrow_sell()
            self.tomorrow_buy()
            self.update_value()

        else :
            self.send_message(f"{self.bid} {self.D['prev_date']} 이후 업데이트된 정보가 없습니다")
            return

        self.send_message(f"{self.bid} {self.D['today']} 업데이트")

# --------------------------------------------------------------------------------------------------------    

today = my.kor_loc_date('US/Eastern')[0:10]
weekd = my.dayofdate(today)

B = update_Vtactic3()
chk_holiday = B.DB.exe(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
chk_off = chk_holiday[0][0] if chk_holiday else ''

skip = (weekd in ['토','일']) or chk_off

if  skip :
    pass

else :
    B.bid = 'IGUIDE'
    B.oneWrite()
    B.bid = 'V240805'
    B.oneWrite()
        