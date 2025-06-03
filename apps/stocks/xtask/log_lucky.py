import myutils.my_utils as my
from lib_rsn   import update_Log
from lib_lucky import update_lucky


today = my.kor_loc_date('US/Eastern')[0:10]
weekd = my.dayofdate(today)
RSN = update_Log()
LUCKY = update_lucky()

ck_holiday = LUCKY.DB.exe(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday[0][0] if ck_holiday else ''

skip = (weekd in ['토','일']) or is_holiday

if  skip :
    pass

else :
    # 1. Lucky 정보 가져오기 None 이면 현재 진행중인 lucky는 없음
    set = int(LUCKY.DB.parameter('L0200'))
    # 2. RSN 에서 현재 S가 진행중인지 확인
    RSN.do_tacticsLog(today)
    DS = RSN.get_luckyLog()
    
    if  not set : 
        
        if  DS['진행시작'] :
            LD = LUCKY.do_log_setting(DS)
            LUCKY.DB.parameter_update('L0200',LD['진행시즌'])
            LUCKY.DB.parameter_update('L0201',LD['기준단가'])
            
            LUCKY.DB.parameter_update('L0215',LD['일오수량']); LUCKY.DB.parameter_update('L0216','0')
            LUCKY.DB.parameter_update('L0220',LD['이공수량']); LUCKY.DB.parameter_update('L0221','0')
            LUCKY.DB.parameter_update('L0225',LD['이오수량']); LUCKY.DB.parameter_update('L0226','0')
            LUCKY.DB.parameter_update('L0230',LD['삼공수량']); LUCKY.DB.parameter_update('L0231','0')
            
            LUCKY.send_message(f"{today}일 LUCKY 초기셋팅 완료")
        else : 
            LUCKY.send_message(f"{today}일 LUCKY 모드 진행 대기")
    
    else :
        LUCKY.send_message(f"{today}일 LUCKY 매매 결과 기록")
        # LUCKY.today_check()
        
    
    
    
       