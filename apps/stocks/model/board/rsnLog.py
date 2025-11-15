from system.core.load import Model

class Ajax(Model) :

    def view_log(self) :

        theday = self.D['post']['theday']
        tactic = self.D['post']['tactic']

        LD = self.DB.line(f"SELECT * FROM h_rsnLog_board WHERE add0='{theday}'")
        PD = {}

        PD['a01'] = LD[tactic+'_01']  # 입금 
        PD['a02'] = LD[tactic+'_02']  # 출금
        PD['a03'] = LD[tactic+'_03']  # 잔액 
        PD['a04'] = f"{float(LD[tactic+'_03'])/float(LD[tactic+'_14'])*100:.2f}" # 현금비중 

        PD['b01'] = LD[tactic+'_04']  # 매수금액 
        PD['b02'] = LD[tactic+'_05']  # 매도금액 
        PD['b03'] = LD[tactic+'_06']  # 변동수량
        PD['b04'] = f"{float(LD[tactic+'_10'])/float(LD[tactic+'_14'])*100:.2f}" # 레버비중 

        PD['c01'] = LD['add3']  # 당일종가 
        PD['c02'] = LD['add4']  # 종가변동 
        PD['c03'] = LD[tactic+'_07']  # 보유수량 
        PD['c04'] = LD[tactic+'_08']  # 현수익률 

        PD['d01'] = LD[tactic+'_09']  # 평균단가 
        PD['d02'] = LD[tactic+'_10']  # 현재가치 
        PD['d03'] = LD[tactic+'_11']  # 현매수금 
        PD['d04'] = LD[tactic+'_12']  # 현재손익

        PD['e01'] = LD['add1']  # 현재시즌 
        PD['e02'] = LD[tactic+'_15']  # 일매수금 
        PD['e03'] = LD[tactic+'_17']  # 매수수량 
        PD['e04'] = LD[tactic+'_19']  # 매도수량

        PD['f01'] = LD['add2']  # 경과일수 
        PD['f02'] = LD[tactic+'_16']  # 기초수량 
        PD['f03'] = LD[tactic+'_18']  # 매수가격 
        PD['f04'] = LD[tactic+'_20']  # 매도가격

        PD['g01'] = LD[tactic+'_23']  # 진행상황 
        PD['g02'] = LD['add5']  # 종가추이 
        PD['g03'] = LD[tactic+'_21']  # 초기금액 
        PD['g04'] = LD['add15']  # 초기일자

        PD['h01'] = LD[tactic+'_14']  # 가치합계 
        PD['h02'] = LD[tactic+'_22']  # 수수료등 
        PD['h03'] = f"{float(PD['h01'])-float(PD['g03']):,.2f}"  # 누적수익 
        PD['h04'] = LD['add17']  # 카테고리

        return self.SYS.json(PD)
    
    def dailyCheckUpdate(self) :
        
        odrday = self.D['post']['odrday']
        option = self.D['post']['option']
        
        if  option == 'RSN'   : key = 'TX070'
        if  option == 'N315'  : key = 'N0710'
        if  option == 'LUCKY' : key = 'L0500'
        self.DB.parameter_update(key,odrday)


    def season_chart(self) :

        season = self.D['post']['season']
        sdate  = self.D['post']['sdate']

        qry = f"SELECT CAST(add3 as float), CAST(v_09 as float), CAST(r_09 as float), CAST(s_09 as float), CAST(n_09 as float) FROM h_rsnLog_board WHERE add1='{season}' ORDER BY add0 ASC"
        RST = self.DB.exe(qry)

        profit = self.DB.oneline(f"SELECT add10, add11 FROM h_rsnLog_board WHERE add0='{sdate}'")

        cnt = len(RST)
        PD = {}
        PD['C'] = [0.0]*cnt
        PD['V'] = [0.0]*cnt
        PD['R'] = [0.0]*cnt
        PD['S'] = [0.0]*cnt
        PD['N'] = [0.0]*cnt

        for idx,rst in enumerate(RST) :
            PD['C'][idx] = rst[0]
            PD['V'][idx] = rst[1] if rst[1] else None
            PD['R'][idx] = rst[2] if rst[2] else None
            PD['S'][idx] = rst[3] if rst[3] else None
            PD['N'][idx] = rst[4] if rst[4] else None

        PD['amin'] = min(PD['C'])
        PD['amax'] = max(PD['C'])
        PD['profit'] = profit[0]
        PD['prate']  = profit[1]

        return self.SYS.json(PD)    