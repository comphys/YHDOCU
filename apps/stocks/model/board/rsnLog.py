from system.core.load import Model
import system.core.my_utils as my

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
        if  option == 'N315'  : key = 'N0710_' + self.D['USER']['uid']
        if  option == 'LUCKY' : key = 'L0500'
        self.DB.parameter_update(key,odrday)


    def season_chart(self) :

        season = self.D['post']['season']

        qry = f"SELECT CAST(add3 as float), CAST(v_09 as float), CAST(r_09 as float), CAST(s_09 as float), CAST(n_09 as float), add0 FROM h_rsnLog_board WHERE add1='{season}' ORDER BY add0 ASC"
        RST = self.DB.exe(qry)
        sdate = RST[-1][5]
        
        profit = self.DB.oneline(f"SELECT add10, add11, add6, v_08,r_08,s_08,n_08 FROM h_rsnLog_board WHERE add0='{sdate}'")

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
        PD['sdate']  = sdate
        PD['season'] = season
        PD['stocks'] = my.sv(profit[2],'i')

        PD['sfc'] = PD['C'][0]
        PD['slc'] = PD['C'][-1]
        PD['scd'] = f"{(PD['slc']/PD['sfc'] -1) * 100:.2f}"

        PD['vpr']  = profit[3]
        PD['rpr']  = profit[4]
        PD['spr']  = profit[5]
        PD['npr']  = profit[6]
        
        return self.SYS.json(PD)    
    
    def update_log(self) :

        tday = self.D['post']['tday']
        lday = self.DB.last_date('h_stockHistory_board')

        if tday > lday : return self.SYS.json("최종 업데이트가 완료되어 있습니다.")

        RSN  = self.SYS.load_app_lib('rsn')

        RSN.do_tacticsLog(tday)
        DV = RSN.get_simulLog('V')
        DR = RSN.get_simulLog('R')
        DS = RSN.get_simulLog('S')
        DN = RSN.get_simulLog('N')

        if   RSN.D['시작일자'] == RSN.D['종료일자'] :  카테고리 = '초기셋팅' 
        elif DV['sub29'] in ('익절매도','손절매도') :  카테고리 = '수익실현'
        else : 카테고리 = '일반진행'
        
        LD = {}
        LD['add0']  = tday
        LD['add1']  = RSN.DB.last_data_one('add1','h_rsnLog_board')    # 시즌
        LD['add2']  = DV['sub12']           # 날수
        LD['add3']  = DV['add14']           # 종가
        LD['add4']  = DV['add20']           # 종가 변동
        LD['add5']  = DV['sub5']            # 추이
        LD['add6']  = my.sv(DR['add9'],'i') + my.sv(DS['add9'],'i') + my.sv(DN['add9'],'i')       # 보유수량   
        LD['add7']  = my.sv(DR['add6']) + my.sv(DS['add6']) + my.sv(DN['add6'])  # 현재 총매수금
        LD['add8']  = round(LD['add7']/LD['add6'],4) if LD['add6'] else 0 # 평균단가
        LD['add9']  = round(LD['add3']*LD['add6'],2) # 평가금액
        LD['add10'] = my.sv(DR['add18']) + my.sv(DS['add18']) + my.sv(DN['add18'])  # 현재수익
        
        if  LD['add2']  == 1 :
            new_season  = int(my.sv(LD['add1'],'i')) + 1
            LD['add1']  = str(new_season)    


        # 전체 매도 시 전시즌 대비 수익률
        if  DV['sub29'] in ('익절매도','손절매도') : 
            LD['add10'] = my.sv(RSN.D['손익통계'][-1][2])
            LD['add11'] = my.sv(RSN.D['손익통계'][-1][3])
        else :
            LD['add11'] = round((LD['add3'] / LD['add8'] -1) * 100,2) if LD['add8'] else 0 # 현수익률 진행중일 때
        

        LD['add12'] = my.sv(DR['add3']) + my.sv(DS['add3']) + my.sv(DN['add3'])  # 현재잔액
        LD['add13'] = my.sv(DR['add12']) + my.sv(DS['add12']) + my.sv(DN['add12'])  # 총매도금
        LD['add14'] = my.sv(DR['add17']) + my.sv(DS['add17']) + my.sv(DN['add17'])  # 자산총액
        LD['add15'] = DV['sub32'] # 초기일자
        LD['add16'] = DV['sub29'] # 진행상황
        LD['add17'] = 카테고리
        # prettify
        LD['add6'] = f"{LD['add6']:}"
        LD['add7'] = f"{LD['add7']:.2f}"
        LD['add8'] = f"{LD['add8']:.4f}"
        LD['add9'] = f"{LD['add9']:.2f}"
        LD['add10'] = f"{LD['add10']:.2f}"
        LD['add11'] = f"{LD['add11']:.2f}"
        LD['add12'] = f"{LD['add12']:.2f}"
        LD['add14'] = f"{LD['add14']:.2f}"
        
        for (tac,key) in [(DV,'v'),(DR,'r'),(DS,'s'),(DN,'n')] :         
            # LD[key+'_01']  = tac['sub6'] if 카테고리 == '초기셋팅' else '0.00' # 입금
            LD[key+'_01']  = '0.00'
            LD[key+'_02']  = '0.00' # 출금
            LD[key+'_03']  = tac['add3']    # 잔액
            LD[key+'_04']  = tac['add11']   # 매수금
            LD[key+'_05']  = tac['add12']   # 매도금
            LD[key+'_06']  = tac['add5']    # 변동수량
            LD[key+'_07']  = tac['add9']    # 보유수량
            LD[key+'_08']  = tac['add8']    # 현수익률
            LD[key+'_09']  = tac['add7']    # 평균단가
            LD[key+'_10']  = tac['add15']   # 현재가치
            LD[key+'_11']  = tac['add6']    # 현매수금
            LD[key+'_12']  = tac['add18']   # 현재손익
            LD[key+'_14']  = tac['add17']   # 가치합계
            LD[key+'_15']  = tac['sub4']    # 일매수금(VRS), 매수차수(N)
            LD[key+'_16']  = tac['sub18']   # 기초수량(VRS), 매금단계(N)
            LD[key+'_17']  = tac['sub2']    # 예정 매수수량
            LD[key+'_18']  = tac['sub19']   # 예정 매수가격 
            LD[key+'_19']  = tac['sub3']    # 예정 매도수량
            LD[key+'_20']  = tac['sub20']   # 예정 매도가격
            LD[key+'_21']  = tac['sub6']    # 초기자금
            LD[key+'_22']  = tac['sub30']   # 수수료
            LD[key+'_23']  = tac['sub29']   # 진행상황

        # 각 전략의 잔액도 함께 목록에 표시하기 위함
        LD['add18'] = DR['add3']
        LD['add19'] = DS['add3']
        LD['add20'] = DN['add3']
        
        LD['uid']   = 'comphys'
        LD['uname'] = '정용훈'
        LD['wdate'] = LD['mdate'] = my.now_timestamp()     
        
        qry=RSN.DB.qry_insert('h_rsnLog_board',LD)
        RSN.DB.exe(qry)

        return self.SYS.json("OK")
