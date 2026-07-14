import myutils.my_utils as my
from lib_diy import update_DIY


today = my.kor_loc_date('US/Eastern')[0:10]
weekd = my.dayofdate(today)
DIY = update_DIY()

ck_holiday = DIY.DB.exe(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday[0][0] if ck_holiday else ''

skip = (weekd in ['토','일']) or is_holiday

if  skip :
    pass

else :
    
    board = 'h_log315A_board'
    ini_data = DIY.DB.oneline(f"SELECT add18,add19,add1 FROM {board} ORDER BY add0 DESC LIMIT 1")
    ini_date = ini_data[0]
    ini_capt = f"{my.sv(ini_data[1]):,.2f}"
    season   = ini_data[2]
    
    DIY.do_tacticLog(ini_date,today,ini_capt)
    LD = DIY.get_simulLog()
    
    LD['uid']   = 'comphys'
    LD['uname'] = '정용훈'
    LD['wdate'] = LD['mdate'] = my.now_timestamp() 

    LD['add1'] = int(season) + 1 if LD['add2'] == 1 else season
        
    if  not LD['첫날기록'] or LD['add6'] in('익절매도','손절매도') :   
        del LD['첫날기록']  
        qry=DIY.DB.qry_insert(board,LD)
        DIY.DB.exe(qry)
        DIY.send_message(f"{today}일 DIY 업데이트 완료")
        
    else :
        DIY.send_message(f"{today}일 DIY 변동사항 없음")
         