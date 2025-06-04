import myutils.my_utils as my
from lib_rsn   import update_Log
from lib_lucky import update_lucky


today = my.kor_loc_date('US/Eastern')[0:10]
today = '2025-03-06'
weekd = my.dayofdate(today)
RSN = update_Log()
LUC = update_lucky()

ck_holiday = LUC.DB.exe(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday[0][0] if ck_holiday else ''

skip = (weekd in ['토','일']) or is_holiday

if  skip :
    pass

else :
    # 1. Lucky 정보 가져오기 None 이면 현재 진행중인 lucky는 없음
    set = int(LUC.DB.parameter('L0200'))
    # 2. RSN 에서 현재 S가 진행중인지 확인
    RSN.do_luckyLog(today)
    DS = RSN.get_luckyLog()
    
    if  not set : 
        
        if  DS['진행시작'] :
            
            LUC.set_new_season(DS)
            LUC.send_message(f"{today}일 LUCKY 초기셋팅 완료")

        else : 
            LUC.send_message(f"{today}일 LUCKY 모드 진행 대기")
    
    else :
        LUC.M['당일종가'] = DS['당일종가']
        LUC.M['전일종가'] = DS['전일종가']
        LUC.M['매도예가'] = DS['매도예가']
        LUC.today_check()
        LUC.send_message(f"{today}일 LUCKY 매매 결과 기록")
        # LUCKY.today_check()
        
    
    
    
       