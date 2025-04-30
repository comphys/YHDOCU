import myutils.my_utils as my
from lib_rsn import update_Log


today = my.kor_loc_date('US/Eastern')[0:10]
weekd = my.dayofdate(today)
RSN = update_Log()

ck_holiday = RSN.DB.exe(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday[0][0] if ck_holiday else ''

skip = (weekd in ['토','일']) or is_holiday

if  skip :
    pass

else :
    RSN.do_tacticsLog(today)
    DV = RSN.get_simulLog('V')
    DR = RSN.get_simulLog('R')
    DS = RSN.get_simulLog('S')
    DN = RSN.get_simulLog('N')

    opt = '초기셋팅' if RSN.D['시작일자'] == RSN.D['종료일자'] else '일반진행'
    
    LD = {}
    LD['add0']  = today
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
        LD[key+'_04']  = tac['add11']   # 매수금
        LD[key+'_05']  = tac['add12']   # 매도금
        LD[key+'_06']  = tac['add5']    # 변동수량
        LD[key+'_07']  = tac['add9']    # 보유수량
        LD[key+'_08']  = tac['add8']    # 현수익률
        LD[key+'_09']  = tac['add7']    # 평균단가
        LD[key+'_10']  = tac['add15']   # 현재가치
        LD[key+'_11']  = tac['add17']   # 가치합계
        LD[key+'_12']  = tac['add18']   # 수익현황    
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
    
    qry=RSN.DB.qry_insert('h_rsnLog_board',LD)
    RSN.DB.exe(qry)

    RSN.send_message(f"{today}일 VRSN 업데이트 완료")
    
    # 자산현황 업데이트
    # 초기값 설정(1차변경 2025.02.06, 2차변경 2025.02.19)
    # init_capital = 178443.0
    # jyh = 0.77746
    # jyw = 0.11127
    # jhj = 0.11127
       