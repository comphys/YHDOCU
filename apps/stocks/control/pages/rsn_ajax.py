from system.core.load import Control
import system.core.my_utils as my

class Rsn_ajax(Control) :

    def _auto(self) :
        
        self.DB = self.db('stocks')
    
    def log_rsn(self) :
        
        RSN = self.load_app_lib('rsn')
        
        PD = {} # post data

        PD['기회자금'] = self.D['post']['기회자금']
        PD['안정자금'] = self.D['post']['안정자금']
        PD['생활자금'] = self.D['post']['생활자금']

        PD['시작일자'] = self.D['post']['시작일자']
        PD['종료일자'] = self.D['post']['종료일자']
        PD['기회시점'] = self.D['post']['기회시점']
        PD['기회회복'] = self.D['post']['기회회복']
        PD['안정시점'] = self.D['post']['안정시점']
        PD['안정회복'] = self.D['post']['안정회복']        
        
        PD['수료적용'] = 'on' if self.D['post']['수료적용'] == 'true' else 'off'
        PD['세금적용'] = 'on' if self.D['post']['세금적용'] == 'true' else 'off'
        PD['일밸런싱'] = 'on' if self.D['post']['일밸런싱'] == 'true' else 'off'
        PD['이밸런싱'] = 'on' if self.D['post']['이밸런싱'] == 'true' else 'off'
        PD['가상손실'] = 'on' if self.D['post']['가상손실'] == 'true' else 'off'
        
        key = self.D['post']['적용전략']
            
        RSN.D |= PD
        RSN.get_simResult(PD['시작일자'],PD['종료일자'])
        DC = RSN.get_simulLog(key)
        return self.json(DC)
    
    def synchro(self) :
        
        opt = self.D['post']['opt']
        ldate = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")
    
        if  opt == 'real' :
            sdate = self.DB.parameters('TX050')
            T_mon = my.sv(self.DB.parameters('TX051'))
            mode_ = self.DB.parameters('TX052')
        elif opt == 'test' :
            sdate = my.dayofdate(ldate,delta=-365*2)[0]
            T_mon = my.sv(self.DB.parameters('TC010'))
            mode_ = '기본진행'
        
        alloc = my.sf(self.DB.parameters('TC011'))
        R_mon = round(T_mon * alloc[0]/100,2)
        S_mon = round(T_mon * alloc[1]/100,2)
        N_mon = T_mon - R_mon - S_mon
        
        RD = {}
        RD['sdate'] = sdate
        RD['ldate'] = ldate
        RD['R_mon'] = f"{R_mon:,.2f}"
        RD['S_mon'] = f"{S_mon:,.2f}"
        RD['N_mon'] = f"{N_mon:,.2f}"
        RD['mode_'] = mode_
        
        return self.json(RD)
    
    def log_invest(self) :
        
        ldate = self.D['post']['종료일자']
        
        sdate = self.DB.parameters('TX050')
        T_mon = my.sv(self.DB.parameters('TX051'))
        mode_ = self.DB.parameters('TX052')
        
        alloc = my.sf(self.DB.parameters('TC011'))
        R_mon = round(T_mon * alloc[0]/100,2)
        S_mon = round(T_mon * alloc[1]/100,2)
        N_mon = T_mon - R_mon - S_mon
        
        PD = {} # post data

        PD['기회자금'] = f"{R_mon:,.2f}"
        PD['안정자금'] = f"{S_mon:,.2f}"
        PD['생활자금'] = f"{N_mon:,.2f}"

        PD['시작일자'] = sdate
        PD['종료일자'] = ldate
        PD['기회시점'] = f"{self.DB.parameters('TR021'):.1f}"
        PD['기회회복'] = f"{self.DB.parameters('TR022'):.1f}"
        PD['안정시점'] = f"{self.DB.parameters('TS021'):.1f}"
        PD['안정회복'] = f"{self.DB.parameters('TS022'):.1f}"      
        
        PD['수료적용'] = 'on' 
        PD['세금적용'] = 'off' 
        PD['일밸런싱'] = 'on' 
        PD['이밸런싱'] = 'on' 
        PD['가상손실'] = 'on' if mode_ == '전략진행' else 'off'
        
        opt = '초기셋팅' if sdate == ldate else '일반진행'
        
        RSN = self.load_app_lib('rsn')
        RSN.D |= PD
        RSN.get_simResult(PD['시작일자'],PD['종료일자'])
        DV = RSN.get_simulLog('V')
        DR = RSN.get_simulLog('R')
        DS = RSN.get_simulLog('S')
        DN = RSN.get_simulLog('N')
        
        LD = {}
        LD['add0'] = ldate
        LD['add1']  = DV['sub1']            # 시즌
        LD['add2']  = DV['sub12']           # 날수
        LD['add3']  = DV['add14']           # 종가
        LD['add4']  = DV['add20']           # 종가 변동
        LD['add5']  = DV['sub5']            # 추이
        LD['add6']  = my.sv(DR['add9'],'i') + my.sv(DS['add9'],'i') + my.sv(DN['add9'],'i')       # 보유수량   
        LD['add7']  = my.sv(DR['add6']) + my.sv(DS['add6']) + my.sv(DN['add6'])  # 총매수금
        LD['add8']  = round(LD['add7']/LD['add6'],4) if LD['add6'] else '0.0000' # 평균단가
        LD['add9']  = round(LD['add3']*LD['add6'],2) # 평가금액
        LD['add10'] = my.sv(DR['add18']) + my.sv(DS['add18']) + my.sv(DN['add18'])  # 현재수익
        LD['add11'] = round(LD['add10'] / LD['add7'] * 100,2) if LD['add7'] else '0.00' # 현수익률
        
        if  DV['sub29'] in ('익절매도','손절매도') : 
            매도금합 = my.sv(DR['add12']) + my.sv(DS['add12']) + my.sv(DN['add12'])
            매수금합 = RSN.DB.one(f"SELECT CAST(add7 as float) FROM h_rsnLog_board WHERE add0 < '{today}' ORDER BY add0 DESC LIMIT 1")
            LD['add11'] = round((매도금합/매수금합-1) * 100,2)     
        
        LD['add12'] = my.sv(DR['add3']) + my.sv(DS['add3']) + my.sv(DN['add3'])  # 현재잔액
        LD['add14'] = my.sv(DR['add17']) + my.sv(DS['add17']) + my.sv(DN['add17'])  # 자산총액
        LD['add15'] = DV['sub32'] # 초기일자
        LD['add16'] = DV['sub29'] # 진행상황
        LD['add17'] = opt # 카테고리
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
            LD[key+'_01']  = tac['sub6'] if opt == '초기셋팅' else '0.00' # 입금
            LD[key+'_02']  = '0.00' # 출금
            LD[key+'_03']  = tac['add3']    # 잔액
            LD[key+'_04']  = tac['add11']   # 매수금
            LD[key+'_05']  = tac['add12']   # 매도금
            LD[key+'_06']  = tac['add5']    # 변동수량
            LD[key+'_07']  = tac['add9']    # 보유수량
            LD[key+'_08']  = tac['add8']    # 현수익률
            LD[key+'_09']  = tac['add7']    # 평균단가
            LD[key+'_10']  = tac['add15']   # 현재가치
            LD[key+'_11']  = tac['add17']   # 가치합계
            LD[key+'_12']  = tac['add18']   # 수익현황 
            LD[key+'_13']  = tac['add6']    # 현매수금      
            LD[key+'_14']  = tac['add17']   # 가치합계
            LD[key+'_15']  = tac['sub4']    # 일매수금(VRS), 매수차수(N)
            LD[key+'_16']  = tac['sub18']   # 기초수량(VRS), 매금단계(N)
            LD[key+'_17']  = tac['sub2']    # 예정 매수수량
            LD[key+'_18']  = tac['sub19']   # 예정 매수가격 
            LD[key+'_19']  = tac['sub3']    # 예정 매도수량
            LD[key+'_20']  = tac['sub20']   # 예정 매도가격
            LD[key+'_21']  = tac['sub6']    # 초기자금
            LD[key+'_22']  = tac['sub30']   # 수수료
        
        # 각 전략의 잔액도 함께 목록에 표시하기 위함
        LD['add18'] = DR['add3']
        LD['add19'] = DS['add3']
        LD['add20'] = DN['add3']
        
        LD['uid']   = 'comphys'
        LD['uname'] = '정용훈'
        LD['wdate'] = LD['mdate'] = my.now_timestamp() 
        qry=self.DB.qry_insert('h_rsnLog_board',LD); self.DB.exe(qry) 
     
        
        return self.json(PD)
        
        
        