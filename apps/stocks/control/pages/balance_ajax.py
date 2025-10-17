from system.core.load import Control
import system.core.my_utils as my

class Balance_ajax(Control) :

    def _auto(self) :
        
        self.DB = self.db('stocks')
        self.msg  = ''
    
    
    def re_balance(self) :
        
        s_ch = self.D['post']['choice']
        m_in = self.D['post']['money_in']
        m_ex = self.D['post']['money_ex']
        m_nw = self.D['post']['money_nw']
        
        if   s_ch == 'RSN'  : self.rsn(m_in,m_ex,m_nw)
        elif s_ch == 'N315' : self.n315(m_in,m_ex,m_nw)
        else : self.lucky(m_in,m_ex,m_nw)

        return self.msg

    def next_stock_day(self,today) :
        
        delta = 1
        while delta :
            temp = my.dayofdate(today,delta)
            weekend = 1 if temp[1] in ('토','일') else 0
            holiday = 1 if self.DB.cnt(f"SELECT key FROM parameters WHERE val='{temp[0]}' and cat='미국증시휴장일'") else 0 
            delta = 0 if not (weekend + holiday) else delta + 1
        return temp


    def rsn(self,m_in,m_ex,m_nw) :

        LD = self.DB.last_record('h_rsnLog_board')

        if  LD['add17'] != '수익실현' : 
            self.msg = '현재 시즌 진행 중입니다. 시즌 종료 후 작업하시기 바랍니다.'
            return
        
        next_day = self.next_stock_day(LD['add0'])

        or_mon = my.sv(LD['add18'])
        os_mon = my.sv(LD['add19'])
        on_mon = my.sv(LD['add20'])
        ov_mon = my.sv(LD['v_03'])

        # 잔액 및 가치합계 재 설정
        total = or_mon + os_mon + ov_mon  # R잔액 + S잔액 + N잔액
        
        if my.sv(m_in) : total += my.sv(m_in)
        if my.sv(m_ex) : total -= my.sv(m_ex)
        if my.sv(m_nw) : total  = my.sv(m_nw)

        ST = self.DB.parameters_dict('매매전략/RSN')
        allot = my.sf(ST['TC011'])
        
        r_mon  = round(total*allot[0]/100,2);  LD['r_14'] = LD['r_03'] = LD['add18'] = f"{r_mon:.2f}"
        s_mon  = round(total*allot[1]/100,2);  LD['s_14'] = LD['s_03'] = LD['add19'] = f"{s_mon:.2f}"
        n_mon  = total - r_mon - s_mon;        LD['n_14'] = LD['n_03'] = LD['add20'] = f"{n_mon:.2f}"
        v_mon  = total;                        LD['v_14'] = LD['v_03'] = LD['add12'] = LD['add14'] = f"{v_mon:.2f}"

        if r_mon > or_mon : LD['r_01'] = f"{r_mon - or_mon:.2f}"
        else : LD['r_02'] = f"{or_mon - r_mon:.2f}"
        if s_mon > os_mon : LD['s_01'] = f"{s_mon - os_mon:.2f}"
        else : LD['s_02'] = f"{os_mon - s_mon:.2f}"
        if n_mon > on_mon : LD['n_01'] = f"{n_mon - on_mon:.2f}"
        else : LD['n_02'] = f"{on_mon - n_mon:.2f}"
        if v_mon > ov_mon : LD['v_01'] = f"{v_mon - ov_mon:.2f}"
        else : LD['v_02'] = f"{ov_mon - v_mon:.2f}"

        # 기초수량 재 선정
        r_bm = int(r_mon/ST['TV010']); LD['r_15'] = f"{r_bm:.2f}" # 일매수금
        r_bq = my.ceil(r_bm / my.sv(LD['add3'])); LD['r_16'] = str(r_bq) # 기초수량
        LD['r_17'] = LD['r_16'] # 매수수량

        s_bm = int(s_mon/ST['TV010']); LD['s_15'] = f"{s_bm:.2f}" # 일매수금
        s_bq = my.ceil(s_bm / my.sv(LD['add3'])); LD['s_16'] = str(s_bq) # 기초수량

        n_allot = my.sf(ST['TN010'])
        LD['n_16'] = int(n_mon * n_allot[0])
        LD['n_16'] = str(LD['n_16'])

        v_bm = int(v_mon/ST['TV010']); LD['v_15'] = f"{v_bm:.2f}" # 일매수금
        v_bq = my.ceil(v_bm / my.sv(LD['add3'])); LD['v_16'] = str(v_bq) # 기초수량
        LD['v_17'] = LD['v_16'] # 매수수량

        LD['add2'] = 'R' # 새로운 베이스 임을 표시
        x_mon = f"(증) {v_mon-ov_mon:,.2f}" if v_mon > ov_mon else f"(감) {ov_mon-v_mon:,.2f}"
        LD['content'] = f"투자금액 변경 (기존) {ov_mon:,.2f} > (변경) {v_mon:,.2f}, {x_mon}, (변경시작일) {next_day[0]}" 
        
        # 불필요한 데이타 삭제 None 필드 등 
        del(LD['no']); del(LD['brother']); del(LD['tle_color']); del(LD['reply']); del(LD['hit'])
        del(LD['v_13']); del(LD['v_24']); del(LD['v_25'])
        del(LD['r_13']); del(LD['r_24']); del(LD['r_25'])
        del(LD['s_13']); del(LD['s_24']); del(LD['s_25'])
        del(LD['n_13']); del(LD['n_24']); del(LD['n_25'])


        LD['wdate'] = LD['mdate'] = my.now_timestamp()
        qry=self.DB.qry_insert('h_rsnLog_board',LD)
        self.DB.exe(qry)

        # 파라미터 업데이트
        self.DB.parameter_update('TX050',next_day[0])
        self.DB.parameter_update('TX051',f"{my.sv(LD['add12']):,.2f}")
        
        self.msg = "RSN 에 대한 투자금액 변경작업이 정상적으로 변경되었습니다."

    
    def n315(self,m_in,m_ex,m_nw) :

        LD = self.DB.last_record('h_log315_board')

        if  LD['add20'] not in ('수익실현','기초셋팅') : 
            self.msg = '현재 시즌 진행 중입니다. 시즌 종료 후 작업하시기 바랍니다.'
            return
        
        next_day = self.next_stock_day(LD['add0'])

        # 잔액 및 가치합계 재 설정
        o_mon = my.sv(LD['add5'])
        if my.sv(m_in) : n_mon = o_mon + my.sv(m_in)
        if my.sv(m_ex) : n_mon = o_mon - my.sv(m_ex)
        if my.sv(m_nw) : n_mon  = my.sv(m_nw)
        x_mon = f"(증) {n_mon-o_mon:,.2f}" if n_mon > o_mon else f"(감) {o_mon-n_mon:,.2f}"

        LD['add0'] = LD['add18'] = next_day[0]
        LD['add5'] = LD['add16'] = LD['add19'] = f"{n_mon:.2f}"
        LD['add6'] = ''
        LD['content'] = f"투자금액 변경 (기존) {o_mon:,.2f} > (변경) {n_mon:,.2f}, {x_mon}, (변경시작일) {next_day[0]}" 
        LD['add2'] = 'R' # 새로운 베이스 임을 표시 
        LD['add3'] = LD['add4'] = LD['add13'] = LD['add14'] = LD['add15'] = LD['add17'] = LD['add21'] = '0.00' 
        LD['add20'] = '기초셋팅'
        
        # 새로운 데이타 
        del(LD['no']); del(LD['brother']); del(LD['tle_color']); del(LD['reply']); del(LD['hit'])
        LD['wdate'] = LD['mdate'] = my.now_timestamp()
        qry=self.DB.qry_insert('h_log315_board',LD)
        self.DB.exe(qry)

        # 파라미터 업데이트
        self.DB.parameter_update('N0701',next_day[0])
        self.DB.parameter_update('N0702',f"{n_mon:,.2f}")

        self.msg = "N315 에 대한 투자금액 변경에 대한 파라미터가 정상적으로 변경되었습니다."

    
    def lucky(self,m_in,m_ex,m_nw) :

        LD = self.DB.last_record('h_log_lucky_board')

        if  LD['add17'] not in ('수익실현','초기셋팅') : 
            self.msg = '현재 시즌 진행 중입니다. 시즌 종료 후 작업하시기 바랍니다.'
            return
        
        next_day = self.next_stock_day(LD['add0'])

        # 잔액 및 가치합계 재 설정
        o_mon = my.sv(LD['add5'])
        if my.sv(m_in) : n_mon = o_mon + my.sv(m_in)
        if my.sv(m_ex) : n_mon = o_mon - my.sv(m_ex)
        if my.sv(m_nw) : n_mon  = my.sv(m_nw)
        x_mon = f"(증) {n_mon-o_mon:,.2f}" if n_mon > o_mon else f"(감) {o_mon-n_mon:,.2f}"

        LD['add0'] = next_day[0]
        LD['add5'] = LD['add15']  = f"{n_mon:.2f}"
        LD['add10'] = LD['add20'] = '0.00'
        LD['add8'] = '0'
        LD['add9'] = '0.0000'
        LD['add21']= '초기셋팅' 
        LD['content'] = f"투자금액 변경 (기존) {o_mon:,.2f} > (변경) {n_mon:,.2f}, {x_mon}, (변경시작일) {next_day[0]}" 
        LD['add2'] = 'R' # 새로운 베이스 임을 표시 
        
        # 새로운 데이타 
        del(LD['no']); del(LD['brother']); del(LD['tle_color']); del(LD['reply']); del(LD['hit'])
        del(LD['add21'])
        LD['wdate'] = LD['mdate'] = my.now_timestamp()
        qry=self.DB.qry_insert('h_log_lucky_board',LD)

        self.DB.exe(qry)

        self.msg = "Lucky 에 대한 투자금액 변경이 정상적으로 변경되었습니다."
        
        
        